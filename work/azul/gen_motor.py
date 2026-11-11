# Monta src/video.src.html: base (globo, personagens, texto) + deixas + relógio da história + cenas.js
import json, re
w = json.load(open('audio/palavras.json'))
base = open('src/base.part.html').read()
cues = '''const C = {
  odisseia: cue('odisseia'), vinho: cue('vinho'), azul1: cue('azul', 1), quem: cue('quem'), william: cue('william'), contou: cue('contou'),
  preto: cue('preto', 1), branco: cue('branco', 1), vermelho: cue('vermelho', 1), azul2: cue('azul', 2), nenhuma: cue('nenhuma'),
  depois1: cue('depois', 1), lazarus: cue('lazarus'), biblia: cue('bíblia'), alcorao: cue('alcorão'), vedas: cue('vedas'), achou: cue('achou'),
  viu: cue('viu'), padrao: cue('padrão'), preto2: cue('preto', 2), branco2: cue('branco', 2), vermelho2: cue('vermelho', 2),
  amarelo: cue('amarelo'), verde: cue('verde'), azul3: cue('azul', 4), excecao: cue('exceção'), egipcios: cue('egípcios'),
  fabricar: cue('fabricar'), tinta: cue('tinta'), pra: cue('pra', 1), voce: cue('você'), ceu1: cue('céu', 1), linguista2: cue('linguista', 2),
  guy: cue('guy'), ensinou: cue('ensinou'), cores2: cue('cores', 2), ceu2: cue('céu', 2), perguntou: cue('perguntou'), demorou: cue('demorou'),
  branco3: cue('branco', 3), homero2: cue('homero', 2), mesmo: cue('mesmo'), nome: cue('nome', 1), enxergar: cue('enxergar')
};
C.DUR = DUR; C.RW0 = C.enxergar + .6; C.TITLE = C.RW0 + .9;'''
rw = '''// ---------- dois relógios: rewind de 0,8 s ao mar cor de vinho de Homero; o mar vira azul sob o título ----------
const RW0 = C.RW0, RW1 = RW0 + .8, SLOW = .1;
const RW_BACK = C.vinho + .2;'''
base = base.replace('//@@CUES@@', cues).replace('//@@RW@@', rw)
base = base.replace('<title>38 Minutos</title>', '<title>O Azul Foi a Última Cor</title>').replace('//  38 MINUTOS. Cada frame', '//  O AZUL FOI A ÚLTIMA COR. Cada frame')
base = re.sub(r'const DUR = [0-9.]+;', f'const DUR = {round(w[-1]["t1"] + 4.0, 1)};', base)
base = base.replace('//@@SCENES@@\n', '//@include cenas.js\n')
base = re.sub(r'\nconst SUBSOLAR = \[-129, -21\];[^\n]*', '', base)
open('src/video.src.html', 'w').write(base)
print('DUR', round(w[-1]['t1'] + 3.6, 1))
