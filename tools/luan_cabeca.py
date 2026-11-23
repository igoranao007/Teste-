# CABEÇA DO LUAN GORDO (aliado do DOM) — mesmo método da Entrada (loft de anéis + textura única pintada), sem foto:
# rosto redondo e cheio (papada), pele "branco queimado", olhos e sobrancelhas PINTADOS, cabelo escuro meio cacheado em tufos,
# ÓCULOS de armação preta e MÁSCARA DE GÁS (metade de baixo do rosto) com dois filtros de aro amarelo (luz própria).
# Roda no python do sistema (numpy + PIL). Saída em material/producao/personagens/luan/texturas/.
import json, math, os, sys
import numpy as np
from PIL import Image, ImageFilter
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ED = os.path.join(RAIZ, 'material/producao/personagens/luan')
TX = os.path.join(ED, 'texturas')
R = {'pele': [206, 166, 136], 'testa': [214, 176, 146]}        # "branco queimado" (pele clara bronzeada)

# ------------------------------------------------------------------ medidas (cm; x = esquerda do personagem, y = pra TRÁS, z = cima; 0 = altura dos olhos)
K = .0125                                   # cm → unidades do Blender (personagem de 2,04 u = 1,73 m no motor)
OFS = np.array([0.0, -.005, 1.895])         # onde fica o ponto (0,0,0) da cabeça no mundo
COL = [0, 10, 22, 34, 50, 70, 95, 130, 180]                       # colunas (graus a partir da frente), densas no rosto
XS = [0, .17, .37, .56, .78, .95]                                 # x/a das colunas do rosto
# anel: z, meia-largura a, fundo bb, frente (y das colunas 0..70) ou None (elipse com frente bf), sobrescritas de x
ANEIS = [                                                          # alturas tiradas da foto (proporções relativas olho→queixo = 10,6 cm)
    ('N0', -18.5, 5.6, 5.6, None, 5.0, {}),                                          # pescoço (entra na gola)
    ('N1', -14.0, 5.9, 5.9, None, 5.6, {}),
    ('J1', -12.0, 6.0, 6.0, None, 7.0, {}),                                          # papada                                          # garganta, logo abaixo do queixo
    ('J0', -10.4, 6.1, 6.2, [-8.6, -8.4, -7.6, -6.4, -5.0, -2.8], 0, {}),            # base do queixo / embaixo da mandíbula
    ('C1', -9.0, 6.6, 6.6, [-9.6, -9.4, -8.6, -7.4, -5.8, -3.0], 0, {22: 2.2, 34: 3.5, 50: 4.9}),   # queixo
    ('M1', -7.4, 7.2, 7.4, [-9.7, -9.5, -8.8, -7.8, -6.3, -3.2], 0, {22: 2.5, 34: 3.9, 50: 5.4}),   # lábio de baixo / ângulo da mandíbula
    ('M0', -6.45, 7.5, 8.0, [-9.3, -9.2, -8.9, -8.0, -6.5, -3.4], 0, {22: 2.6, 50: 5.6}),  # linha da boca (cantos em ±2,6)
    ('M2', -5.3, 7.6, 8.7, [-9.9, -9.7, -9.0, -8.1, -6.6, -3.5], 0, {22: 2.6}),   # lábio de cima
    ('S', -4.1, 7.6, 9.3, [-9.7, -10.0, -9.1, -8.2, -6.7, -3.6], 0, {10: 1.85}),     # base do nariz (asas)
    ('T', -3.1, 7.6, 9.7, [-11.3, -10.0, -9.0, -8.4, -6.8, -3.7], 0, {10: 1.6}),      # ponta do nariz
    ('E', -1.5, 7.55, 10.0, [-10.0, -9.1, -8.5, -8.4, -7.0, -3.8], 0, {10: 1.1, 22: 3.0}),   # meio do nariz, maçã do rosto
    ('B', 0.0, 7.2, 10.3, [-9.6, -8.9, -7.95, -7.6, -6.7, -3.7], 0, {10: 1.05, 22: 3.1, 34: 4.5}),   # olhos (órbita), ponte do nariz
    ('G', 2.4, 7.3, 10.4, [-9.1, -9.0, -8.9, -8.2, -6.8, -3.7], 0, {22: 3.05}),     # sobrancelha (arcada)
    ('F', 5.0, 7.2, 10.2, [-8.6, -8.5, -8.2, -7.6, -6.3, -3.5], 0, {}),             # testa
    ('H', 7.8, 6.7, 9.3, [-7.3, -7.2, -6.9, -6.4, -5.4, -3.0], 0, {}),              # alto da testa
    ('K', 10.2, 4.9, 6.8, [-4.6, -4.5, -4.3, -4.0, -3.4, -1.8], 0, {}),             # topo
]
TOPO = np.array([0, 1.2, 11.6])
ANG = [-c for c in COL[::-1][:-1]] + COL                        # -180..180 (17 colunas; a primeira e a última são o mesmo ponto)

