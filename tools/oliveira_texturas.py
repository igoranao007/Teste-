# Texturas PS1 da armadura do Oliveira (128 px, 15 bits): placa de "pedra-metal" preta gasta, placa com painéis/ranhuras/respiros,
# metal grafite escovado e tecido escuro do tabardo. Saída: material/producao/personagens/oliveira/texturas/
import random, math
from PIL import Image, ImageDraw, ImageFilter
random.seed(21); D = 'material/producao/personagens/oliveira/texturas/'
def q15(im): return im.point(lambda v: (v // 8) * 8)
def ruido(N, base, amp, blur=0.8, esc=1):
    im = Image.new('RGB', (N // esc, N // esc)); px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r = random.randint(-amp, amp); px[x, y] = tuple(max(0, min(255, b + r)) for b in base)
    return im.resize((N, N), Image.NEAREST).filter(ImageFilter.GaussianBlur(blur))
N = 128
# placa: pedra-metal preta, com rachaduras finas e cantos gastos
im = ruido(N, (50, 50, 55), 10, 0.6, 2); d = ImageDraw.Draw(im)
for _ in range(14):
    x, y = random.randint(0, N), random.randint(0, N); pts = [(x, y)]
    for _ in range(random.randint(3, 7)): x += random.randint(-9, 9); y += random.randint(-9, 9); pts.append((x, y))
    d.line(pts, fill=(22, 22, 25), width=1)
for _ in range(60):
    x, y = random.randint(0, N - 2), random.randint(0, N - 2); d.point((x, y), fill=(74, 74, 80))
d.rectangle((0, 0, N - 1, N - 1), outline=(58, 58, 64)); d.line((1, N - 2, N - 2, N - 2), fill=(20, 20, 22))
q15(im).save(D + 'placa.png')
# placa2: painéis com ranhura, chanfro claro em cima/esquerda, respiros e parafusos
im = ruido(N, (46, 46, 51), 7, 0.6, 2); d = ImageDraw.Draw(im)
for (x0, y0, x1, y1) in ((4, 4, 60, 60), (68, 4, 124, 36), (68, 44, 124, 124), (4, 68, 60, 124)):
    d.rectangle((x0, y0, x1, y1), outline=(18, 18, 20)); d.line((x0 + 1, y0 + 1, x1 - 1, y0 + 1), fill=(70, 70, 76)); d.line((x0 + 1, y0 + 1, x0 + 1, y1 - 1), fill=(62, 62, 68))
    for (bx, by) in ((x0 + 4, y0 + 4), (x1 - 4, y0 + 4), (x0 + 4, y1 - 4), (x1 - 4, y1 - 4)): d.rectangle((bx - 1, by - 1, bx + 1, by + 1), fill=(88, 88, 94))
for k in range(5): d.rectangle((76, 56 + k * 10, 116, 59 + k * 10), fill=(14, 14, 16)); d.line((76, 60 + k * 10, 116, 60 + k * 10), fill=(60, 60, 66))
d.line((12, 92, 52, 92), fill=(16, 16, 18), width=2)
q15(im).save(D + 'placa2.png')
# metal grafite escovado
im = Image.new('RGB', (N, N)); px = im.load()
for y in range(N):
    lv = random.randint(-6, 6)
    for x in range(N): v = 72 + lv + random.randint(-5, 5); px[x, y] = (v, v, v + 5)
d = ImageDraw.Draw(im)
for _ in range(25): x, y = random.randint(0, N), random.randint(0, N); d.line((x, y, x + random.randint(4, 16), y), fill=(104, 104, 110))
q15(im).save(D + 'metal.png')
# tecido do tabardo: trama escura, faixa de cima com debrum amarelo-escuro e fios soltos
im = Image.new('RGB', (64, 128)); px = im.load()
for y in range(128):
    for x in range(64):
        v = 26 + (4 if (x + y) % 4 < 2 else 0) + random.randint(-3, 3) + (6 if x % 16 == 0 else 0); px[x, y] = (v, v - 1, v - 2)
d = ImageDraw.Draw(im); d.rectangle((0, 0, 63, 5), fill=(46, 42, 30)); d.line((0, 6, 63, 6), fill=(150, 116, 30))
for _ in range(10): x = random.randint(0, 63); d.line((x, 100 + random.randint(0, 20), x + random.randint(-2, 2), 127), fill=(14, 14, 14))
q15(im).save(D + 'tecido.png'); print('ok')
