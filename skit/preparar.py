# Prepara as camadas de cada still: recorte dos personagens, fundo preenchido,
# tela do PC limpa (sem os olhos originais), mapas de brilho (flores/luzes) e estrelas.
# Saída: prep/<S>_*.png|npy  (rodar uma vez; depois render.py só lê)
import json, numpy as np, cv2
from PIL import Image
from rembg import remove, new_session
from scipy import ndimage as ndi

CFG = json.load(open("cena.json"))
sess = new_session("isnet-general-use")
import os; os.makedirs("prep", exist_ok=True)

def maior_componente(m, n=1, min_area=4000):
    lab, k = ndi.label(m > 0.5)
    if k == 0: return m
    areas = ndi.sum(np.ones_like(lab), lab, range(1, k + 1))
    keep = [i + 1 for i in np.argsort(areas)[::-1][:n] if areas[i] >= min_area]
    return m * np.isin(lab, keep)

import sys
SO = sys.argv[1:] or list(CFG["shots"])
for S, c in CFG["shots"].items():
    if S not in SO: continue
    img = np.array(Image.open(f"stills/{S}.jpg").convert("RGB"))
    h, w = img.shape[:2]
    plate = img.copy()
    # 1) recortes
    for nome, ch in c.get("chars", {}).items():
        m = np.array(remove(Image.fromarray(img), session=sess, only_mask=True)).astype(np.float32) / 255
        x0, x1 = ch.get("xrange", [0, w])               # separa personagens pela faixa horizontal
        m[:, :x0] = 0; m[:, x1:] = 0
        m = maior_componente(m) if ch.get("largest", True) else m
        m = cv2.GaussianBlur(m, (0, 0), 0.8)
        if (m > 0.5).sum() < 2000: m[:] = 0   # não achou o personagem: fica no fundo, sem recorte
        np.save(f"prep/{S}_{nome}_mask.npy", m.astype(np.float16))
        if m.max() == 0: continue
        hole = cv2.dilate((m > 0.05).astype(np.uint8), np.ones((15, 15), np.uint8))
        plate = cv2.inpaint(plate, hole, 9, cv2.INPAINT_TELEA)
    # 2) tela do PC limpa: apaga os olhos originais
    if "pc_face" in c:
        f = c["pc_face"]; scr = np.zeros((h, w), np.uint8)
        for (x0, y0, x1, y1) in f["eyes"]:
            p = f.get("eye_pad", 6)
            scr[y0 - p:y1 + p, x0 - p:x1 + p] = 1
        for tgt in [img, plate]:
            tgt[:] = cv2.inpaint(tgt, scr, 15, cv2.INPAINT_TELEA)
        # suaviza o miolo pra não sobrar mancha do brilho antigo
        x0, y0, x1, y1 = f["screen"]
        for tgt in [img, plate]:
            roi = tgt[y0:y1, x0:x1].astype(np.float32)
            bl = cv2.GaussianBlur(roi, (0, 0), (x1 - x0) / 12)
            mm = cv2.GaussianBlur(scr[y0:y1, x0:x1].astype(np.float32), (0, 0), 6)[..., None]
            tgt[y0:y1, x0:x1] = (roi * (1 - mm) + bl * mm).clip(0, 255).astype(np.uint8)
    Image.fromarray(img).save(f"prep/{S}_full.png")
    Image.fromarray(plate).save(f"prep/{S}_plate.png")
    # 3) brilhos vivos: pixels muito claros e saturados no fundo (flores, luminárias, plaquinhas)
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32) / 255
    chars = sum((np.load(f"prep/{S}_{n}_mask.npy").astype(np.float32) for n in c.get("chars", {})), np.zeros((h, w), np.float32))
    glow = ((hsv[..., 2] > 0.78) & (hsv[..., 1] > 0.35)).astype(np.uint8) * (chars < 0.1)
    if "pc_face" in c:  # não pulsar a tela do PC
        x0, y0, x1, y1 = c["pc_face"]["screen"]; glow[y0 - 20:y1 + 20, x0 - 20:x1 + 20] = 0
    lab, k = ndi.label(cv2.dilate(glow, np.ones((9, 9), np.uint8)))
    np.save(f"prep/{S}_glowlab.npy", (lab * glow).astype(np.int32))
    # 4) estrelas: pontinhos claros no céu escuro (metade de cima)
    lum = img.astype(np.float32).mean(2) / 255
    sky = np.zeros((h, w), bool); sky[: int(h * c.get("sky_frac", 0.45))] = True
    dark = cv2.erode((cv2.GaussianBlur(lum, (0, 0), 6) < 0.14).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    peaks = (lum == ndi.maximum_filter(lum, 5)) & (lum > cv2.GaussianBlur(lum, (0, 0), 4) + 0.06)
    ys, xs = np.where(peaks & sky & dark & (chars < 0.1))
    json.dump([[int(x), int(y), float(lum[y, x])] for x, y in zip(xs, ys)], open(f"prep/{S}_stars.json", "w"))
    print(S, "chars", list(c.get("chars", {})), "glows", k, "stars", len(xs), flush=True)
