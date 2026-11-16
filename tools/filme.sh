#!/usr/bin/env bash
# Monta o filme: som (cues + voz) → render dos 10 planos → junta → out/the-green-path.mp4
# uso: bash tools/filme.sh [--so-juntar]
set -euo pipefail
cd "$(dirname "$0")/.."
audio/.venv/bin/python tools/som.py; audio/.venv/bin/python audio/synth.py 00
if [ "${1:-}" != "--so-juntar" ]; then node render.mjs ${PLANOS:-01 02 03 04 05 06 07 08 09 10} --conc=2; fi
: > out/lista.txt; for n in 01-estrada 02-dentro-do-carro 03-a-placa 04-corte-por-cor 05-a-casa 06-elevador 07-igor-anao 08-o-computador 09-projeto-mogg 10-final; do echo "file '$n.mp4'" >> out/lista.txt; done
ffmpeg -y -loglevel error -f concat -safe 0 -i out/lista.txt -i audio/00-filme.wav -map 0:v -map 1:a -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -c:a aac -b:a 256k -t 90 -movflags +faststart out/the-green-path.mp4
ffprobe -v error -show_entries format=duration,size:stream=codec_name,width,height,r_frame_rate -of default=nw=1 out/the-green-path.mp4