def ponto(anel, th):
    nome, z, a, bb, fy, bf, xo = anel
    s = 1 if th >= 0 else -1; t = abs(th); r = math.radians(t)
    if t <= 70 and fy is not None:
        i = COL.index(t); x = xo.get(t, XS[i] * a); y = fy[i]
    elif t <= 90: x, y = a * math.sin(r), -(bf if bf else -fy[-1] / math.cos(math.radians(70))) * math.cos(r)
    else: x, y = a * math.sin(r), -bb * math.cos(r)
    return np.array([s * x, y, z])

def u_de(th):                                                   # UV: o rosto (±55°) ocupa 72 % da largura da textura
    s = 1 if th >= 0 else -1; t = abs(th)
    return .5 + s * (.36 * t / 55 if t <= 55 else .36 + .14 * (t - 55) / 125)
def v_de(z): return float(np.interp(z, [-18.5, -11, 6, 11.6], [.02, .12, .74, .88]))   # rosto (queixo→testa) = 62 % da altura; orelhas em v > .9

# ------------------------------------------------------------------ malha da cabeça
V, F, UV, MAT = [], [], [], []                                    # vértices (cm), faces (índices), uv por canto, material (0 cabeça, 1 orelha)
grade = []
for an in ANEIS:
    linha = []
    for j, th in enumerate(ANG):
        if j == len(ANG) - 1: linha.append(linha[0]); continue      # 180° = -180°: mesmo vértice, UV diferente
        V.append(ponto(an, th)); linha.append(len(V) - 1)
    grade.append(linha)
V.append(TOPO); itopo = len(V) - 1
for i in range(len(ANEIS) - 1):
    for j in range(len(ANG) - 1):
        a, b, c, d = grade[i][j], grade[i][j + 1], grade[i + 1][j + 1], grade[i + 1][j]
        F.append([a, b, c, d]); MAT.append(0)
        z0, z1 = ANEIS[i][1], ANEIS[i + 1][1]
        UV.append([(u_de(ANG[j]), v_de(z0)), (u_de(ANG[j + 1]), v_de(z0)), (u_de(ANG[j + 1]), v_de(z1)), (u_de(ANG[j]), v_de(z1))])
for j in range(len(ANG) - 1):
    a, b = grade[-1][j], grade[-1][j + 1]; F.append([a, b, itopo]); MAT.append(0)
    zt = ANEIS[-1][1]; UV.append([(u_de(ANG[j]), v_de(zt)), (u_de(ANG[j + 1]), v_de(zt)), ((u_de(ANG[j]) + u_de(ANG[j + 1])) / 2, v_de(11.6))])
NCAB = len(F)

# orelhas: concha de 8 lados presa na frente, abertas ~35° (orelhas de abano, como nas fotos), com o verso
OREL = [(0, -2.4), (.9, -3.0), (1.8, -2.5), (2.4, -1.0), (2.6, .7), (2.2, 1.9), (1.2, 2.5), (.2, 1.9)]
def orelha(s):
    base = len(V); ab = math.radians(35)
    def P(u, w, fora=0.0): return np.array([s * (7.15 + 1.15 * u * math.sin(ab) + fora), .2 + 1.15 * u * math.cos(ab), -.75 + 1.2 * w])
    pts = [P(u, w) for u, w in OREL]; ctr = P(1.1, -.1, -.35)               # centro afundado (concha)
    for p in pts: V.append(p)
    V.append(ctr); ic = len(V) - 1
    for p in pts: V.append(p + np.array([s * -.3, .05, 0]))                  # verso
    iv = len(V) - len(pts)
    n = len(pts)
    def uvo(u, w, verso): return (.03 + .1 * (u / 2.8) + (.13 if verso else 0), .905 + .09 * (w + 3.1) / 5.7)
    for k in range(n):
        k2 = (k + 1) % n
        f = [base + k, base + k2, ic] if s > 0 else [base + k2, base + k, ic]
        F.append(f); MAT.append(1); UV.append([uvo(*OREL[k], 0), uvo(*OREL[k2], 0), uvo(1.1, -.1, 0)] if s > 0 else [uvo(*OREL[k2], 0), uvo(*OREL[k], 0), uvo(1.1, -.1, 0)])
        g = [base + k2, base + k, iv + k, iv + k2] if s > 0 else [base + k, base + k2, iv + k2, iv + k]   # borda (espessura)
        F.append(g); MAT.append(1); UV.append([uvo(1.1, -.1, 1)] * 4)
    f = list(range(iv, iv + n)); ordem = list(range(n))[::-1] if s > 0 else list(range(n))
    F.append([iv + k for k in ordem]); MAT.append(1); UV.append([uvo(*OREL[k], 1) for k in ordem])
orelha(1); orelha(-1)
NOR = len(F) - NCAB

