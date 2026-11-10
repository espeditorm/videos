"""Segunda passada: tinta e pintura de cada quadro.
Lê o EXR do Eevee (cor de tinta, luz de cel, ids, profundidade, normais; mar numa camada separada),
pinta céu e fundos como guache, aplica cel com sombra lavanda, traça linhas de nanquim, desenha os
efeitos em dois quadros (água em lâminas com coroa de espuma, raios, faíscas, chuva) e finaliza.
Uso: python3 inkpaint.py states.pkl exrdir outdir f0 f1 [step]
"""
import sys, os, math, pickle, json
import numpy as np, cv2, OpenEXR, Imath

W_, H_ = 1920, 1080

# ------------------------------------------------------------------ EXR
def read_exr(path):
    f = OpenEXR.InputFile(path)
    hdr = f.header(); dw = hdr['dataWindow']; w = dw.max.x - dw.min.x + 1; h = dw.max.y - dw.min.y + 1
    pt = Imath.PixelType(Imath.PixelType.FLOAT)
    out = {}
    for ch in hdr['channels']:
        out[ch] = np.frombuffer(f.channel(ch, pt), np.float32).reshape(h, w)
    return out, w, h

def get(ch, *names, default=None):
    for n in names:
        if n in ch: return ch[n]
    if default is not None: return default
    raise KeyError(names[0] + ' / have: ' + ', '.join(sorted(ch)[:60]))

# ------------------------------------------------------------------ cores
def hexc(h): h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255
def mix(a, b, u): return a + (b - a) * u
def smooth(a, b, x):
    u = np.clip((x - a) / (b - a), 0, 1); return u * u * (3 - 2 * u)

INK = hexc('#2b1f27')
SKY_TOP, SKY_MID, SKY_HOR = hexc('#1d4fc9'), hexc('#3d8fe6'), hexc('#a9dcf7')
DAWN = hexc('#ffd6a0')
STORM_TOP, STORM_HOR = hexc('#262a5c'), hexc('#5b6a9a')
SEA_NEAR, SEA_FAR = hexc('#20b6c4'), hexc('#1b4fae')
STORM_SEA_NEAR, STORM_SEA_FAR = hexc('#2a7f92'), hexc('#223a7a')
SHADOW_TINT = np.array([0.60, 0.60, 0.86], np.float32)
SUN_TINT = np.array([1.04, 0.99, 0.93], np.float32)

# ------------------------------------------------------------------ câmera
def cam_rays(st, w, h):
    M = np.array(st['cam']); lens = st['lens']; sw = 36.0
    fx = lens / sw * w
    xs = (np.arange(w) + 0.5 - w / 2) / fx; ys = -(np.arange(h) + 0.5 - h / 2) / fx
    X, Y = np.meshgrid(xs, ys)
    d_cam = np.stack([X, Y, -np.ones_like(X)], -1)       # câmera olha para -Z
    R = M[:3, :3]; o = M[:3, 3]
    d_w = d_cam @ R.T
    return o, d_w, d_cam, fx

def project(st, P, w=None, h=None):
    """Mundo -> pixel (x, y, profundidade). P: (...,3)."""
    w = w or W_; h = h or H_
    M = np.array(st['cam']); R = M[:3, :3]; o = M[:3, 3]
    fx = st['lens'] / 36.0 * w
    q = (np.asarray(P, float) - o) @ R
    z = -q[..., 2]
    x = q[..., 0] / np.maximum(z, 1e-3) * fx + w / 2; y = -q[..., 1] / np.maximum(z, 1e-3) * fx + h / 2
    return x, y, z

# ------------------------------------------------------------------ ruídos estáveis no mundo
def hash3(ix, iy, iz):
    h = (ix * 374761393 + iy * 668265263 + iz * 2147483647) & 0xFFFFFFFF
    h = (h ^ (h >> 13)) * 1274126177 & 0xFFFFFFFF
    return (h & 0xFFFF) / 65535.0

def value_noise(P, scale):
    """Ruído de valor 3D (para textura de pincel presa ao mundo)."""
    p = P / scale; i = np.floor(p).astype(np.int64); fr = p - i
    fr = fr * fr * (3 - 2 * fr)
    acc = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (fr[..., 0] if dx else 1 - fr[..., 0]) * (fr[..., 1] if dy else 1 - fr[..., 1]) * (fr[..., 2] if dz else 1 - fr[..., 2])
                acc = acc + w * hash3(i[..., 0] + dx, i[..., 1] + dy, i[..., 2] + dz)
    return acc

