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
QUENTE = (1.02, 0.90, 0.74)
PELE = [sum(c[i] for c in am) / len(am) * QUENTE[i] for i in range(3)]
_amostra = amostra
def amostra(mx, my): c = _amostra(mx, my); return [c[i] * QUENTE[i] for i in range(3)]
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
    # ---- pescoço (pele) e gola em V branca da camisa
    rn = math.hypot(X, (Y - 0.035) * 1.2)
    if Z > 1.53 and rn < 0.085: return [PELE[i] * (0.80 + 0.1 * r) for i in range(3)]
    # ---- mãos e braço (manga curta até a metade do braço)
    if ax > 0.33: return [PELE[i] * luz for i in range(3)]
    if 0.30 < ax <= 0.33: return [c * luz for c in BRANCO] if 0.305 < ax < 0.318 else [c * luz for c in PRETO]   # punho da manga
    # ---- chuteira
    if Z < 0.105: return [c * (0.8 + 0.5 * max(0, n[2]) + 0.15 * r) for c in (24, 24, 26)]
    # ---- meião preto com listras brancas
    if Z < 0.47:
        if 0.395 < Z < 0.425: return [c * luz for c in BRANCO]
        if 0.345 < Z < 0.36: return [c * luz for c in BRANCO]
        if 0.15 < Z < 0.19 and n[1] < -0.3 and abs(ax - HXP) < 0.025: return [c * luz for c in BRANCO]   # logo do meião
        return [c * luz * (0.9 + 0.12 * r) for c in PRETO]
    # ---- joelho/coxa de fora (pele)
    if Z < 0.62: return [PELE[i] * luz for i in range(3)]
    # ---- calção preto com 99
    if Z < 0.94:
        if 0.62 <= Z < 0.645: return [c * luz for c in PRETO2]
        t = texto(DESENHO_FRENTE, X, Z) if n[1] < 0 else texto(DESENHO_COSTAS, -X, Z)
        if t: return [c * luz for c in t]
        return [c * luz * (0.92 + 0.1 * r) for c in PRETO]
    # ---- camisa preta com a faixa diagonal branca
    if n[1] < -0.2:
        t = texto(DESENHO_FRENTE, X, Z)
        if t: return [c * luz for c in t]
    elif n[1] > 0.2:
        t = texto(DESENHO_COSTAS, -X, Z)
        if t: return [c * luz for c in t]
    # faixa diagonal (só na frente): da gola (lado esquerdo do corpo) até o quadril direito
    A, Bp = (0.045, 1.50), (-0.20, 0.97)
    dx, dz = Bp[0] - A[0], Bp[1] - A[1]; L = math.hypot(dx, dz)
    dist = abs((X - A[0]) * dz - (Z - A[1]) * dx) / L
    if dist < 0.042 and Z > 0.94 and Y < 0.03: return [c * luz * (0.94 + 0.08 * r) for c in BRANCO]
    if 0.27 < ax <= 0.30 and Z > 1.3: return [c * luz for c in BRANCO]       # barra branca na manga
    if n[1] < -0.2 and Z > 1.42:                                               # gola em V com friso branco
        v = 0.06 * ss(1.42, 1.54, Z)
        if ax < v: return [PELE[i] * (0.78 + 0.1 * r) for i in range(3)]
        if ax < v + 0.013: return [c * luz for c in BRANCO]
    if Z > 1.50 and rn < 0.10: return [c * luz for c in BRANCO]              # gola atrás
    return [c * luz * (0.92 + 0.1 * r) for c in PRETO]
# ---- desenhos (texto/escudo) projetados de frente e de costas: tela em metros -> pixels
from PIL import ImageDraw, ImageFont
FONTE = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
PRETO, PRETO2, BRANCO, VERM = (24, 24, 27), (36, 36, 40), (232, 232, 228), (200, 30, 36)
HXP = 0.087
ESCALA = 1000   # px por metro
def tela(): return Image.new('RGBA', (800, 1000), (0, 0, 0, 0))     # x -0,4..0,4 ; z 1,7..0,7
def pm(xm, zm): return (int((xm + 0.4) * ESCALA), int((1.7 - zm) * ESCALA))
def escrever(im, txt, xm, zm, alt, cor=BRANCO, cond=1.0):
    f = ImageFont.truetype(FONTE, int(alt * ESCALA)); d = ImageDraw.Draw(im)
    w = d.textlength(txt, font=f); x, y = pm(xm, zm)
    tmp = Image.new('RGBA', (int(w) + 4, int(alt * ESCALA * 1.3)), (0, 0, 0, 0)); ImageDraw.Draw(tmp).text((2, 0), txt, font=f, fill=cor + (255,))
    tmp = tmp.resize((max(1, int(tmp.width * cond)), tmp.height)); im.alpha_composite(tmp, (x - tmp.width // 2, y - tmp.height // 2))
def cruz(im, xm, zm, tam):
    d = ImageDraw.Draw(im); x, y = pm(xm, zm); t = int(tam * ESCALA); e = t // 3
    d.polygon([(x - e // 2, y - t // 2), (x + e // 2, y - t // 2), (x + e // 4, y), (x - e // 4, y)], fill=VERM + (255,))
    d.polygon([(x - e // 2, y + t // 2), (x + e // 2, y + t // 2), (x + e // 4, y), (x - e // 4, y)], fill=VERM + (255,))
    d.polygon([(x - t // 2, y - e // 2), (x - t // 2, y + e // 2), (x, y + e // 4), (x, y - e // 4)], fill=VERM + (255,))
    d.polygon([(x + t // 2, y - e // 2), (x + t // 2, y + e // 2), (x, y + e // 4), (x, y - e // 4)], fill=VERM + (255,))
DESENHO_FRENTE = tela(); DESENHO_COSTAS = tela()
cruz(DESENHO_FRENTE, 0.095, 1.34, 0.065)                       # cruz de malta no peito esquerdo
escrever(DESENHO_FRENTE, 'K', -0.10, 1.36, 0.035)              # marca no peito direito
escrever(DESENHO_FRENTE, 'betfair', 0.0, 1.17, 0.058)          # patrocínio
escrever(DESENHO_FRENTE, '99', 0.12, 0.74, 0.07)               # calção: 99 na perna esquerda
cruz(DESENHO_FRENTE, -0.12, 0.74, 0.05)                        # calção: cruz na perna direita
cruz(DESENHO_COSTAS, 0.0, 1.47, 0.03)                          # costas: cruzinha
escrever(DESENHO_COSTAS, 'VEGETTI', 0.0, 1.38, 0.05, cond=0.85)
escrever(DESENHO_COSTAS, '99', 0.0, 1.20, 0.19, cond=0.85)
escrever(DESENHO_COSTAS, 'K', 0.12, 0.70, 0.035)
DF, DC = DESENHO_FRENTE.load(), DESENHO_COSTAS.load()
def texto(im, xm, zm):
    x, y = pm(xm, zm)
    if not (0 <= x < 800 and 0 <= y < 1000): return None
    c = (DF if im is DESENHO_FRENTE else DC)[x, y]
    return c[:3] if c[3] > 128 else None
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
import os
RES = int(os.environ.get('RES', '256'))
if RES < N: tex = tex.resize((RES, RES), Image.BOX).resize((N, N), Image.NEAREST)   # pixelado de PS1
tex.save(OUT); print('textura', N, '->', RES, 'texels', len(pintado))