# ------------------------------------------------------------------ cabelo: casca com volume, franja em mechas, rente nos lados, nuca baixa
def sup(th, z):                                                    # ponto da superfície da cabeça na coluna th, altura z (interpola anéis)
    zs = [a[1] for a in ANEIS]
    if z >= zs[-1]:
        t = (z - zs[-1]) / (TOPO[2] - zs[-1]); return ponto(ANEIS[-1], th) * (1 - t) + TOPO * t
    i = max(k for k in range(len(zs)) if zs[k] <= z); t = (z - zs[i]) / (zs[i + 1] - zs[i])
    return ponto(ANEIS[i], th) * (1 - t) + ponto(ANEIS[i + 1], th) * t
LINHA = {0: 5.6, 10: 5.8, 22: 5.4, 34: 4.4, 50: 3.4, 70: 2.6, 95: 2.4, 130: 1.0, 180: -1.5}   # lados e nuca: degradê PINTADO abaixo da casca
FRANJA = {0: -1.1, 10: -.1, 22: -1.0, 34: -.3, 50: -.6, 70: -.2}           # pontas da franja (mechas desiguais)
SS = [0, .16, .36, .6, .8, .94]
PICO = {0: .9, 22: 1.1, 34: .4, 50: .8, 95: .5, 130: .7}           # pontas soltas no alto (silhueta bagunçada como nas fotos)
HV0 = len(V); hg = []
CEN = np.array([0, .6, 0])
for s_ in SS + ['dentro']:
    linha = []
    for j, th in enumerate(ANG):
        if j == len(ANG) - 1: linha.append(linha[0]); continue
        t = abs(th); zl = LINHA[t]
        if s_ == 'dentro':
            p = sup(th, zl + .6); n = p - np.array([0, CEN[1], min(p[2], 2)]); n /= np.linalg.norm(n); V.append(p + n * .08); linha.append(len(V) - 1); continue
        z = zl + (11.6 - zl) * s_
        if s_ == 0: z += FRANJA.get(t, 0)
        p = sup(th, min(z, 11.3)); n = p - np.array([0, CEN[1], min(p[2], 2)]); n /= np.linalg.norm(n)
        frente = max(0, 1 - t / 45)
        lado = math.exp(-((t - 75) / 35) ** 2) * math.sin(math.pi * min(1, s_ / .7))          # volume nas laterais do alto (cabelo cheio, como nas fotos)
        esp = .9 + 1.4 * lado + 1.0 * frente * (1 - s_) + 2.3 * s_ ** .9 * (.75 + .25 * frente) + 1.1 * frente * math.sin(math.pi * min(1, s_ / .8)) + (PICO.get(t, 0) * (1 if th >= 0 else .8) if s_ in (.36, .6) and (j + int(s_ * 10)) % 2 == 0 else 0)   # topete na frente
        q = p + n * esp
        if s_ in (0, .16) and t <= 50: q += np.array([-.5, -.6 if s_ == 0 else -.35, 0]) * (1 - t / 70)   # franja caindo pra frente, penteada pro lado direito da pessoa
        V.append(q); linha.append(len(V) - 1)
    hg.append(linha)
V.append(TOPO + np.array([0, -.4, 2.9])); htopo = len(V) - 1
HF0 = len(F)
def uvh(j, s): return (j / (len(ANG) - 1), .04 + .92 * s)
for i in range(len(SS) - 1):
    for j in range(len(ANG) - 1):
        F.append([hg[i][j], hg[i][j + 1], hg[i + 1][j + 1], hg[i + 1][j]]); MAT.append(2)
        UV.append([uvh(j, SS[i]), uvh(j + 1, SS[i]), uvh(j + 1, SS[i + 1]), uvh(j, SS[i + 1])])
for j in range(len(ANG) - 1):
    F.append([hg[len(SS) - 1][j], hg[len(SS) - 1][j + 1], htopo]); MAT.append(2)
    UV.append([uvh(j, SS[-1]), uvh(j + 1, SS[-1]), ((j + .5) / (len(ANG) - 1), .99)])
    F.append([hg[-1][j], hg[-1][j + 1], hg[0][j + 1], hg[0][j]]); MAT.append(2)          # borda de baixo (fecha a casca por dentro)
    UV.append([uvh(j, 0), uvh(j + 1, 0), uvh(j + 1, .03), uvh(j, .03)])

