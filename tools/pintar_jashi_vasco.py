"""Repinta a textura do Simple PSX Character (JashiPSX) como o Vegetti com o uniforme do Vasco:
rosto da foto de frente (metade boa espelhada), cabelo castanho, camisa preta com faixa branca, cruz, betfair,
VEGETTI 99 nas costas, calção preto com 99, meião com listras, chuteira preta. Mantém as dobras/sombra pintadas do original.
Uso: pintar_jashi_vasco.py tris.json textura_original.png foto.jpg saida.png"""
import json, sys, math, colorsys
sys.path.insert(0, 'tools')
from rasterizar_texels import texels
from PIL import Image, ImageDraw, ImageFont, ImageFilter
TRIS, ORIG, FOTO, OUT = sys.argv[1:5]; N = 1024
orig = Image.open(ORIG).convert('RGB').resize((N, N), Image.NEAREST); O = orig.load()
L = [t for t in json.load(open(TRIS)) if t['mat'] != 'glass']
def lum(c): return (0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]) / 255
def ss(a, b, v): return max(0.0, min(1.0, (v - a) / (b - a)))
# ---------- foto
CZ, ESC = 1.86, 0.4
PY = [(242, 10), (290, 140), (360, 180), (378.5, 215), (422.5, 280), (465, 330), (530, 385), (600, 440)]
PX = [(478, 256), (435, 200), (370, 165), (320, 130)]
def interp(pts, v):
    pts = sorted(pts, key=lambda p: p[1])
    for a, b in zip(pts, pts[1:]):
        if a[1] <= v <= b[1]: return a[0] + (v - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
    a, b = (pts[0], pts[1]) if v < pts[0][1] else (pts[-2], pts[-1])
    return a[0] + (v - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
foto = Image.open(FOTO).convert('RGB').filter(ImageFilter.MedianFilter(3)); F = foto.load(); FW, FH = foto.size
QUENTE = (1.0, 0.93, 0.82)
def amostra(mx, my):
    d = abs(mx - 256); fx = min(max(interp(PX, 256 - d), 0), FW - 1); fy = min(max(interp(PY, my), 0), FH - 1)
    c = F[int(fx), int(fy)]; return [c[i] * QUENTE[i] for i in range(3)]
am = [amostra(256 + dx, y) for dx in range(-60, 61, 6) for y in (200, 250, 300)]
PELE = [sum(c[i] for c in am) / len(am) for i in range(3)]
# ---------- desenhos do uniforme (tela em metros)
FONTE = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; FONTE_C = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
PRETO, BRANCO, VERM, CAB = (22, 22, 25), (226, 226, 222), (196, 30, 36), (48, 33, 22)
EM = 1000
def tela(): return Image.new('RGBA', (900, 1900), (0, 0, 0, 0))     # x -0,45..0,45 ; z 1,9..0
def pm(xm, zm): return (int((xm + 0.45) * EM), int((1.9 - zm) * EM))
def escrever(im, txt, xm, zm, alt, larg=None, fonte=FONTE):
    f = ImageFont.truetype(fonte, int(alt * EM)); bb = ImageDraw.Draw(im).textbbox((0, 0), txt, font=f)
    tmp = Image.new('RGBA', (bb[2] + 4, bb[3] + 4), (0, 0, 0, 0)); ImageDraw.Draw(tmp).text((2, 0), txt, font=f, fill=BRANCO + (255,))
    tmp = tmp.crop(tmp.getbbox())
    if larg: tmp = tmp.resize((int(larg * EM), int(alt * EM)))
    x, y = pm(xm, zm); im.alpha_composite(tmp, (x - tmp.width // 2, y - tmp.height // 2))
def cruz(im, xm, zm, tam):
    d = ImageDraw.Draw(im); x, y = pm(xm, zm); t = int(tam * EM); e = int(t * 0.42); m = int(t * 0.12)
    for sx, sy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
        if sx == 0: d.polygon([(x - e // 2, y + sy * t // 2), (x + e // 2, y + sy * t // 2), (x + m // 2, y), (x - m // 2, y)], fill=VERM + (255,))
        else: d.polygon([(x + sx * t // 2, y - e // 2), (x + sx * t // 2, y + e // 2), (x, y + m // 2), (x, y - m // 2)], fill=VERM + (255,))
FR, CO = tela(), tela()
cruz(FR, 0.115, 1.56, 0.075); escrever(FR, 'Kappa', -0.115, 1.58, 0.022); escrever(FR, 'betfair', 0.0, 1.33, 0.065, 0.30)
cruz(FR, -0.115, 0.62, 0.055); escrever(FR, '99', 0.115, 0.62, 0.07, 0.07)
cruz(CO, 0.0, 1.66, 0.03); escrever(CO, 'VEGETTI', 0.0, 1.565, 0.055, 0.25, FONTE_C); escrever(CO, '99', 0.0, 1.37, 0.20, 0.26, FONTE_C); escrever(CO, 'Kappa', -0.11, 0.60, 0.02)
DF, DC = FR.load(), CO.load()
def desenho(frente, X, Z):
    x, y = pm(X if frente else -X, Z)
    if not (0 <= x < 900 and 0 <= y < 1900): return None
    c = (DF if frente else DC)[x, y]; return c[:3] if c[3] > 110 else None
# ---------- regras
def regiao(t, p, o):
    X, Y, Z = p; ax = abs(X); h, s, v = colorsys.rgb_to_hsv(*[q / 255 for q in o])
    if t['obj'] == 'head':
        return 'cabelo' if v < 0.33 and not (0.0 <= h < 0.12 and s > 0.35 and v > 0.25) else 'pele_cab'
    if t['obj'] == 'arms': return 'manga' if ax < 0.43 else 'pele'
    if Z > 0.96:
        if Z > 1.69 and (0.0 <= h < 0.12 and s > 0.2): return 'pele'      # pescoço
        return 'camisa'
    if Z > 0.52: return 'calcao'
    if Z > 0.40: return 'pele'
    if Z > 0.115: return 'meiao'
    return 'chuteira'
grupos = {}
lista = list(texels(L, N))
for x, y, p, t in lista: grupos.setdefault(regiao(t, p, O[x, y]), []).append(lum(O[x, y]))
media = {k: sum(v) / len(v) for k, v in grupos.items()}; print({k: (len(v), round(media[k], 2)) for k, v in grupos.items()})
def dobra(o, k, forca=1.0):
    f = 1 + (lum(o) / max(media[k], 0.05) - 1) * forca; return max(0.55, min(1.35, f))
tex = Image.new('RGB', (N, N), (0, 0, 0)); T = tex.load(); feito = set()
for x, y, p, t in lista:
    o = O[x, y]; k = regiao(t, p, o); X, Y, Z = p; ax = abs(X); n = t['n']
    if k == 'pele_cab':
        mx, my = X / ESC * 512 + 256, (CZ - Z) / ESC * 512 + 256
        w = max(0.0, min(1.0, (1 - math.hypot((mx - 256) / 88, (my - 285) / 150)) / 0.3)) * (ss(-0.1, -0.55, n[1]) if n[1] > -0.55 else 1)
        base = [PELE[i] * dobra(o, k, 0.8) for i in range(3)]
        if w > 0: f = amostra(mx, my); base = [base[i] * (1 - w) + f[i] * w for i in range(3)]
        c = base
    elif k == 'cabelo':
        c = [CAB[i] * dobra(o, k, 1.0) for i in range(3)]
        lado = abs(n[0]) > 0.45 or n[1] > 0.4
        if lado and Z < 1.95:                                   # degradê: laterais e nuca raspadas
            f = ss(1.95, 1.84, Z)
            rasp = [PELE[i] * 0.62 + CAB[i] * 0.35 for i in range(3)]
            c = [c[i] * (1 - f) + rasp[i] * f * dobra(o, k, 0.4) for i in range(3)]
    elif k == 'pele': c = [PELE[i] * dobra(o, k, 0.9) for i in range(3)]
    elif k == 'manga':
        c = [q * dobra(o, k) for q in (BRANCO if 0.395 < ax < 0.415 else PRETO)]
    elif k == 'camisa':
        frente = n[1] < 0
        dsg = desenho(frente, X, Z) if abs(n[1]) > 0.25 else None
        A, B = (0.13, 1.71), (-0.24, 0.98); dx, dz = B[0] - A[0], B[1] - A[1]
        dist = abs((X - A[0]) * dz - (Z - A[1]) * dx) / math.hypot(dx, dz)
        cor = PRETO
        if frente and Y < 0.0 and dist < 0.052: cor = BRANCO
        if Z > 1.63 and frente:                                   # gola em V com friso branco
            vv = 0.07 * ss(1.62, 1.73, Z)
            if vv - 0.002 < ax < vv + 0.010: cor = BRANCO
        if dsg: cor = dsg
        c = [q * dobra(o, k) for q in cor]
    elif k == 'calcao':
        dsg = desenho(n[1] < 0, X, Z) if abs(n[1]) > 0.25 else None
        c = [q * dobra(o, k) for q in (dsg or PRETO)]
    elif k == 'meiao':
        cor = BRANCO if (0.355 < Z < 0.378 or 0.33 < Z < 0.342) else PRETO
        dsg = desenho(n[1] < 0, X if n[1] < 0 else X, Z + 0.0) if False else None
        c = [q * dobra(o, k, 0.7) for q in cor]
    else: c = [q * dobra(o, k, 0.8) for q in (26, 26, 28)]
    T[x, y] = tuple(max(0, min(255, int(v))) for v in c); feito.add((x, y))
for _ in range(6):
    novo = {}
    for (x, y) in feito:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in feito and q not in novo and 0 <= q[0] < N and 0 <= q[1] < N: novo[q] = T[x, y]
    for q, c in novo.items(): T[q] = c
    feito.update(novo)
RES = int(__import__('os').environ.get('RES', '512')); tex.resize((RES, RES), Image.BOX).save(OUT); print('OK', RES)
