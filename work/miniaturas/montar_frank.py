# Capas do "QUEM É O MONSTRO?": gancho = contradição ("FRANKENSTEIN NÃO É O MONSTRO") + pergunta aberta ("E A IA?")
from PIL import Image, ImageDraw, ImageFilter
from montar import font, text_w, spaced, pill, vignette, place, TEAL, GOLD, CORAL, WHITE
from montar_v2 import headline, stamp, glow, RED
GREEN = (95, 196, 122)
lab = Image.open('quadros/frankenstein_15.0.png').convert('RGBA'); ai = Image.open('quadros/frankenstein_54.3.png').convert('RGBA')
SCI, CRE, MON = (610, 760), (1120, 740), (1020, 620)
def mark_x(img, cx, cy, r):
    d = ImageDraw.Draw(img); w = int(r * .32)
    d.line([(cx - r, cy - r), (cx + r, cy + r)], fill=RED + (255,), width=w); d.line([(cx - r, cy + r), (cx + r, cy - r)], fill=RED + (255,), width=w)
def mark_v(img, cx, cy, r):
    d = ImageDraw.Draw(img); d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GREEN + (255,))
    d.line([(cx - r * .45, cy + r * .02), (cx - r * .1, cy + r * .38), (cx + r * .5, cy - r * .35)], fill=(255, 255, 255, 255), width=int(r * .22), joint='curve')
def arrow(img, x0, y0, x1, y1, col, w=16):
    import math
    d = ImageDraw.Draw(img); d.line([(x0, y0), (x1, y1)], fill=col + (255,), width=w)
    a = math.atan2(y1 - y0, x1 - x0); L = w * 2.6
    d.polygon([(x1 + math.cos(a) * L * .6, y1 + math.sin(a) * L * .6), (x1 + math.cos(a + 2.4) * L, y1 + math.sin(a + 2.4) * L), (x1 + math.cos(a - 2.4) * L, y1 + math.sin(a - 2.4) * L)], fill=col + (255,))

# ---------- YouTube ----------
yt = Image.new('RGBA', (1920, 1080)); Z = 1.6; C0 = (865, 700); T0 = (520, 720)
place(yt, lab, Z, C0[0], C0[1], T0[0], T0[1])
right = Image.new('RGBA', (1920, 1080)); place(right, ai, 1.7, MON[0], MON[1], 1530, 640)
mask = Image.new('L', (1920, 1080)); md = ImageDraw.Draw(mask); md.polygon([(1180, 0), (1920, 0), (1920, 1080), (1020, 1080)], fill=255)
yt.paste(right, (0, 0), mask)
gl = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0)); gd = ImageDraw.Draw(gl); gd.line([(1180, 0), (1020, 1080)], fill=GOLD + (255,), width=16); yt.alpha_composite(gl.filter(ImageFilter.GaussianBlur(5)))
P = lambda p: (T0[0] + (p[0] - C0[0]) * Z, T0[1] + (p[1] - C0[1]) * Z)
cx, cy = P(CRE); sx, sy = P(SCI)
mark_x(yt, cx + 10, cy - 150, 70)
mark_v(yt, sx + 10, sy - 330, 52)
top = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0)); td = ImageDraw.Draw(top)
for y in range(330): td.line([(0, y), (1920, y)], fill=(6, 14, 30, int(220 * (1 - y / 330))))
yt.alpha_composite(top)
headline(yt, 960, 150, [('FRANKENSTEIN NÃO É O MONSTRO', 104, WHITE, 4)], anchor='m')
pill(yt, sx + 230, sy - 430, [('ELE É O CRIADOR', 40, GOLD, 4)], pad=22, alpha=225)
stamp(yt, 1560, 930, 'E A IA?', 92, RED, -6)
vignette(yt, .45); yt.convert('RGB').resize((1280, 720), Image.LANCZOS).save('quem_e_o_monstro_youtube.jpg', quality=93)

# ---------- vertical ----------
v = Image.new('RGBA', (1080, 1920)); Z2 = 1.7; T2 = (540, 980)
place(v, lab, Z2, C0[0], C0[1], T2[0], T2[1])
low = Image.new('RGBA', (1080, 1920)); place(low, ai, 1.7, MON[0], MON[1], 560, 1560)
mask = Image.new('L', (1080, 1920)); md = ImageDraw.Draw(mask); md.polygon([(0, 1330), (1080, 1250), (1080, 1920), (0, 1920)], fill=255)
v.paste(low, (0, 0), mask)
gl = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); gd = ImageDraw.Draw(gl); gd.line([(0, 1330), (1080, 1250)], fill=GOLD + (255,), width=14); v.alpha_composite(gl.filter(ImageFilter.GaussianBlur(5)))
P2 = lambda p: (T2[0] + (p[0] - C0[0]) * Z2, T2[1] + (p[1] - C0[1]) * Z2)
cx, cy = P2(CRE); sx, sy = P2(SCI)
mark_x(v, cx + 8, cy - 130, 60); mark_v(v, sx + 8, sy - 300, 46)
pill(v, 540, 420, [('FRANKENSTEIN', 96, WHITE, 5), ('NÃO É O MONSTRO', 78, GOLD, 5)], pad=36, alpha=225)
pill(v, sx + 150, sy - 400, [('ELE É O CRIADOR', 36, GOLD, 4)], pad=20, alpha=225)
stamp(v, 600, 1520, 'E A IA?', 104, RED, -6)
vignette(v, .45); v.convert('RGB').save('quem_e_o_monstro_capa_vertical.jpg', quality=93)
print('ok')
