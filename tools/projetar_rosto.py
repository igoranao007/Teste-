"""Projeta a foto de frente de uma pessoa no rosto de um modelo low-poly (textura com UV espelhado).
Uso: projetar_rosto.py tris.json textura.png foto.png saida.png  (parâmetros de alinhamento no topo)"""
import json, sys, math
from PIL import Image, ImageFilter
TRIS, TEX, FOTO, OUT = sys.argv[1:5]
CX, CZ, ESC = -0.85561, 1.58514, 0.4          # câmera orto da frente: centro e largura (m) -> 512 px
# alinhamento foto (recorte 480x480) -> imagem orto do modelo (512x512)
OLHO_F, OLHO_M = (257, 199), (255, 170)
SX, SY = 0.80, 1.05
# máscara (em px da imagem orto): elipse do rosto, sem cabelo/orelha
MC, MR = (255, 250), (96, 150)
tex = Image.open(TEX).convert('RGBA'); T = tex.load(); W, H = tex.size
foto = Image.open(FOTO).convert('RGB'); F = foto.load()
def orto(p): return ((p[0] - CX) / ESC * 512 + 256, (CZ - p[2]) / ESC * 512 + 256)
def amostra(mx, my):
    fx = (mx - OLHO_M[0]) / SX + OLHO_F[0]; fy = (my - OLHO_M[1]) / SY + OLHO_F[1]
    fx = min(max(fx, 0), 479); fy = min(max(fy, 0), 479)
    x0, y0 = int(fx), int(fy); x1, y1 = min(x0 + 1, 479), min(y0 + 1, 479); ax, ay = fx - x0, fy - y0
    c = [F[x0, y0][i] * (1 - ax) * (1 - ay) + F[x1, y0][i] * ax * (1 - ay) + F[x0, y1][i] * (1 - ax) * ay + F[x1, y1][i] * ax * ay for i in range(3)]
    return c
# a foto é pequena: olhos, sobrancelhas e boca ficam os do modelo (nítidos); da foto vem pele, barba, maxilar e queixo
PRESERVA = [((198, 165), (48, 30)), ((312, 165), (48, 30)), ((255, 274), (46, 16))]
def peso(mx, my):
    d = math.hypot((mx - MC[0]) / MR[0], (my - MC[1]) / MR[1])
    w = max(0.0, min(1.0, (1.0 - d) / 0.18))
    for (cx, cy), (rx, ry) in PRESERVA:
        e = math.hypot((mx - cx) / rx, (my - cy) / ry)
        w *= max(0.0, min(1.0, (e - 0.75) / 0.35))
    return w
foto = foto.filter(ImageFilter.UnsharpMask(3, 120, 2)); F = foto.load()
# 1ª passada: junta os texels do rosto pra igualar o tom de pele do resto do modelo ao da foto
tris = [t for t in json.load(open(TRIS)) if t['n'][1] <= -0.05 and min(p[2] for p in t['p']) >= 1.40]
def texels(t):
    uv = [(u * W, (1 - v) * H) for u, v in t['uv']]; om = [orto(p) for p in t['p']]
    (x0, y0), (x1, y1), (x2, y2) = uv
    den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if abs(den) < 1e-9: return
    for y in range(int(min(y0, y1, y2)), int(max(y0, y1, y2)) + 2):
        for x in range(int(min(x0, x1, x2)), int(max(x0, x1, x2)) + 2):
            px, py = x + .5, y + .5
            a = ((y1 - y2) * (px - x2) + (x2 - x1) * (py - y2)) / den
            b = ((y2 - y0) * (px - x2) + (x0 - x2) * (py - y2)) / den
            c = 1 - a - b
            if min(a, b, c) < -0.02 or not (0 <= x < W and 0 <= y < H): continue
            yield x, y, a * om[0][0] + b * om[1][0] + c * om[2][0], a * om[0][1] + b * om[1][1] + c * om[2][1]
so = [0, 0, 0]; sf = [0, 0, 0]; k = 0
for t in tris:
    for x, y, mx, my in texels(t):
        if peso(mx, my) >= 0.99 and 200 < my < 340:
            o = T[x, y]; f = amostra(mx, my); k += 1
            for i in range(3): so[i] += o[i]; sf[i] += f[i]
