# Amostras XTTS-v2 (vozes internas do modelo) falando pt-BR
import os, subprocess, sys
os.environ["COQUI_TOS_AGREED"] = "1"   # licença CPML (uso não comercial), aceita pelo usuário ao escolher o XTTS
from TTS.api import TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
print([s for s in tts.speakers][:60])
txt = "Sábado, treze de janeiro de dois mil e dezoito, oito e sete da manhã, no Havaí. De repente, os celulares do estado inteiro vibram ao mesmo tempo."
for i, spk in enumerate(sys.argv[1:]):
    f = f"vozes/xtts_{i+1}_{spk.split()[0].lower()}"
    tts.tts_to_file(text=txt, speaker=spk, language="pt", file_path=f + ".wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f + ".wav", "-b:a", "96k", f + ".mp3"]); os.remove(f + ".wav")
    print("ok", f)
