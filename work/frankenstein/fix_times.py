# Corrige os tempos do whisper: cada frase fica presa ao intervalo real gerado pelo TTS (frases.json)
import json
W = json.load(open('audio/palavras.json')); F = json.load(open('audio/frases.json'))
i = 0
for f in F:
    n = len(f['s'].split()); seg = W[i:i + n]; i += n
    a0, a1 = seg[0]['t0'], seg[-1]['t1']
    for w in seg:   # remapeia linearmente o trecho do whisper para [t0, t1] da frase
        for k in ('t0', 't1'):
            w[k] = round(f['t0'] + (w[k] - a0) / max(a1 - a0, 1e-3) * (f['t1'] - f['t0']), 3)
assert i == len(W)
json.dump(W, open('audio/palavras.json', 'w'), ensure_ascii=False, indent=0)
print('ok', len(W))