# MECHAS: fitas com crista que acompanham a casca e terminam em ponta — franja caindo pra frente (penteada pro lado
# direito da pessoa) e tufos soltos no alto, como nas fotos. Cada mecha: seção triangular (borda esq., crista, borda dir.)
rngm = np.random.default_rng(11)
NC = len(ANG) - 1
def _v(i, j): return np.array(V[hg[i][j % NC]], float)
def _n(p): n = p - np.array([0, .6, min(p[2], 2)]); return n / np.linalg.norm(n)
MECHAS0 = len(F)
def mecha(caminho, ponta, larg=.9, crista=.55, lift=.12, u0=0.):
    idx = []
    for k, c in enumerate(caminho):
        prox = caminho[min(k + 1, len(caminho) - 1)] if k < len(caminho) - 1 else ponta
        d = prox - c; d /= np.linalg.norm(d) + 1e-9; n = _n(c); lado = np.cross(d, n); lado /= np.linalg.norm(lado) + 1e-9
        w = larg * (1 - .25 * k / len(caminho))
        V.extend([c + n * lift + lado * w / 2, c + n * (lift + crista), c + n * lift - lado * w / 2]); idx.append(len(V) - 3)
    V.append(ponta); it = len(V) - 1
    for k in range(len(idx) - 1):
        a, b = idx[k], idx[k + 1]; v0, v1 = .9 - .8 * k / len(idx), .9 - .8 * (k + 1) / len(idx)
        for f, uv in (([a, b, b + 1, a + 1], [(u0, v0), (u0, v1), (u0 + .03, v1), (u0 + .03, v0)]),
                      ([a + 1, b + 1, b + 2, a + 2], [(u0 + .03, v0), (u0 + .03, v1), (u0 + .06, v1), (u0 + .06, v0)])):
            F.append(f); MAT.append(2); UV.append(uv)
    a = idx[-1]
    for f in ([a, it, a + 1], [a + 1, it, a + 2]): F.append(f); MAT.append(2); UV.append([(u0, .1), (u0 + .03, .02), (u0 + .06, .1)])
ifr = ANG.index(0)
for j in range(NC):                                                # CACHOS: tufos curtos e enrolados em volta da cabeça toda (2 fileiras + franja)
    for i_, (alt, larg) in enumerate(((0, 1.4), (1, 1.6), (2, 1.7), (3, 1.8), (4, 1.8))):
        c0 = _v(alt + 1, j); c1 = _v(alt, j); n_ = _n(c0)
        giro = np.array([math.cos(j * 2.1 + i_ * 1.3), math.sin(j * 1.7 + i_ * 2.1), 0]) * 1.1
        ponta = c1 + n_ * (1.6 + .7 * ((j + i_) % 3)) + giro - np.array([0, 0, .4 if alt else .8])   # cacho: sai pra fora e enrola
        mecha([c0, c1], ponta, larg=larg, crista=.55, lift=.08, u0=((j * 3 + i_) * .07) % .9)
for i in range(MECHAS0, len(F)):                                       # frente das fitas sempre pra fora
    p_ = np.array([V[v] for v in F[i]]); nn = np.zeros(3)
    for k in range(len(p_)): nn += np.cross(p_[k], p_[(k + 1) % len(p_)])
    if np.dot(nn, p_.mean(0) - np.array([0, .6, 1.0])) < 0: F[i] = F[i][::-1]; UV[i] = UV[i][::-1]
# ------------------------------------------------------------------ ÓCULOS e MÁSCARA DE GÁS (geometria apoiada no rosto)
def surf(th, z):                                                   # ponto da pele em qualquer ângulo (interpola entre as colunas)
    t = min(abs(th), 180); s_ = 1 if th >= 0 else -1
    k = max(i for i in range(len(COL)) if COL[i] <= t); k2 = min(k + 1, len(COL) - 1)
    w = 0 if k2 == k else (t - COL[k]) / (COL[k2] - COL[k])
    return sup(s_ * COL[k], z) * (1 - w) + sup(s_ * COL[k2], z) * w
def radial(p, desce=0.0):
    n = np.array([p[0], p[1] - .6, 0.0]); n /= np.linalg.norm(n) + 1e-9; n[2] = -desce; return n / np.linalg.norm(n)
OX0 = len(F); DESEJO = {}
def novo(p): V.append(np.array(p, float)); return len(V) - 1
def face(vs, mat, uvs=None, quer=None):
    F.append(list(vs)); MAT.append(mat); UV.append(uvs or [(.5, .5)] * len(vs))
    if quer is not None: DESEJO[len(F) - 1] = np.array(quer, float)
