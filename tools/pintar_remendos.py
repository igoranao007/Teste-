"""Gera o xadrez do cobertor (com bordas rasgadas = preto) e costura remendos na textura de trapo.
Uso: pintar_remendos.py trapo_512.png saida_trapo.png saida_xadrez.png"""
import sys, random
from PIL import Image, ImageDraw
ENT, SAI, XAD = sys.argv[1:4]; random.seed(7)
# xadrez gasto (verde musgo / marrom / creme)
N = 256; x = Image.new('RGB', (N, N)); P = x.load()
for j in range(N):
    for i in range(N):
        a = (i // 16) % 4 == 0; b = (j // 16) % 4 == 0; c = (i // 4) % 8 == 0 or (j // 4) % 8 == 0
        base = [70, 62, 44]
        if a: base = [88, 54, 40]
        if b: base = [52, 66, 46]
        if a and b: base = [110, 92, 64]
        if c: base = [v + 18 for v in base]
        k = 0.8 + 0.35 * random.random()
        P[i, j] = tuple(min(255, int(v * k)) for v in base)
d = ImageDraw.Draw(x)
for _ in range(14):   # furos e borda de baixo rasgada
    cx, cy, r = random.randint(0, N), random.randint(0, N), random.randint(4, 12); d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(0, 0, 0))
for i in range(0, N, 6):
    h = random.randint(4, 30); d.rectangle((i, N - h, i + 5, N), fill=(0, 0, 0))
x.save(XAD)
# remendos costurados no trapo
t = Image.open(ENT).convert('RGB'); d = ImageDraw.Draw(t)
for (x0, y0, w, h, cor) in [(60, 60, 34, 26, 'xad'), (300, 90, 28, 34, (84, 84, 80)), (120, 250, 40, 24, 'xad'), (40, 330, 30, 22, (70, 70, 74)), (200, 200, 26, 30, (92, 60, 40))]:
    if cor == 'xad': t.paste(x.crop((0, 0, w, h)), (x0, y0))
    else: d.rectangle((x0, y0, x0 + w, y0 + h), fill=cor)
    for k in range(0, w, 4): d.point([(x0 + k, y0 - 1), (x0 + k, y0 + h + 1)], fill=(210, 200, 170))
    for k in range(0, h, 4): d.point([(x0 - 1, y0 + k), (x0 + w + 1, y0 + k)], fill=(210, 200, 170))
t.save(SAI); print('ok')
