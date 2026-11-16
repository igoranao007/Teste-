#!/usr/bin/env bash
# Baixa de novo os modelos gratuitos do itch.io usados no projeto e converte pra GLB em material/modelos/itch/.
# (Ficam fora do git: algumas licenças permitem usar no vídeo, mas não redistribuir os arquivos.)
# uso: bash tools/baixar-itch.sh   — precisa do Blender no PATH
set -euo pipefail
T=${TMPDIR:-/tmp}/itch-dl; O=material/modelos/itch; mkdir -p "$T" $O/carros $O/gente $O/rua
python3 tools/itch.py "$T" https://csaf.itch.io/psx-characters-sampler https://ggbot.itch.io/psx-style-cars \
  https://heyheythere.itch.io/psx-vehicles-free https://chuckyassets.itch.io/psx-cars-free-sample
for z in "$T"/*/*.zip; do unzip -qo "$z" -d "${z%.zip}"; done
conv(){ blender -b --disable-autoexec --python tools/para_glb.py -- "$1" "$2" | grep RESUMO; }
B=$(dirname "$(find "$T" -name sy_boss_skin0.glb)"); cp "$B/sy_boss_skin0.glb" $O/gente/csaf-sy_boss.glb; cp "$B/textures/sy_boss_skin0.png" $O/gente/csaf-sy_boss.png
for n in 1 2 3 4 5 6 7 8; do conv "$(find "$T" -path "*Car 0$n/*" -name 'Car*.blend' | sort | head -1)" $O/carros/ggbot-car$n.glb; done
H=$(find "$T" -path "*/glb/*" -name sedan_blue.glb); cp "$H" $O/carros/hey-sedan-blue.glb; cp "$(dirname "$H")/road.glb" $O/rua/hey-road.glb
cp "$(find "$T" -name Sedan.glb | head -1)" $O/carros/chucky-sedan.glb
