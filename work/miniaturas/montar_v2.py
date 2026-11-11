# Miniaturas v2 com estrutura de gancho: contradição / fato surpreendente + pergunta aberta + resumo em 1 linha
import math
from PIL import Image, ImageDraw, ImageFilter
from montar import font, text_w, spaced, pill, vignette, place, TEAL, GOLD, CORAL, WHITE
RED = (255, 72, 88)
def headline(img, x, y, lines, anchor='l', shadow=True):
    # texto grande sem caixa, com sombra suave para leitura em tamanho pequeno
    d = ImageDraw.Draw(img)
    for s, px, col, ls in lines:
        if shadow:
            sh = Image.new('RGBA', img.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
            spaced(sd, (x + 6, y + 8), s, px, (0, 0, 0, 190), ls, anchor if anchor == 'm' else 'l')
            img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
        spaced(d, (x, y), s, px, col, ls, anchor if anchor == 'm' else 'l')
        y += px * 1.02
def stamp(img, cx, cy, s, px, col, ang, pad=34):
    w = text_w(s, px, 6) + pad * 2; h = px * 1.35
    layer = Image.new('RGBA', (int(w) + 40, int(h) + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.rounded_rectangle([20, 20, 20 + w, 20 + h], radius=22, fill=col + (255,))
    spaced(d, (20 + w / 2, 20 + h / 2 + px * .36), s, px, WHITE, 6, 'm')
    layer = layer.rotate(ang, expand=True, resample=Image.BICUBIC)
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0)); sh.paste((0, 0, 0, 150), (int(cx - layer.width / 2 + 8), int(cy - layer.height / 2 + 12)), layer)
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    img.alpha_composite(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)))
def ring(img, cx, cy, rx, ry, col, wdt=12):
    # destaque circular (anel preenchido com brilho), aponta o detalhe que importa
    g = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=col + (255,), width=wdt)
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(6))); img.alpha_composite(g)
def glow(img, cx, cy, r, col, a):
    g = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col + (a,))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(r * .45)))

# ========================= 38 MINUTOS =========================
fr = Image.open('quadros/havai_16.0.png').convert('RGBA')
FX, FY = 705, 525          # centro do celular no quadro
LINE = (705, 588)          # "THIS IS NOT A DRILL" na tela
# YouTube
yt = Image.new('RGBA', (1920, 1080)); S = 1.18; TX, TY = 600, 500
place(yt, fr, S, FX, FY, TX, TY)
grad = Image.new('L', (1920, 1080)); gd = ImageDraw.Draw(grad)
for x in range(1920): gd.line([(x, 0), (x, 1080)], fill=int(235 * max(0, min(1, (x - 820) / 420))))
yt.paste(Image.new('RGBA', (1920, 1080), (14, 10, 26, 255)), (0, 0), grad)
glow(yt, 1420, 520, 420, RED, 70)
lx, ly = TX + (LINE[0] - FX) * S, TY + (LINE[1] - FY) * S
ring(yt, lx, ly, 175, 62, RED)
headline(yt, 1000, 330, [('“NÃO É UM', 128, WHITE, 4), ('SIMULADO”', 150, WHITE, 5)])
stamp(yt, 1480, 640, 'ERA FALSO', 104, RED, 8)
pill(yt, 1370, 860, [('38 MINUTOS DE PÂNICO NO HAVAÍ', 46, GOLD, 4)], pad=30, alpha=225)
pill(yt, 1370, 965, [('ATÉ O JIM CARREY ACREDITOU', 36, TEAL, 4)], pad=22, alpha=225)
vignette(yt, .5); yt.convert('RGB').resize((1280, 720), Image.LANCZOS).save('38_minutos_youtube.jpg', quality=93)
# Vertical (texto-chave dentro do recorte 4:5, y 285-1635)
v = Image.new('RGBA', (1080, 1920)); place(v, fr, 1.9, 640, 540, 540, 960); v = v.filter(ImageFilter.GaussianBlur(28))
v.alpha_composite(Image.new('RGBA', v.size, (14, 10, 26, 150)))
S2 = 1.25; TX2, TY2 = 560, 1040
place(v, fr, S2, FX, FY, TX2, TY2)
glow(v, 560, 1040, 380, RED, 55)
ring(v, TX2 + (LINE[0] - FX) * S2, TY2 + (LINE[1] - FY) * S2, 165, 58, RED)
pill(v, 540, 410, [('“NÃO É UM', 104, WHITE, 4), ('SIMULADO”', 120, WHITE, 5)], pad=40, alpha=225)
stamp(v, 700, 1330, 'ERA FALSO', 96, RED, 8)
pill(v, 540, 1530, [('38 MINUTOS DE PÂNICO NO HAVAÍ', 44, GOLD, 3), ('ATÉ O JIM CARREY ACREDITOU', 34, TEAL, 3)], pad=30, alpha=225)
vignette(v, .45); v.convert('RGB').save('38_minutos_capa_vertical.jpg', quality=93)

