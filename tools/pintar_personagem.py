"""Pinta a textura inteira de um personagem sobre a base paga (psx_humanoid_male): rosto da foto (projeção de frente,
metade espelhada), cabelo pintado no couro (curto/degradê), terno + camisa + gravata, sapato, luz pintada.
Uso: pintar_personagem.py tris.json foto.jpg saida.png [tamanho]"""
import json, sys, math, colorsys
from PIL import Image, ImageFilter
TRIS, FOTO, OUT = sys.argv[1:4]; N = int(sys.argv[4]) if len(sys.argv) > 4 else 1024
# câmera orto de referência (512 px, 0,4 m, centro z=1,62) e pontos do rosto: foto -> malha (px orto)
CZ, ESC = 1.62, 0.4
PY = [(242, 22), (360, 140), (378.5, 160), (422.5, 212), (465, 250), (530, 298), (600, 340)]   # topo, sobrancelha, olho, nariz, boca, queixo, pescoço
PX = [(478, 256), (435, 220), (370, 176), (320, 140)]                                               # meio, olho, bochecha, borda
MEIO = 478
FACE_C, FACE_R = (256, 165), (70, 158)
def interp(pts, v):   # malha -> foto (pts = [(foto, malha)])
    pts = sorted(pts, key=lambda p: p[1])
    if v <= pts[0][1]: a, b = pts[0], pts[1]
    elif v >= pts[-1][1]: a, b = pts[-2], pts[-1]
    else:
        for i in range(len(pts) - 1):
            if pts[i][1] <= v <= pts[i + 1][1]: a, b = pts[i], pts[i + 1]; break
    return a[0] + (v - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
foto = Image.open(FOTO).convert('RGB').filter(ImageFilter.GaussianBlur(0.6)); F = foto.load(); FW, FH = foto.size
def amostra(mx, my):
    d = abs(mx - 256); fx = interp(PX, 256 - d); fy = interp(PY, my)   # sempre a metade boa (olho visível) da foto
    fx = min(max(fx, 0), FW - 2); fy = min(max(fy, 0), FH - 2); x0, y0 = int(fx), int(fy); ax, ay = fx - x0, fy - y0
    return [F[x0, y0][i] * (1 - ax) * (1 - ay) + F[x0 + 1, y0][i] * ax * (1 - ay) + F[x0, y0 + 1][i] * (1 - ax) * ay + F[x0 + 1, y0 + 1][i] * ax * ay for i in range(3)]
def orto(p): return (p[0] / ESC * 512 + 256, (CZ - p[2]) / ESC * 512 + 256)
def ss(a, b, v): return max(0.0, min(1.0, (v - a) / (b - a)))
def ruido(x, y, s=0): return ((x * 73856093) ^ (y * 19349663) ^ (s * 83492791)) % 1000 / 1000
# pele: média da foto nas bochechas/testa
am = [amostra(256 + dx, y) for dx in range(-60, 61, 6) for y in (120, 190, 230)]
PELE = [sum(c[i] for c in am) / len(am) for i in range(3)]
CAB, TERNO, CAMISA, GRAV, GRAV_N, SAPATO = (52, 38, 27), (44, 46, 54), (228, 229, 224), (38, 186, 84), (24, 130, 58), (20, 20, 23)
print('pele', [int(c) for c in PELE])
tex = Image.new('RGB', (N, N), (0, 0, 0)); T = tex.load(); pintado = set()
def cor(p, n, x, y):
    X, Y, Z = p; ax = abs(X); mx, my = orto(p); r = ruido(x, y)
    luz = 0.80 + 0.16 * n[2] - 0.06 * max(0, n[1]) + 0.04 * (r - 0.5)   # luz pintada: em cima mais claro
    # ---- cabeça
    rn = math.hypot(X, (Y - 0.035) * 1.2)
    if (Z > 1.592 and ax < 0.15) or (Z > 1.56 and Y < -0.045 and ax < 0.075):   # cabeça (inclui embaixo do queixo)
        orelha = ax > 0.075 and 1.62 < Z < 1.72 and abs(n[0]) > 0.35 and Y > -0.02
        frente = n[1] < -0.15
        if frente and not orelha:
            w = max(0.0, min(1.0, (1 - math.hypot((mx - FACE_C[0]) / FACE_R[0], (my - FACE_C[1]) / FACE_R[1])) / 0.32))
            w *= ss(-0.10, -0.60, n[1]) if n[1] > -0.60 else 1.0     # lados do rosto: some a foto (evita esticar/fundo)
        else: w = 0.0
        # cabelo: topo escuro; degradê nas laterais e nuca
        if n[1] < -0.45: h_top = ss(1.745, 1.770, Z)
        else: h_top = ss(1.695, 1.725, Z)
        fade = ss(1.60, 1.70, Z) * (1.0 if n[1] > -0.45 else 0.0) * (0 if orelha else 1)
        base = [PELE[i] * luz for i in range(3)]
        if fade > 0:
            k = 0.55 + 0.25 * r
            raspado = [PELE[i] * 0.55 + CAB[i] * 0.6 for i in range(3)]
            base = [base[i] * (1 - fade) + raspado[i] * k * fade for i in range(3)]
        if Z < 1.60 and n[1] > -0.2: base = [c * (0.85 + 0.15 * ss(1.545, 1.60, Z)) for c in base]
        if w > 0:
            f = amostra(mx, my); base = [base[i] * (1 - w) + f[i] * w for i in range(3)]
        if h_top > 0:
            fio = ruido(int(X * 900), int(Z * 260), 7) * 0.6 + ruido(int(X * 300), int(Z * 90), 3) * 0.4   # fios no sentido frente-trás
            k = 0.55 + 0.75 * fio
            h = h_top * (1 - w * 0.85)
            base = [base[i] * (1 - h) + CAB[i] * k * h for i in range(3)]
        return base
    # ---- pescoço / gola
    if Z > 1.53 and rn < 0.068:
        if Z > 1.592: return [PELE[i] * (0.72 + 0.1 * r) for i in range(3)]   # pescoço com sombra do queixo
        return [c * (0.9 + 0.1 * n[2]) for c in CAMISA]                         # gola em volta do pescoço
    # ---- mãos e punho
    if ax > 0.585: return [PELE[i] * luz for i in range(3)]
    if ax > 0.57: return [c * luz for c in CAMISA]
    # ---- pés
    if Z < 0.105 and ax < 0.2: return [c * (0.8 + 0.5 * max(0, n[2]) + 0.1 * r) for c in SAPATO]
    # ---- terno (paletó até z 0,90; calça abaixo)
    tecido = TERNO
    k = luz * (0.95 + 0.08 * r)
    if Z < 0.905 and ax < 0.25:
        if Z > 0.86 and n[1] > -0.2 and ax > 0.03: k *= 0.8          # sombra da barra do paletó
        if ax < 0.03 and Z > 0.70: k *= 0.7                            # entreperna
        return [c * k for c in tecido]
    if n[1] < -0.3 and ax < 0.26 and Z > 0.90:   # frente do paletó
        v = 0.05 * ss(1.28, 1.50, Z)
        if ax < v:
            t = ss(v, v - 0.006, ax)
            cam = [c * (0.88 + 0.08 * r) for c in CAMISA]; lap = [c * k * 0.6 for c in tecido]
            return [cam[i] * t + lap[i] * (1 - t) for i in range(3)]
        if ax < v + 0.012 and Z > 1.285: return [c * k * 0.6 for c in tecido]                    # lapela
        if Z < 1.27 and any(abs(Z - bz) < 0.010 for bz in (1.20, 1.09)) and abs(ax - 0.035) < 0.009: return [18, 18, 20]  # botões
        if abs(Z - 1.0) < 0.012 and 0.06 < ax < 0.15: return [c * k * 0.7 for c in tecido]       # bolso
    if 0.22 < ax < 0.27 and Z > 1.3: k *= 0.85                                                  # costura do ombro
    return [c * k for c in tecido]
L = json.load(open(TRIS))
for t in L:
    uv = [(u * N, (1 - v) * N) for u, v in t['uv']]; P = t['p']; n = t['n']
    (x0, y0), (x1, y1), (x2, y2) = uv
    den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if abs(den) < 1e-12: continue
    for y in range(int(min(y0, y1, y2)) - 1, int(max(y0, y1, y2)) + 2):
        for x in range(int(min(x0, x1, x2)) - 1, int(max(x0, x1, x2)) + 2):
            if not (0 <= x < N and 0 <= y < N): continue
            px, py = x + .5, y + .5
            a = ((y1 - y2) * (px - x2) + (x2 - x1) * (py - y2)) / den
            b = ((y2 - y0) * (px - x2) + (x0 - x2) * (py - y2)) / den
            c = 1 - a - b
            if min(a, b, c) < -0.6 / max(1, abs(den) ** 0.5): continue
            p = [a * P[0][i] + b * P[1][i] + c * P[2][i] for i in range(3)]
            T[x, y] = tuple(max(0, min(255, int(v))) for v in cor(p, n, x, y)); pintado.add((x, y))
for _ in range(4):   # margem nas bordas das ilhas
    novo = {}
    for (x, y) in pintado:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in pintado and q not in novo and 0 <= q[0] < N and 0 <= q[1] < N: novo[q] = T[x, y]
    for q, c in novo.items(): T[q] = c
    pintado.update(novo)
tex.save(OUT); print('textura', N, 'texels', len(pintado))
