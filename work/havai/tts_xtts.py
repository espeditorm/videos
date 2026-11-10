# Narração com XTTS-v2, voz "Abrahan Mack" (escolhida pelo usuário). Frase a frase, sem pontuação final
# (o XTTS às vezes lê o ponto como "ponto"); cada frase é conferida com o whisper contra o roteiro.
import os, re, json, sys, difflib, unicodedata, numpy as np, soundfile as sf
os.environ["COQUI_TOS_AGREED"] = "1"
from TTS.api import TTS
from scipy.signal import resample_poly
from faster_whisper import WhisperModel
from num2words import num2words
SPK, SPEED = "Abrahan Mack", float(sys.argv[1]) if len(sys.argv) > 1 else 1.1
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
wm = WhisperModel("small", device="cpu", compute_type="int8")
norm = lambda s: re.sub(r'[^a-z0-9 ]', '', unicodedata.normalize('NFD', s.lower()).encode('ascii', 'ignore').decode()).split()
SAY = {"Jim Carrey": os.environ.get("JIM", "Jim Carrey")}
text = open("narracao.txt").read()
sents = [s.strip() for s in re.split(r'(?<=[.?])\s+', text.replace("\n", " ")) if s.strip()]
SR = 24000
def trim(a, th=0.01):
    idx = np.where(np.abs(a) > th)[0]
    return a[max(idx[0] - 240, 0):idx[-1] + 600] if len(idx) else a
def gen(s):
    say = s.rstrip('.')                      # sem ponto final; "?" fica para a entonação
    for k, v in SAY.items(): say = say.replace(k, v)
    best, bs = None, -1
    for tries in range(6):
        a = np.array(tts.tts(text=say, speaker=SPK, language="pt", speed=SPEED, split_sentences=False), np.float32)
        a = trim(a)
        segs, _ = wm.transcribe(resample_poly(a, 2, 3).astype(np.float32), language="pt")
        heard_txt = re.sub(r'\d+', lambda m: num2words(int(m.group()), lang='pt_BR'), " ".join(x.text for x in segs))
        heard = norm(heard_txt.replace('-', ' ')); want = norm(s)
        extra = [w for w in heard if w in ("ponto", "pontos", "interrogacao", "virgula")]
        r = difflib.SequenceMatcher(None, " ".join(heard), " ".join(want)).ratio()
        ok = not extra and r >= .9
        print(f"  try{tries} {'ok' if ok else 'RUIM'} {r:.2f} | {' '.join(heard)}", flush=True)
        if ok: return a
        if not extra and r > bs: best, bs = a, r
    print("  !! nenhuma tentativa perfeita, usando a melhor", flush=True); return best if best is not None else a
out = [np.zeros(int(0.3 * SR), np.float32)]; meta = []
for i, s in enumerate(sents):
    print(i, s, flush=True)
    a = gen(s)
    gap = 0.36 if s.startswith("O motivo") else 0.24
    if i: out.append(np.zeros(int(gap * SR), np.float32))
    t0 = sum(len(x) for x in out) / SR; out.append(a)
    meta.append({"s": s, "t0": round(t0, 3), "t1": round(t0 + len(a) / SR, 3)})
audio = np.concatenate(out); sf.write("audio/voz.wav", audio, SR)
json.dump(meta, open("audio/frases.json", "w"), ensure_ascii=False, indent=1)
print("TOTAL", len(audio) / SR)
