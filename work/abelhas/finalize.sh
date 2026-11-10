#!/bin/bash
# Junta as partes, codifica master (CRF 16) e entrega (CRF 20) com o áudio masterizado
set -e
cd "$(dirname "$0")"
NOME=${NOME:-video}   # nome-base dos arquivos em out/
printf "file 'part_0.mkv'\nfile 'part_1.mkv'\nfile 'part_2.mkv'\n" > chunks/list.txt
mkdir -p out
ffmpeg -v error -y -f concat -safe 0 -i chunks/list.txt -i audio/mix.wav -map 0:v -map 1:a \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  -c:a aac -b:a 320k -movflags +faststart -shortest out/${NOME}_master.mp4
ffmpeg -v error -y -i out/${NOME}_master.mp4 -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 256k -movflags +faststart out/${NOME}.mp4
ls -la out
