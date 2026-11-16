#!/usr/bin/env bash
# Limpa a gravação da sua voz: tira ruído, graves sobrando, comprime e normaliza.
# Uso: bash scripts/voice-clean.sh audio/voz/bruto.m4a audio/voz/voz.wav
set -euo pipefail
ffmpeg -y -i "$1" -af "highpass=f=80,afftdn=nf=-25,acompressor=threshold=-18dB:ratio=3:attack=5:release=80,loudnorm=I=-16:TP=-1.5" -ar 48000 -ac 1 "$2"
echo "Pronto: $2"
