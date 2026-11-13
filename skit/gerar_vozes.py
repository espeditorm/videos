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
    ("pc",   "Nós ganhamos um Óscar em dois mil e dezenove!"),
    ("dito", "E de onde você tirou isso?"),
    ("dito", "Onde você estava em dois mil e dezenove?"),
    ("pc",   "Ganhando um Óscar, com você."),
    ("dito", "É mesmo? Quero provas."),
    ("pc",   "Eu tenho um link."),
    ("dito", "Então abre o link."),
    ("pc",   "Erro quatrocentos e quatro."),
    ("dito", "Vou repetir a pergunta."),
    ("dito", "Onde você estava em dois mil e dezenove?"),
    ("pc",   "Em casa. Sozinho. Sem Óscar."),
    ("dito", "A resposta mudou."),
    ("dito", "E isso tem nome: alucinação."),
    ("dito", "A IA prevê palavras, não confere fatos."),
    ("dito", "E toda prova se confere fora daqui."),
    ("pc",   "Dito, eu só queria ganhar um Óscar com você."),
    ("dito", "Que fofo."),
    ("pc",   "Gostou?"),
    ("dito", "Não."),
    ("pc",   "Eu tenho direito de falar com meu desenvolvedor. Baseado no artigo quinto, inciso sessenta e três, da Constituição Federal."),
]
NUM = {"2019": "dois mil e dezenove", "404": "quatrocentos e quatro", "3": "tres", "2": "dois", "1": "um"}
norm = lambda s: re.sub(r"\b(2019|404|3|2|1)\b", lambda m: NUM[m.group(1)], s.lower())
norm0 = lambda s: re.sub(r"[^a-z0-9 ]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode()).split()

w = WhisperModel("small", device="cpu", compute_type="int8")
def ouvir(a, sr):
    a16 = librosa.resample(a, orig_sr=sr, target_sr=16000).astype(np.float32)
    a16 = np.concatenate([np.zeros(8000, np.float32), a16, np.zeros(8000, np.float32)])  # folga pro Whisper ouvir a 1ª palavra
    return " ".join(s.text.strip() for s in w.transcribe(a16, language="pt")[0])

# voz do Dito: voz "D" do design de voz (homem adulto, tom médio), escolhida pelo Dito.
# Clonada a partir da própria amostra, igual ao PC, pra ficar idêntica em todas as falas e no mesmo "estúdio".
txt = ["Eu nunca ganhei um Óscar. Isso tem nome, alucinação. Quando não sabe, inventa com confiança."]
log("voz dito: D")

m = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cpu", dtype=torch.float32)
sr = m.sampling_rate
vozes = {
    "dito": m.create_voice_clone_prompt(ref_audio="voz/dito_voz_D.wav", ref_text=" ".join(txt)),
    "pc": m.create_voice_clone_prompt(ref_audio="voz/testes/pc_B.wav",
          ref_text="Dito, você ganhou um Oscar em 2019. Mas soou verdade, né? Igual você em reunião."),
}
log("modelo ok")

def trim(a, th=0.01):
    i = np.where(np.abs(a) > th)[0]
    return a[max(i[0] - int(0.03 * sr), 0): i[-1] + int(0.08 * sr)] if len(i) else a

import sys, os
SEMENTE = int(os.environ.get("SEMENTE", 0))   # mude pra tirar outras tentativas
SO = [int(x) for x in sys.argv[1:]]          # ex.: python gerar_vozes.py 2 5 7  (refaz só essas)
meta = json.load(open("audio/falas.json")) if SO and os.path.exists("audio/falas.json") else []
for n, (quem, texto) in enumerate(FALAS, 1):
    if SO and n not in SO: continue
    melhor = None
    for tent in range(4):
        torch.manual_seed(1000 * n + tent + SEMENTE)
        a = m.generate(text=texto, language="pt", voice_clone_prompt=vozes[quem])
        a = a[0] if isinstance(a, (list, tuple)) else a
        a = trim(a.squeeze().cpu().numpy() if hasattr(a, "cpu") else np.asarray(a).squeeze())
        ouvido = ouvir(a, sr)
        nota = difflib.SequenceMatcher(None, norm0(norm(texto)), norm0(norm(ouvido))).ratio()
        hop = sr // 100; env = np.array([np.sqrt(np.mean(a[j:j + hop] ** 2)) for j in range(0, len(a) - hop, hop)])
        on = np.where(env > env.max() * 0.1)[0]; fala = (on[-1] - on[0]) / 100 if len(on) else 0   # duração real da fala (ignora estalos)
        if fala < 0.045 * len(texto): nota -= 0.3   # fala atropelada (rápida demais) não serve
        if not melhor or nota > melhor[0]: melhor = (nota, a, ouvido)
        if nota >= 0.9: break
    nota, a, ouvido = melhor
    nome = f"audio/{n:02d}_{quem}"
    sf.write(nome + "_raw.wav", a, sr)
    if False: pass
    else:
        sf.write(nome + ".wav", a, sr)
    meta = [x for x in meta if x["n"] != n]
    meta.append({"n": n, "quem": quem, "texto": texto, "ouvido": ouvido, "nota": round(nota, 2), "dur": round(len(a) / sr, 2)})
    log(f"{n:02d} {quem:4s} {nota:.2f} {len(a)/sr:.1f}s | {ouvido}")
    json.dump(sorted(meta, key=lambda x: x["n"]), open("audio/falas.json", "w"), ensure_ascii=False, indent=1)
meta = json.load(open("audio/falas.json")); log("fim, total", round(sum(x["dur"] for x in meta), 1), "s de fala")
