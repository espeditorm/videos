import json, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
C = json.load(open('shots/cues.json'))
B = [(1.5,'abertura 08:07'),(C['havai']+.6,'Havaí: ilhas'),(C['vibram']+.5,'vibram: pulso'),(C['homem']+.3,'mergulho: homem'),
 (C['carrey']+.4,'Jim Carrey'),(C['ameaca']+.6,'alerta no celular'),(C['isto']+.6,'não é simulado'),(C['se']+.6,'recuo: globo'),
 (C['vinte']+.5,'≈20 MIN no arco'),(C['voce']+.5,'você: pino'),(C['esconder']+.8,'esconderijos'),(C['quem']+.5,'e com quem: gato'),
 (C['vazio']+.5,'céu vazio'),(C['tres']+.8,'contador começa'),(C['lancamento']+.4,'08:10 nenhum lançamento'),(C['cinco']+.4,'08:45 frente de correção'),
 (C['trinta1']+.6,'38 MIN'),(C['tela']+.4,'a tela'),(C['real2']+.15,'clique no real'),(C['iguais']+.4,'mesma lista'),
 (C['dois2']+.4,'mesma confirmação'),(C['desmentir']+.5,'não existia'),(C['acordou']+.4,'Carrey acorda'),(C['dez']+.5,'10 minutos'),
 (C['FA']+.25,'08:45 alarme falso'),(C['trinta2']+.45,'rewind 0,8 s'),(C['mundo'],'callback em câmera lenta'),(C['menu']+.1,'clique em "menu"'),(59.9,"título")]
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
