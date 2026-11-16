#!/usr/bin/env bash
# Junta o vídeo do Remotion com voz, música e efeitos (ffmpeg).
# Uso: bash scripts/mix-audio.sh out/video.mp4 audio/voz/voz.wav audio/musica/musica.mp3 [saida.mp4]
set -euo pipefail
VIDEO=$1; VOZ=$2; MUSICA=$3; OUT=${4:-out/final.mp4}
ffmpeg -y -i "$VIDEO" -i "$VOZ" -i "$MUSICA" -filter_complex \
 "[2:a]volume=0.35[m];[m][1:a]sidechaincompress=threshold=0.05:ratio=8:attack=20:release=300[duck];\
  [duck][1:a]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]" \
 -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest "$OUT"
echo "Pronto: $OUT"
