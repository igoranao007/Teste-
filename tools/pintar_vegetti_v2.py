"""Pinta a textura do Vegetti v2 sobre o atlas da base PSX (heyheythere, CC BY 4.0).
Método do estudo: tinta de cada peça assada na textura, rosto com 3-4 traços fortes em poucos pixels."""
import json, sys, colorsys
from PIL import Image, ImageDraw
BASE, UVS, OUT = sys.argv[1:4]
a = Image.open(BASE).convert('RGB'); px = a.load()
d = json.load(open(UVS))
def mascara(k):
    m = Image.new('L', a.size, 0); dr = ImageDraw.Draw(m)
    for p in d[k]: dr.polygon([tuple(q) for q in p['uv']], fill=255)
    return m.load()
TINTA = {'jacket': (44, 46, 52), 'jeans': (48, 50, 57), 'boots': (24, 24, 27), 'tee': (236, 236, 232), 'hair_short': (52, 36, 24)}
for k, (r, g, b) in TINTA.items():
    m = mascara(k)
    for y in range(128):
        for x in range(1024):
            if m[x, y]:
                c = px[x, y]; l = sum(c) / 765
                px[x, y] = (int(r * (.55 + .6 * l)), int(g * (.55 + .6 * l)), int(b * (.55 + .6 * l)))
# pele: morena -> clara rosada (só na malha do corpo)
m = mascara('corpo')
for y in range(128):
    for x in range(1024):
        if not m[x, y]: continue
        r, g, b = px[x, y]; h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if .02 < h < .12 and s > .18 and v > .5:   # pele
            px[x, y] = (min(255, int(r * 1.07 + 6)), min(255, int(g * 1.13)), min(255, int(b * 1.28)))
        elif .02 < h < .14 and v <= .5 and y < 48 and x < 128:   # cabelo pintado na cabeça: castanho escuro
            px[x, y] = (int(r * .5), int(g * .45), int(b * .4))
# rosto (faixa 0..128 x 0..48). Olhos em ~x52-56 / 70-74, y15; boca ~y25
dr = ImageDraw.Draw(a)
SOB = (40, 28, 20)
dr.rectangle((50, 11, 57, 12), fill=SOB); dr.rectangle((69, 11, 76, 12), fill=SOB)   # sobrancelhas grossas e retas
for x, y in [(57, 13), (69, 13)]: px[x, y] = SOB
BARBA = (120, 92, 80)
for y in range(20, 36):
    for x in range(44, 84):
        dx, dy = (x - 63.5) / 17, (y - 23) / 12
        if dx * dx + dy * dy > 1 or y < 23 and abs(x - 63.5) < 15: continue   # contorno do queixo e maxilar, bochecha livre
        if 60 <= x <= 67 and 24 <= y <= 26: continue   # boca
        if ((x * 7919 + y * 104729) ^ (x * y * 31)) % 100 > 38: continue   # pontilhado ralo e irregular
        r, g, b = px[x, y]
        if r > 150: px[x, y] = ((r * 2 + BARBA[0]) // 3, (g * 2 + BARBA[1]) // 3, (b * 2 + BARBA[2]) // 3)
# laterais raspadas: cabelo encostado na pele vira degradê (2-3 px), sem retângulo
ori = a.copy().load()
for y in range(4, 30):
    for x in range(20, 108):
        r, g, b = ori[x, y]
        if r >= 120: continue
        viz = [ori[x + i, y + j][0] >= 150 for i in (-3, -2, -1, 1, 2, 3) for j in (-2, 0, 2) if 0 <= y + j < 48]
        if any(viz) and (x < 46 or x > 81): px[x, y] = ((r + 150) // 2, (g + 118) // 2, (b + 104) // 2)
# terno: decote em V com camisa branca e gravata verde no peito do paletó
mj = mascara('jacket'); cx = 578
for y in range(0, 20):
    w = int(6 * (1 - y / 20))
    for x in range(cx - w, cx + w + 1):
        if mj[x, y]: px[x, y] = (232, 232, 226)
for y in range(0, 24):
    w = 1
    for x in range(cx - w, cx + w + 1):
        if mj[x, y]: px[x, y] = (40, 190, 80) if y >= 3 else (28, 140, 58)
for y in range(0, 20):   # lapela (linha escura na borda do V)
    w = int(6 * (1 - y / 20))
    for x in (cx - w - 1, cx + w + 1):
        if mj[x, y]: px[x, y] = (26, 27, 31)
# botas viram sapato social: o cano (acima do tornozelo) fica da cor da calça
zc = .12   # acima do tornozelo (o pé vai até ~0,09 m)
mc = Image.new('L', a.size, 0); dm = ImageDraw.Draw(mc)
for p in d['boots']:
    if p['z'] > zc: dm.polygon([tuple(q) for q in p['uv']], fill=255)
mc = mc.load()
for y in range(128):
    for x in range(1024):
        if mc[x, y]:
            l = sum(px[x, y]) / 765 / .25; r, g, b = TINTA['jeans']
            px[x, y] = tuple(min(255, int(c * (.75 + .25 * min(l, 1.6)))) for c in (r, g, b))
print('cano acima de z', round(zc, 3))
a.save(OUT)
