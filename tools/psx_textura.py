"""Converte imagem pra textura PS1: recorte, reduz pra L×A, 15 bits (5 por canal) com pontilhado Bayer 4×4.
uso: psx_textura.py entrada saida largura altura [x0,y0,x1,y1]"""
import sys
from PIL import Image
e, s, W, H = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
im = Image.open(e).convert('RGB')
if len(sys.argv) > 5: im = im.crop(tuple(int(v) for v in sys.argv[5].split(',')))
im = im.resize((W, H), Image.LANCZOS); P = im.load()
B = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
for y in range(H):
    for x in range(W):
        d = (B[y % 4][x % 4] / 16 - .5) * 8
        P[x, y] = tuple(max(0, min(255, (int(c + d) >> 3) << 3)) for c in P[x, y])
im.save(s); print('ok', s, W, H)
