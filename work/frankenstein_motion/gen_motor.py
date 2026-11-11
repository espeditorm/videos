# Monta src/video.src.html: base (globo, personagens, texto) + deixas + relógio da história + cenas.js
import json, re
w = json.load(open('audio/palavras.json'))
base = open('src/base.part.html').read()
cues = '''const C = {
  escreveu: cue('escreveu'), frank1: cue('frankenstein', 1), livro1: cue('livro', 1), vida: cue('vida'), consequencias: cue('consequências'),
  resultado: cue('resultado'), criatura1: cue('criatura', 1), rejeitada: cue('rejeitada'), confusa: cue('confusa'), perigosa: cue('perigosa'),
  detalhe: cue('detalhe'), frank2: cue('frankenstein', 2), criatura2: cue('criatura', 2), criador: cue('criador'), hoje1: cue('hoje', 1),
  costuras: cue('costuras'), eletricidade: cue('eletricidade'), inteligencias: cue('inteligências'), sistemas: cue('sistemas'), decidem: cue('decidem'),
  carro: cue('carro'), escolher: cue('escolher'), proteger: cue('proteger'), acidente: cue('acidente'), algoritmo: cue('algoritmo'),
  emprestimo: cue('empréstimo'), preconceitos: cue('preconceitos'), diferente: cue('diferente'), rosto: cue('rosto'), recomendacoes: cue('recomendações'),
  decisoes: cue('decisões'), escrito: cue('escrito'), aviso: cue('aviso'), criar: cue('criar'), entao: cue('então'), aliadas: cue('aliadas'), monstros2: cue('monstros', 2)
};
C.DUR = DUR; C.RW0 = C.monstros2 + .75; C.TITLE = C.RW0 + .9;'''
rw = '''// ---------- dois relógios: rewind de 0,8 s depois da pergunta, de volta à virada "é o criador" ----------
const RW0 = C.RW0, RW1 = RW0 + .8, SLOW = .4;
const RW_BACK = C.criador - .5;'''
base = base.replace('//@@CUES@@', cues).replace('//@@RW@@', rw)
base = base.replace('<title>38 Minutos</title>', '<title>Quem é o Monstro</title>').replace('//  38 MINUTOS. Cada frame', '//  QUEM É O MONSTRO. Cada frame')
base = re.sub(r'const DUR = [0-9.]+;', f'const DUR = {round(w[-1]["t1"] + 4.0, 1)};', base)
base = base.replace('//@@SCENES@@\n', '//@include cenas.js\n')
base = re.sub(r'\nconst SUBSOLAR = \[-129, -21\];[^\n]*', '', base)
open('src/video.src.html', 'w').write(base)
print('DUR', round(w[-1]['t1'] + 3.6, 1))
