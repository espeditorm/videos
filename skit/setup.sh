#!/bin/bash
# Instala o ambiente do skit (CPU). Uma vez por máquina: bash skit/setup.sh
# Precisa de python3 e de um ffmpeg com rubberband (o ffmpeg do Ubuntu/Debian já tem).
set -e
cd "$(dirname "$0")"
python3 -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q --index-url https://download.pytorch.org/whl/cpu torch torchaudio
.venv/bin/pip install -q omnivoice faster-whisper soundfile librosa "rembg[cpu]" opencv-python-headless \
    noisereduce fonttools brotli scipy pillow "numpy>=2.0,<2.8"
ffmpeg -hide_banner -filters 2>/dev/null | grep -q rubberband || echo "AVISO: seu ffmpeg não tem o filtro rubberband"
echo "ok: ambiente em skit/.venv"
