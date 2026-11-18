#!/usr/bin/env bash
# THE GREEN PATH v4: som → render dos 16 planos → edição no Remotion → out/the-green-path-v4.mp4
# uso: bash tools/filme4.sh        PLANOS="43 44" bash tools/filme4.sh (refaz só esses)        PLANOS=" " bash tools/filme4.sh (só a edição)
set -euo pipefail
cd "$(dirname "$0")/.."
audio/.venv/bin/python tools/som4.py; audio/.venv/bin/python audio/synth.py 00-filme4
P="${PLANOS-41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56}"; if [ -n "${P// /}" ]; then node render.mjs $P --conc=${CONC:-2}; fi
mkdir -p edicao/public/planos edicao/public/fonts
for n in $(python3 -c "import json; print(' '.join(n for n, d in json.load(open('edicao/src/legendas4.json'))['planos']))"); do ln -f out/$n.mp4 edicao/public/planos/$n.mp4 2>/dev/null || cp out/$n.mp4 edicao/public/planos/; done
cp audio/00-filme4.wav edicao/public/trilha4.wav
cp lib/fonts/geist_v5_gyByhwUxId8gMEwcGFWNOITd_woff2 edicao/public/fonts/geist.woff2; cp lib/fonts/jetbrainsmono_v24_tDbV2o_flEEny0FZhsfKu5WU4xD7OwGtT0rU_woff2 edicao/public/fonts/jetbrains.woff2
CHROME=$(ls -d /opt/pw-browsers/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell 2>/dev/null | head -1 || true)
npx remotion render edicao/src/index.ts Filme4 out/the-green-path-v4.mp4 --public-dir=edicao/public --codec=h264 --crf=21 --concurrency=4 --log=error ${CHROME:+--browser-executable="$CHROME"}
ffprobe -v error -show_entries format=duration,size -of default=nw=1 out/the-green-path-v4.mp4
