# Renderiza o skit: python render.py [worker nworkers]  -> out/parte_<w>.mkv (ou out/video_mudo.mp4)
# Tudo em float, sem arredondar posição (nada de pixel-snapping), sem grão.
import sys, json, math, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

FPS, W, H = 30, 1080, 1920
CFG = json.load(open("cena.json"))["shots"]
TL = json.load(open("timeline.json"))
DUR = TL["dur"]; LIN = TL["linhas"]
rng = np.random.default_rng(7)
ease = lambda x: 0.5 - 0.5 * math.cos(math.pi * min(max(x, 0), 1))

# ---------- camera por plano: (foco x,y em coords do still, zoom início, zoom fim)
CAM = {
 "S7in": (430, 1085, 1.00, 1.30), "S7out": (430, 1085, 1.22, 1.00),
 "S1": (470, 820, 1.03, 1.08),
 "S2": (380, 900, 1.03, 1.08), "S2b": (370, 860, 1.17, 1.22),
 "S3": (520, 1000, 1.03, 1.08), "S3b": (520, 985, 1.16, 1.21), "S3c": (520, 990, 1.06, 1.20),
 "S4": (400, 950, 1.02, 1.07), "S4b": (390, 890, 1.18, 1.24),
 "S5": (540, 1110, 1.00, 1.10), "S5b": (540, 1110, 1.12, 1.26),
 "S6": (472, 840, 1.00, 1.04),
}
# ---------- segmentos de plano (corte 0,12 s antes da fala)
segs = [("S7in", 0.0)]
for l in LIN:
    t = max(l["t0"] - 0.12, 0.01)
    if l["shot"] != segs[-1][0]: segs.append((l["shot"], t))
segs.append(("S7out", LIN[-1]["t1"] + 0.55))
segs = [(k, t, segs[i + 1][1] if i + 1 < len(segs) else DUR) for i, (k, t) in enumerate(segs)]

# ---------- carregamento das camadas preparadas
def load(S):
    c = CFG[S]; d = {"cfg": c}
    d["full"] = np.array(Image.open(f"prep/{S}_full.png").convert("RGB"))
    d["plate"] = np.array(Image.open(f"prep/{S}_plate.png").convert("RGB")).astype(np.float32)
    d["chars"] = {}
    for n in c.get("chars", {}):
        m = np.load(f"prep/{S}_{n}_mask.npy").astype(np.float32)
        if (m > 0.5).sum() < 2000: continue   # personagem não recortado (pequeno/de costas)
        ys, xs = np.where(m > 0.05)
        pad = 24
        box = (max(xs.min() - pad, 0), max(ys.min() - 40, 0), min(xs.max() + pad, m.shape[1]), min(ys.max() + 2, m.shape[0]))
        d["chars"][n] = (m, box)
    lab = np.load(f"prep/{S}_glowlab.npy"); k = lab.max()
    ph = rng.uniform(0, 2 * np.pi, k + 1); per = rng.uniform(2.2, 4.8, k + 1)
    src = d["full"].astype(np.float32) * (lab > 0)[..., None]
    d["glow"] = (cv2.GaussianBlur(src, (0, 0), 7), ph[lab].astype(np.float32), per[lab].astype(np.float32), lab > 0)
    stars = json.load(open(f"prep/{S}_stars.json"))
    d["stars"] = [(x, y, l, rng.uniform(0, 6.28), rng.uniform(1.2, 3.5)) for x, y, l in stars]
    return d
SH = {S: load(S) for S in CFG}

# ---------- trilhas de voz -> abertura de boca por frame
import soundfile as sf
def envelope(path):
    a, sr = sf.read(path); a = a if a.ndim == 1 else a.mean(1)
    hop = sr // FPS; n = int(DUR * FPS) + 2
    rms = np.array([np.sqrt(np.mean(a[i * hop:(i + 1) * hop] ** 2)) if i * hop < len(a) else 0 for i in range(n)])
    rms = rms / (np.percentile(rms[rms > 1e-4], 92) + 1e-9)
    env = np.clip((rms - 0.10) / 0.8, 0, 1); out = np.zeros_like(env); v = 0
    for i, x in enumerate(env):  # ataque rápido, soltura suave
        v = x if x > v else v * 0.55 + x * 0.45; out[i] = v
    return out
