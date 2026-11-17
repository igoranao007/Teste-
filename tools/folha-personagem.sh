#!/usr/bin/env bash
# Folha de personagem pra aprovação: 5 vistas (frente, 3/4, lado, costas, rosto) + 1 no visual PS1 → previews/personagem-<nome>.jpg
# uso: bash tools/folha-personagem.sh vegetti gusta ittu metalis
set -euo pipefail
cd "$(dirname "$0")/.."; T=$(mktemp -d)
for p in "$@"; do
  for v in frente tres lado costas rosto; do node tools/foto.mjs 97-elenco 0 "p=$p&v=$v" $T/$p-$v.jpg; done
  node tools/foto.mjs 97-elenco 0 "p=$p&v=tres&ps1=1&fundo=%2306140b" $T/$p-ps1.jpg
  python3 -I - "$T" "$p" <<'PY'
import sys
from PIL import Image, ImageDraw, ImageFont
T, p = sys.argv[1], sys.argv[2]
c = Image.new('RGB', (1920, 1080), (16, 20, 18)); d = ImageDraw.Draw(c)
lay = [('rosto', (0, 0, 960, 720)), ('frente', (960, 0, 320, 540)), ('tres', (1280, 0, 320, 540)), ('lado', (1600, 0, 320, 540)), ('costas', (960, 540, 320, 540)), ('ps1', (1280, 540, 640, 540))]
for v, (x, y, w, h) in lay:
    im = Image.open(f'{T}/{p}-{v}.jpg'); W, H = im.size
    if v == 'rosto': im = im.crop((W // 2 - 600, 60, W // 2 + 600, 960)).resize((w, h))
    elif v == 'ps1': im = im.crop((W // 2 - 520, 40, W // 2 + 520, 1060)).resize((w, h))
    else: im = im.crop((W // 2 - 300, 0, W // 2 + 300, 1012)).resize((w, h))
    c.paste(im, (x, y)); d.text((x + 10, y + 8), {'ps1': 'no visual PS1', 'tres': '3/4'}.get(v, v), fill=(185, 255, 201))
try: f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 64)
except Exception: f = None
d.text((30, 740), p.upper(), fill=(57, 255, 106), font=f)
c.save(f'previews/personagem-{p}.jpg', quality=90)
PY
  echo "previews/personagem-$p.jpg"
done
rm -rf "$T"
