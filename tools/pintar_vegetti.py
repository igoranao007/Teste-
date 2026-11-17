"""VEGETTI — texturas pintadas (cabeça 512×256 no UV cilíndrico, olhos 128×64, corpo 256 repintado do atlas do sy_boss).
uso: python3 -I tools/pintar_vegetti.py material/producao/personagens/vegetti"""
import sys, json, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
OUT = sys.argv[1]; R = random.Random(7)
info = json.load(open(OUT + '/cabeca_uv.json'))
W, H = 512, 256
def px(u, v): return (u * W, (1 - v) * H)
PELE = (222, 168, 140); PELE_ESC = (184, 126, 100); CAB = (46, 34, 26); BARBA = (96, 72, 60)
# pontos-chave (px)
EE = px(*info['pts']['olhoE']['uv']); ED = px(*info['pts']['olhoD']['uv']); NZ = px(*info['pts']['nariz']['uv'])
Q = px(*info['pts']['queixo']['uv']); OE = px(*info['pts']['orelhaE']['uv']); OD = px(*info['pts']['orelhaD']['uv'])
YOLHO = EE[1]; BOCA = (W / 2, YOLHO + 0.70 * (Q[1] - YOLHO)); CX = W / 2
img = Image.new('RGB', (W, H), PELE); d = ImageDraw.Draw(img, 'RGBA')
# textura de pele: variação suave
for _ in range(5000):
    x, y = R.random() * W, R.random() * H; c = R.choice([(0, 0, 0, 10), (255, 230, 210, 12), (150, 80, 60, 10)]); d.point((x, y), fill=c)
# sombras pintadas: maçãs do rosto, laterais do nariz, embaixo do queixo/pescoço, cavidade dos olhos
d.ellipse((CX - 95, YOLHO + 18, CX - 45, YOLHO + 58), fill=(200, 110, 90, 22)); d.ellipse((CX + 45, YOLHO + 18, CX + 95, YOLHO + 58), fill=(200, 110, 90, 22))
for e in (EE, ED): d.ellipse((e[0] - 24, e[1] - 13, e[0] + 24, e[1] + 15), fill=(120, 70, 55, 55))                       # olheira/cavidade
d.polygon([(CX - 6, YOLHO + 4), (CX - 13, NZ[1] + 2), (CX - 4, NZ[1] + 4)], fill=(150, 90, 70, 60))                         # lateral do nariz
d.polygon([(CX + 6, YOLHO + 4), (CX + 13, NZ[1] + 2), (CX + 4, NZ[1] + 4)], fill=(150, 90, 70, 45))
d.rectangle((0, Q[1] + 6, W, H), fill=(150, 95, 75, 90))                                                                   # embaixo do queixo
# barba por fazer (mandíbula, queixo, buço, bochecha baixa)
for _ in range(9000):
    x, y = R.random() * W, R.random() * H; dx = (x - CX) / 120
    lim = BOCA[1] - 30 + 40 * dx * dx                                                                                       # linha da barba sobe pras costeletas
    if y > lim and y < Q[1] + 22 and abs(x - CX) < 150 and not (abs(x - CX) < 26 and -8 < y - BOCA[1] < 12):
        d.point((x, y), fill=BARBA + (R.randint(70, 140),))
for _ in range(500):                                                                                                        # buço (leve)
    x, y = CX + (R.random() - .5) * 46, BOCA[1] - 13 + R.random() * 8; d.point((x, y), fill=BARBA + (R.randint(40, 90),))