BOCA = {"dito": envelope("audio/trilha_dito.wav"), "pc": envelope("audio/trilha_pc.wav")}

# ---------- piscadas
def piscadas(seed, a, b):
    r = np.random.default_rng(seed); t, out = 0.6, []
    while t < DUR: out.append(t); t += r.uniform(a, b)
    return out
PISCA = {"dito": piscadas(1, 2.4, 4.6), "pc": piscadas(2, 3.0, 5.5)}
def fechamento(q, t):
    for b in PISCA[q]:
        x = (t - b) * FPS
        if 0 <= x < 5: return [0.5, 1, 1, 0.6, 0.2][int(x)]
    return 0.0

# ---------- expressão do PC por fala
L_ = lambda n: next(l for l in LIN if l["n"] == n)
def expressao_pc(t):
    if L_(8)["t0"] - 0.05 <= t < L_(9)["t0"] - 0.15: return "404"          # tela de erro na pausa "segundos depois"
    if L_(16)["t0"] - 0.6 <= t <= L_(18)["t1"] + 0.3: return "terno"
    return "convencido"

OLHOS = {
 "convencido": ["111111", "111111", "011111", "001110"],
 "aberto":     ["011110", "111111", "111111", "111111", "011110"],
 "terno":      ["011110", "111001", "111001", "111111", "111111", "011110"],
 "fechado":    ["000000", "000000", "111111"],
}
DIG = {"4": ["101", "101", "111", "001", "001"], "0": ["111", "101", "101", "101", "111"]}
def boca_pc(k, expr):
    if k == 0: return ["011110"] if expr == "terno" else ["000110", "011100"]
    return ["011110"] + ["111111"] * (k - 1) + ["011110"]

