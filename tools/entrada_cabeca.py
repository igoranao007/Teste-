# CABEÇA DA ENTRADA v2 — geometria facial própria + textura única REPINTADA (estilo NPC de terror PS1).
# Roda no python do sistema (numpy + PIL). Gera:
#   material/producao/personagens/entrada/texturas/cabeca.json      malha (cabeça+pescoço, cabelo, orelhas) em coordenadas do mundo
#   material/producao/personagens/entrada/texturas/rosto_v2.png     textura única da cabeça (256 px = página de textura do PS1), UV contínuo
#   material/producao/personagens/entrada/texturas/cabelo_v2.png    textura do cabelo (64 px)
# A cabeça é um "loft" de anéis horizontais com colunas mais densas na frente (nariz, olhos, boca, maçãs, mandíbula modelados).
# A foto NÃO é colada: dela saem só o tom da pele e o DETALHE (olhos, sobrancelhas, boca, sombras) por cima de uma pele pintada
# contínua em volta da cabeça inteira, com sombreamento assado — por isso não há emenda entre "foto" e "pele".
import json, math, os, sys
import numpy as np
from PIL import Image, ImageFilter
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ED = os.path.join(RAIZ, 'material/producao/personagens/entrada')
TX = os.path.join(ED, 'texturas')
R = json.load(open(os.path.join(TX, 'rosto.json')))

