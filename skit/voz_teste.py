# Testes de voz: clona o Dito a partir da referência e desenha opções de voz pro Dito PC (OmniVoice, CPU)
import json, time, torch, soundfile as sf
from faster_whisper import WhisperModel
from omnivoice import OmniVoice
torch.set_num_threads(4)
REF = "voz/dito_ref.wav"; OUT = "voz/testes/"
t = time.time()
w = WhisperModel("small", device="cpu", compute_type="int8")
import numpy as np, librosa
seg16 = librosa.load(REF, sr=16000)[0].astype(np.float32)
segs, _ = w.transcribe(seg16, language="pt")
ref_text = " ".join(s.text.strip() for s in segs)
open(OUT + "ref_text.txt", "w").write(ref_text); print("REF:", ref_text, f"{time.time()-t:.0f}s", flush=True)
m = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cpu", dtype=torch.float32)
sr = m.sampling_rate; print("model ok", f"{time.time()-t:.0f}s", flush=True)
def save(name, a):
    a = a[0] if isinstance(a, (list, tuple)) else a
    a = a.squeeze().cpu().numpy() if hasattr(a, "cpu") else a
    sf.write(OUT + name + ".wav", a, sr); print(name, f"{len(a)/sr:.1f}s", f"{time.time()-t:.0f}s", flush=True)
voce = ["Eu nunca ganhei um Oscar.", "Isso tem nome, alucinação.", "Quando não sabe, inventa com confiança."]
pc = ["Dito, você ganhou um Oscar em 2019.", "Mas soou verdade, né?", "Igual você em reunião."]
prompt = m.create_voice_clone_prompt(ref_audio=REF, ref_text=ref_text)
save("dito_clone", m.generate(text=" ".join(voce), language="pt", voice_clone_prompt=prompt))
opts = {"pc_A": "male, young adult, high pitch", "pc_B": "male, middle-aged, low pitch",
        "pc_C": "male, elderly, moderate pitch", "pc_D": "male, teenager, very high pitch"}
for k, ins in opts.items():
    save(k, m.generate(text=" ".join(pc), language="pt", instruct=ins))
