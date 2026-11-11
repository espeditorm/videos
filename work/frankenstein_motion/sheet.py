import json, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
C = json.load(open('shots/cues.json'))
B = [(1.0,'escrivaninha 1818'),(C['frank1']+.3,'o livro abre'),(C['vida']+.1,'raio: cria vida'),(C['consequencias']+.6,'ele vira as costas'),
 (C['rejeitada']+.5,'rejeitada'),(C['perigosa']+.3,'a sombra: perigosa'),(C['criatura2']+.4,'FRANKENSTEIN ✗ criatura'),(C['criador']+.6,'✓ é o criador'),
 (C['costuras']+.4,'costuras e eletricidade'),(C['inteligencias']+.6,'vira rede de IA'),(C['decidem']+.4,'decidem por nós'),(C['proteger']+.4,'carro: quem proteger'),
 (C['emprestimo']+.6,'empréstimo, vaga'),(C['preconceitos']+.5,'PRECONCEITO'),(C['rosto']+.6,'sem rosto'),(C['recomendacoes']+.5,'recomendações'),
 (C['decisoes']+.8,'fios nas decisões'),(C['aviso']+.3,'o livro: um aviso'),(C['criar']+.6,'não basta criar'),(C['aliadas']+.4,'aliadas'),
 (C['monstros2']+.4,'ou monstros'),(C['RW0']+.4,'rewind 0,8 s'),(C['TITLE']+1.0,'título'),(C['DUR']-.2,'fim')]
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