# ------------------------------------------------------------------ medidas (cm; x = esquerda do personagem, y = pra TRÁS, z = cima; 0 = altura dos olhos)
K = .0125                                   # cm → unidades do Blender (personagem de 2,04 u = 1,73 m no motor)
OFS = np.array([0.0, -.005, 1.895])         # onde fica o ponto (0,0,0) da cabeça no mundo
COL = [0, 10, 22, 34, 50, 70, 95, 130, 180]                       # colunas (graus a partir da frente), densas no rosto
XS = [0, .17, .37, .56, .78, .95]                                 # x/a das colunas do rosto
# anel: z, meia-largura a, fundo bb, frente (y das colunas 0..70) ou None (elipse com frente bf), sobrescritas de x
ANEIS = [                                                          # alturas tiradas da foto (proporções relativas olho→queixo = 10,6 cm)
    ('N0', -18.5, 4.3, 4.6, None, 4.0, {}),                                          # pescoço (entra na gola)
    ('N1', -14.0, 4.4, 4.9, None, 4.3, {}),
    ('J1', -12.0, 4.3, 5.0, None, 4.9, {}),                                          # garganta, logo abaixo do queixo
    ('J0', -10.4, 4.4, 5.4, [-8.2, -7.8, -6.6, -5.1, -3.7, -2.2], 0, {}),            # base do queixo / embaixo da mandíbula
    ('C1', -9.0, 4.4, 6.0, [-9.75, -9.4, -8.1, -6.4, -4.4, -2.2], 0, {22: 1.9, 34: 2.9, 50: 3.8}),   # queixo
    ('M1', -7.4, 5.2, 6.9, [-9.6, -9.4, -8.45, -7.0, -5.1, -2.1], 0, {22: 2.35, 34: 3.5, 50: 4.4}),   # lábio de baixo / ângulo da mandíbula
    ('M0', -6.45, 5.7, 7.6, [-9.15, -9.05, -8.65, -7.3, -5.5, -2.7], 0, {22: 2.6, 50: 4.6}),  # linha da boca (cantos em ±2,6)
    ('M2', -5.3, 6.2, 8.5, [-9.85, -9.65, -8.75, -7.5, -5.8, -3.0], 0, {22: 2.6}),   # lábio de cima
    ('S', -4.1, 6.75, 9.3, [-9.6, -9.9, -8.8, -7.8, -6.2, -3.4], 0, {10: 1.75}),     # base do nariz (asas)
    ('T', -3.1, 6.9, 9.7, [-11.4, -9.9, -8.7, -8.0, -6.4, -3.5], 0, {10: 1.5}),      # ponta do nariz
    ('E', -1.5, 7.05, 10.0, [-10.2, -9.0, -8.3, -8.1, -6.8, -3.7], 0, {10: 1.1, 22: 3.0}),   # meio do nariz, maçã do rosto
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
LINHA = {0: 5.4, 10: 5.6, 22: 5.0, 34: 3.8, 50: 2.6, 70: 2.8, 95: 3.6, 130: 3.2, 180: 2.0}   # lados e nuca: degradê PINTADO abaixo da casca
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
        esp = .3 + 1.2 * lado + 1.0 * frente * (1 - s_) + 2.3 * s_ ** .9 * (.75 + .25 * frente) + 1.1 * frente * math.sin(math.pi * min(1, s_ / .8)) + (PICO.get(t, 0) * (1 if th >= 0 else .8) if s_ in (.36, .6) and (j + int(s_ * 10)) % 2 == 0 else 0)   # topete na frente
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
for n_, dj in enumerate((-3, -2, -1, 0, 1, 2)):                         # FRANJA
    j = ifr + dj; t = abs(ANG[j])
    cam = [_v(3, j), _v(2, j), _v(1, j), _v(0, j)]
    ponta = _v(0, j) + np.array([-.8, -1.0, -.9 - .9 * (n_ % 2)])
    mecha(cam, ponta, larg=1.3, crista=.5, u0=(n_ * .16) % .9)
for n_, (j, ang) in enumerate(((ifr, 0), (ifr + 2, 1), (ifr - 2, -1), (ifr + 4, 2), (ifr - 4, -2), (0, 3), (ifr + 6, 4))):   # tufos no alto
    c0 = _v(5, j); c1 = _v(4, j)
    ponta = c0 + _n(c0) * 1.4 + np.array([.4 * ang, 1.6, .6])
    mecha([c1, c0], ponta, larg=1.6, crista=.7, lift=.05, u0=(n_ * .13) % .9)
for i in range(MECHAS0, len(F)):                                       # frente das fitas sempre pra fora
    p_ = np.array([V[v] for v in F[i]]); nn = np.zeros(3)
    for k in range(len(p_)): nn += np.cross(p_[k], p_[(k + 1) % len(p_)])
    if np.dot(nn, p_.mean(0) - np.array([0, .6, 1.0])) < 0: F[i] = F[i][::-1]; UV[i] = UV[i][::-1]
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
FOTO = Image.open(os.path.join(ED, 'referencia/foto_original.jpg')).convert('RGB')
FS = 4; foto = np.asarray(FOTO.resize((FOTO.width // FS, FOTO.height // FS), Image.LANCZOS)).astype(float)
_pele = np.array(R['pele'], float)
_m = (np.abs(foto - _pele).sum(-1) < 75).astype(float)                       # máscara de PELE na foto (sem parede, cabelo, olho)
def _gb(a): return np.asarray(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(18))).astype(float)
_mb = np.asarray(Image.fromarray((_m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(18))).astype(float)[..., None] / 255
borra = np.stack([_gb(foto[..., k] * _m) for k in range(3)], -1) / np.maximum(_mb, .05)   # média só da pele em volta
borra = np.where(_mb > .05, borra, _pele)
def amostra(img, px, py):                                          # bilinear (px, py em pixels da foto original)
    x = np.clip(px / FS, 0, img.shape[1] - 2); y = np.clip(py / FS, 0, img.shape[0] - 2)
    x0, y0 = x.astype(int), y.astype(int); fx, fy = (x - x0)[..., None], (y - y0)[..., None]
    return (img[y0, x0] * (1 - fx) * (1 - fy) + img[y0, x0 + 1] * fx * (1 - fy) + img[y0 + 1, x0] * (1 - fx) * fy + img[y0 + 1, x0 + 1] * fx * fy)
# pontos de apoio: (x, z) da GEOMETRIA ↔ (px, py) da FOTO — thin-plate spline
(ex1, ey1), (ex2, ey2) = R['olhos']
APOIO = [((-3.15, 0), (900, 1038)), ((3.15, 0), (1385, 1070)),                       # olhos
         ((0, -3.1), (1150, 1285)), ((0, -4.1), (1150, 1345)), ((-1.85, -3.7), (1020, 1320)), ((1.85, -3.7), (1290, 1330)),   # nariz
         ((0, -6.45), (1135, 1515)), ((-2.6, -6.45), (945, 1515)), ((2.6, -6.45), (1310, 1525)),                  # boca
         ((0, -9.2), (1125, 1745)), ((-3.1, 2.4), (890, 870)), ((3.1, 2.4), (1385, 905)), ((0, 5.6), (1150, 660)),  # queixo, sobrancelhas, cabelo
         ((-6.3, -1), (640, 1100)), ((6.3, -1), (1540, 1110)), ((-5.8, -6.45), (680, 1515)), ((5.8, -6.45), (1470, 1525)),
         ((-3.7, -9.0), (820, 1720)), ((3.7, -9.0), (1350, 1730)), ((-5.0, 4.0), (700, 760)), ((5.0, 4.0), (1500, 800))]
A = np.array([a for a, b in APOIO]); B_ = np.array([b for a, b in APOIO], float)
def U(r): return np.where(r > 0, r * r * np.log(r + 1e-12), 0)
n_ = len(A); Kd = U(np.linalg.norm(A[:, None] - A[None], axis=2)); Pm = np.hstack([np.ones((n_, 1)), A])
L = np.zeros((n_ + 3, n_ + 3)); L[:n_, :n_] = Kd; L[:n_, n_:] = Pm; L[n_:, :n_] = Pm.T
W_ = np.linalg.solve(L, np.vstack([B_, np.zeros((3, 2))]))
def tps(xz):
    d = U(np.linalg.norm(xz[:, None] - A[None], axis=2)); return d @ W_[:n_] + np.hstack([np.ones((len(xz), 1)), xz]) @ W_[n_:]

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
# DETALHE da foto (razão foto / foto borrada): olhos, sobrancelhas, boca, marcas — por cima da pintura
xz = np.stack([x, z], -1).reshape(-1, 2); pxy = tps(xz)
ph = amostra(foto, pxy[:, 0], pxy[:, 1]).reshape(TR, TR, 3); pb = amostra(borra, pxy[:, 0], pxy[:, 1]).reshape(TR, TR, 3)
razao = np.clip(ph / (pb + 1), .25, 1.6)
frente = ss(60, 40, np.abs(th)) * ss(-11.2, -10.0, z) * ss(zt + .4, zt - .6, z) * ss(-.1, -.45, ny) * (~ore)
feat = np.clip(.68 + 1.0 * (bolha(np.abs(x), z, 3.15, .1, 2.0, .95) + bolha(np.abs(x), z, 3.1, 2.4, 2.4, .7)      # olhos, sobrancelhas
                             + bolha(x, z, 0, -6.45, 2.9, 1.1)), 0, 1) * (1 - .8 * bolha(x, z, 0, -4.0, 2.0, .7))   # base do nariz: pouca foto (a sombra virava bigode)   # boca, base do nariz
w = (frente * feat)[..., None]
lum = razao.mean(-1, keepdims=True)
det = (razao * .75 + lum * .25)
sobr = (frente * bolha(np.abs(x), z, 3.1, 2.5, 2.3, .6))[..., None]
det = det ** (1 + .35 * sobr)                                            # sobrancelhas grossas e escuras como na foto
olho = (frente * bolha(np.abs(x), z, 3.15, .1, 1.7, .7))[..., None]
det = det ** (1 + .15 * olho)                                             # olhos um pouco mais marcados (leitura a distância)                                         # cor do detalhe um pouco dessaturada (pintura, não foto)
cor = cor * (1 + w * (det - 1))
# DEGRADÊ dos lados/nuca pintado na pele (cabelo curtinho), abaixo da casca do cabelo
HC_ = np.array(HCOR) if 'HCOR' in dir() else None
zf = np.interp(np.abs(th), [0, 45, 62, 75, 88, 97, 108, 140, 180], [9, 9, 1.6, -.6, 1.2, 1.0, -.6, -2.4, -3.2])   # costeleta, contorno atrás da orelha, nuca   # costeleta na frente da orelha, nuca baixa
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
Image.fromarray(cor.astype(np.uint8)).save(os.path.join(ED, 'inspecao/rosto_v2_1024.png')) if os.path.isdir(os.path.join(ED, 'inspecao')) else None

# ------------------------------------------------------------------ textura do cabelo (fios na direção do penteado, castanho-escuro da foto)
hc = np.asarray(FOTO.crop((700, 300, 1600, 600))).reshape(-1, 3).astype(float)
hc = hc[hc.sum(1) < np.percentile(hc.sum(1), 60)].mean(0)                # tom do cabelo
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
         'pecas': {'cabeca': [0, NCAB + NOR], 'cabelo': [HF0, len(F)]}}
json.dump(saida, open(os.path.join(TX, 'cabeca.json'), 'w'))
tri = lambda a, b: sum(len(F[i]) - 2 for i in range(a, b))
print('cabeça+pescoço', tri(0, NCAB), 'orelhas', tri(NCAB, NCAB + NOR), 'cabelo', tri(HF0, len(F)), 'total', tri(0, len(F)))
print('tom do cabelo', hc.round())
