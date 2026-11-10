import json, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
C = json.load(open('shots/cues.json'))
B = [(1.0,'globo à noite, EUA'),(C['votam']+.8,'votam: urnas'),(C['nao1']+.5,'NÃO em cascata'),(C['uma']+.3,'uma: SIM'),
 (C['harwood']+.6,'SIM voa até Harwood'),(C['menos2']+.4,'mergulho: a cidade'),(C['tres']+.9,'325 de 430 votos'),(C['bilhoes']+.6,'data center surge'),
 (C['sua']+.4,'você: conta de luz'),(C['mark1']+.5,'Mark Kerkvliet'),(C['garantiram']+.6,'sem aumento'),(C['topou']+.5,'topou: joinha + frase'),
 (C['imposto']+.9,'imposto: contador'),(C['seis']+.6,'6x a arrecadação'),(C['muitos']+.6,'recuo: pradaria'),(C['fargo']+.8,'Fargo a 16 km'),
 (C['mas']+.8,'robô de IA chega'),(C['fa']+.5,'não virou fã'),(C['pais']+.2,'rewind 0,8 s'),(C['contas']+.6,'título'),(C['DUR']-.2,'fim')]
fs = []
subprocess.run(['node','shot.js','shots']+[f'{t:.2f}' for t,_ in B], check=True, capture_output=True)
cols, tw, th = 4, 640, 360
rows = (len(B)+cols-1)//cols
sheet = Image.new('RGB', (cols*tw, rows*(th+44)), (10,14,24)); d = ImageDraw.Draw(sheet)
font = ImageFont.truetype('../assets/fonts/X7n64b87HvSqjb_WIi2yDCRwoQ_k7367_DWu89U.woff2', 24)
for i,(t,lab) in enumerate(B):
    im = Image.open(f'shots/f_{t:06.2f}.png').convert('RGB').resize((tw,th)); x,y=(i%cols)*tw,(i//cols)*(th+44)
    sheet.paste(im,(x,y+44)); d.text((x+10,y+9), f'{t:.1f}s  {lab}', fill=(143,216,230), font=font)
sheet.save(sys.argv[1], quality=86); print(sheet.size)
