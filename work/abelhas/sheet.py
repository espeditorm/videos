import json, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
C = json.load(open('shots/cues.json'))
B = [(1.0,'jardim com abelhas'),(C['mais']+.6,'abelhas somem'),(C['flores']+.6,'flores murcham'),(C['tres']+.9,'75% das culturas'),
 (C['parece']+1.0,'recuo: globo'),(C['so']+1.2,'volta ao jardim'),(C['robos']+.5,'abelha-robô'),(C['mit1']+.4,'MIT 2025'),
 (C['clipe']+.5,'menos que um clipe'),(C['dezessete']+1.0,'17 min de voo'),(C['fazendas']+.4,'fazenda indoor'),(C['sombrio']+.4,'sombrio: luzes falham'),
 (C['black1']+.6,'Black Mirror'),(C['hackeia']+.5,'hackeada'),(C['armas']+.2,'enxame: armas'),(C['mit2']+.5,'e se hackeassem o MIT'),
 (C['culpado']+.5,'quem é o culpado'),(C['nos']+.5,'nós: pino VOCÊ'),(C['drone']+.5,'carro, drone'),(C['cresce']+.6,'a lista cresce'),
 (C['riscos2']+.4,'balança'),(C['questionar']+.2,'close na abelhinha'),(C['porque']+.3,'rewind 0,8 s'),(C['TITLE']+.8,'título'),(C['DUR']-.2,'fim')]
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
