"""Realinha o rosto de uma folha (layout do Simple PSX Character) desenhada fora de escala: cada texel da frente
da cabeça busca a cor na folha pela posição 3D (projeção de frente) -> marcos (olhos, boca, queixo, testa) da folha.
Uso: realinhar_rosto.py tris.json folha.png saida.png "olhoD_u,olhoD_v olhoE_u,olhoE_v boca_u,boca_v queixo_u,queixo_v testa_u,testa_v" """
import json, sys, math
sys.path.insert(0, 'tools')
from rasterizar_texels import texels
from PIL import Image
TRIS, FOLHA, OUT, MARCOS = sys.argv[1:5]
im = Image.open(FOLHA).convert('RGB'); N = im.width; S = im.copy().load(); T = im.load()
import os
ORIG = os.environ.get('ORIG')   # textura original do modelo: onde ela é cabelo, não projeta o rosto
OR = Image.open(ORIG).convert('RGB').resize((N, N), Image.NEAREST).load() if ORIG else None
CZ, ESC = 1.86, 0.4
ORTO = [(200, 215), (312, 215), (256, 330), (256, 375), (256, 160)]       # olhoD, olhoE, boca, queixo, testa (câmera de frente)
NOVO = [tuple(float(v) for v in m.split(',')) for m in MARCOS.split()]
# afim por mínimos quadrados: [u v] = [mx my 1] @ A
def resolve(X, y):   # 3x3 normal equations
    import itertools
    XtX = [[sum(X[k][i] * X[k][j] for k in range(len(X))) for j in range(3)] for i in range(3)]
    Xty = [sum(X[k][i] * y[k] for k in range(len(X))) for i in range(3)]
    M = [r + [v] for r, v in zip(XtX, Xty)]
    for c in range(3):
        p = max(range(c, 3), key=lambda r: abs(M[r][c])); M[c], M[p] = M[p], M[c]
        for r in range(3):
            if r != c:
                f = M[r][c] / M[c][c]; M[r] = [a - f * b for a, b in zip(M[r], M[c])]
    return [M[i][3] / M[i][i] for i in range(3)]
X = [[mx, my, 1] for mx, my in ORTO]
Au = resolve(X, [u for u, v in NOVO]); Av = resolve(X, [v for u, v in NOVO])
for (mx, my), (u, v) in zip(ORTO, NOVO):
    print('marco', (mx, my), '->', (round(Au[0] * mx + Au[1] * my + Au[2]), round(Av[0] * mx + Av[1] * my + Av[2])), 'alvo', (u, v))
L = [t for t in json.load(open(TRIS)) if t['obj'] == 'head' and t['mat'] != 'glass']
n = 0
for x, y, p, t in texels(L, N):
    X_, Y_, Z_ = p; nn = t['n']
    if nn[1] > 0.10 or Z_ < 1.70 or Z_ > 1.99: continue
    mx, my = X_ / ESC * 512 + 256, (CZ - Z_) / ESC * 512 + 256
    w = max(0.0, min(1.0, (1 - math.hypot((mx - 256) / 96, (my - 250) / 150)) / 0.22)) * min(1.0, (0.10 - nn[1]) / 0.30)
    if w <= 0: continue
    if OR is not None:
        r, g, b = OR[x, y]
        if (r + g + b) / 3 < 75 and Z_ > 1.93: continue          # cabelo do modelo original (topo)
    mx = min(max(mx, 160), 352)   # testa acima disso: repete a pele da testa (o cabelo da folha fica mais baixo)
    u = Au[0] * mx + Au[1] * my + Au[2]; v = Av[0] * mx + Av[1] * my + Av[2]
    if not (0 <= u < N - 1 and 0 <= v < N - 1): continue
    c = S[int(u), int(v)]; o = T[x, y]
    T[x, y] = tuple(int(o[i] * (1 - w) + c[i] * w) for i in range(3)); n += 1
# 2ª passada: onde o modelo original é cabelo -> cabelo (cor da folha, textura do original); sobra solta na têmpora -> pele
if OR is not None:
    CAB = [0, 0, 0]; k = 0
    for xx in range(1180, 1240, 4):
        for yy in range(420, 760, 8):
            c = S[min(xx, N - 1), yy]
            if sum(c) / 3 < 90: CAB = [CAB[i] + c[i] for i in range(3)]; k += 1
    CAB = [v / max(k, 1) for v in CAB]
    PELE = S[int(Au[0] * 256 + Au[1] * 250 + Au[2]), int(Av[0] * 256 + Av[1] * 250 + Av[2])]
    print('cabelo', [int(v) for v in CAB], 'pele', PELE)
    m = 0
    for x, y, p, t in texels(L, N):
        X_, Y_, Z_ = p; r, g, b = OR[x, y]; l = (r + g + b) / 3
        mx_, my_ = X_ / ESC * 512 + 256, (CZ - Z_) / ESC * 512 + 256
        dentro = math.hypot((mx_ - 256) / 80, (my_ - 255) / 105) < 1 and t['n'][1] < -0.3   # olhos/sobrancelha do original
        if l < 75 and not dentro:
            if os.environ.get('CABELO_FOLHA') == '1':      # usa o cabelo desenhado na folha (cachos), não cor lisa
                c = S[x, y]
                if True:   # sempre um pedaço de cabelo da folha (cachos), repetido
                    hx0, hy0, hw, hh = [int(v) for v in os.environ.get('AMOSTRA_CABELO', '1150,400,70,80').split(',')]
                    c = S[hx0 + x % hw, hy0 + y % hh]
                T[x, y] = c; m += 1
            else:
                f = max(0.6, min(1.5, l / 40)); T[x, y] = tuple(int(min(255, CAB[i] * f)) for i in range(3)); m += 1
        elif Z_ > 1.83 and t['n'][1] > -0.5 and abs(X_) > 0.05:
            mx = X_ / ESC * 512 + 256
            if abs(mx - 256) > 60: T[x, y] = tuple(int(PELE[i] * (0.9 + 0.1 * (l / 160))) for i in range(3))
    print('cabelo texels', m)
im.save(OUT); print('texels', n)
