# Monta src/video.src.html: base (globo, personagens, texto) + deixas + relógio da história + cenas.js
import json, re
w = json.load(open('audio/palavras.json'))
base = open('src/base.part.html').read()
cues = '''const C = {
  mais: cue('mais', 1), flores: cue('flores'), comida: cue('comida'), tres: cue('três'), quatro: cue('quatro'), real: cue('real'),
  so: cue('só', 1), robos: cue('abelhas-robôs', 1), pesquisadores: cue('pesquisadores'), mit1: cue('mit', 1), clipe: cue('clipe'),
  dezessete: cue('dezessete'), futuro: cue('futuro'), fazendas: cue('fazendas'), sombrio: cue('sombrio'), black1: cue('black', 1),
  hackeia: cue('hackeia'), armas: cue('armas'), agora: cue('agora'), mit2: cue('mit', 2), quem: cue('quem'), culpado: cue('culpado'),
  fabricante: cue('fabricante'), hacker: cue('hacker'), nos: cue('nós'), abelha: cue('abelha'), carro: cue('carro'), drone: cue('drone'),
  lista: cue('lista'), cresce: cue('cresce'), tecnologia1: cue('tecnologia', 1), quanto: cue('quanto'), riscos1: cue('riscos', 1),
  riscos2: cue('riscos', 2), ponto: cue('ponto'), questionar: cue('questionar'), porque: cue('lição') - .7, salva: cue('salva'), condena: cue('condena')
};
C.DUR = DUR; C.TITLE = C.condena + .35;'''
rw = '''// ---------- dois relógios: rewind de 0,8 s em "Porque" de volta à abelha-robô reanimando a flor ----------
const RW0 = C.porque - .25, RW1 = RW0 + .8, SLOW = .08;
const RW_BACK = C.robos + .55;'''
base = base.replace('//@@CUES@@', cues).replace('//@@RW@@', rw)
base = base.replace('<title>38 Minutos</title>', '<title>Salva ou Condena</title>').replace('//  38 MINUTOS. Cada frame', '//  SALVA OU CONDENA. Cada frame')
base = re.sub(r'const DUR = [0-9.]+;', f'const DUR = {round(w[-1]["t1"] + 2.75, 1)};', base)
base = base.replace('//@@SCENES@@\n', '//@include cenas.js\n')
base = re.sub(r'\nconst SUBSOLAR = \[-129, -21\];[^\n]*', '', base)
open('src/video.src.html', 'w').write(base)
print('DUR', round(w[-1]['t1'] + 2.75, 1))
