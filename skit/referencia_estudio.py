# Cria uma referência "de estúdio" pra voz do Dito, sem a sala do áudio de WhatsApp:
# 1) limpa a gravação (ruído + ressonância de caixa + rabo de eco)
# 2) clona a partir dela e gera frases neutras
# 3) escolhe a frase mais limpa e usa como nova referência (voz/dito_ref_estudio.wav)
import subprocess, numpy as np, torch, librosa, soundfile as sf, noisereduce as nr
from omnivoice import OmniVoice
torch.set_num_threads(4)

a, sr = librosa.load("voz/dito_ref.wav", sr=24000)
a = a[: int(6.25 * sr)]
a = nr.reduce_noise(y=a, sr=sr, stationary=False, prop_decrease=0.85)
sf.write("voz/_ref_nr.wav", a, sr)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "voz/_ref_nr.wav", "-af",
    "highpass=f=90,equalizer=f=250:t=q:w=1:g=-3,equalizer=f=480:t=q:w=1:g=-6,equalizer=f=900:t=q:w=1.5:g=-2,"
    "equalizer=f=2600:t=q:w=1.2:g=7,highshelf=f=5000:g=6,"
    "agate=threshold=0.02:range=0.25:attack=3:release=60:ratio=3", "voz/dito_ref_limpo.wav"], check=True)

m = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cpu", dtype=torch.float32); sr = m.sampling_rate
P = m.create_voice_clone_prompt(ref_audio="voz/dito_ref_limpo.wav",
        ref_text="Imagina um mundo onde as abelhas não existem mais, sem aquele zumbido tranquilo no jardim.")
FR = "Oi, eu sou o Dito. Hoje eu vou te mostrar um jeito simples de saber se a inteligência artificial está falando a verdade."
fr = librosa.fft_frequencies(sr=sr, n_fft=2048)
def caixa(x):  # quanto menor, menos "caixa": energia 300-700 Hz relativa a 1,5-4 kHz + rabo de eco
    p = (np.abs(librosa.stft(x, n_fft=2048)) ** 2).mean(1)
    db = lambda lo, hi: 10 * np.log10(p[(fr >= lo) & (fr < hi)].mean() + 1e-12)
    e = librosa.feature.rms(y=x, hop_length=240)[0]; e = 20 * np.log10(e + 1e-6)
    cauda = np.mean(np.clip(np.diff(e), -60, 0)[np.diff(e) < -3])  # decaimento médio: mais negativo = mais seco
    return db(300, 700) - db(1500, 4000) + 0.3 * cauda
best = None
for s in range(4):
    torch.manual_seed(500 + s)
    x = m.generate(text=FR, language="pt", voice_clone_prompt=P); x = x[0] if isinstance(x, (list, tuple)) else x
    x = x.squeeze().cpu().numpy() if hasattr(x, "cpu") else np.asarray(x).squeeze()
    c = caixa(x); print(s, f"caixa {c:.1f}", f"{len(x)/sr:.1f}s", flush=True)
    sf.write(f"voz/_cand{s}.wav", x, sr)
    if best is None or c < best[0]: best = (c, x, s)
sf.write("voz/dito_ref_estudio.wav", best[1], sr)
open("voz/dito_ref_estudio.txt", "w").write(FR)
print("escolhida", best[2], round(best[0], 1))
