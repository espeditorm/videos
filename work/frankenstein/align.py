# Tempos por palavra: faster-whisper sobre a voz, alinhado ao texto do roteiro
import json, re, unicodedata, difflib, numpy as np, soundfile as sf
from scipy.signal import resample_poly
from faster_whisper import WhisperModel
a, sr = sf.read("audio/voz.wav"); a = resample_poly(a, 2, 3).astype(np.float32)
m = WhisperModel("small", device="cpu", compute_type="int8")
segs, _ = m.transcribe(a, language="pt", word_timestamps=True)
W = [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]
norm = lambda s: re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFD', s.lower()).encode('ascii','ignore').decode())
script = open("narracao.txt").read().split()
A = [norm(x) for x in script]; B = [norm(w[0]) for w in W]
sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
times = [None]*len(A)
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op == 'equal':
        for k in range(i2-i1): times[i1+k] = (W[j1+k][1], W[j1+k][2])
    elif j2 > j1:  # replace: spread whisper span over script words
        t0, t1 = W[j1][1], W[j2-1][2]
        for k in range(i2-i1):
            times[i1+k] = (t0+(t1-t0)*k/(i2-i1), t0+(t1-t0)*(k+1)/(i2-i1))
for i in range(len(times)):  # fill gaps by interpolation
    if times[i] is None:
        p = times[i-1] if i else (0, 0); times[i] = (p[1], p[1]+0.2)
out = [{"w": w, "t0": round(t[0], 3), "t1": round(t[1], 3)} for w, t in zip(script, times)]
json.dump(out, open("audio/palavras.json", "w"), ensure_ascii=False, indent=0)
print(sm.ratio()); print(" ".join(f'{o["w"]}@{o["t0"]}' for o in out))