# ========================= SALVA OU CONDENA =========================
good = Image.open('quadros/abelhas_75.6.png').convert('RGBA'); evil = Image.open('quadros/abelhas_46.2.png').convert('RGBA')
yt = Image.new('RGBA', (1920, 1080)); place(yt, good, 1.3, 960, 470, 470, 600)
right = Image.new('RGBA', (1920, 1080)); place(right, evil, 1.6, 940, 520, 1450, 620)
mask = Image.new('L', (1920, 1080)); md = ImageDraw.Draw(mask); md.polygon([(1080, 0), (1920, 0), (1920, 1080), (880, 1080)], fill=255)
yt.paste(right, (0, 0), mask)
gl = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0)); gd = ImageDraw.Draw(gl); gd.line([(1080, 0), (880, 1080)], fill=GOLD + (255,), width=16)
yt.alpha_composite(gl.filter(ImageFilter.GaussianBlur(5)))
top = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0)); td = ImageDraw.Draw(top)
for y in range(330): td.line([(0, y), (1920, y)], fill=(6, 14, 30, int(210 * (1 - y / 330))))
yt.alpha_composite(top)
headline(yt, 960, 175, [('ABELHAS-ROBÔS JÁ EXISTEM', 116, WHITE, 5)], anchor='m')
pill(yt, 330, 300, [('PROTÓTIPO DO MIT', 40, TEAL, 5)], pad=24, alpha=225)
stamp(yt, 1360, 925, 'E SE FOREM HACKEADAS?', 60, RED, 4)
vignette(yt, .45); yt.convert('RGB').resize((1280, 720), Image.LANCZOS).save('salva_ou_condena_youtube.jpg', quality=93)
# Vertical
v = Image.new('RGBA', (1080, 1920)); place(v, good, 1.45, 960, 470, 540, 640)
low = Image.new('RGBA', (1080, 1920)); place(low, evil, 1.9, 940, 520, 540, 1430)
mask = Image.new('L', (1080, 1920)); md = ImageDraw.Draw(mask); md.polygon([(0, 1060), (1080, 940), (1080, 1920), (0, 1920)], fill=255)
v.paste(low, (0, 0), mask)
gl = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); gd = ImageDraw.Draw(gl); gd.line([(0, 1060), (1080, 940)], fill=GOLD + (255,), width=14)
v.alpha_composite(gl.filter(ImageFilter.GaussianBlur(5)))
pill(v, 540, 340, [('ABELHAS-ROBÔS', 92, WHITE, 5), ('JÁ EXISTEM', 92, GOLD, 5)], pad=36, alpha=225)
pill(v, 540, 950, [('PROTÓTIPO DO MIT', 38, TEAL, 5)], pad=22, alpha=225)
stamp(v, 540, 1440, 'E SE FOREM', 84, RED, 5)
stamp(v, 560, 1570, 'HACKEADAS?', 92, RED, 5)
vignette(v, .45); v.convert('RGB').save('salva_ou_condena_capa_vertical.jpg', quality=93)
print('ok')
