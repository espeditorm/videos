# Narração com XTTS-v2 (voz em $VOZ, padrão "Abrahan Mack", a favorita do usuário). Frase a frase, sem pontuação final
# (o XTTS às vezes lê o ponto como "ponto"); cada frase é conferida com o whisper contra o roteiro.
import os, re, json, sys, difflib, unicodedata, numpy as np, soundfile as sf
os.environ["COQUI_TOS_AGREED"] = "1"
from TTS.api import TTS
from scipy.signal import resample_poly
from faster_whisper import WhisperModel
from num2words import num2words
SPK, SPEED = os.environ.get("VOZ", "Abrahan Mack"), float(sys.argv[1]) if len(sys.argv) > 1 else 1.1
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
wm = WhisperModel("small", device="cpu", compute_type="int8")
norm = lambda s: re.sub(r'[^a-z0-9 ]', '', unicodedata.normalize('NFD', s.lower()).encode('ascii', 'ignore').decode()).split()
SAY = {"Jim Carrey": os.environ.get("JIM", "Jim Carrey")}
# nomes em inglês falados com pronúncia inglesa: o trecho é gerado com language="en" e emendado na frase
ENMAP = dict((w.split("=") + [w])[:2] for w in os.environ.get("EN", "").split("|") if w)   # "MIT=M. I. T.": como falar em inglês
EN = list(ENMAP)
def seg_ok(a, txt, lang):
    # confere um trecho sozinho: o whisper deve ouvir exatamente as palavras pedidas (pega sílabas inventadas)
    segs, _ = wm.transcribe(resample_poly(a, 2, 3).astype(np.float32), language=lang)
    h = norm(re.sub(r'\d+', lambda m: num2words(int(m.group()), lang='pt_BR' if lang == 'pt' else 'en'), " ".join(x.text for x in segs)).replace('-', ' '))
    w = norm(txt.replace('-', ' '))
    if lang == 'en' and len(w) > 0 and all(len(x) == 1 for x in w): w = [''.join(w)]   # sigla soletrada: "m i t"
    r = difflib.SequenceMatcher(None, " ".join(h), " ".join(w)).ratio()
    return len(h) <= len(w) and r >= (.6 if lang == 'en' else .85)
def synth(say):
    parts = re.split("(" + "|".join(re.escape(w) for w in EN) + ")", say) if EN else [say]
    out = []
    for p in parts:
        if not re.search(r"\w", p): continue          # pontuação solta ("?") não vira trecho de áudio
        lang = "en" if p in EN else "pt"
        txt = ENMAP.get(p, p).strip(" ,")
        for k in range(5):
            a = trim(np.array(tts.tts(text=txt, speaker=SPK, language=lang, speed=SPEED, split_sentences=False), np.float32))
            if len(parts) == 1 or seg_ok(a, txt, lang): break
            print(f"    trecho refeito ({lang}): {txt}", flush=True)
        out += [a, np.zeros(int(.06 * SR), np.float32)]
    return np.concatenate(out[:-1])
text = open("narracao.txt").read()
sents = [s.strip() for s in re.split(r'(?<=[.?])\s+', text.replace("\n", " ")) if s.strip()]
SR = 24000
def trim(a, th=0.01):
    idx = np.where(np.abs(a) > th)[0]
    return a[max(idx[0] - 1800, 0):idx[-1] + 600] if len(idx) else a
def gen(s):
    say = s.rstrip('.')                      # sem ponto final; "?" fica para a entonação
    for k, v in SAY.items(): say = say.replace(k, v)
    best, bs = None, -1
    for tries in range(6):
        a = synth(say)
        segs, _ = wm.transcribe(resample_poly(a, 2, 3).astype(np.float32), language="pt")
        heard_txt = re.sub(r'\d+', lambda m: num2words(int(m.group()), lang='pt_BR'), " ".join(x.text for x in segs))
        heard = norm(heard_txt.replace('-', ' ')); want = norm(s)
        extra = [w for w in set(heard) if w in ("ponto", "pontos", "interrogacao", "virgula") and heard.count(w) > want.count(w)]
        r = difflib.SequenceMatcher(None, " ".join(heard), " ".join(want)).ratio()
        ok = not extra and r >= .93 and abs(len(heard) - len(want)) <= 1
        print(f"  try{tries} {'ok' if ok else 'RUIM'} {r:.2f} | {' '.join(heard)}", flush=True)
        if ok: return a
        if not extra and r > bs: best, bs = a, r
    print("  !! nenhuma tentativa perfeita, usando a melhor", flush=True); return best if best is not None else a
OLD = {f["s"]: f for f in json.load(open("audio/frases.json"))} if os.path.exists("audio/frases.json") else {}
OLDA = sf.read("audio/voz.wav", dtype="float32")[0] if OLD else None
out = [np.zeros(int(0.3 * SR), np.float32)]; meta = []
for i, s in enumerate(sents):
    print(i, s, flush=True)
    if s in OLD and not (os.environ.get("FORCE") and re.search(os.environ["FORCE"], s)): a = OLDA[int(OLD[s]["t0"] * SR):int(OLD[s]["t1"] * SR)]; print("  reaproveitada", flush=True)
    else: a = gen(s)
    gap = 0.36 if s.startswith("O motivo") else 0.24
    if i: out.append(np.zeros(int(gap * SR), np.float32))
    t0 = sum(len(x) for x in out) / SR; out.append(a)
    meta.append({"s": s, "t0": round(t0, 3), "t1": round(t0 + len(a) / SR, 3)})
audio = np.concatenate(out); sf.write("audio/voz.wav", audio, SR)
json.dump(meta, open("audio/frases.json", "w"), ensure_ascii=False, indent=1)
print("TOTAL", len(audio) / SR)