# ÓCULOS: aros retangulares grossos (frente + espessura), lentes, ponte e hastes até as orelhas
for sx in (1, -1):
    cx, cz, y0, hw, hh = sx * 3.3, .3, -9.45, 2.25, 1.45
    ret = [(-1, -1), (-.35, -1.12), (.35, -1.12), (1, -1), (1.06, 0), (1, 1), (0, 1.05), (-1, 1), (-1.06, 0)]
    fora = [novo((cx + a * hw, y0, cz + b * hh)) for a, b in ret]
    dentro = [novo((cx + a * hw * .8, y0, cz + b * hh * .74)) for a, b in ret]
    tras = [novo((cx + a * hw, y0 + .55, cz + b * hh)) for a, b in ret]
    n = len(ret)
    for k in range(n):
        k2 = (k + 1) % n
        face((fora[k], fora[k2], dentro[k2], dentro[k]), 3, quer=(0, -1, 0))
        face((tras[k], tras[k2], fora[k2], fora[k]), 3, quer=(V[fora[k]][0] - cx, 0, V[fora[k]][2] - cz))
    lente = [novo((cx + a * hw * .8, y0 + .2, cz + b * hh * .74)) for a, b in ret]
    face(lente, 4, [(.5 + .5 * a, .5 + .5 * b) for a, b in ret], quer=(0, -1, 0))
    p0, p1 = np.array([cx + sx * hw, y0 + .3, cz + .6]), np.array([sx * 7.25, 1.2, .9])     # haste
    q = [novo(p0), novo(p1), novo(p1 + (0, 0, .45)), novo(p0 + (0, 0, .45))]
    face(q, 3, quer=(sx, 0, 0)); face(q[::-1], 3, quer=(-sx, 0, 0))
b_ = [novo((-1.05, -9.55, .45)), novo((1.05, -9.55, .45)), novo((1.05, -9.55, .85)), novo((-1.05, -9.55, .85))]   # ponte
face(b_, 3, quer=(0, -1, 0))
# MÁSCARA: casca sobre nariz/boca/queixo, com bojo na frente da boca e borda fechada até a pele
THS = list(np.linspace(-64, 64, 11)); NR = 6
def ztop(th): return -1.2 - 2.2 * (abs(th) / 64) ** 1.5
ZB = -10.8
grade_m = []; pele_m = []
for r in range(NR):
    lin, linp = [], []
    for th_ in THS:
        z = ztop(th_) + (ZB - ztop(th_)) * r / (NR - 1)
        p = surf(th_, z); n = radial(p, desce=.6 if r == NR - 1 else (.25 if r == NR - 2 else 0))
        bojo = 1.3 * math.exp(-((th_ / 30) ** 2) - ((z + 6.2) / 2.6) ** 2)
        lin.append(novo(p + n * (.75 + bojo))); linp.append(novo(p + n * .06))
    grade_m.append(lin); pele_m.append(linp)
for r in range(NR - 1):
    for c in range(len(THS) - 1):
        a, b, c2, d = grade_m[r][c], grade_m[r][c + 1], grade_m[r + 1][c + 1], grade_m[r + 1][c]
        face((a, b, c2, d), 5, [(c / 10, 1 - r / 5), ((c + 1) / 10, 1 - r / 5), ((c + 1) / 10, 1 - (r + 1) / 5), (c / 10, 1 - (r + 1) / 5)],
             quer=radial(V[a]) * 1.0 + np.array([0, 0, -.3 if r >= NR - 2 else 0]))
borda_m = [(0, c) for c in range(len(THS))] + [(r, len(THS) - 1) for r in range(1, NR)] + [(NR - 1, c) for c in range(len(THS) - 2, -1, -1)] + [(r, 0) for r in range(NR - 2, 0, -1)]
for k in range(len(borda_m)):                                      # borda: fecha o vão entre a máscara e a pele
    (r0, c0), (r1, c1) = borda_m[k], borda_m[(k + 1) % len(borda_m)]
    if (r0, c0) == (NR - 1, 0) and (r1, c1) == (NR - 2, 0): pass
    face((grade_m[r0][c0], grade_m[r1][c1], pele_m[r1][c1], pele_m[r0][c0]), 5)
def cilindro_cm(base, eixo, r, comp, n, mat_lado, mat_tampa):
    e = np.array(eixo, float); e /= np.linalg.norm(e)
    a_ = np.cross(e, [0, 0, 1.0]); a_ /= np.linalg.norm(a_); b_ = np.cross(e, a_)
    an0 = [novo(base + (a_ * math.cos(2 * math.pi * k / n) + b_ * math.sin(2 * math.pi * k / n)) * r) for k in range(n)]
    an1 = [novo(base + e * comp + (a_ * math.cos(2 * math.pi * k / n) + b_ * math.sin(2 * math.pi * k / n)) * r) for k in range(n)]
    for k in range(n):
        k2 = (k + 1) % n; mid = (a_ * math.cos(2 * math.pi * (k + .5) / n) + b_ * math.sin(2 * math.pi * (k + .5) / n))
        face((an0[k], an0[k2], an1[k2], an1[k]), mat_lado, quer=mid)
    c_ = novo(base + e * (comp + .05))
    for k in range(n):
        k2 = (k + 1) % n; ang, ang2 = 2 * math.pi * k / n, 2 * math.pi * k2 / n
        face((an1[k], an1[k2], c_), mat_tampa, [(.5 + .5 * math.cos(ang), .5 + .5 * math.sin(ang)), (.5 + .5 * math.cos(ang2), .5 + .5 * math.sin(ang2)), (.5, .5)], quer=e)
