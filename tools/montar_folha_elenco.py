"""Monta a folha da tools/folha_elenco.mjs: linhas = personagens, colunas = clipes, com nomes.
uso: python3 tools/montar_folha_elenco.py <pasta> saida.jpg "TÍTULO" """
import sys, os, re
from PIL import Image, ImageDraw, ImageFont
pasta, saida, titulo = sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else ''
arqs = sorted(f for f in os.listdir(pasta) if f.endswith('.jpg'))
linhas = {}
for f in arqs:
    n, i, c = f[:-4].split('__'); linhas.setdefault(n, []).append((i, c, f))
cols = max(len(v) for v in linhas.values()); L, TOP, ESQ = 300, 60, 150
try: fonte = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 20); grande = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 30)
except Exception: fonte = grande = ImageFont.load_default()
im = Image.new('RGB', (ESQ + cols * L, TOP + 28 + len(linhas) * L), (16, 20, 18)); d = ImageDraw.Draw(im)
d.text((12, 14), titulo, fill=(57, 255, 106), font=grande)
for r, (n, v) in enumerate(linhas.items()):
    y = TOP + 28 + r * L; d.text((10, y + L // 2 - 12), n, fill=(230, 230, 230), font=fonte)
    for k, (i, c, f) in enumerate(sorted(v)):
        x = ESQ + k * L; im.paste(Image.open(os.path.join(pasta, f)).resize((L - 4, L - 4)), (x, y))
        if r == 0: d.text((x + 4, TOP + 2), c, fill=(255, 210, 30), font=fonte)
im.save(saida, quality=88); print('folha', saida, im.size)
