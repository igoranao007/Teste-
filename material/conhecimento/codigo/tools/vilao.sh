#!/usr/bin/env bash
# Voz de VILÃO (Dom): engrossa sem mudar a velocidade (−4 semitons), soma uma camada uma oitava abaixo, graves, saturação leve e eco de sala grande.
# uso: bash tools/vilao.sh entrada.wav saida.wav
set -euo pipefail
IN="$1"; OUT="$2"; SR=$(ffprobe -v 0 -select_streams a:0 -show_entries stream=sample_rate -of csv=p=0 "$IN")
ffmpeg -y -loglevel error -i "$IN" -filter_complex "\
[0:a]asplit=2[a][b];\
[a]asetrate=${SR}*0.79,aresample=${SR},atempo=1.2658,equalizer=f=110:t=q:w=1.1:g=6,equalizer=f=2600:t=q:w=1.4:g=-3[voz];\
[b]asetrate=${SR}*0.5,aresample=${SR},atempo=2.0,lowpass=f=900,volume=0.42[sub];\
[voz][sub]amix=inputs=2:normalize=0,acompressor=threshold=-20dB:ratio=4:attack=5:release=120,\
asoftclip=type=tanh:threshold=0.85,aecho=0.8:0.55:70|140:0.22|0.12,loudnorm=I=-16" -ar 48000 -ac 1 "$OUT"
echo "ok $OUT"