for sx in (1, -1):                                                 # FILTROS laterais (tampa com aro amarelo aceso)
    p = surf(sx * 46, -6.6); n = radial(p); base = p + n * 1.5
    cilindro_cm(base, n + np.array([0, -.55, -.15]), 1.55, 1.7, 12, 7, 6)
p = surf(0, -6.4); cilindro_cm(p + radial(p) * 2.0, radial(p) + np.array([0, 0, -.2]), .95, .8, 10, 7, 5)   # válvula da frente
for sx in (1, -1):                                                 # TIRAS da máscara em volta da cabeça
    tira = []
    for th_ in np.linspace(62, 178, 7):
        for z in (-2.6, -1.7):
            p = surf(sx * th_, z); tira.append(novo(p + radial(p) * .3))
    for k in range(6):
        a, b, c2, d = tira[2 * k], tira[2 * k + 2], tira[2 * k + 3], tira[2 * k + 1]
        face((a, b, c2, d), 5, quer=radial(V[a]))
for i, quer in DESEJO.items():                                     # cada peça com a frente pro lado certo
    p_ = np.array([V[v] for v in F[i]]); nn = np.zeros(3)
    for k in range(len(p_)): nn += np.cross(p_[k], p_[(k + 1) % len(p_)])
    if np.dot(nn, quer) < 0: F[i] = F[i][::-1]; UV[i] = UV[i][::-1]
for i in range(OX0, len(F)):                                       # borda da máscara: pra fora
    if i in DESEJO: continue
    p_ = np.array([V[v] for v in F[i]]); nn = np.zeros(3)
    for k in range(len(p_)): nn += np.cross(p_[k], p_[(k + 1) % len(p_)])
    c = p_.mean(0)
    if np.dot(nn, c - np.array([0, .6, c[2]])) < 0: F[i] = F[i][::-1]; UV[i] = UV[i][::-1]
V = np.array(V)

# ------------------------------------------------------------------ normais e orientação (todas as faces pra FORA)
def nface(f):
    p = V[f]; n = np.zeros(3)
    for k in range(len(f)): n += np.cross(p[k], p[(k + 1) % len(f)])
    return n / (np.linalg.norm(n) + 1e-12)
def centro(f): return V[f].mean(0)
# (todas as faces já são montadas com a frente pra fora: colunas crescem da direita pra esquerda do personagem, anéis de baixo pra cima)
dentro = [i for i, f in enumerate(F) if MAT[i] == 0 and np.dot(nface(f), centro(f) - np.array([0, .6, np.clip(centro(f)[2], -14, 3)])) < 0]
print('faces da cabeça viradas pra dentro:', len(dentro))
# normais suaves por vértice (só pra pintar o sombreamento)
VN = np.zeros_like(V)
for i, f in enumerate(F):
    if MAT[i] == 0:
        for v in f: VN[v] += nface(f)
VN /= np.linalg.norm(VN, axis=1, keepdims=True) + 1e-12

# ------------------------------------------------------------------ TEXTURA DO ROSTO (pintada em 1024 e reduzida pra 256)
TR = 1024
pos = np.zeros((TR, TR, 3)); nor = np.zeros((TR, TR, 3)); tem = np.zeros((TR, TR), bool); ore = np.zeros((TR, TR), bool)
def raster(i):
    f = F[i]; uvs = UV[i]
    for k in range(1, len(f) - 1):
        tri = [0, k, k + 1]; P = np.array([uvs[t] for t in tri]) * TR; P[:, 1] = TR - P[:, 1]
        x0, y0 = np.floor(P.min(0)).astype(int); x1, y1 = np.ceil(P.max(0)).astype(int)
        xs, ys = np.meshgrid(np.arange(max(x0, 0), min(x1, TR - 1) + 1) + .5, np.arange(max(y0, 0), min(y1, TR - 1) + 1) + .5)
        d = (P[1, 1] - P[2, 1]) * (P[0, 0] - P[2, 0]) + (P[2, 0] - P[1, 0]) * (P[0, 1] - P[2, 1])
        if abs(d) < 1e-9: continue
        l1 = ((P[1, 1] - P[2, 1]) * (xs - P[2, 0]) + (P[2, 0] - P[1, 0]) * (ys - P[2, 1])) / d
        l2 = ((P[2, 1] - P[0, 1]) * (xs - P[2, 0]) + (P[0, 0] - P[2, 0]) * (ys - P[2, 1])) / d
        l3 = 1 - l1 - l2; m = (l1 >= -.02) & (l2 >= -.02) & (l3 >= -.02)
        if not m.any(): continue
        vi = [f[t] for t in tri]; L3 = np.stack([l1, l2, l3], -1)[m]
        X = (xs[m] - .5).astype(int); Y = (ys[m] - .5).astype(int)
        pos[Y, X] = L3 @ V[vi]; nn = L3 @ (VN[vi] if MAT[i] == 0 else np.tile(nface(f), (3, 1))); nor[Y, X] = nn / np.linalg.norm(nn, axis=1, keepdims=True)
        tem[Y, X] = True
        if MAT[i] == 1: ore[Y, X] = True
