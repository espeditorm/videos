# Amostras de pronúncia dos nomes com a voz escolhida (Abrahan Mack, XTTS)
import os, subprocess, numpy as np, soundfile as sf
os.environ["COQUI_TOS_AGREED"] = "1"
from TTS.api import TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
V = [("1", "Harwood, Dakota do Norte. Era o medo de Mark Kerkvliet, morador há quarenta anos"),
     ("2", "Rárwud, Dakota do Norte. Era o medo de Mark Kérk-vlit, morador há quarenta anos"),
     ("3", "Rárvud, Dakota do Norte. Era o medo de Mark Kérkvlít, morador há quarenta anos")]
parts = []
for tag, txt in V:
    a = np.array(tts.tts(text=txt, speaker="Abrahan Mack", language="pt", speed=1.25, split_sentences=False), np.float32)
    parts += [a, np.zeros(int(.7 * 24000), np.float32)]
sf.write("vozes/tmp.wav", np.concatenate(parts), 24000)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "vozes/tmp.wav", "-b:a", "96k", "vozes/pronuncia_nomes.mp3"]); os.remove("vozes/tmp.wav")
print("ok")