RAZ = [sf[i] / max(so[i], 1) for i in range(3)]; print('tom', [round(r, 2) for r in RAZ])
import colorsys
for y in range(H):
    for x in range(W):
        r, g, b, al = T[x, y]; h, s_, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if 0.0 <= h < 0.11 and 0.12 < s_ < 0.75 and v > 0.40:
            T[x, y] = tuple(min(255, int(T[x, y][i] * RAZ[i])) for i in range(3)) + (al,)
# laterais da cabeça e pescoço (não projetados): mesma média de cor da pele da foto
lado = [t for t in json.load(open(TRIS)) if t['n'][1] > -0.05 and min(p[2] for p in t['p']) >= 1.45 and abs(t['n'][2]) < 0.8]
alvo = [sf[i] / max(k, 1) for i in range(3)]
pts = set()
for t in lado:
    for x, y, mx, my in texels(t):
        r, g, b, al = T[x, y]
        if r > g > b and r > 90: pts.add((x, y))
if pts:
    med = [sum(T[x, y][i] for x, y in pts) / len(pts) for i in range(3)]
    R2 = [alvo[i] / med[i] for i in range(3)]; print('lado', [round(r, 2) for r in R2], len(pts))
    for x, y in pts: T[x, y] = tuple(min(255, int(T[x, y][i] * R2[i])) for i in range(3)) + (255,)
n = 0
for t in []:
    if t['n'][1] > -0.2 or min(p[2] for p in t['p']) < 1.40: continue
    uv = [(u * W, (1 - v) * H) for u, v in t['uv']]; om = [orto(p) for p in t['p']]
    (x0, y0), (x1, y1), (x2, y2) = uv
    den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if abs(den) < 1e-9: continue
    for y in range(int(min(y0, y1, y2)), int(max(y0, y1, y2)) + 2):
        for x in range(int(min(x0, x1, x2)), int(max(x0, x1, x2)) + 2):
            px, py = x + .5, y + .5
            a = ((y1 - y2) * (px - x2) + (x2 - x1) * (py - y2)) / den
            b = ((y2 - y0) * (px - x2) + (x0 - x2) * (py - y2)) / den
            c = 1 - a - b
            if min(a, b, c) < -0.02 or not (0 <= x < W and 0 <= y < H): continue
            mx = a * om[0][0] + b * om[1][0] + c * om[2][0]; my = a * om[0][1] + b * om[1][1] + c * om[2][1]
            w = peso(mx, my)
            if w <= 0: continue
            f = amostra(mx, my); o = T[x, y]
            T[x, y] = tuple(int(o[i] * (1 - w) + f[i] * w) for i in range(3)) + (255,); n += 1
for t in tris:
    for x, y, mx, my in texels(t):
        w = peso(mx, my)
        if w <= 0: continue
        f = amostra(mx, my); o = T[x, y]
        cor = [o[i] * (1 - w) + f[i] * w for i in range(3)]
        # barba rala do Vegetti: sombra pontilhada no maxilar, queixo e buço
        bj = math.hypot((mx - 255) / 92, (my - 305) / 70)
        f_barba = max(0.0, min(1.0, (1 - bj) / 0.35)) * max(0.0, min(1.0, (my - 238) / 40))
        f_buco = max(0.0, min(1.0, (1 - math.hypot((mx - 255) / 36, (my - 257) / 10)) / 0.5)) * 0.7
        f_boca = max(0.0, min(1.0, (1 - math.hypot((mx - 255) / 38, (my - 274) / 11)) / 0.4))
        fb = max(f_barba, f_buco) * (1 - f_boca)
        if fb > 0:
            ru = ((x * 73856093) ^ (y * 19349663)) % 100 / 100
            k = 1 - fb * (0.10 + 0.10 * ru)
            cor = [cor[0] * k * 0.98, cor[1] * k, cor[2] * k * 1.02]
        T[x, y] = tuple(int(min(255, c)) for c in cor) + (255,); n += 1
tex.save(OUT); print('texels', n)