for i in range(len(F)):
    if MAT[i] in (0, 1): raster(i)

def ss(e0, e1, x): t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)
def bolha(x, z, cx, cz, rx, rz): return np.exp(-(((x - cx) / rx) ** 2 + ((z - cz) / rz) ** 2))
x, y, z = pos[..., 0], pos[..., 1], pos[..., 2]; nx, ny, nz = nor[..., 0], nor[..., 1], nor[..., 2]
th = np.degrees(np.arctan2(x, -y))
fr = ss(-1.0, -4.0, y)
zt = np.interp(np.abs(th), [0, 22, 34, 50, 70], [5.1, 4.7, 3.5, 2.4, 2.0])     # onde o cabelo começa (o rosto da foto para antes)                                                   # só a metade da FRENTE recebe os realces do rosto
PELE = np.array(R['pele'], float) * 1.07; TESTA = np.array(R['testa'], float) * 1.05   # um pouco mais claro: a luz do jogo escurece
# pele base pintada (contínua em volta da cabeça): testa mais clara, bochechas/nariz/orelhas mais rosados, pescoço mais escuro
base = PELE[None, None] * np.ones((TR, TR, 1))
base = base * (1 - ss(1, 5, z)[..., None] * .6) + TESTA * (ss(1, 5, z)[..., None] * .6)
rosa = np.array([1.03, .985, .975])
br = (fr * (bolha(np.abs(x), z, 4.6, -3.6, 2.0, 1.8) + .8 * bolha(x, z, 0, -3.0, 1.4, 1.2)))[..., None]
base = base * (1 + (rosa - 1) * np.clip(br, 0, 1))
base = base * (1 - .14 * ss(-10.5, -14.5, z))[..., None] * np.array([1, .98, .97]) ** ss(-10.5, -14.5, z)[..., None]
base[ore] = PELE * np.array([1.0, .95, .93]) * .95
# sombreamento assado (luz de cima/frente), cavidades
Ld = np.array([.25, -.75, .6]); Ld /= np.linalg.norm(Ld)
lam = np.clip(nx * Ld[0] + ny * Ld[1] + nz * Ld[2], 0, 1)
sh = .85 + .17 * lam
sh *= 1 - .22 * ss(-.35, -.8, nz) * ss(-9.6, -11.5, z)                 # embaixo do queixo
sh *= 1 - .16 * fr * bolha(np.abs(x), z, .85, -4.05, .6, .35)                 # narinas
sh *= 1 - .12 * fr * bolha(np.abs(x), z, 1.6, -2.4, .7, 1.4)                # lados do nariz
sh *= 1 - .07 * fr * bolha(np.abs(x), z, 3.1, 1.2, 1.9, .9)                  # sob a arcada da sobrancelha
sh *= 1 + .06 * fr * bolha(x, z, 0, -8.4, 2.4, .9)                          # sob o lábio de baixo
sh *= 1 - .10 * ss(70, 115, np.abs(th)) * ss(-5, -13, z)
sh *= 1 + .40 * fr * bolha(x, z, 0, -3.7, 1.8, .6)                    # base do nariz (virada pra baixo) um pouco mais clara
sh[ore] = .9
labio = (fr * bolha(x, z, 0, -6.6, 2.4, .9))[..., None]
base = base * (1 - .12 * labio) + np.array([170, 112, 100]) * (.12 * labio)   # boca levemente rosada
sh *= 1 - .04 * fr * bolha(x, z, 0, -6.9, 2.3, .45)                    # lábio de baixo sem faixa clara
cor = base * sh[..., None]
# OLHOS e SOBRANCELHAS pintados (sem foto): olho amendoado (branco, íris castanho-escura, pálpebra de cima escura), sobrancelha grossa
for sx in (1, -1):
    ex, ez = sx * 3.15, .1
    du, dv = (x - ex) / 1.35, (z - ez) / .55
    amend = (du ** 2 + dv ** 2 * np.clip(1 + .25 * du * sx, .6, 1.4) < 1) & (np.abs(du) < 1.1) & (np.abs(dv) < 1.2) & (fr > .5)
    cor[amend] = np.array([228, 220, 208])
    iris = ((x - ex) ** 2 + (z - ez - .02) ** 2 < .42 ** 2) & amend
    cor[iris] = np.array([72, 48, 34]); cor[iris & ((x - ex) ** 2 + (z - ez) ** 2 < .2 ** 2)] = np.array([22, 16, 12])
    palp = (np.abs(dv - np.sqrt(np.clip(1 - du ** 2, 0, 1))) < .28) & (np.abs(du) < 1.05) & (fr > .5)
    cor[palp] = np.array([48, 34, 28])
    sob = (np.abs(z - (2.35 + .3 * (1 - ((x - ex - sx * .3) / 2.2) ** 2))) < .32) & (np.abs(x - ex - sx * .3) < 2.0) & (fr > .5)
    cor[sob] = cor[sob] * .25 + np.array([40, 30, 24]) * .75
