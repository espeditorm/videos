#!/bin/bash
# Prévia: 640x360, quadros pares (animação em dois), 2 processos em paralelo, sem trilha
cd "$(dirname "$0")"
mkdir -p prev_exr prev_png
for k in 0 1; do
  xvfb-run -a blender -b harbor.blend -P render.py -- states.pkl prev_exr $((k*2)) 2160 4 640 360 > prev_r$k.log 2>&1 &
done
wait
python3 inkpaint.py states.pkl prev_exr prev_png 0 2160 2 > prev_p.log 2>&1
# repete cada quadro par no ímpar seguinte
ffmpeg -v error -y -framerate 12 -i prev_png/f%04d.png -vf "fps=24" -c:v libx264 -crf 20 -pix_fmt yuv420p prev_tmp.mp4 2>/dev/null || true
python3 - <<'PY'
import glob, os, shutil
fs = sorted(glob.glob('prev_png/f*.png'))
os.makedirs('prev_seq', exist_ok=True)
for i, f in enumerate(fs):
    shutil.copy(f, f'prev_seq/{2*i:05d}.png'); shutil.copy(f, f'prev_seq/{2*i+1:05d}.png')
PY
ffmpeg -v error -y -framerate 24 -i prev_seq/%05d.png -c:v libx264 -crf 20 -pix_fmt yuv420p unit07_previa.mp4
echo PREVIEW_DONE
