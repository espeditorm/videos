# Monta a linha do tempo: junta as falas com pausas, aplica o "som de computador" no PC,
# tira os tempos de cada palavra (Whisper) e grava timeline.json + trilhas por personagem.
import json, re, subprocess, unicodedata, numpy as np, soundfile as sf, librosa
from faster_whisper import WhisperModel

SR = 48000
INTRO, OUTRO = 1.5, 1.9
# texto da legenda (como aparece na tela) e plano de cada fala
ROTEIRO = [
    ("S1",  "Nós ganhamos um Oscar em 2019!"),
    ("S4",  "E de onde você tirou isso?"),
    ("S2",  "Onde você estava em 2019?"),
    ("S3",  "Ganhando um Oscar, com você."),
    ("S2b", "É mesmo? Quero provas."),
    ("S3",  "Eu tenho um link."),
    ("S6",  "Então abre o link."),
    ("S3b", "Erro 404."),
    ("S2",  "Vou repetir a pergunta."),
    ("S6",  "Onde você estava em 2019?"),
    ("S3",  "Em casa. Sozinho. Sem Oscar."),
    ("S4b", "A resposta mudou."),
    ("S2",  "E isso tem nome: alucinação."),
    ("S2b", "A IA prevê palavras, não confere fatos."),
    ("S6",  "E toda prova se confere fora daqui."),
    ("S5",  "Dito, eu só queria ganhar um Oscar com você."),
    ("S4",  "Que fofo."),
    ("S5b", "Gostou?"),
    ("S4b", "Não."),
    ("S3c", "Quero falar com o meu desenvolvedor."),
]
# pausas curtas entre falas (método do Notion: tira o silêncio de cada fala e junta com respiros curtos)
MESMO, TROCA = 0.18, 0.28          # mesma pessoa continua / outra pessoa responde
PAUSA = {7: 0.3, 9: 1.3, 10: 0.3, 15: 0.3, 16: 0.6, 17: 0.4, 19: 0.3, 20: 0.3}   # respiros especiais antes da fala n (9: "segundos depois" do 404)

def limpar(a, sr, lead=0.05, tail=0.08, max_pausa=0.28):
    """Corta silêncio do começo/fim (pelo volume) e encurta pausas internas longas."""
    hop = int(sr * 0.01); e = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a) - hop, hop)])
    on = np.where(e > e.max() * 0.06)[0]
    if not len(on): return a
    a = a[max(on[0] * hop - int(lead * sr), 0): min((on[-1] + 1) * hop + int(tail * sr), len(a))]
    e = e[max(on[0] - int(lead * 100), 0): on[-1] + 1 + int(tail * 100)]
    quiet = e < e.max() * 0.06; out, i = [], 0
    while i < len(quiet):
        j = i
        while j < len(quiet) and quiet[j] == quiet[i]: j += 1
        seg = a[i * hop: j * hop]
        if quiet[i] and (j - i) / 100 > max_pausa and 0 < i and j < len(quiet):
            k = int(max_pausa * sr / 2); seg = np.concatenate([seg[:k], seg[-k:]])
        out.append(seg); i = j
    out.append(a[len(quiet) * hop:])
    return np.concatenate(out)
falas = json.load(open("audio/falas.json"))
w = WhisperModel("small", device="cpu", compute_type="int8")
norm = lambda s: re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())

# mesma "sala de estúdio" pras duas vozes: corta grave sobrando e caixa, presença igual,
# expansor suave pra secar o rabo de eco, compressão leve e volume igualado por fala
ESTUDIO = ("highpass=f=85,equalizer=f=450:t=q:w=1.2:g=-2,equalizer=f=3000:t=q:w=1.4:g=1.5,"
           "agate=threshold=0.015:range=0.3:attack=2:release=50:ratio=2,"
           "acompressor=threshold=-20dB:ratio=2.5:attack=6:release=90:makeup=2dB,deesser=i=0.2,"
           "loudnorm=I=-18:TP=-2:LRA=7,aresample=48000")
def estudio(src, dst):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", ESTUDIO, dst], check=True)

def efeito_pc(src, dst):  # leve timbre digital: comb curto + bitcrush discreto + brilho
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af",
        "aresample=48000,highpass=f=110,aecho=0.85:0.5:7:0.22,acrusher=bits=10:mix=0.12:mode=log:aa=1,"
        "equalizer=f=3200:t=q:w=1.2:g=2", dst], check=True)

voz = {"dito": [], "pc": []}; cur = INTRO; linhas = []; prev = None
for f, (shot, legenda) in zip(falas, ROTEIRO):
    n, quem = f["n"], f["quem"]
    src = f"audio/{n:02d}_{quem}.wav"
    if quem == "pc":
        efeito_pc(src, f"audio/{n:02d}_pc_fx.wav"); src = f"audio/{n:02d}_pc_fx.wav"
    estudio(src, f"audio/{n:02d}_{quem}_est.wav"); src = f"audio/{n:02d}_{quem}_est.wav"
    a, _ = librosa.load(src, sr=SR); a = limpar(a, SR)
    gap = PAUSA.get(n, TROCA if quem != prev else MESMO)
    if n > 1: cur += gap
    t0, t1 = cur, cur + len(a) / SR
    # tempos das palavras
    segs, _ = w.transcribe(librosa.resample(a, orig_sr=SR, target_sr=16000), language="pt", word_timestamps=True)
    ww = [(x.word.strip(), x.start, x.end) for s in segs for x in s.words]
    disp = legenda.split()
    if ww and len(ww) == len(disp):
        tempos = [(t0 + s, t0 + e) for _, s, e in ww]
    else:  # distribui pelo tamanho das palavras entre o início e o fim da fala
        s0, s1 = (ww[0][1], ww[-1][2]) if ww else (0.0, len(a) / SR)
        L = np.cumsum([0] + [len(norm(d)) + 2 for d in disp]); L = L / L[-1]
        tempos = [(t0 + s0 + (s1 - s0) * L[i], t0 + s0 + (s1 - s0) * L[i + 1]) for i in range(len(disp))]
    linhas.append({"n": n, "quem": quem, "shot": shot, "texto": legenda, "t0": round(t0, 3), "t1": round(t1, 3),
                   "palavras": [{"w": d, "t0": round(a_, 3), "t1": round(b_, 3)} for d, (a_, b_) in zip(disp, tempos)]})
    voz[quem].append((t0, a)); cur = t1; prev = quem
    print(f"{n:02d} {quem:4s} {shot:4s} {t0:6.2f}-{t1:6.2f} {legenda}")
total = cur + OUTRO
for quem, partes in voz.items():
    tr = np.zeros(int(total * SR) + SR, np.float32)
    for t0, a in partes:
        i = int(t0 * SR); tr[i:i + len(a)] += a
    sf.write(f"audio/trilha_{quem}.wav", tr[: int(total * SR)], SR)
json.dump({"dur": round(total, 3), "intro": INTRO, "outro": OUTRO, "linhas": linhas},
          open("timeline.json", "w"), ensure_ascii=False, indent=1)
print("total", round(total, 2), "s")
