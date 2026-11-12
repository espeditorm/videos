import json, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
C = json.load(open('shots/cues.json'))
B = [(0.9,'você no sofá'),(C['compartilha']+.4,'compartilha: post voa'),(C['milhoes']+.5,'milhões: globo'),(C['muda']+.3,'quase nada muda'),
 (C['anton']+.6,'Anton Jäger'),(C['hiper']+.5,'HIPERPOLÍTICA'),(C['consequencias']+.5,'politização x consequências'),(C['organiza']+.6,'dois eixos'),
 (C['seculo']+.8,'século 20: ponto no alto'),(C['clubes']+.4,'sindicatos, partidos...'),(C['multidoes']+.8,'multidões'),(C['muro']+.6,'queda do muro'),
 (C['despencaram']+1.0,'anos 90: ponto despenca'),(C['casa']+.4,'gestão / foram pra casa'),(C['crise']+.8,'crise de 2008'),(C['nao1']+.2,'a raiva voltou; organizações, não'),
 (C['brexit']+.4,'2016: Trump, Brexit'),(C['explodem']+.8,'hashtags explodem'),(C['lotam']+.6,'protestos lotam'),(C['outro']+.4,'#outroassunto'),
 (C['facil2']+.4,'fácil de entrar/sair'),(C['anos2']+.4,'sindicato: reunião, mensalidade, anos'),(C['segundo']+.4,'like: 1 s'),(C['voto']+.5,'lei, salário, voto vazios'),
 (C['inutil']+.4,'não é inútil'),(C['basta']+.3,'não basta: fecha o livro'),(C['revoltar']+.4,'você de novo'),(C['compartilhar']+.6,'o que vem?'),
 (C['RW0']+.4,'rewind 0,8 s'),(C['DUR']-.3,'título')]
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