# DEGRADÊ dos lados/nuca pintado na pele (cabelo curtinho), abaixo da casca do cabelo
HC_ = np.array(HCOR) if 'HCOR' in dir() else None
zf = np.interp(np.abs(th), [0, 45, 62, 75, 88, 97, 108, 140, 180], [9, 9, 2.2, -.2, 1.4, 1.2, -1.0, -3.0, -4.0])   # costeleta, contorno atrás da orelha, nuca   # costeleta na frente da orelha, nuca baixa
cab = ss(zf - .4, zf + 3.6, z) ** .8 * (~ore) * .85                   # degradê: escuro em cima, clareando até a pele
cor = cor * (1 - .86 * cab[..., None]) + np.array([46, 38, 33]) * (.86 * cab[..., None]) * (.85 + .3 * np.random.default_rng(3).random((TR, TR, 1)))
cor = np.clip(cor, 0, 255) * tem[..., None]
# reduz pra 256 (média) e preenche fora das ilhas
img = Image.fromarray(cor.astype(np.uint8)); msk = Image.fromarray((tem * 255).astype(np.uint8))
OUT = 256
pre = np.asarray(img.resize((OUT, OUT), Image.BOX)).astype(float); m128 = np.asarray(msk.resize((OUT, OUT), Image.BOX)).astype(float) / 255
pre = np.where(m128[..., None] > .05, pre / np.maximum(m128[..., None], .05) * (m128[..., None] > .05), 0)
ok = m128 > .05
for _ in range(24):                                                      # dilatação: a borda das ilhas não puxa preto
    viz = np.zeros_like(pre); cnt = np.zeros(ok.shape)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        sh_ = np.roll(np.roll(pre * ok[..., None], dy, 0), dx, 1); so = np.roll(np.roll(ok, dy, 0), dx, 1)
        viz += sh_; cnt += so
    novo = (~ok) & (cnt > 0); pre[novo] = viz[novo] / cnt[novo][:, None]; ok = ok | novo
BAY = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 - .47
q = np.clip(np.floor(pre / 8 + .5 + np.tile(BAY, (OUT // 4, OUT // 4))[..., None]) * 8, 0, 255).astype(np.uint8)   # 15 bits com pontilhado (PS1)
Image.fromarray(q).save(os.path.join(TX, 'rosto_v2.png'))

# ------------------------------------------------------------------ textura do cabelo (fios na direção do penteado, castanho-escuro da foto)
hc = np.array([44.0, 33, 26])                                            # castanho bem escuro
rng = np.random.default_rng(7); H = np.zeros((64, 64, 3))
fio = rng.random(64)
for xx in range(64):
    for yy in range(64):
        k = (xx + int(3 * math.sin(yy * .25 + xx * .3))) % 64
        v = .75 + 1.1 * fio[k] ** 3 + .15 * rng.random() + .35 * (yy < 14) * fio[(k + 5) % 64]   # fios claros e pontas mais claras
        if yy > 56: v *= .8                                               # alto da cabeça (redemoinho) um pouco mais escuro
        H[63 - yy, xx] = hc * v
Image.fromarray(np.clip(np.round(H / 8) * 8, 0, 255).astype(np.uint8)).save(os.path.join(TX, 'cabelo_v2.png'))

# ------------------------------------------------------------------ pesos e saída
pesos = []
for i, p in enumerate(V):
    if i >= HV0: pesos.append({'spine.005': 1.0}); continue
    if p[2] <= -16: pesos.append({'spine.004': 1.0})
    elif p[2] <= -13.5: pesos.append({'spine.004': .5, 'spine.005': .5})
    else: pesos.append({'spine.005': 1.0})
mundo = V * K + OFS
saida = {'v': mundo.round(5).tolist(), 'f': F, 'uv': UV, 'mat': MAT, 'peso': pesos,
         'pecas': {'cabeca': [0, NCAB + NOR], 'cabelo': [HF0, OX0], 'acessorios': [OX0, len(F)]}}
json.dump(saida, open(os.path.join(TX, 'cabeca.json'), 'w'))
tri = lambda a, b: sum(len(F[i]) - 2 for i in range(a, b))
print('cabeça+pescoço', tri(0, NCAB), 'orelhas', tri(NCAB, NCAB + NOR), 'cabelo', tri(HF0, OX0), 'óculos+máscara', tri(OX0, len(F)), 'total', tri(0, len(F)))
print('tom do cabelo', hc.round())
