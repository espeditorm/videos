import json, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
C = json.load(open('shots/cues.json'))
B = [(1.0,'Homero e o mar'),(C['vinho']+.4,'mar cor de vinho'),(C['azul1']+.4,'nenhum azul'),(C['william']+.5,'Gladstone'),
 (C['preto']+.8,'contagem: preto'),(C['nenhuma']+.4,'azul: 0'),(C['lazarus']+.6,'Geiger, globo'),(C['achou']+.4,'nenhum azul no mundo'),
 (C['padrao']+.4,'a ordem das cores'),(C['vermelho2']+.4,'vermelho'),(C['verde']+.4,'amarelo e verde'),(C['azul3']+.6,'o azul acende'),
 (C['tinta']+.5,'azul egípcio'),(C['ceu1']+.2,'de que cor é o céu?'),(C['ensinou']+.8,'cartões de cor'),(C['ceu2']+.2,'aponta o céu'),
 (C['demorou']+.5,'ela pensa...'),(C['branco3']+.4,'"branco"'),(C['nome']+.4,'AZUL no mar'),(C['RW0']+.4,'rewind 0,8 s'),(C['TITLE']+.6,'título, mar vinho'),(C['DUR']-.2,'mar fica azul')]
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
