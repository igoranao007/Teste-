"""Numa textura no layout do Simple PSX Character: pinta manga comprida de paletó (até o pulso) com punho de camisa,
mantendo as dobras da textura. Uso: manga_comprida.py tris.json textura.png saida.png [cor_paleto r,g,b]"""
import json, sys
sys.path.insert(0, 'tools')
from rasterizar_texels import texels
from PIL import Image, ImageFilter
TRIS, TEX, OUT = sys.argv[1:4]
COR = tuple(int(v) for v in sys.argv[4].split(',')) if len(sys.argv) > 4 else (26, 26, 29)
PUNHO = (225, 225, 220); PULSO = 0.80
im = Image.open(TEX).convert('RGB'); N = im.width; T = im.load()
B = im.filter(ImageFilter.GaussianBlur(N / 128)).load()
L = [t for t in json.load(open(TRIS)) if t['obj'] == 'arms']
def lum(c): return (0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]) / 255
pts = [(x, y, p) for x, y, p, t in texels(L, N) if 0.36 < abs(p[0]) < PULSO]
med = sum(lum(B[x, y]) for x, y, p in pts) / max(1, len(pts)); n = 0
for x, y, p in pts:
    ax = abs(p[0]); f = max(0.7, min(1.25, 1 + (lum(B[x, y]) / med - 1) * 0.6))
    c = PUNHO if ax > PULSO - 0.025 else COR
    T[x, y] = tuple(int(min(255, v * f)) for v in c); n += 1
im.save(OUT); print('manga texels', n)
