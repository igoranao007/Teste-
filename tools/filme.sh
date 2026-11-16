#!/usr/bin/env bash
# Monta o filme: som (cues + falas) → render dos planos (skill PS1) → edição final no Remotion (título, ficha, legendas, trilha) → out/the-green-path.mp4
# uso: bash tools/filme.sh          (tudo)      PLANOS="07 08" bash tools/filme.sh   (refaz só esses planos)      PLANOS=" " bash tools/filme.sh  (só a edição)
set -euo pipefail
cd "$(dirname "$0")/.."
audio/.venv/bin/python tools/som.py; audio/.venv/bin/python audio/synth.py 00
P="${PLANOS-01 02 03 04 05 06 07 08 09 10}"; if [ -n "${P// /}" ]; then node render.mjs $P --conc=2; fi
mkdir -p edicao/public/planos edicao/public/fonts
for n in 01-estrada 02-dentro-do-carro 03-a-placa 04-corte-por-cor 05-a-casa 06-elevador 07-igor-anao 08-o-computador 09-projeto-mogg 10-final; do ln -f out/$n.mp4 edicao/public/planos/$n.mp4 2>/dev/null || cp out/$n.mp4 edicao/public/planos/; done
cp audio/00-filme.wav edicao/public/trilha.wav
cp lib/fonts/geist_v5_gyByhwUxId8gMEwcGFWNOITd_woff2 edicao/public/fonts/geist.woff2; cp lib/fonts/jetbrainsmono_v24_tDbV2o_flEEny0FZhsfKu5WU4xD7OwGtT0rU_woff2 edicao/public/fonts/jetbrains.woff2
CHROME=$(ls -d /opt/pw-browsers/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell 2>/dev/null | head -1 || true)
npx remotion render edicao/src/index.ts Filme out/the-green-path.mp4 --public-dir=edicao/public --codec=h264 --crf=21 --concurrency=4 --log=error ${CHROME:+--browser-executable="$CHROME"}
ffprobe -v error -show_entries format=duration,size -of default=nw=1 out/the-green-path.mp4
