# Miniaturas: YouTube 1280x720 e capa vertical 1080x1920 (Reels/TikTok), a partir de quadros limpos dos vídeos
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FONT = '../havai/assets/fonts/Fredoka-Bold.ttf'
TEAL, GOLD, CORAL, WHITE = (143, 216, 230), (255, 217, 138), (255, 138, 122), (255, 255, 255)
def font(px): return ImageFont.truetype(FONT, px)
def text_w(s, px, ls): f = font(px); return sum(f.getlength(c) for c in s) + ls * (len(s) - 1)
def spaced(d, xy, s, px, col, ls, anchor='l'):
    f = font(px); w = text_w(s, px, ls); x, y = xy
    if anchor == 'm': x -= w / 2
    for c in s:
        d.text((x, y), c, font=f, fill=col, anchor='ls'); x += f.getlength(c) + ls
    return w
def pill(img, cx, cy, lines, pad=40, alpha=200, anchor='m', radius=None):
    # lines: [(texto, px, cor, espaçamento)]
    ws = [text_w(s, px, ls) for s, px, c, ls in lines]; hs = [px * 1.05 for s, px, c, ls in lines]
    W_, H_ = max(ws) + pad * 2, sum(hs) + pad * 1.2 + 14 * (len(lines) - 1)
    x0 = cx - W_ / 2 if anchor == 'm' else cx
    ov = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    d.rounded_rectangle([x0, cy - H_ / 2, x0 + W_, cy + H_ / 2], radius=radius or min(H_ / 2, 60), fill=(6, 20, 40, alpha))
    img.alpha_composite(ov); d = ImageDraw.Draw(img)
    y = cy - H_ / 2 + pad * .6
    for (s, px, c, ls), h in zip(lines, hs):
        y += px * .86
        spaced(d, (x0 + W_ / 2, y), s, px, c, ls, 'm'); y += px * .19 + 14
    return W_, H_
def vignette(img, a=.45):
    w, h = img.size; m = Image.new('L', (w, h), 0); d = ImageDraw.Draw(m)
    for i in range(60):
        k = i / 60; d.ellipse([-w * .3 * k, -h * .3 * k, w + w * .3 * k, h + h * .3 * k], outline=int(255 * a * k ** 2), width=int(max(w, h) / 50))
    m = m.filter(ImageFilter.GaussianBlur(max(w, h) / 30))
    dark = Image.new('RGBA', (w, h), (4, 4, 20, 255)); img.paste(dark, (0, 0), m)
def place(dst, src, scale, fx, fy, tx, ty):
    # coloca src escalado de forma que o ponto (fx,fy) de src caia em (tx,ty) de dst
    s = src.resize((int(src.width * scale), int(src.height * scale)), Image.LANCZOS)
    dst.alpha_composite(s.convert('RGBA'), (0, 0), (max(0, int(fx * scale - tx)), max(0, int(fy * scale - ty)))) if False else dst.paste(s, (int(tx - fx * scale), int(ty - fy * scale)))