def desenha_pc(img, f, t, falando):
    (ex0, ey0, ex1, ey1), (fx0, fy0, fx1, fy1) = f["eyes"]
    u = ((ex1 - ex0) + (fx1 - fx0)) / 12
    expr = expressao_pc(t)
    cel = []
    if expr == "404":  # escreve 404 em pixel no meio da tela, sem olhos nem boca
        x0, y0, x1, y1 = f["screen"]; U = u * 1.25
        gx = (x0 + x1) / 2 - 5.5 * U; gy = (ey0 + ey1 + fy0 + fy1) / 4 - 2.5 * U + u
        for k, ch in enumerate("404"):
            for r, row in enumerate(DIG[ch]):
                for c, v in enumerate(row):
                    if v == "1": cel.append((gx + (k * 4 + c) * U, gy + r * U))
        falando = 0; u = U
    shape = OLHOS["fechado"] if fechamento("pc", t) > 0.5 else OLHOS.get(expr, OLHOS["convencido"])
    if expr == "404": shape = []
    for (x0, y0, x1, y1) in f["eyes"]:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        gx, gy = cx - 3 * u, cy - len(shape) * u / 2
        for r, row in enumerate(shape):
            for c, v in enumerate(row):
                if v == "1": cel.append((gx + c * u, gy + r * u))
    k = int(round(falando * 3.2)) if falando > 0.08 else 0
    bm = [] if expr == "404" else boca_pc(min(k, 3), expr)
    mx = (ex0 + ex1 + fx0 + fx1) / 4; my = max(ey1, fy1) + 2.2 * u
    for r, row in enumerate(bm):
        for c, v in enumerate(row):
            if v == "1": cel.append((mx - 3 * u + c * u, my + r * u))
    x0, y0, x1, y1 = f["screen"]; pad = int(4 * u) + 10
    X0, Y0, X1, Y1 = int(x0) - pad, int(y0) - pad, int(x1) + pad, int(y1) + pad
    core = np.zeros((Y1 - Y0, X1 - X0), np.float32)
    S = 4  # supersample pra borda suave sem tremido
    big = np.zeros(((Y1 - Y0) * S, (X1 - X0) * S), np.uint8)
    for (px, py) in cel:
        cv2.rectangle(big, (int((px - X0) * S), int((py - Y0) * S)), (int((px + u * 0.92 - X0) * S), int((py + u * 0.92 - Y0) * S)), 255, -1)
    core = cv2.resize(big, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    glow = cv2.GaussianBlur(core, (0, 0), u * 0.9)
    roi = img[Y0:Y1, X0:X1].astype(np.float32)
    roi += glow[..., None] * np.array([40, 230, 170], np.float32) * 0.9
    roi = roi * (1 - core[..., None]) + core[..., None] * np.array([200, 255, 232], np.float32)
    img[Y0:Y1, X0:X1] = roi.clip(0, 255).astype(np.uint8)

def desenha_dito(img, f, t, falando):
    S = 4
    cx, cy, w, tilt = f["mouth"]
    if falando > 0.06:
        X0, Y0 = int(cx - w), int(cy - w * 0.6); X1, Y1 = int(cx + w), int(cy + w * 0.9)
        big = np.zeros(((Y1 - Y0) * S, (X1 - X0) * S), np.uint8); teeth = big.copy()
        ax, ay = w * 0.36, max(w * 0.30 * falando, 1.4)
        c = ((cx - X0) * S, (cy - Y0 + ay * 0.55) * S)
        cv2.ellipse(big, (int(c[0]), int(c[1])), (int(ax * S), int(ay * S)), tilt, 0, 360, 255, -1, cv2.LINE_AA)
        if falando > 0.45:
            cv2.ellipse(teeth, (int(c[0]), int(c[1] - ay * S * 0.55)), (int(ax * S * 0.8), int(ay * S * 0.35)), tilt, 0, 360, 255, -1, cv2.LINE_AA)
        m = cv2.resize(big, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA).astype(np.float32)[..., None] / 255
        tm = cv2.resize(teeth, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA).astype(np.float32)[..., None] / 255 * m
        roi = img[Y0:Y1, X0:X1].astype(np.float32)
        roi = roi * (1 - m) + m * np.array([52, 20, 18], np.float32)
        roi = roi * (1 - tm) + tm * np.array([226, 214, 204], np.float32)
        img[Y0:Y1, X0:X1] = roi.clip(0, 255).astype(np.uint8)
    fe = fechamento("dito", t)
    if fe > 0:
        for (ex, ey, rx, ry) in f["eyes"]:
            X0, Y0, X1, Y1 = int(ex - rx - 4), int(ey - ry - 8), int(ex + rx + 4), int(ey + ry + 4)
            pele = img[max(Y0 - 2, 0):Y0 + 3, int(ex - 3):int(ex + 3)].reshape(-1, 3).mean(0) * 0.96
            big = np.zeros(((Y1 - Y0) * S, (X1 - X0) * S), np.uint8)
            cv2.ellipse(big, (int((ex - X0) * S), int((ey - Y0) * S)), (int((rx + 2) * S), int((ry + 2) * S)), 0, 0, 360, 255, -1, cv2.LINE_AA)
            lid = int((ey - ry - 2 + (2 * ry + 4) * fe - Y0) * S); big[lid:] = 0
            m = cv2.resize(big, (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_AREA).astype(np.float32)[..., None] / 255
            roi = img[Y0:Y1, X0:X1].astype(np.float32)
            roi = roi * (1 - m) + m * pele
            if fe > 0.8:  # linha dos cílios
                ly = ey - ry - 2 + (2 * ry + 4) * fe - 1
                cv2.ellipse(roi, (int((ex - X0) * 4), int((ly - Y0 - ry * 0.3) * 4)), (int(rx * 4), int(ry * 0.3 * 4)), 0, 20, 160, (60, 34, 28), 2, cv2.LINE_AA, 2)
            img[Y0:Y1, X0:X1] = roi.clip(0, 255).astype(np.uint8)

# ---------- legendas e cards
F = lambda p, s: ImageFont.truetype(p, s)
FT = {"900": "assets/fonts/Montserrat-900.ttf", "800": "assets/fonts/Montserrat-800.ttf", "700": "assets/fonts/Montserrat-700.ttf"}
CAP = F(FT["900"], 74)
COR = {"dito": (255, 216, 74), "pc": (124, 255, 212)}
def blocos(pal):
    out, cur = [], []
    for p in pal:
        cur.append(p)
        if len(cur) == 3 or p["w"][-1] in ",.?!" and len(cur) >= 2: out.append(cur); cur = []
    if cur:
        if len(cur) == 1 and out and len(out[-1]) < 4: out[-1] += cur
        else: out.append(cur)
    return out
CHUNKS = []
for l in LIN:
    bs = blocos(l["palavras"])
    for i, b in enumerate(bs):
        fim = bs[i + 1][0]["t0"] if i + 1 < len(bs) else l["t1"] + 0.25
        CHUNKS.append((b[0]["t0"] - 0.04, fim, b, l["quem"]))

def legenda(draw, t, y):
    for (a, b, ws, q) in CHUNKS:
        if a <= t < b:
            vis = [p for p in ws if p["t0"] - 0.04 <= t]
            txt = " ".join(p["w"] for p in ws)
            tw = draw.textlength(txt, font=CAP); x = (W - tw) / 2
            for p in ws:
                pw = draw.textlength(p["w"] + " ", font=CAP)
                if p in vis:
                    k = min((t - p["t0"] + 0.04) / 0.10, 1)
                    atual = p["t0"] - 0.04 <= t < p["t1"] + 0.05
                    cor = COR[q] if atual else (255, 255, 255)
                    dy = (1 - k) * 10
                    draw.text((x, y + dy), p["w"], font=CAP, fill=cor + (int(255 * k),), stroke_width=7, stroke_fill=(18, 14, 26, int(235 * k)))
                x += pw
            return

CARDS = [(7, "1", "PEÇA A FONTE", "e abra o link"), (10, "2", "PERGUNTE DE NOVO", "se mudar, desconfie"), (15, "3", "CONFIRA FORA", "em outra fonte")]
def card_img(num, tit, sub):
    w, h = 860, 150; im = Image.new("RGBA", (w + 40, h + 40)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 26, 20 + w, 26 + h), 34, fill=(0, 0, 0, 90))
    d.rounded_rectangle((20, 20, 20 + w, 20 + h), 34, fill=(12, 26, 38, 225), outline=(124, 255, 212, 255), width=4)
    d.ellipse((48, 45, 148, 145), fill=(124, 255, 212, 255))
    fn = F(FT["900"], 58); d.text((98, 95), num, font=fn, fill=(12, 26, 38, 255), anchor="mm")
    d.text((176, 58), tit, font=F(FT["900"], 50), fill=(255, 255, 255, 255))
    d.text((178, 118), sub, font=F(FT["700"], 32), fill=(184, 255, 236, 255))
    return im
CARD_IM = [card_img(n, a, b) for _, n, a, b in CARDS]
T_CARD = {c[0]: next(l["t0"] for l in LIN if l["n"] == c[0]) for c in CARDS}

def cards(frame_rgba, t, seg_key):
    if seg_key != "S6": return
    for i, (n, *_r) in enumerate(CARDS):
        t0 = T_CARD[n] - 0.05
        if t < t0: continue
        x = min((t - t0) / 0.32, 1); s = 1 + 0.12 * math.sin(math.pi * x) * (1 - x) - 0.15 * (1 - x) ** 3
        im = CARD_IM[i]
        if x < 1:
            im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
            a = im.getchannel("A").point(lambda v: int(v * min(x * 1.8, 1))); im.putalpha(a)
        y = 170 + i * 175 + (CARD_IM[i].height - im.height) / 2
        frame_rgba.alpha_composite(im, (int((W - im.width) / 2), int(y)))

VIG = None
def vinheta():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    return (1 - 0.22 * np.clip(r - 0.55, 0, 1) ** 1.5 / 0.45 ** 1.5).clip(0.75, 1)[..., None]
VIG = vinheta()

def estica(layer, mask, box, sy, sx=1.0):
    x0, y0, x1, y1 = box
    ax, ay = (x0 + x1) / 2 - x0, y1 - y0
    M = np.array([[sx, 0, (1 - sx) * ax], [0, sy, (1 - sy) * ay]], np.float32)
    L = cv2.warpAffine(layer[y0:y1, x0:x1], M, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    Mk = cv2.warpAffine(mask[y0:y1, x0:x1], M, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR)
    return L, Mk

def quadro(i):
    t = i / FPS
    key, s0, s1 = next(s for s in segs if s[1] <= t < s[2]) if t < segs[-1][2] else segs[-1]
    S = key[:2]; d = SH[S]; c = d["cfg"]
    img = d["plate"].copy()
    # fundo vivo: flores/luzes pulsando + estrelas piscando
    gsrc, ph, per, gm = d["glow"]
    puls = 0.32 * np.sin(2 * np.pi * t / per + ph)
    img += gsrc * cv2.GaussianBlur(puls * gm, (0, 0), 5)[..., None] * 1.6
    for (x, y, l, p, f) in d["stars"]:
        a = (0.5 + 0.5 * math.sin(2 * math.pi * t / f + p)) * 160 * l
        x0, y0 = int(x) - 2, int(y) - 2
        if 0 <= x0 < img.shape[1] - 5 and 0 <= y0 < img.shape[0] - 5:
            img[y0:y0 + 5, x0:x0 + 5] += STAR[..., None] * a
    # personagens: rosto desenhado + respiração
    for n, (m, box) in d["chars"].items():
        lay = d["full"].copy()
        fal = BOCA[n][i]
        if n == "dito" and "dito_face" in c: desenha_dito(lay, c["dito_face"], t, fal)
        if n == "pc" and "pc_face" in c: desenha_pc(lay, c["pc_face"], t, fal)
        if n == "dito": sy = 1 + 0.0055 * (0.5 - 0.5 * math.cos(2 * math.pi * t / 3.7)) + 0.004 * fal
        else: sy = 1 + 0.004 * (0.5 - 0.5 * math.cos(2 * math.pi * t / 2.9 + 1)) + 0.012 * fal
        L, Mk = estica(lay, m, box, sy, 1 + (sy - 1) * 0.25)
        x0, y0, x1, y1 = box
        roi = img[y0:y1, x0:x1]
        img[y0:y1, x0:x1] = roi * (1 - Mk[..., None]) + L.astype(np.float32) * Mk[..., None]
    # rosto do PC quando ele não tem recorte próprio (ex.: S1)
    if "pc_face" in c and "pc" not in d["chars"]:
        tmp = img.clip(0, 255).astype(np.uint8); desenha_pc(tmp, c["pc_face"], t, BOCA["pc"][i]); img = tmp.astype(np.float32)
    # câmera
    fx, fy, z0, z1 = CAM[key]
    z = z0 + (z1 - z0) * ease((t - s0) / max(s1 - s0, 0.01))
    h, w = img.shape[:2]; sc = (W / w) * z
    vw, vh = w / z, h / z
    cx = min(max(fx, vw / 2), w - vw / 2); cy = min(max(fy, vh / 2), h - vh / 2)
    M = np.array([[sc, 0, W / 2 - cx * sc], [0, sc, H / 2 - cy * sc]], np.float32)
    out = cv2.warpAffine(img.clip(0, 255), M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    out = (out * VIG).clip(0, 255).astype(np.uint8)
    fr = Image.fromarray(out).convert("RGBA")
    ov = Image.new("RGBA", (W, H)); cards(ov, t, key)
    legenda(ImageDraw.Draw(ov), t, CFG[S]["caption_y"] if S != "S6" else 760)
    fr.alpha_composite(ov)
    # fade de entrada/saída
    k = min(t / 0.5, (DUR - t) / 0.6, 1)
    arr = np.asarray(fr.convert("RGB"))
    return arr if k >= 1 else (arr * max(k, 0)).astype(np.uint8)

yy, xx = np.mgrid[-2:3, -2:3]; STAR = np.exp(-(xx ** 2 + yy ** 2) / 1.2).astype(np.float32)

if __name__ == "__main__":
    import os; os.makedirs("out", exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "frame":   # python render.py frame 12.5 arquivo.jpg
        Image.fromarray(quadro(int(float(sys.argv[2]) * FPS))).save(sys.argv[3], quality=92); sys.exit()
    wk, nw = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (0, 1)
    N = int(DUR * FPS); per = math.ceil(N / nw); a, b = wk * per, min(N, (wk + 1) * per)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", f"out/parte_{wk}.mkv"], stdin=subprocess.PIPE)
    import time; t0 = time.time()
    for i in range(a, b):
        ff.stdin.write(quadro(i).tobytes())
        if (i - a) % 60 == 0: print(f"w{wk} {i - a}/{b - a} {time.time() - t0:.0f}s", flush=True)
    ff.stdin.close(); ff.wait(); print(f"w{wk} ok")
