import glob, sys
from PIL import Image, ImageDraw, ImageFont
LAB = {1.5:"estrela 20× Sol",4.85:"colapsa: incha 6%",5.75:"explode: flash + choque",6.4:"recuo, supernova",8.9:"luz: 1% luz",10.2:"neutrinos: 99%",11.5:"mergulho 2,3x na Terra",13.5:"trilhões: contador",15.2:"você: pino",16.3:"sente: colisões 0",17.8:"recuo até 0,3x",20.0:"58 dígitos no anel",22.0:"quão perto: círculo",24.3:"parsec: distância + dose",25.8:"banana",27.9:"Netuno, ainda vivo",29.4:"Júpiter, ainda vivo",31.5:"rumo a 2,3 UA",33.5:"cinturão, frente vindo",35.5:"4 sieverts",36.8:"LETAL",38.5:"clarão",40.0:"×190 milhões",42.0:"bomba H no olho",43.8:"óculos escuros",45.0:"não vai ajudar",45.6:"rewind 0,8 s",47.0:"1987",48.5:"trilhões de trilhões",51.8:"detectores",53.2:"24 detectados",55.0:"neutrino 2,3 UA",57.2:"callback",58.3:"título",61.5:"fim"}
fs = sorted(glob.glob("shots/f_*.png")); cols = 5; tw, th = 640, 360
rows = (len(fs) + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw, rows * (th + 40)), (10, 14, 24))
d = ImageDraw.Draw(sheet)
try: font = ImageFont.truetype("assets/fonts/X7n64b87HvSqjb_WIi2yDCRwoQ_k7367_DWu89U.woff2", 24)
except Exception: font = ImageFont.load_default(24)
for i, f in enumerate(fs):
    t = float(f.split('_')[1][:-4]); im = Image.open(f).convert("RGB").resize((tw, th)); x, y = (i % cols) * tw, (i // cols) * (th + 40)
    sheet.paste(im, (x, y + 40)); d.text((x + 10, y + 8), f"{t:.1f}s  {LAB.get(t,'')}", fill=(143, 216, 230), font=font)
sheet.save(sys.argv[1], quality=88); print(sheet.size)
