# Capas com gancho: O AZUL FOI A ÚLTIMA COR
from PIL import Image, ImageDraw, ImageFilter
from montar import pill, vignette, place, TEAL, GOLD, WHITE
exec(open('montar_v2.py').read().split('# ====')[0])
GREEN = (60, 190, 110); WINE = (150, 30, 70); BLUE = (40, 120, 220)

# ========================= O AZUL =========================
vin = Image.open('quadros/azul_3.6.png').convert('RGBA'); azl = Image.open('quadros/azul_61.9.png').convert('RGBA')
yt = Image.new('RGBA', (1920, 1080)); place(yt, vin, 1.2, 600, 700, 520, 720)
r = Image.new('RGBA', (1920, 1080)); place(r, azl, 1.2, 700, 640, 1500, 700)
m = Image.new('L', (1920, 1080)); ImageDraw.Draw(m).polygon([(1060, 0), (1920, 0), (1920, 1080), (900, 1080)], fill=255)
yt.paste(r, (0, 0), m)
gl = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0)); ImageDraw.Draw(gl).line([(1060, 0), (900, 1080)], fill=GOLD + (255,), width=16)
yt.alpha_composite(gl.filter(ImageFilter.GaussianBlur(5)))
top = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0)); td = ImageDraw.Draw(top)
for y in range(360): td.line([(0, y), (1920, y)], fill=(14, 8, 20, int(215 * (1 - y / 360))))
yt.alpha_composite(top)
headline(yt, 960, 180, [('O MAR ERA COR DE VINHO', 118, WHITE, 5)], anchor='m')
pill(yt, 470, 330, [('SEGUNDO HOMERO', 40, GOLD, 5)], pad=24, alpha=225)
stamp(yt, 1420, 900, 'E O AZUL?', 104, BLUE, -6)
vignette(yt, .45); yt.convert('RGB').resize((1280, 720), Image.LANCZOS).save('o_azul_foi_a_ultima_cor_youtube.jpg', quality=93)
v = Image.new('RGBA', (1080, 1920)); place(v, vin, 1.5, 600, 700, 470, 860)
low = Image.new('RGBA', (1080, 1920)); place(low, azl, 1.5, 700, 640, 600, 1500)
m = Image.new('L', (1080, 1920)); ImageDraw.Draw(m).polygon([(0, 1080), (1080, 960), (1080, 1920), (0, 1920)], fill=255)
v.paste(low, (0, 0), m)
gl = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); ImageDraw.Draw(gl).line([(0, 1080), (1080, 960)], fill=GOLD + (255,), width=14)
v.alpha_composite(gl.filter(ImageFilter.GaussianBlur(5)))
pill(v, 540, 360, [('O MAR ERA', 96, WHITE, 5), ('COR DE VINHO', 96, (255, 140, 170), 5)], pad=36, alpha=225)
pill(v, 540, 560, [('SEGUNDO HOMERO', 38, GOLD, 5)], pad=22, alpha=225)
stamp(v, 560, 1520, 'E O AZUL?', 110, BLUE, -6)
vignette(v, .45); v.convert('RGB').save('o_azul_foi_a_ultima_cor_capa_vertical.jpg', quality=93)

print('ok')
