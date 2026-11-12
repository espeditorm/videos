# Gera as 18 falas do roteiro, uma por arquivo (OmniVoice, CPU).
# Dito: clone da referência (trecho de ~10 s) + leve descida de tom.
# Dito PC: clone da voz B aprovada (voz/testes/pc_B.wav), pra ficar igual em todas as falas.
# Cada fala é conferida com Whisper; se sair errada, gera de novo (até 3 tentativas).
import re, json, time, difflib, unicodedata, subprocess, numpy as np, torch, librosa, soundfile as sf
from faster_whisper import WhisperModel
from omnivoice import OmniVoice
torch.set_num_threads(4)
t0 = time.time()
log = lambda *a: print(f"[{time.time()-t0:5.0f}s]", *a, flush=True)

# texto falado (grafia ajustada pra pronúncia) — o texto da legenda fica no roteiro.md
FALAS = [
    ("pc",   "Dito, você ganhou um Óscar em dois mil e dezenove."),
    ("dito", "Eu nunca ganhei um Óscar."),
    ("pc",   "Mas soou verdade, né?"),
    ("dito", "Isso tem nome, alucinação."),
    ("dito", "A IA não consulta fatos, ela prevê palavras."),
    ("pc",   "E eu prevejo muito bem."),
    ("dito", "Quando não sabe, inventa com confiança."),
    ("pc",   "Igual você em reunião."),
    ("dito", "Três jeitos de pegar ela no flagra."),
    ("dito", "Um, peça a fonte, e abra o link."),
    ("pc",   "Eu invento link também."),
    ("dito", "Dois, pergunte de novo, de outro jeito."),
    ("dito", "Se a resposta mudar, desconfie."),
    ("dito", "Três, número, data ou citação, confira fora dela."),
    ("pc",   "Dito, eu não minto por maldade."),
    ("pc",   "Eu só quero te agradar."),
    ("dito", "Que bonito."),
    ("pc",   "Por isso você ganhou dois Óscars."),
]
norm = lambda s: re.sub(r"[^a-z0-9 ]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode()).split()

w = WhisperModel("small", device="cpu", compute_type="int8")
def ouvir(a, sr):
    a16 = librosa.resample(a, orig_sr=sr, target_sr=16000).astype(np.float32)
    return " ".join(s.text.strip() for s in w.transcribe(a16, language="pt")[0])

# referência do Dito: primeiros segmentos até ~10 s
ref, rsr = librosa.load("voz/dito_ref.wav", sr=24000)
segs = list(w.transcribe(librosa.resample(ref, orig_sr=rsr, target_sr=16000).astype(np.float32), language="pt")[0])
fim, txt = 0, []
for s in segs:
    if s.end > 11 and txt: break
    fim, txt = s.end, txt + [s.text.strip()]
ref_cut = ref[: int((fim + 0.15) * rsr)]
sf.write("voz/dito_ref10.wav", ref_cut, rsr)
log("ref dito:", f"{fim:.1f}s", " ".join(txt))

m = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cpu", dtype=torch.float32)
sr = m.sampling_rate
vozes = {
    "dito": m.create_voice_clone_prompt(ref_audio="voz/dito_ref10.wav", ref_text=" ".join(txt)),
    "pc": m.create_voice_clone_prompt(ref_audio="voz/testes/pc_B.wav",
          ref_text="Dito, você ganhou um Oscar em 2019. Mas soou verdade, né? Igual você em reunião."),
}
log("modelo ok")

def trim(a, th=0.01):
    i = np.where(np.abs(a) > th)[0]
    return a[max(i[0] - int(0.03 * sr), 0): i[-1] + int(0.08 * sr)] if len(i) else a

meta = []
for n, (quem, texto) in enumerate(FALAS, 1):
    melhor = None
    for tent in range(3):
        torch.manual_seed(1000 * n + tent)
        a = m.generate(text=texto, language="pt", voice_clone_prompt=vozes[quem])
        a = a[0] if isinstance(a, (list, tuple)) else a
        a = trim(a.squeeze().cpu().numpy() if hasattr(a, "cpu") else np.asarray(a).squeeze())
        ouvido = ouvir(a, sr)
        nota = difflib.SequenceMatcher(None, norm(texto), norm(ouvido)).ratio()
        if not melhor or nota > melhor[0]: melhor = (nota, a, ouvido)
        if nota >= 0.9: break
    nota, a, ouvido = melhor
    nome = f"audio/{n:02d}_{quem}"
    sf.write(nome + "_raw.wav", a, sr)
    if quem == "dito":  # ~1,4 semitom mais grave (tom + timbre), mesma duração
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", nome + "_raw.wav", "-af",
                        f"asetrate={sr}*0.92,aresample={sr},atempo=1/0.92", nome + ".wav"], check=True)
    else:
        sf.write(nome + ".wav", a, sr)
    meta.append({"n": n, "quem": quem, "texto": texto, "ouvido": ouvido, "nota": round(nota, 2), "dur": round(len(a) / sr, 2)})
    log(f"{n:02d} {quem:4s} {nota:.2f} {len(a)/sr:.1f}s | {ouvido}")
json.dump(meta, open("audio/falas.json", "w"), ensure_ascii=False, indent=1)
log("fim, total", round(sum(x["dur"] for x in meta), 1), "s de fala")
