# Mixagem final: vozes + música baixinha (com ducking) + "plim" nos cards, -14 LUFS. Junta com o vídeo.
import json, subprocess, sys
TL = json.load(open("timeline.json")); D = TL["dur"]
MUS = "assets/musica.wav"   # trilha original (musica.py), gerada com a duração do vídeo
subprocess.run([sys.executable, "musica.py", str(D + 0.5)], check=True)
SFX = "../work/assets/sfx/pino.ogg"
cards = [l["t0"] - 0.05 for l in TL["linhas"] if l["n"] in (10, 12, 14)]
inp = ["-i", "audio/trilha_dito.wav", "-i", "audio/trilha_pc.wav", "-i", MUS] + sum([["-i", SFX] for _ in cards], [])
fc = ["[0][1]amix=inputs=2:normalize=0,volume=1.0,asplit=2[voz][sc]",
      f"[2]atrim=0:{D},asetpts=PTS-STARTPTS,volume=0.30,afade=t=in:d=1.0,afade=t=out:st={D-2.2}:d=2.2[mu]",
      "[mu][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[mud]"]
sx = []
for i, t in enumerate(cards):
    fc.append(f"[{3+i}]adelay={int(t*1000)}|{int(t*1000)},volume=0.5[s{i}]"); sx.append(f"[s{i}]")
fc.append(f"[voz][mud]{''.join(sx)}amix=inputs={2+len(sx)}:normalize=0,loudnorm=I=-14:TP=-1.0:LRA=9,aresample=48000[out]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", ";".join(fc), "-map", "[out]", "-t", str(D),
                "-c:a", "pcm_s16le", "out/mix.wav"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "out/video_mudo.mp4", "-i", "out/mix.wav", "-map", "0:v", "-map", "1:a",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", "out/skit01_alucinacao.mp4"], check=True)
print("ok out/skit01_alucinacao.mp4")
