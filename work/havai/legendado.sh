#!/bin/bash
# Original 16:9 com legenda queimada (palavra por palavra) + .srt separado
set -e
cd "$(dirname "$0")"
G=$(mktemp -d)/gray.raw
ffmpeg -v error -y -i out/38_minutos_master.mp4 -vf "fps=10,scale=480:270,format=gray" -f rawvideo "$G"
python3 legenda.py original "$G"
ffmpeg -v error -y -i out/38_minutos_master.mp4 -vf "subtitles=legenda_original.ass:fontsdir=assets/fonts" \
  -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -c:a copy -movflags +faststart out/38_minutos_legendado.mp4
ls -la out/38_minutos_legendado.mp4
