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
OB = orig.filter(ImageFilter.GaussianBlur(9)).load()   # só as dobras grandes (sem estampa)
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
import os
ROUPA = os.environ.get('ROUPA', 'vasco')
from PIL import ImageEnhance
foto = ImageEnhance.Contrast(Image.open(FOTO).convert('RGB').filter(ImageFilter.GaussianBlur(0.5))).enhance(float(os.environ.get('CONTRASTE', '1.25'))).filter(ImageFilter.UnsharpMask(2, 90, 2)); F = foto.load(); FW, FH = foto.size
QUENTE = tuple(float(v) for v in os.environ.get('QUENTE', '1.0,0.93,0.82').split(','))
def amostra(mx, my):
    d = abs(mx - 256); fx = min(max(interp(PX, 256 - d), 0), FW - 1); fy = min(max(interp(PY, my), 0), FH - 1)
    c = F[int(fx), int(fy)]; return [c[i] * QUENTE[i] for i in range(3)]
am = [amostra(256 + dx, y) for dx in range(-60, 61, 6) for y in (200, 250, 300)]
PELE = [sum(c[i] for c in am) / len(am) for i in range(3)]
if os.environ.get('PELE_RGB'): PELE = [float(v) for v in os.environ['PELE_RGB'].split(',')]
# ---------- desenhos do uniforme (tela em metros)
FONTE = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; FONTE_C = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
PRETO, BRANCO, VERM, CAB = (22, 22, 25), (226, 226, 222), (196, 30, 36), (48, 33, 22)
if os.environ.get('CAB'): CAB = tuple(int(v) for v in os.environ['CAB'].split(','))
EM = 1000
PULSO = 0.80
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
if ROUPA == 'luan_canvas':                                           # (antigo) escudo/logo desenhados — agora vêm da foto
    FR, CO = tela(), tela()
    esc_ = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'material/producao/personagens/luan/texturas/escudo_cam_hd.png')).convert('RGBA')
    esc_ = esc_.resize((int(0.085 * EM), int(0.105 * EM)), Image.LANCZOS); x_, y_ = pm(0.105, 1.505); FR.alpha_composite(esc_, (x_ - esc_.width // 2, y_ - esc_.height // 2))
    d_ = ImageDraw.Draw(FR); OURO_ = (200, 154, 74, 255); x0_, y0_ = pm(-0.135, 1.535)
    for k_, alt_ in enumerate((0.018, 0.027, 0.036)):                  # 3 barras inclinadas (logo do fornecedor)
        bx = x0_ + int(k_ * 0.014 * EM); w_ = int(0.009 * EM); h_ = int(alt_ * EM)
        d_.polygon([(bx, y0_), (bx + w_, y0_), (bx + w_ + int(h_ * .45), y0_ - h_), (bx + int(h_ * .45), y0_ - h_)], fill=OURO_)
DF, DC = FR.load(), CO.load()
if ROUPA == 'luan':
    _D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'material/producao/personagens/luan/')
    CF = Image.open(_D + 'referencia/camisa_atletico.jpg').convert('RGB'); CC = Image.open(_D + 'texturas/camisa_costas.png').convert('RGB')
    CFp, CCp = CF.load(), CC.load()
    def amostra_cam(img, px, py):                                     # bilinear na foto da camisa (736 px)
        px = max(0, min(734.999, px)); py = max(0, min(734.999, py)); x0, y0 = int(px), int(py); fx, fy = px - x0, py - y0
        c = [img[x0, y0][i] * (1 - fx) * (1 - fy) + img[x0 + 1, y0][i] * fx * (1 - fy) + img[x0, y0 + 1][i] * (1 - fx) * fy + img[x0 + 1, y0 + 1][i] * fx * fy for i in range(3)]
        return c
    _ARM = {}
    for t_ in L:
        if t_['obj'] == 'arms':
            for q_ in t_['p']: _ARM.setdefault(round(abs(q_[0]) * 50), []).append(q_)
    EIXO = {k_: (sum(q_[1] for q_ in v_) / len(v_), sum(q_[2] for q_ in v_) / len(v_)) for k_, v_ in _ARM.items()}
    def eixo(ax_):
        k_ = round(ax_ * 50)
        while k_ not in EIXO and k_ > 0: k_ -= 1
        return EIXO.get(k_, (0.0, 1.55))
    def camisa_ombro(X_, Y_, Z_):                                     # alto do ombro: segue a faixa das 3 listras da foto (da gola até a manga)
        t_ = max(0.0, min(1.0, (abs(X_) - 0.075) / (0.245 - 0.075)))
        px = 288 + (150 - 288) * t_; py = 48 + (168 - 48) * t_
        off = max(-0.25, min(1.0, -(Y_ - 0.03) / 0.07)) * 26            # frente (Y<0) -> pra dentro da camisa na foto
        px += 0.65 * off; py += 0.76 * off
        if X_ > 0: px = 736 - px
        return amostra_cam(CFp, px, py)
    def camisa_tronco(X_, Y_, Z_, nz=0.0):                            # foto de frente / costas projetada no tronco (ângulo elíptico)
        if nz > 0.5 and Z_ > 1.62 and abs(X_) > 0.07:
            c_ = camisa_ombro(X_, Y_, Z_)
            return [30, 30, 33] if (min(c_) > 120 and c_[2] > 0.8 * c_[0]) else c_
        py = 50 + (1.75 - Z_) / 0.00122
        uf = math.atan2(X_ / 0.21, -(Y_ - 0.02) / 0.14) / (math.pi / 2)
        if abs(uf) <= 1: c_ = amostra_cam(CFp, 373 + uf * 176, py)
        else:
            ub = math.atan2(X_ / 0.21, (Y_ - 0.02) / 0.14) / (math.pi / 2); c_ = amostra_cam(CCp, 373 - ub * 176, py)
        if min(c_) > 120 and c_[2] > 0.8 * c_[0]: c_ = [30, 30, 33]          # fundo branco da foto (fora da camisa) -> preto
        return c_
    def camisa_manga(X_, Y_, Z_):                                     # manga: quadrilátero da manga na foto (o lado da foto conforme o braço)
        ax_ = abs(X_); yc, zc = eixo(ax_); s_ = max(0.0, min(1.0, (ax_ - 0.235) / (0.43 - 0.235)))
        fi = math.atan2(-(Y_ - yc), Z_ - zc)                           # 0 em cima, +pi/2 na frente, pi embaixo
        t_ = min(1.0, abs(fi) / math.pi)
        T0, T1, B0, B1 = (158, 150), (76, 312), (190, 250), (188, 345)
        top = (T0[0] + (T1[0] - T0[0]) * s_, T0[1] + (T1[1] - T0[1]) * s_); bot = (B0[0] + (B1[0] - B0[0]) * s_, B0[1] + (B1[1] - B0[1]) * s_)
        px = top[0] + (bot[0] - top[0]) * t_; py = top[1] + (bot[1] - top[1]) * t_
        if X_ > 0: px = 736 - px                                      # braço esquerdo do personagem = manga da direita da foto
        return amostra_cam(CFp if fi >= 0 else CCp, px, py)
def desenho(frente, X, Z):
    x, y = pm(X if frente else -X, Z)
    if not (0 <= x < 900 and 0 <= y < 1900): return None
    c = (DF if frente else DC)[x, y]; return c[:3] if c[3] > 110 else None
# ---------- regras
def regiao(t, p, o):
    X, Y, Z = p; ax = abs(X); h, s, v = colorsys.rgb_to_hsv(*[q / 255 for q in o])
    if t['obj'] == 'head':
        return 'cabelo' if v < 0.33 and not (0.0 <= h < 0.12 and s > 0.35 and v > 0.25) else 'pele_cab'
    if ROUPA == 'terno':
        if t['obj'] == 'arms': return 'manga' if ax < PULSO else 'pele'
        if Z > 0.96:
            if Z > 1.69 and (0.0 <= h < 0.12 and s > 0.2): return 'pele'
            return 'paleto'
        return 'calca' if Z > 0.115 else 'chuteira'
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
_pc = [O[x, y] for x, y, p_, t_ in lista if regiao(t_, p_, O[x, y]) == 'pele_cab']
PELE_ORIG = [sum(c[i] for c in _pc) / max(1, len(_pc)) for i in range(3)]
def dobra(o, k, forca=1.0):
    f = 1 + (lum(o) / max(media[k], 0.05) - 1) * forca
    lo = 0.80 if (ROUPA == 'terno' and k in ('paleto', 'manga')) else 0.55   # tira a estampa da camiseta original
    return max(lo, min(1.35, f))
tex = Image.new('RGB', (N, N), (0, 0, 0)); T = tex.load(); feito = set()
TROCA = os.environ.get('INVERTE', '1') == '1'    # paletó preto + camisa verde
VERDE, VERDE_L, CAM, GRAV = ((22, 22, 25), (36, 36, 40), (30, 92, 56), (16, 16, 18)) if TROCA else ((26, 78, 48), (34, 96, 60), (20, 20, 23), (48, 48, 54))
def cor_terno(k, p, n, o):
    X, Y, Z = p; ax = abs(X); frente = n[1] < -0.2
    if k == 'manga':
        if ax > PULSO - 0.035: return [q * dobra(o, k) for q in (CAM if ax > PULSO - 0.012 else [q * 0.8 for q in VERDE])]   # punho
        return [q * dobra(o, k) for q in VERDE]
    if k == 'calca':
        return [q * dobra(o, k, 0.25) for q in (22, 22, 25)]
    if k == 'paleto':
        if frente:
            v = 0.105 * ss(1.28, 1.72, Z)                          # abertura em V
            if ax < v:
                if ax < 0.022 and Z > 1.30: return [q * dobra(o, k, 0.6) for q in GRAV] if Z < 1.68 else [q * 0.8 for q in GRAV]   # gravata + nó
                return [q * dobra(o, k, 0.7) for q in CAM]
            if ax < v + 0.032 and Z > 1.40: return [q * dobra(o, k) * (1.0 if ax > v + 0.004 else 0.6) for q in VERDE_L]   # lapela
            if Z < 1.30 and ax < 0.010: return [q * 0.55 for q in VERDE]                      # fecho
            if any(abs(Z - bz) < 0.012 for bz in (1.23, 1.12)) and abs(ax - 0.028) < 0.011: return [14, 14, 16]   # botões
            if abs(Z - 1.06) < 0.008 and 0.07 < ax < 0.19: return [q * 0.55 for q in VERDE]     # bolsos
            if abs(Z - 1.52) < 0.006 and 0.11 < X < 0.19: return [q * 0.6 for q in VERDE]      # bolso do peito
        elif n[1] > 0.2 and ax < 0.006 and Z < 1.55: return [q * 0.6 for q in VERDE]            # costura das costas
        if Z > 1.70 and n[1] > -0.2: return [q * dobra(o, k) for q in CAM]                     # gola da camisa atrás
        return [q * dobra(o, k) for q in VERDE]
    return [q * dobra(o, k, 0.8) for q in (24, 24, 27)]
for x, y, p, t in lista:
    o = O[x, y]; k = regiao(t, p, o); X, Y, Z = p; ax = abs(X); n = t['n']; rn_ = math.hypot(X, Y + 0.02)
    if ROUPA == 'luan' and t['obj'] == 'head' and .42 < x / N < .80 and y / N > .90:   # armação dos óculos (preta)
        T[x, y] = (14, 14, 16); feito.add((x, y)); continue
    if ROUPA == 'luan' and k == 'pele_cab':                           # mantém o rosto pintado do modelo; só troca o tom da pele
        c = [o[i] * PELE[i] / max(PELE_ORIG[i], 1) for i in range(3)]
        T[x, y] = tuple(max(0, min(255, int(v))) for v in c); feito.add((x, y)); continue
    if ROUPA == 'luan' and k not in ('pele_cab', 'cabelo'):
        # LUAN: camisa do Atlético-MG (preta com padrão em V grafite, debrum/listras/gola/punhos dourados, escudo e logo),
        # calça preta com frisos amarelos e joelheira, coturno preto, luvas pretas com friso amarelo
        PRETO_L, GRAF_L, OURO_L, AMAR_L, CALCA_L, BOTA_L, LUVA_L, JOELHO_L = (22, 22, 25), (58, 58, 64), (200, 154, 74), (255, 212, 36), (24, 24, 27), (16, 16, 18), (20, 20, 22), (44, 44, 48)
        frente = n[1] < -0.2
        def padrao_v(X_, Z_):                                          # colunas com "V" grafite (como a camisa da foto)
            col = math.floor((X_ + 0.45) / 0.04); u_ = (X_ + 0.45) / 0.04 - col
            zz = Z_ / 0.018 + abs(u_ - 0.5) * 1.4
            base_ = (26, 26, 29) if col % 2 else (21, 21, 24)
            return GRAF_L if (zz % 1) < 0.28 else base_
        def perto_linha(px, pz, pts, larg):
            for (x1, z1), (x2, z2) in zip(pts, pts[1:]):
                dx, dz = x2 - x1, z2 - z1; tt = max(0, min(1, ((px - x1) * dx + (pz - z1) * dz) / (dx * dx + dz * dz)))
                if math.hypot(px - x1 - tt * dx, pz - z1 - tt * dz) < larg: return True
            return False
        DEBRUM = [(0.07, 1.71), (0.14, 1.66), (0.185, 1.56), (0.20, 1.40), (0.205, 1.18), (0.205, 0.97)]
        if t['obj'] == 'arms':
            if ax >= PULSO - 0.005: c = [q * dobra(o, 'pele', 0.6) for q in (AMAR_L if PULSO + 0.004 < ax < PULSO + 0.012 else LUVA_L)]   # luva preta com friso
            elif ax > 0.435: c = [PELE[i] * dobra(o, 'pele', 0.9) for i in range(3)]                                            # antebraço
            else:
                cor = camisa_manga(X, Y, Z)
                if min(cor) > 150 and cor[2] > 0.8 * cor[0]: cor = [30, 30, 33]
                if ax > 0.413: cor = OURO_L                                                                                        # punho dourado
                yc_, zc_ = eixo(ax); fi_ = math.atan2(-(Y - yc_), Z - zc_)
                if ax < 0.33 and any(abs(fi_ - f0) < 0.075 for f0 in (-0.30, 0.0, 0.30)): cor = OURO_L                           # 3 listras no alto do ombro
                c = [q * (0.86 if cor is not OURO_L else 1.0) * dobra(OB[x, y], 'manga', 0.45) for q in cor]
        elif k == 'chuteira': c = [q * dobra(o, k, 0.8) for q in BOTA_L]
        elif Z < 0.96 and t['obj'] == 'body':                                                                                       # calça blindada
            cor = CALCA_L
            if frente and abs(ax - 0.095) < 0.006 and 0.55 < Z < 0.92: cor = AMAR_L                                                # friso de energia
            lado_ = n[0] * X > 0.55
            if lado_ and abs(Y - 0.02) < 0.007 and 0.12 < Z < 0.92: cor = AMAR_L                                                   # friso na lateral da perna
            if frente and abs(Z - 0.78) < 0.006 and 0.10 < ax < 0.20: cor = AMAR_L                                                 # placa da coxa (linha horizontal)
            if frente and abs(Z - 0.66) < 0.006 and 0.12 < ax < 0.19: cor = AMAR_L
            if frente and 0.40 < Z < 0.53 and abs(ax - 0.10) < 0.055: cor = JOELHO_L if (0.41 < Z < 0.52 and abs(ax - 0.10) < 0.047) else AMAR_L   # joelheira com aro
            if abs(Z - 0.93) < 0.012: cor = (34, 34, 38)                                                                          # cós
            c = [q * dobra(OB[x, y], 'calcao', 0.6) for q in cor]
        elif k == 'pele': c = [PELE[i] * dobra(o, k, 0.9) for i in range(3)]
        else:                                                                                                                       # camisa = foto (frente) / costas montadas da foto
            cor = camisa_tronco(X, Y, Z, n[2])
            c = [q * 0.84 * dobra(OB[x, y], 'camisa', 0.25) for q in cor]                                                      # foto um pouco mais escura (o motor clareia)
        T[x, y] = tuple(max(0, min(255, int(v))) for v in c); feito.add((x, y)); continue
    if ROUPA == 'dom' and k not in ('pele_cab', 'cabelo'):
        # DOM: casaco branco (manga comprida até o pulso) aberto em V sobre blusa preta de zíper, fivela laranja, gola alta branca;
        # calça escura e sapato preto
        CASACO, BLUSA, ZIPER, LARANJA, CALCA_D, SAP, AMAR = (226, 222, 212), (20, 20, 23), (120, 122, 126), (226, 112, 30), (36, 37, 44), (18, 18, 20), (236, 190, 40)
        frente = n[1] < -0.2
        if t['obj'] == 'arms': c = [q * dobra(OB[x, y], 'manga', 0.5) for q in (AMAR if PULSO - 0.045 < ax < PULSO - 0.012 else CASACO)] if ax < PULSO else [PELE[i] * dobra(o, 'pele', 0.9) for i in range(3)]   # punho amarelo
        elif k == 'chuteira': c = [q * dobra(o, k, 0.8) for q in SAP]
        elif Z < 0.96 and t['obj'] == 'body':
            cor = CASACO if (Z > 0.80 and not (frente and ax < 0.05)) else CALCA_D                # barra do casaco cobre o quadril (aberta na frente)
            if cor == CASACO and Z < 0.83: cor = AMAR                                                # barra amarela
            c = [q * dobra(OB[x, y], 'calcao', 0.35 if cor == CASACO else 0.6) for q in cor]
        elif k == 'pele': c = [PELE[i] * dobra(o, k, 0.9) for i in range(3)]
        else:
            cor = CASACO
            if frente:
                v = 0.012 + 0.085 * ss(1.18, 1.70, Z)                                            # abertura em V
                if ax < v and Z > 1.10:
                    cor = BLUSA
                    if ax < 0.006: cor = ZIPER                                                    # zíper
                elif ax < v + 0.014 and Z > 1.10: cor = AMAR                                       # debrum amarelo na abertura
                if abs(Z - 1.24) < 0.016 and ax < 0.045: cor = LARANJA                            # fivela laranja
                if Z <= 1.10 and ax < 0.007: cor = (150, 148, 140)                                # fecho do casaco
            if Z > 1.64 and rn_ < 0.13: cor = BLUSA if (frente and ax < 0.05) else CASACO        # gola alta branca (blusa preta na frente)
            c = [q * dobra(OB[x, y], 'camisa' if t['obj'] != 'arms' else 'manga', 0.3) for q in cor]   # dobras leves (sem a estampa da camiseta original)
        T[x, y] = tuple(max(0, min(255, int(v))) for v in c); feito.add((x, y)); continue
    if ROUPA == 'frentista' and k not in ('pele_cab', 'cabelo'):
        CAM_F, CALCA_F, REFL, BOTA = (56, 74, 102), (30, 38, 56), (196, 200, 196), (20, 20, 22)
        if k == 'pele' and not (t['obj'] == 'body' and Z < 0.96): c = [PELE[i] * dobra(o, k, 0.9) for i in range(3)]
        elif k == 'chuteira': c = [q * dobra(o, k, 0.8) for q in BOTA]
        elif Z < 0.96 and t['obj'] == 'body': c = [q * dobra(o, 'calcao', 0.6) for q in CALCA_F]          # calça (calção, pele e meião)
        else:                                                                                       # camisa de frentista
            cor = CAM_F
            if t['obj'] != 'arms' and abs(Z - 1.36) < 0.022: cor = REFL                              # faixa refletiva no peito/costas
            if t['obj'] == 'arms' and 0.36 < ax < 0.40: cor = REFL                                   # faixa na manga
            if t['obj'] != 'arms' and n[1] < -0.3:
                if 0.07 < X < 0.15 and 1.44 < Z < 1.52: cor = (236, 236, 230)                        # crachá
                if -0.16 < X < -0.06 and 1.42 < Z < 1.52 and (abs(X + 0.11) > 0.046 or abs(Z - 1.47) > 0.046): cor = (40, 54, 76)   # bolso
                if ax < 0.006 and Z < 1.62: cor = (36, 48, 70)                                       # abotoadura
            if Z > 1.66 and rn_ < 0.12 and t['obj'] == 'body': cor = (44, 60, 86)                    # gola
            c = [q * dobra(OB[x, y], 'camisa' if t['obj'] != 'arms' else 'manga', 0.8) for q in cor]
        T[x, y] = tuple(max(0, min(255, int(v))) for v in c); feito.add((x, y)); continue
    if ROUPA == 'terno' and k in ('manga', 'calca', 'paleto', 'chuteira'):
        T[x, y] = tuple(max(0, min(255, int(v))) for v in cor_terno(k, p, n, OB[x, y] if k in ('paleto', 'manga') else o)); feito.add((x, y)); continue
    if k == 'pele_cab':
        mx, my = X / ESC * 512 + 256, (CZ - Z) / ESC * 512 + 256
        w = max(0.0, min(1.0, (1 - math.hypot((mx - 256) / 88, (my - 285) / 150)) / 0.3)) * (ss(-0.1, -0.55, n[1]) if n[1] > -0.55 else 1)
        base = [PELE[i] * dobra(o, k, 0.8) for i in range(3)]
        if w > 0 and os.environ.get('ROSTO_LISO') != '1': f = amostra(mx, my); base = [base[i] * (1 - w) + f[i] * w for i in range(3)]   # ROSTO_LISO=1: só pele (o rosto vem de uma máscara por cima)
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