# narinas e ponta do nariz
for s in (-1, 1): d.ellipse((CX + s * 7 - 3, NZ[1] + 1, CX + s * 7 + 3, NZ[1] + 5), fill=(90, 50, 40, 200))
d.ellipse((CX - 7, NZ[1] - 8, CX + 7, NZ[1] + 1), fill=(235, 180, 150, 60))
# boca: lábio de cima mais escuro, linha da boca, lábio de baixo com brilho
d.polygon([(CX - 22, BOCA[1]), (CX - 8, BOCA[1] - 5), (CX, BOCA[1] - 3), (CX + 8, BOCA[1] - 5), (CX + 22, BOCA[1])], fill=(160, 92, 82, 230))
d.line([(CX - 23, BOCA[1] + 1), (CX + 23, BOCA[1] + 1)], fill=(80, 40, 36, 255), width=2)
d.polygon([(CX - 19, BOCA[1] + 2), (CX + 19, BOCA[1] + 2), (CX + 11, BOCA[1] + 9), (CX - 11, BOCA[1] + 9)], fill=(190, 115, 100, 210))
d.line([(CX - 8, BOCA[1] + 5), (CX + 8, BOCA[1] + 5)], fill=(225, 160, 145, 140), width=1)
# sobrancelhas grossas e escuras, um pouco caídas pra fora (o olhar sério da foto)
for e, s in ((EE, 1), (ED, -1)):
    for k in range(9):
        y0 = e[1] - 17 + abs(k - 4) * .25
        d.line([(e[0] - s * 22, e[1] - 15), (e[0] - s * 4 + s * k * 3.2, y0 - 2 + k * .15), (e[0] + s * 22, e[1] - 12)], fill=CAB + (230,), width=4)
    d.line([(e[0] - 20, e[1] - 6), (e[0] + 20, e[1] - 6)], fill=(110, 60, 48, 150), width=2)                                # dobra da pálpebra
# orelhas: contorno e concha
for o in (OE, OD):
    d.ellipse((o[0] - 12, o[1] - 20, o[0] + 12, o[1] + 18), fill=(196, 132, 108, 255)); d.ellipse((o[0] - 6, o[1] - 12, o[0] + 6, o[1] + 10), fill=(150, 90, 72, 255))
# cabelo curto: linha do cabelo na testa, laterais e nuca mais baixas (máquina), volume em cima
hair = Image.new('L', (W, H), 0); hd = ImageDraw.Draw(hair)
def linha(u):                                                                                                               # altura (px) da linha do cabelo ao redor da cabeça
    a = abs(u - .5) * 2 * math.pi                                                                                         # 0 = frente, π = nuca
    if a < .38: return YOLHO - 60 + 4 * (a / .38) ** 2                                                                     # testa alta
    if a < .62: return YOLHO - 56 - 9 * math.sin((a - .38) / .24 * math.pi)                                                # entradas (sobe nas têmporas)
    if a < 1.35: return YOLHO - 56 + 40 * ((a - .62) / .73)                                                                # desce até a costeleta
    if a < 1.75: return YOLHO - 14
    return YOLHO + 30 * min(1, (a - 1.75) / .9)                                                                            # nuca
for xx in range(0, W):
    u = xx / W; hd.line([(xx, 0), (xx, linha(u) + 2.5 * math.sin(xx * .9) + 1.5 * math.sin(xx * 2.3))], fill=255)
hair = hair.filter(ImageFilter.GaussianBlur(1.2))
cab = Image.new('RGB', (W, H), CAB); cd = ImageDraw.Draw(cab, 'RGBA')
for _ in range(2600):                                                                                                       # fios
    x, y = R.random() * W, R.random() * H; L = R.randint(3, 9); c = R.choice([(30, 22, 16, 160), (80, 60, 44, 140), (20, 14, 10, 120)])
    cd.line([(x, y), (x + R.uniform(-2, 2), y + L)], fill=c, width=1)
lado = Image.new('L', (W, H), 0); ld = ImageDraw.Draw(lado)                                                                # laterais/nuca raspadas: cabelo mais ralo (mistura com pele)
for xx in range(W):
    a = abs(xx / W - .5) * 2 * math.pi
    if a > 1.1: top = linha(xx / W) - (26 if a < 1.8 else 48); ld.line([(xx, top), (xx, H)], fill=150)
