"""Pinta terno escuro + camisa branca + gravata verde num modelo low-poly de textura fotográfica (dudes 3D).
Classifica cada triângulo pela posição no corpo e recolore os texels mantendo as dobras (luminância) da foto original."""
import json, sys, math
from PIL import Image
TRIS, TEX, OUT = sys.argv[1:4]
CX = float(sys.argv[4]) if len(sys.argv) > 4 else -0.85561
tex = Image.open(TEX).convert('RGBA'); T = tex.load(); W, H = tex.size
TERNO, CALCA, SAPATO = (46, 48, 55), (44, 46, 53), (22, 22, 25)
CAMISA, GRAVATA, GRAV_N = (226, 228, 222), (38, 186, 84), (26, 138, 60)
def lum(c): return (0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]) / 255
def tingir(c, alvo, base_l):
    k = max(0.56, min(0.80, 0.65 + 0.7 * (lum(c) - base_l)))   # dobras da foto viram sombra/luz no tecido novo
    return tuple(max(0, min(255, int(alvo[i] * k / 0.65 * 0.65 + alvo[i] * 0.35))) for i in range(3))
def parte(t):
    zs = [p[2] for p in t['p']]; xs = [abs(p[0] - CX) for p in t['p']]; z = sum(zs) / 3; x = max(xs)
    if z > 1.47 and x >= 0.12: return 'terno'
    if z > 1.47:                                   # gola da camisa (cinza na foto) vira branca; pele fica
        import colorsys
        sat = [colorsys.rgb_to_hsv(*[q / 255 for q in T[x, y][:3]])[1] for x, y, _ in texels(t)]
        return 'gola' if sat and sum(sat) / len(sat) < 0.16 and z < 1.60 and x < 0.12 else None
    if x > 0.66: return None                       # mãos
    if z < 0.10: return 'sapato'
    if z < 0.92 and x < 0.30: return 'calca'
    return 'terno'
L = json.load(open(TRIS))
def texels(t):
    uv = [(u * W, (1 - v) * H) for u, v in t['uv']]; P = t['p']
    (x0, y0), (x1, y1), (x2, y2) = uv
    den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if abs(den) < 1e-9: return
    for y in range(int(min(y0, y1, y2)), int(max(y0, y1, y2)) + 2):
        for x in range(int(min(x0, x1, x2)), int(max(x0, x1, x2)) + 2):
            px, py = x + .5, y + .5
            a = ((y1 - y2) * (px - x2) + (x2 - x1) * (py - y2)) / den
            b = ((y2 - y0) * (px - x2) + (x0 - x2) * (py - y2)) / den
            c = 1 - a - b
            if min(a, b, c) < -0.03 or not (0 <= x < W and 0 <= y < H): continue
            yield x, y, [a * P[0][i] + b * P[1][i] + c * P[2][i] for i in range(3)]
# luminância média de cada parte (pra manter só a variação das dobras)
grupos = {}
for t in L:
    k = parte(t)
    if k: grupos.setdefault(k, []).append(t)
base = {}
for k, ts in grupos.items():
    v = [lum(T[x, y]) for t in ts for x, y, _ in texels(t)]; base[k] = sum(v) / max(len(v), 1)
feito = {}
for k, ts in grupos.items():
    alvo = {'terno': TERNO, 'calca': CALCA, 'sapato': SAPATO, 'gola': CAMISA}[k]
    for t in ts:
        frente = t['n'][1] < -0.3
        tl = [lum(T[x, y]) for x, y, _ in texels(t)]; bl = sum(tl) / max(len(tl), 1)
        for x, y, p in texels(t):
            if (x, y) in feito: continue
            c = tingir(T[x, y], alvo, bl)
            if k == 'terno' and frente:
                dx, z = abs(p[0] - CX), p[2]
                v_lim = 0.085 * max(0.0, (z - 1.24) / 0.23)          # decote em V do paletó
                if dx < v_lim:
                    c = tingir(T[x, y], CAMISA, bl)
                    if dx < 0.016 and z > 1.25: c = GRAV_N if z > 1.42 else GRAVATA
                elif z > 1.245 and dx < v_lim + 0.012: c = tuple(int(q * 0.6) for q in c)   # borda da lapela
                if z < 1.24 and any(abs(z - bz) < 0.012 for bz in (1.18, 1.07)) and abs(dx - 0.03) < 0.01: c = (18, 18, 20)  # botões
            feito[(x, y)] = c
for (x, y), c in feito.items(): T[x, y] = c + (T[x, y][3],)   # mantém o recorte (alfa) original
# margem: estende a cor pintada 3 px pra fora das ilhas do UV (senão a borda da ilha mostra a cor antiga)
for _ in range(8):
    novo = {}
    for (x, y), c in feito.items():
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in feito and q not in novo and 0 <= q[0] < W and 0 <= q[1] < H: novo[q] = c
    for (x, y), c in novo.items(): T[x, y] = c + (T[x, y][3],)
    feito.update(novo)
tex.save(OUT); print({k: len(v) for k, v in grupos.items()}, 'texels', len(feito))