def gerar_v1():
    # ---------------- 38 MINUTOS (Havaí, Jim Carrey) ----------------
    fr = Image.open('quadros/havai_16.0.png').convert('RGBA')
    yt = Image.new('RGBA', (1920, 1080)); place(yt, fr, 1.12, 705, 525, 640, 560)
    # lado direito escurecido para o texto
    grad = Image.new('L', (1920, 1080)); gd = ImageDraw.Draw(grad)
    for x in range(1920): gd.line([(x, 0), (x, 1080)], fill=int(170 * max(0, min(1, (x - 900) / 500))))
    yt.paste(Image.new('RGBA', (1920, 1080), (8, 22, 44, 255)), (0, 0), grad)
    d = ImageDraw.Draw(yt)
    spaced(d, (1490, 420), '38', 330, GOLD, 6, 'm')
    spaced(d, (1490, 560), 'MINUTOS', 120, WHITE, 8, 'm')
    pill(yt, 1490, 690, [('POR CAUSA DE UM MENU', 54, TEAL, 5)], pad=34)
    pill(yt, 1490, 830, [('JIM CARREY ESTAVA LÁ', 44, CORAL, 5)], pad=28)
    vignette(yt, .5); yt.convert('RGB').resize((1280, 720), Image.LANCZOS).save('38_minutos_youtube.jpg', quality=93)
    # vertical
    bg = Image.new('RGBA', (1080, 1920)); place(bg, fr, 1.78, 600, 540, 540, 960); bg = bg.filter(ImageFilter.GaussianBlur(30))
    bg.alpha_composite(Image.new('RGBA', bg.size, (6, 16, 36, 140)))
    place(bg, fr, 1.05, 705, 560, 520, 1080)
    d = ImageDraw.Draw(bg)
    pill(bg, 540, 330, [('38', 210, GOLD, 6), ('MINUTOS', 96, WHITE, 8)], pad=40, alpha=215)
    pill(bg, 540, 1520, [('POR CAUSA DE UM MENU', 52, TEAL, 4), ('JIM CARREY ESTAVA LÁ', 40, CORAL, 4)], pad=36, alpha=215)
    vignette(bg, .45); bg.convert('RGB').save('38_minutos_capa_vertical.jpg', quality=93)

    # ---------------- SALVA OU CONDENA (abelhas-robôs) ----------------
    good = Image.open('quadros/abelhas_75.6.png').convert('RGBA'); evil = Image.open('quadros/abelhas_46.2.png').convert('RGBA')
    yt = Image.new('RGBA', (1920, 1080)); place(yt, good, 1.25, 960, 470, 480, 520)
    right = Image.new('RGBA', (1920, 1080)); place(right, evil, 1.55, 940, 520, 1440, 520)
    mask = Image.new('L', (1920, 1080)); md = ImageDraw.Draw(mask); md.polygon([(1060, 0), (1920, 0), (1920, 1080), (860, 1080)], fill=255)
    yt.paste(right, (0, 0), mask)
    glow = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow); gd.line([(1060, 0), (860, 1080)], fill=(255, 217, 138, 255), width=16)
    yt.alpha_composite(glow.filter(ImageFilter.GaussianBlur(5)))
    pill(yt, 960, 930, [('SALVA OU CONDENA?', 124, WHITE, 8)], pad=42, alpha=215)
    pill(yt, 300, 110, [('ABELHAS-ROBÔS', 50, GOLD, 6)], pad=28, alpha=215)
    vignette(yt, .45); yt.convert('RGB').resize((1280, 720), Image.LANCZOS).save('salva_ou_condena_youtube.jpg', quality=93)
    # vertical: em cima a abelhinha (salva), embaixo o enxame (condena)
    v = Image.new('RGBA', (1080, 1920)); place(v, good, 1.45, 960, 470, 540, 470)
    low = Image.new('RGBA', (1080, 1920)); place(low, evil, 1.9, 940, 520, 540, 1400)
    mask = Image.new('L', (1080, 1920)); md = ImageDraw.Draw(mask); md.polygon([(0, 1000), (1080, 880), (1080, 1920), (0, 1920)], fill=255)
    v.paste(low, (0, 0), mask)
    glow = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow); gd.line([(0, 1000), (1080, 880)], fill=(255, 217, 138, 255), width=14)
    v.alpha_composite(glow.filter(ImageFilter.GaussianBlur(5)))
    pill(v, 540, 200, [('ABELHAS-ROBÔS', 52, GOLD, 6)], pad=28, alpha=215)
    pill(v, 540, 850, [('SALVA', 140, TEAL, 8)], pad=30, alpha=215)
    pill(v, 540, 1110, [('OU CONDENA?', 104, CORAL, 7)], pad=30, alpha=215)
    vignette(v, .45); v.convert('RGB').save('salva_ou_condena_capa_vertical.jpg', quality=93)
    print('ok')

if __name__ == "__main__":
    gerar_v1()
