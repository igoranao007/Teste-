#!/usr/bin/env bash
# Prepara um vídeo REAL pra fita de evidência (A.evidencia): quadros JPEG de 480 linhas + quadros.json {fps, n, w, h}.
# O navegador do render não toca H.264; quadro em JPEG é exato e não depende de codec.
# uso: bash tools/quadros.sh <video> <pasta-saida> [ini_s=0] [dur_s=tudo] [fps=30]
set -euo pipefail
IN="${1:?uso: quadros.sh <video> <pasta-saida> [ini_s] [dur_s] [fps]}"; OUT="${2:?falta a pasta de saída}"
INI="${3:-0}"; DUR="${4:-}"; FPS="${5:-30}"
rm -rf "$OUT"; mkdir -p "$OUT"
ffmpeg -hide_banner -loglevel error -ss "$INI" ${DUR:+-t "$DUR"} -i "$IN" -an -vf "fps=$FPS,scale=-2:480:flags=lanczos" -q:v 3 "$OUT/%05d.jpg"
N=$(ls "$OUT" | grep -c '\.jpg$'); WH=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0:s=, "$OUT/00001.jpg")
printf '{"fps": %s, "n": %s, "w": %s, "h": %s, "origem": "%s", "ini": %s}\n' "$FPS" "$N" "${WH%,*}" "${WH#*,}" "$(basename "$IN")" "$INI" > "$OUT/quadros.json"
echo "$OUT: $N quadros a $FPS qps ($(du -sh "$OUT" | cut -f1)) → A.evidencia({ quadros: '$OUT', fonte: 'SOURCE: …' })"