lado = lado.filter(ImageFilter.GaussianBlur(4))
# ── foto do Vegetti projetada de frente no rosto (pelo UV novo, sem esticar): cada texel sabe sua posição 3D ──
pos = np.zeros((H, W, 3), np.float32); cob = np.zeros((H, W), bool)
for t2, t3 in zip(info['tris'], info['tris3d']):
    if max(u for u, v in t2) > 1: continue
    for k in range(1, len(t2) - 1):
        A, B, C = [np.array(px(*t2[i])) for i in (0, k, k + 1)]; PA, PB, PC = [np.array(t3[i]) for i in (0, k, k + 1)]
        x0, y0 = np.floor(np.minimum(np.minimum(A, B), C)).astype(int); x1, y1 = np.ceil(np.maximum(np.maximum(A, B), C)).astype(int)
        xs, ys = np.meshgrid(np.arange(max(0, x0), min(W, x1 + 1)) + .5, np.arange(max(0, y0), min(H, y1 + 1)) + .5)
        den = (B[1] - C[1]) * (A[0] - C[0]) + (C[0] - B[0]) * (A[1] - C[1])
        if abs(den) < 1e-9: continue
        l1 = ((B[1] - C[1]) * (xs - C[0]) + (C[0] - B[0]) * (ys - C[1])) / den; l2 = ((C[1] - A[1]) * (xs - C[0]) + (A[0] - C[0]) * (ys - C[1])) / den; l3 = 1 - l1 - l2
        ok = (l1 >= -.01) & (l2 >= -.01) & (l3 >= -.01); yy = (ys - .5).astype(int)[ok]; xx = (xs - .5).astype(int)[ok]
        pos[yy, xx] = (l1[ok][:, None] * PA + l2[ok][:, None] * PB + l3[ok][:, None] * PC); cob[yy, xx] = True
foto = np.asarray(Image.open('material/personagens/vegetti-ref.jpg').convert('RGB'), np.float32)
# 3 âncoras: olhos e boca no 3D (x, z) ↔ na foto (px)
E3, D3 = info['pts']['olhoE']['mundo'], info['pts']['olhoD']['mundo']; zb = info['pts']['queixo']['mundo'][2] + (E3[2] - info['pts']['queixo']['mundo'][2]) * .30
src = np.array([[D3[0], D3[2], 1], [E3[0], E3[2], 1], [0, zb, 1]]); dst = np.array([[343, 63], [386, 63], [364, 90]], float)    # olho direito do personagem = esquerda da foto
Mx = np.linalg.solve(src, dst)
fx = pos[..., 0] * Mx[0, 0] + pos[..., 2] * Mx[1, 0] + Mx[2, 0]; fy = pos[..., 0] * Mx[0, 1] + pos[..., 2] * Mx[1, 1] + Mx[2, 1]
amostra = foto[np.clip(fy.astype(int), 0, foto.shape[0] - 1), np.clip(fx.astype(int), 0, foto.shape[1] - 1)]
verde = (amostra[..., 1] > amostra[..., 0] * 1.03) & (amostra[..., 1] > amostra[..., 2] * 1.1)                                  # fundo verde da foto: não usa
cz = (E3[2] + zb) / 2 - .01
peso = np.clip((info['CY'] - .035 - pos[..., 1]) / .035, 0, 1) * np.clip(1 - ((pos[..., 0] / .068) ** 2 + ((pos[..., 2] - cz) / .085) ** 2), 0, 1) ** .6
peso = np.where(cob & ~verde, np.clip(peso * 1.6, 0, 1) * .6, 0)
boca_px = BOCA[1]; peso[int(boca_px) - 14:int(boca_px) + 14, :] *= .35                                       # a boca pintada fica por cima
base = np.asarray(img, np.float32); img = Image.fromarray((base * (1 - peso[..., None]) + amostra * peso[..., None]).astype(np.uint8))
mask = ImageChops.subtract(hair, lado.point(lambda v: v * .55))
img = Image.composite(cab, img, mask)
# olhos pintados direto na órbita (o globo separado do modelo base ficava escondido atrás da pálpebra)
d = ImageDraw.Draw(img, 'RGBA')
for e, s_ in ((EE, 1), (ED, -1)):
    cx, cy = e[0], e[1] + 1; w, h = 14, 6.5
    d.polygon([(cx - w, cy + 1), (cx - w * .4, cy - h), (cx + w * .5, cy - h * .9), (cx + w, cy), (cx + w * .4, cy + h * .8), (cx - w * .5, cy + h * .75)], fill=(236, 230, 220, 255))
    d.ellipse((cx - 5.5, cy - 5.5, cx + 5.5, cy + 5.5), fill=(84, 104, 74, 255)); d.ellipse((cx - 3.6, cy - 3.6, cx + 3.6, cy + 3.6), fill=(48, 60, 40, 255))
    d.ellipse((cx - 2.2, cy - 2.2, cx + 2.2, cy + 2.2), fill=(10, 8, 6, 255)); d.rectangle((cx - 3, cy - 3.5, cx - 1.5, cy - 2), fill=(255, 255, 250, 255))
    d.line([(cx - w - 1, cy + 1), (cx - w * .4, cy - h - 1), (cx + w * .5, cy - h - .8), (cx + w + 1, cy)], fill=(30, 20, 14, 255), width=3)     # cílio de cima
    d.line([(cx - w, cy + 2), (cx - w * .5, cy + h * .9), (cx + w * .4, cy + h * .95), (cx + w, cy + 1)], fill=(140, 90, 74, 220), width=1)       # pálpebra de baixo