# ------------------------------------------------------------------ Kuwahara (guache)
def kuwahara(img, r):
    """Filtro de Kuwahara clássico via médias em caixa: deixa massas de cor chapadas com bordas de pincel."""
    k = r + 1
    mean = cv2.blur(img, (k, k), borderType=cv2.BORDER_REFLECT)
    sq = cv2.blur(img * img, (k, k), borderType=cv2.BORDER_REFLECT)
    var = (sq - mean * mean).sum(-1)
    best = None; bvar = None
    for dx in (-r // 2, r // 2):
        for dy in (-r // 2, r // 2):
            M = np.float32([[1, 0, dx], [0, 1, dy]])
            m = cv2.warpAffine(mean, M, (img.shape[1], img.shape[0]), borderMode=cv2.BORDER_REFLECT)
            v = cv2.warpAffine(var, M, (img.shape[1], img.shape[0]), borderMode=cv2.BORDER_REFLECT)
            if best is None: best, bvar = m, v
            else:
                sel = v < bvar; best[sel] = m[sel]; bvar = np.minimum(bvar, v)
    return best

PAPER = None
def paper(h, w):
    global PAPER
    if PAPER is None or PAPER.shape[:2] != (h, w):
        r = np.random.default_rng(3)
        n = r.normal(0, 1, (h // 2 + 1, w // 2 + 1)).astype(np.float32)
        n = cv2.GaussianBlur(n, (0, 0), 1.2)
        n = cv2.resize(n, (w, h), interpolation=cv2.INTER_LINEAR)
        n2 = cv2.resize(r.normal(0, 1, (h // 24 + 1, w // 24 + 1)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
        PAPER = (n * 0.6 + n2 * 0.4)
    return PAPER

# ------------------------------------------------------------------ linhas
def ink_lines(oid, lid, depth, nrm, cat, valid, scale):
    """Contorno onde muda objeto/material, onde a profundidade salta e onde a normal dobra."""
    e = np.zeros(oid.shape, bool)
    for a, b in (((slice(None), slice(1, None)), (slice(None), slice(None, -1))), ((slice(1, None), slice(None)), (slice(None, -1), slice(None)))):
        dl = np.abs(lid[a] - lid[b]) > 0.5 / 64
        doid = np.abs(oid[a] - oid[b]) > 0.5
        da, db = depth[a], depth[b]
        dd = np.abs(da - db) > 0.035 * np.minimum(da, db) + 0.6
        dn = (nrm[a] * nrm[b]).sum(-1) < 0.80
        va, vb = valid[a], valid[b]
        edge = (va | vb) & ((va != vb) | dl | doid | dd | dn)
        # nuvens, céu e mar não levam traço; cachoeira e tromba só no recorte
        ca, cb = cat[a], cat[b]
        quiet = ((ca == 5) & (cb == 5)) | ((ca == 5) & ~vb) | ((cb == 5) & ~va)
        quiet |= ((ca == 6) & (cb == 6) & ~dd)
        edge &= ~quiet
        ee = np.zeros_like(e); ee[a] |= edge; e |= ee
    return e

def draw_lines(img, edges, width_map, color):
    if not edges.any(): return img
    inv = (~edges).astype(np.uint8)
    dist, lab = cv2.distanceTransformWithLabels(inv, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    ys, xs = np.nonzero(edges)
    lut = np.zeros(lab.max() + 1, np.float32)
    # rótulos dos pixels de borda -> largura desejada naquela borda
    lut[lab[ys, xs]] = width_map[ys, xs]
    wpx = lut[lab]
    a = np.clip(wpx * 0.5 + 0.5 - dist, 0, 1)[..., None]
    return img * (1 - a) + color * a

# ------------------------------------------------------------------ efeitos 2D
RNG = lambda s: np.random.default_rng(s)
def poly(img, pts, col, alpha=1.0):
    if len(pts) < 3: return
    ov = img.copy()
    cv2.fillPoly(ov, [np.round(np.asarray(pts) * 4).astype(np.int32)], col.tolist(), lineType=cv2.LINE_AA, shift=2)
    img[:] = img * (1 - alpha) + ov * alpha if alpha < 1 else ov
def pline(img, pts, col, w):
    cv2.polylines(img, [np.round(np.asarray(pts) * 4).astype(np.int32)], False, col.tolist(), max(1, int(round(w))), lineType=cv2.LINE_AA, shift=2)

def draw_fx(img, st, glow):
    h, w = img.shape[:2]
    for kind, p in st['fx']:
        if kind == 'bolt': fx_bolt(img, st, p, glow)
        elif kind == 'discharge': fx_discharge(img, st, p, glow)
        elif kind == 'sparks': fx_sparks(img, st, p, glow)
        elif kind in ('splash',): fx_splash(img, st, p)
        elif kind == 'wake': fx_wake(img, st, p)
        elif kind == 'legfoam': fx_legfoam(img, st, p)
        elif kind == 'waterfall': fx_waterfall(img, st, p)
        elif kind in ('debris', 'rustflakes', 'dust', 'bubbles'): fx_bits(img, st, p, kind)
        elif kind == 'rain': fx_rain(img, st, p)
        elif kind == 'spoutspray': fx_spoutspray(img, st, p)
        elif kind == 'tautlines': fx_taut(img, st, p)

def fx_bolt(img, st, p, glow):
    r = RNG(p['seed'])
    a = np.array(p['a'], float); b = np.array(p['b'], float)
    pts = [a]; n = 14
    for i in range(1, n):
        q = a + (b - a) * i / n
        q += np.array([r.normal(0, 40), r.normal(0, 40), 0]) * (1 - abs(i / n - 0.5)) * (1.0 if p['main'] else 2.5)
        pts.append(q)
    pts.append(b)
    x, y, z = project(st, np.array(pts))
    if (z < 1).any(): return
    P2 = np.stack([x, y], 1)
    life = 1.0 if p['age'] < 0.12 else max(0.0, 1 - (p['age'] - 0.12) / 0.3)
    wmain = 9 if p['main'] else 4
    cv2.polylines(glow, [np.round(P2 * 4).astype(np.int32)], False, (0.55 * life, 0.75 * life, 1.0 * life), int(wmain * 7), cv2.LINE_AA, 2)
    pline(img, P2, hexc('#ffffff') * 1.0, wmain)
    # galhos
    for k in range(3):
        i = r.integers(2, n - 2); q0 = np.array(pts[i]); br = [q0]
        for j in range(4): br.append(br[-1] + np.array([r.normal(0, 50), r.normal(0, 50), -abs(r.normal(80, 30))]))
        bx, by, bz = project(st, np.array(br))
        if (bz > 1).all(): pline(img, np.stack([bx, by], 1), hexc('#e8f4ff'), max(1, wmain // 3))

def fx_discharge(img, st, p, glow):
    r = RNG(p['seed']); P = np.array(p['pts'])
    for k in range(5):
        jit = P + r.normal(0, 3.5, P.shape)
        x, y, z = project(st, jit)
        if (z < 1).any(): continue
        P2 = np.stack([x, y], 1)
        cv2.polylines(glow, [np.round(P2 * 4).astype(np.int32)], False, (0.3, 0.6, 1.0), 26, cv2.LINE_AA, 2)
        pline(img, P2, hexc('#dff4ff'), 2)

def fx_sparks(img, st, p, glow):
    r = RNG(p['seed']); c = np.array(p['c']); age = p['age']
    for i in range(p['n']):
        d = r.normal(0, 1, 3); d /= np.linalg.norm(d); sp = r.uniform(0.4, 1.0) * p['r']
        a = c + d * sp * min(1, age * 3); b = a + d * 3 + np.array([0, 0, -age * 6])
        x, y, z = project(st, np.array([a, b]))
        if (z < 1).any(): continue
        life = max(0, 1 - age / 1.2)
        cv2.line(glow, (int(x[0] * 4), int(y[0] * 4)), (int(x[1] * 4), int(y[1] * 4)), (0.4 * life, 0.7 * life, 1.0 * life), 10, cv2.LINE_AA, 2)
        pline(img, np.stack([x, y], 1), hexc('#fffbe8'), 2)

def fx_bits(img, st, p, kind):
    r = RNG(p['seed']); c = np.array(p['c']); age = p['age']
    n = p.get('n', 24); rr = p.get('r', 10)
    col = {'debris': hexc('#c94a40'), 'rustflakes': hexc('#a0532e'), 'dust': hexc('#d8cfc0'), 'bubbles': hexc('#e8fbff')}[kind]
    for i in range(n):
        d = r.normal(0, 1, 3); d[2] = abs(d[2]) * (1 if kind != 'rustflakes' else 0.3)
        q = c + d * rr * (0.3 + age) + np.array([0, 0, (-9.8 * age * age * (0.6 if kind != 'bubbles' else -0.4))])
        x, y, z = project(st, q[None])
        if z[0] < 1: continue
        s = max(1.5, 900 / z[0] * r.uniform(0.5, 1.4))
        if kind == 'dust':
            cv2.circle(img, (int(x[0] * 4), int(y[0] * 4)), int(s * 6 * (1 + age)), (col * (1 - age)).tolist() if False else col.tolist(), -1, cv2.LINE_AA, 2)
        else:
            ang = r.uniform(0, 6.28) + age * 8
            pts = [(x[0] + math.cos(ang + k * 2.1) * s, y[0] + math.sin(ang + k * 2.1) * s * 0.6) for k in range(3)]
            poly(img, pts, col)

def _sea_pts(st, c, r, n, z0=0.0):
    a = np.linspace(0, 2 * math.pi, n, endpoint=False)
    return np.stack([c[0] + np.cos(a) * r, c[1] + np.sin(a) * r, np.full(n, z0)], 1)

def fx_splash(img, st, p):
    """Lâmina de água entintada com coroa de espuma: sobe e cai em dois quadros."""
    r = RNG(p['seed']); c = np.array(p['c'], float); age = p['age']; S = p['size']
    up = math.sin(min(1.0, age / 1.1) * math.pi) * S * 1.4
    spread = S * (0.6 + age * 0.9)
    n = 18
    base = _sea_pts(st, c, spread * 0.55, n)
    tops = []
    for i in range(n):
        a = i / n * math.tau
        hgt = up * (0.6 + 0.4 * math.sin(a * 3 + p['seed'])) * r.uniform(0.7, 1.1)
        tops.append(c + np.array([math.cos(a) * spread, math.sin(a) * spread, hgt]))
    tops = np.array(tops)
    bx, by, bz = project(st, base); tx, ty, tz = project(st, tops)
    if (bz < 1).any() or (tz < 1).any(): return
    # ordena pelo ângulo na tela: um anel de lâminas
    for i in range(n):
        j = (i + 1) % n
        quad = [(bx[i], by[i]), (tx[i], ty[i]), (tx[j], ty[j]), (bx[j], by[j])]
        shade = hexc('#bfeef5') if math.sin(i / n * math.tau) > 0 else hexc('#7fd3e0')
        poly(img, quad, shade, 0.9)
    # contorno e coroa de espuma
    pline(img, np.stack([tx, ty], 1)[list(range(n)) + [0]], INK * 255 / 255, 2)
    for i in range(n):
        s = float(np.clip(900 / tz[i], 2, 14)) * r.uniform(0.6, 1.2)
        cv2.circle(img, (int(tx[i] * 4), int(ty[i] * 4)), int(s * 4), (1, 1, 1), -1, cv2.LINE_AA, 2)
        cv2.circle(img, (int(tx[i] * 4), int(ty[i] * 4)), int(s * 4), tuple(float(v) for v in INK), 4, cv2.LINE_AA, 2)
        # gotas soltas caindo
        if age > 0.3:
            for k in range(2):
                q = tops[i] + np.array([r.normal(0, S * 0.3), r.normal(0, S * 0.3), -age * 20 * r.uniform(0.5, 1)])
                x, y, z = project(st, q[None])
                if z[0] > 1: cv2.circle(img, (int(x[0] * 4), int(y[0] * 4)), int(max(2, 1200 / z[0]) * 4), (1, 1, 1), -1, cv2.LINE_AA, 2)
    # anel de espuma na água
    ring = _sea_pts(st, c, spread * 1.1, 40); x, y, z = project(st, ring)
    if (z > 1).all(): pline(img, np.stack([x, y], 1)[list(range(40)) + [0]], hexc('#ffffff'), float(np.clip(900 / z.mean(), 1.5, 6)))

def fx_wake(img, st, p):
    c = np.array(p['c']); r = RNG(p['seed'])
    for k in range(3):
        rr = p['w'] * (0.6 + k * 0.5)
        ring = _sea_pts(st, c + np.array([r.normal(0, 2), r.normal(0, 2), 0]), rr, 28)
        x, y, z = project(st, ring)
        if (z > 1).all(): pline(img, np.stack([x, y], 1)[list(range(28)) + [0]], hexc('#ffffff'), float(np.clip(700 / z.mean(), 1.2, 5)) * (1 - k * 0.25))

def fx_legfoam(img, st, p):
    c = np.array(p['c']); r = RNG(p['seed'])
    ring = _sea_pts(st, c, p['r'] * r.uniform(0.95, 1.15), 24)
    ring[:, 2] += r.uniform(0, 1.2, 24)
    x, y, z = project(st, ring)
    if (z > 1).all():
        pts = np.stack([x, y], 1)
        pline(img, pts[list(range(24)) + [0]], hexc('#ffffff'), float(np.clip(700 / z.mean(), 1.5, 5)))

def fx_waterfall(img, st, p):
    """Cascata da borda: lâmina branca entintada que se desfaz em névoa no vazio."""
    top = np.array(p['top']); o = np.array([*p['out'], 0.0]); f = p['f']
    side = np.cross(o, [0, 0, 1.0])
    pts_l, pts_r = [], []
    for k in range(12):
        dz = k * 22.0
        spread = 5 + k * 1.6
        wob = math.sin(f * 0.5 + k) * 0.8
        c = top + o * (3 + k * 1.5) + np.array([0, 0, -dz])
        pts_l.append(c - side * (spread + wob)); pts_r.append(c + side * (spread - wob))
    P = np.array(pts_l + pts_r[::-1])
    x, y, z = project(st, P)
    if (z < 1).any(): return
    poly(img, np.stack([x, y], 1), hexc('#eefaff'), 0.85)
    for k in range(1, 4):
        q = np.array(pts_l[k * 3]) * 0.5 + np.array(pts_r[k * 3]) * 0.5
        xx, yy, zz = project(st, np.array([q, q + np.array([0, 0, -14.0])]))
        pline(img, np.stack([xx, yy], 1), hexc('#bfe4f2'), max(1, 1600 / zz.mean()))
    # névoa na ponta
    x2, y2, z2 = project(st, (np.array(pts_l[-1]) + np.array(pts_r[-1]))[None] / 2)
    if z2[0] > 1:
        rad = int(max(6, 9000 / z2[0])); h, w = img.shape[:2]
        x0, y0 = int(x2[0]), int(y2[0])
        ys, xs = np.ogrid[max(0, y0 - 3 * rad):min(h, y0 + 3 * rad), max(0, x0 - 3 * rad):min(w, x0 + 3 * rad)]
        if ys.size and xs.size:
            m = np.exp(-((xs - x0) ** 2 + ((ys - y0) * 1.6) ** 2) / (2 * rad * rad))[..., None] * 0.55
            reg = img[max(0, y0 - 3 * rad):min(h, y0 + 3 * rad), max(0, x0 - 3 * rad):min(w, x0 + 3 * rad)]
            reg[:] = reg + (np.array([0.93, 0.97, 1.0]) - reg) * m

def fx_rain(img, st, p):
    r = RNG(p['f'] // 2 * 7 + 1)
    h, w = img.shape[:2]; k = w / 1920
    n = int(420 * p['amount'])
    lay = np.zeros_like(img)
    xs = r.uniform(-100, w + 100, n); ys = r.uniform(-100, h, n); L = r.uniform(26, 60, n) * k
    for x, y, l in zip(xs, ys, L):
        cv2.line(lay, (int(x * 4), int(y * 4)), (int((x - l * 0.22) * 4), int((y + l) * 4)), (1, 1, 1), 4, cv2.LINE_AA, 2)
    img[:] = img + (np.array([0.80, 0.86, 0.97]) - img) * lay * 0.28

def fx_spoutspray(img, st, p):
    c = np.array(p['c']); r = RNG(p['f'] // 2)
    for k in range(3):
        ring = _sea_pts(st, c, 40 + k * 22 + r.uniform(0, 6), 30); ring[:, 2] += r.uniform(0, 18, 30) * (3 - k)
        x, y, z = project(st, ring)
        if (z > 1).all(): poly(img, np.stack([x, y], 1), hexc('#c9d6ec'), 0.35)

def fx_taut(img, st, p):
    P = np.array(p['pts']); age = p['age']
    x, y, z = project(st, P)
    if (z < 1).any(): return
    for k in (-1, 1):
        off = k * (6 + age * 10)
        pline(img, np.stack([x, y + off], 1), hexc('#ffffff') * 0.9, 2)

# ------------------------------------------------------------------ quadro
def paint_frame(st, exr):
    global W_, H_
    ch, w, h = read_exr(exr)
    W_, H_ = w, h
    t = st['t']
    def g(n, *alts): return get(ch, *[f'main.{a}' for a in (n,) + alts])
    base = np.stack([g('base.R'), g('base.G'), g('base.B')], -1)
    alpha = get(ch, 'main.Combined.A')
    lit = g('lit.X', 'lit.V', 'lit.R')
    lid = g('lid.X', 'lid.V', 'lid.R'); cat = np.round(g('cat.X', 'cat.V', 'cat.R') * 16).astype(np.int32)
    oid = g('oid.X'); depth = g('Depth.Z')
    nrm = np.stack([g('Normal.X'), g('Normal.Y'), g('Normal.Z')], -1)
    sdepth = get(ch, 'sea.Depth.Z'); salpha = get(ch, 'sea.Combined.A')
    valid = alpha > 0.5
    cat = np.where(valid, cat, -1)
    o, d_w, d_cam, fx = cam_rays(st, w, h)
    # mundo de cada pixel (Z do Blender = profundidade ao longo do eixo da câmera)
    Pw = o + d_w * depth[..., None]
    cover = st['cover']; flash = st['flash']; tt = st['t']
    sun_d = np.array(st['sun_dir'])
    warm = max(0.0, 1 - tt / 30.0) * (1 - cover)
    # ---------------------------------------------------------- cel
    th = 0.12
    litm = smooth(th - 0.015, th + 0.015, lit)
    sun_t = SUN_TINT * mix(np.ones(3), np.array([1.08, 0.98, 0.86]), warm)
    sh_t = SHADOW_TINT * mix(np.ones(3), np.array([1.05, 0.95, 1.05]), warm)
    st_lit = mix(sun_t, np.array([0.66, 0.70, 0.90]), cover); st_sh = mix(sh_t, np.array([0.46, 0.48, 0.70]), cover)
    col = base * (st_sh + (st_lit - st_sh) * litm[..., None])
    # brilho de céu na borda (rim) do lado do sol
    # ---------------------------------------------------------- céu (guache)
    dirn = d_w / np.linalg.norm(d_w, axis=-1, keepdims=True)
    el = dirn[..., 2]
    sky = mix(SKY_HOR, SKY_MID, smooth(0.0, 0.18, el)[..., None]); sky = mix(sky, SKY_TOP, smooth(0.15, 0.7, el)[..., None])
    sunness = np.clip((dirn @ -sun_d), 0, 1)
    sky = mix(sky, DAWN, (smooth(0.75, 1.0, sunness) * smooth(0.25, 0.0, el) * (0.4 + warm))[..., None])
    stormsky = mix(STORM_HOR, STORM_TOP, smooth(-0.02, 0.4, el)[..., None])
    sky = mix(sky, stormsky, cover)
    # ---------------------------------------------------------- mar
    sea_valid = salpha > 0.5
    sea_in_front = sea_valid & (~valid | (sdepth < depth - 0.05))
    Ps = o + d_w * sdepth[..., None]
    dist = np.linalg.norm(Ps - o, axis=-1)
    seac = mix(SEA_NEAR, SEA_FAR, smooth(80, 2500, dist)[..., None])
    seac = mix(seac, mix(STORM_SEA_NEAR, STORM_SEA_FAR, smooth(80, 2500, dist)[..., None]), cover)
    seac = mix(seac, sky * 0.9 + 0.08, smooth(1800, 6500, dist)[..., None] * 0.55)
    # faixas de ondas desenhadas (bandas estáveis no mundo)
    wv = np.sin(Ps[..., 0] * 0.045 + Ps[..., 1] * 0.03 + tt * 0.8 * 0) + 0.5 * np.sin(Ps[..., 1] * 0.11 - Ps[..., 0] * 0.02)
    band = smooth(1.15, 1.25, wv) * smooth(1500, 300, dist)
    seac = mix(seac, seac * 1.12 + 0.03, band[..., None])
    # reflexo do sol: estrias claras
    refl = d_w.copy(); refl[..., 2] *= -1
    rn = refl / np.linalg.norm(refl, axis=-1, keepdims=True)
    glit = smooth(0.985, 0.996, rn @ -sun_d) * (1 - cover) * (np.sin(Ps[..., 0] * 0.3) * np.sin(Ps[..., 1] * 0.21) > 0.2)
    seac = mix(seac, np.array([1.0, 0.97, 0.88]), glit[..., None] * 0.8)
    # objetos submersos vistos através da água
    under = sea_in_front & valid
    path = np.clip(depth - sdepth, 0, None) * np.abs(dirn[..., 2]) + np.clip(-Pw[..., 2], 0, None) * 0.4
    trans = np.exp(-path / 9.0)[..., None]
    water_col = np.where(under[..., None], col * trans * mix(np.ones(3), np.array([0.55, 0.95, 1.0]), 0.7) + seac * (1 - trans), seac)
    # ---------------------------------------------------------- composição base
    img = np.where(valid[..., None], col, sky)
    img = np.where(sea_in_front[..., None], water_col, img)
    # guache: céu, nuvens, terreno, rocha da cidade, casas da colina, fundo do mar
    bgmask = (~valid & ~sea_in_front) | np.isin(cat, [4, 5, 6]) | ((cat == 3) & (depth > 450)) | sea_in_front
    pap = paper(h, w)
    PwB = np.where(valid[..., None], Pw, o + dirn * 3000)
    brush = value_noise(PwB, 9.0) * 0.6 + value_noise(PwB, 31.0) * 0.4
    k = kuwahara(img.astype(np.float32), 6)
    painted = k * (1 + (brush[..., None] - 0.5) * 0.10) + pap[..., None] * 0.012
    img = np.where(bgmask[..., None], painted, img)
    # nuvens: sombra lavanda chapada + borda clara do lado do sol
    cl = cat == 5
    if cl.any():
        lavender = mix(np.array([0.74, 0.72, 0.92]), np.array([0.30, 0.31, 0.55]), cover)
        white = mix(np.array([1.0, 0.99, 0.97]) * mix(np.ones(3), np.array([1.05, 0.95, 0.85]), warm), np.array([0.52, 0.55, 0.78]), cover)
        storm = (np.abs(base - np.array([0.231, 0.247, 0.455])).sum(-1) < 0.1) & cl
        cc = mix(lavender, white, litm[..., None])
        cc = np.where(storm[..., None], mix(np.array([0.20, 0.21, 0.42]), np.array([0.36, 0.38, 0.62]), litm[..., None]), cc)
        cc = kuwahara(cc.astype(np.float32), 8)
        img = np.where(cl[..., None], cc * (1 + (brush[..., None] - 0.5) * 0.06), img)
    # ---------------------------------------------------------- emissivos
    glow = np.zeros_like(img, dtype=np.float32)
    eye = cat == 8
    if eye.any():
        e = st['eye']
        img[eye] = mix(np.array([0.10, 0.20, 0.27]), np.array([1.0, 0.82, 0.45]), e)
        glow[eye] = np.array([1.0, 0.62, 0.22]) * e * 1.6
    vis = cat == 9
    if vis.any():
        ys = np.nonzero(vis)[0]
        y0, y1 = ys.min(), ys.max() + 1
        grad = np.linspace(0, 1, y1 - y0)[:, None]
        vc = mix(hexc('#1f5a73'), hexc('#0a1c2c'), grad)
        tmp = np.broadcast_to(vc[:, None, :], (y1 - y0, w, 3))
        reg = img[y0:y1]; m = vis[y0:y1]
        reg[m] = tmp[m]
    cr = cat == 7
    if cr.any():
        img[cr] = mix(img[cr], np.array([0.55, 0.92, 1.0]), 0.55)
        glow[cr] = np.array([0.25, 0.65, 1.0]) * 0.55
    if st['antenna_glow'] > 0:
        J = np.array(st['joints']['head']); tip = J @ np.array([3.6, -1.0, 19.6, 1.0])
        x, y, z = project(st, tip[None, :3])
        if z[0] > 1:
            cv2.circle(glow, (int(x[0]), int(y[0])), int(max(20, 9000 / z[0])), (0.6 * st['antenna_glow'], 0.8 * st['antenna_glow'], 1.0 * st['antenna_glow']), -1, cv2.LINE_AA)
    # ---------------------------------------------------------- linhas de nanquim
    edges = ink_lines(oid, lid, np.where(valid, depth, 1e6), nrm, cat, valid, 1.0)
    edges &= ~(under & (trans[..., 0] < 0.6))
    edges &= ~(sea_in_front & ~valid)
    dclamp = np.where(valid, depth, 3000)
    wmap = np.clip(2.6 * (60 / np.maximum(dclamp, 30)) ** 0.25, 1.0, 3.0).astype(np.float32)
    wmap = np.where(np.isin(cat, [1, 2]), wmap * 1.15, wmap)
    lc = INK if cover < 0.5 else INK * 0.8
    img = draw_lines(img, edges, wmap, lc)
    # linha de contato onde a água encontra pernas e pilares
    contact = valid & sea_valid & (np.abs(sdepth - depth) < 0.012 * depth + 0.4)
    if contact.any():
        cm = cv2.dilate(contact.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        img[cm] = mix(img[cm], np.array([1.0, 1.0, 1.0]), 0.85)
    # ---------------------------------------------------------- efeitos em dois quadros
    fxl = np.ascontiguousarray(img.astype(np.float32))
    draw_fx(fxl, st, glow)
    img = fxl
    # ---------------------------------------------------------- luz da história
    if flash > 0:
        lum = img.mean(-1, keepdims=True)
        hi = np.where(lum > 0.42, np.array([0.92, 0.96, 1.0]), np.array([0.10, 0.12, 0.28]))
        img = mix(img, hi, flash * 0.85)
    for kind, p in st['fx']:
        if kind == 'sunrays':
            a = p['a']
            sx, sy, sz = project(st, (np.array(st['cam'])[:3, 3] - np.array(st['sun_dir']) * 5000)[None])
            yy, xx = np.mgrid[0:h, 0:w]
            ang = np.arctan2(yy - sy[0], xx - sx[0])
            rays = (np.sin(ang * 23) * 0.5 + 0.5) ** 6 * smooth(1400, 200, np.hypot(xx - sx[0], yy - sy[0]))
            img = img + (rays * a * 0.22)[..., None] * np.array([1.0, 0.95, 0.8])
    gl = cv2.GaussianBlur(glow, (0, 0), 14) + cv2.GaussianBlur(glow, (0, 0), 40) * 0.6
    img = img + gl
    # tremida 2D
    sh = st['shake']
    if sh > 0.05:
        r = RNG(st['f'] // 2)
        M = np.float32([[1, 0, r.normal(0, sh)], [0, 1, r.normal(0, sh)]])
        img = cv2.warpAffine(img.astype(np.float32), M, (w, h), borderMode=cv2.BORDER_REFLECT)
    # acabamento: alto-key, leve granulado de filme
    img = np.clip(img, 0, 1)
    img = img ** 0.97
    grain = RNG(st['f'] * 13 + 5).normal(0, 0.008, (h, w, 1)).astype(np.float32)
    img = np.clip(img + grain, 0, 1)
    return (img[..., ::-1] * 255 + 0.5).astype(np.uint8)

if __name__ == '__main__':
    sp, exrdir, outdir, f0, f1 = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
    step = int(sys.argv[6]) if len(sys.argv) > 6 else 1
    states = pickle.load(open(sp, 'rb'))
    os.makedirs(outdir, exist_ok=True)
    for f in range(f0, f1, step):
        ex = os.path.join(exrdir, f'f{f:04d}.exr'); out = os.path.join(outdir, f'f{f:04d}.png')
        if not os.path.exists(ex) or os.path.exists(out): continue
        cv2.imwrite(out, paint_frame(states[f], ex))
        print('painted', f, flush=True)
