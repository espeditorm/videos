# Narração frase a frase: voz Kokoro pf_dora (escolhida pelo usuário, amostra E)
import re, json, sys, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
k = Kokoro("../models/kokoro-v1.0.onnx", "../models/voices-v1.0.bin")
style = k.get_voice_style("pf_dora")
SPEED = float(sys.argv[1]) if len(sys.argv) > 1 else 1.15
text = open("narracao.txt").read()
sents = [s.strip() for s in re.split(r'(?<=[.?])\s+', text.replace("\n", " ")) if s.strip()]
SR = 24000; out = [np.zeros(int(0.3*SR))]; meta = []
def trim(a, th=0.008):
    idx = np.where(np.abs(a) > th)[0]
    return a[max(idx[0]-240, 0):idx[-1]+480] if len(idx) else a
for i, s in enumerate(sents):
    say = s.replace("Jim Carrey", "Djim Keury")   # pronúncia pedida pelo usuário
    a, sr = k.create(say, voice=style, speed=SPEED, lang="pt-br"); a = trim(a)
    gap = 0.24
    if s.startswith("O motivo"): gap = 0.36          # pausa antes da grande revelação
    if i: out.append(np.zeros(int(gap*SR)))
    t0 = sum(len(x) for x in out)/SR; out.append(a)
    meta.append({"s": s, "t0": round(t0, 3), "t1": round(t0+len(a)/SR, 3)})
audio = np.concatenate(out); sf.write("audio/voz.wav", audio, SR)
json.dump(meta, open("audio/frases.json", "w"), ensure_ascii=False, indent=1)
print(len(audio)/SR); [print(m["t0"], m["t1"], m["s"][:50]) for m in meta]