img = img.quantize(64, dither=Image.Dither.NONE).convert('RGB')                                                             # paleta reduzida (cara de PS1)
img.save(OUT + '/texturas/cabeca.png')
# guia: triângulos do UV por cima da textura (só pra conferência)
g = img.copy(); gd = ImageDraw.Draw(g)
for t in info['tris']: gd.polygon([px(u % 1.0001 if u <= 1 else u - 1, v) for u, v in t], outline=(0, 255, 120))
g.save(OUT + '/inspecao/uv_cabeca_guia.png')
# olhos 128×64: metade esquerda = olho esquerdo do personagem, direita = olho direito
o = Image.new('RGB', (128, 64), (196, 140, 114)); od = ImageDraw.Draw(o)
for x0 in (0, 64):                                                                                                          # olho amendoado: pele em cima e embaixo, branco nos cantos, íris grande
    cx, cy = x0 + 32, 32
    od.polygon([(x0 + 2, cy + 2), (cx - 10, cy - 14), (cx + 12, cy - 13), (x0 + 62, cy + 1), (cx + 10, cy + 13), (cx - 12, cy + 12)], fill=(232, 226, 214))
    od.ellipse((cx - 13, cy - 13, cx + 13, cy + 13), fill=(78, 98, 70)); od.ellipse((cx - 9, cy - 9, cx + 9, cy + 9), fill=(52, 64, 44))     # íris esverdeada/castanha
    od.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=(8, 8, 6)); od.rectangle((cx - 7, cy - 8, cx - 3, cy - 4), fill=(255, 255, 250))
    od.line([(x0 + 2, cy + 1), (cx - 10, cy - 15), (cx + 12, cy - 14), (x0 + 62, cy)], fill=(36, 24, 18), width=4)                     # cílio de cima
    od.line([(x0 + 4, cy + 3), (cx - 12, cy + 13), (cx + 10, cy + 14), (x0 + 60, cy + 2)], fill=(150, 98, 82), width=2)               # pálpebra de baixo
o.save(OUT + '/texturas/olhos.png')
# corpo: atlas do sy_boss repintado (terno grafite, camisa branca, gravata verde, mãos e pescoço com a pele do Vegetti)
c = Image.open('material/modelos/itch/gente/csaf/sy_boss.png').convert('RGB'); q = c.load()
for y in range(256):
    for x in range(256):
        r, g_, b = [v / 255 for v in q[x, y]]; lum = .3 * r + .59 * g_ + .11 * b; sat = max(r, g_, b) - min(r, g_, b)
        if r > g_ * 1.5 and r > b * 1.25 and r > .2 and 24 < y < 70 and 88 < x < 110: q[x, y] = tuple(int(v * lum / .3) for v in (0x1c, 0x9a, 0x44)); continue
        if r > g_ * 1.08 and g_ > b * .95 and sat > .06 and r > .18: k = min(1.25, max(.55, lum / .3)); q[x, y] = tuple(int(min(255, v * k)) for v in PELE); continue
        if sat < .14 and lum < .72: q[x, y] = (int(r * 128), int(g_ * 128), int(b * 128 + 4))
c.save(OUT + '/texturas/corpo.png')
print('ok', OUT + '/texturas')
