#!/bin/bash
# Versão vertical 1080x1920 (Instagram/TikTok): vídeo inteiro no meio, fundo desfocado, legenda palavra por palavra
set -e
cd "$(dirname "$0")"
NOME=${NOME:-video}   # nome-base dos arquivos em out/
python3 legenda.py
ffmpeg -v error -y -i out/${NOME}_master.mp4 -filter_complex \
 "[0:v]split[a][b];[a]scale=-2:1920,crop=1080:1920,boxblur=40:2,eq=brightness=-0.22:saturation=0.9[bg];[b]scale=1080:-2:flags=lanczos[fg];[bg][fg]overlay=0:516,subtitles=legenda_vertical.ass:fontsdir=assets/fonts[v]" \
 -map "[v]" -map 0:a -c:v libx264 -preset slow -crf 19 -pix_fmt yuv420p -profile:v high -level 4.2 \
 -c:a copy -movflags +faststart out/${NOME}_vertical.mp4
ls -la out/${NOME}_vertical.mp4
