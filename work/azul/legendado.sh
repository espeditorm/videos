#!/bin/bash
# Original 16:9 com legenda queimada (palavra por palavra) + .srt separado
set -e
cd "$(dirname "$0")"
NOME=${NOME:-video}   # nome-base dos arquivos em out/
G=$(mktemp -d)/gray.raw
ffmpeg -v error -y -i out/${NOME}_master.mp4 -vf "fps=10,scale=480:270,format=gray" -f rawvideo "$G"
python3 legenda.py original "$G"
ffmpeg -v error -y -i out/${NOME}_master.mp4 -vf "subtitles=legenda_original.ass:fontsdir=assets/fonts" \
  -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -c:a copy -movflags +faststart out/${NOME}_legendado.mp4
ls -la out/${NOME}_legendado.mp4
