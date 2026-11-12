#!/bin/bash
# Render em paralelo (4 partes) + concatena + mixa o áudio.
set -e
cd "$(dirname "$0")"
PY=${PY:-python3}
N=${N:-4}
mkdir -p out
for w in $(seq 0 $((N-1))); do $PY render.py $w $N > out/log_$w.txt 2>&1 & done
wait
: > out/lista.txt; for w in $(seq 0 $((N-1))); do echo "file 'parte_$w.mkv'" >> out/lista.txt; done
ffmpeg -v error -y -f concat -safe 0 -i out/lista.txt -c copy out/video_mudo.mp4
$PY mixar.py
