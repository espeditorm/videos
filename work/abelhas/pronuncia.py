# Amostras de pronúncia (Abrahan Mack, XTTS)
import os, subprocess, numpy as np, soundfile as sf
os.environ["COQUI_TOS_AGREED"] = "1"
from TTS.api import TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
V = ["Pesquisadores do MIT criaram um robô-inseto. Lembrei do episódio Hated in the Nation, de Black Mirror",
     "Pesquisadores do M I T criaram um robô-inseto. Lembrei do episódio Rêited in de Nêixon, de Blék Mírror",
     "Pesquisadores do ême-i-tê criaram um robô-inseto. Lembrei do episódio Reitid in dê Neichan, de Bléc Mírôr"]
parts = []
for txt in V:
    a = np.array(tts.tts(text=txt, speaker="Abrahan Mack", language="pt", speed=1.25, split_sentences=False), np.float32)
    parts += [a, np.zeros(int(.8 * 24000), np.float32)]
sf.write("vozes/tmp.wav", np.concatenate(parts), 24000)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "vozes/tmp.wav", "-b:a", "96k", "vozes/pronuncia_nomes.mp3"]); os.remove("vozes/tmp.wav")
print("ok")
