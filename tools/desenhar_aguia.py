# Desenha o distintivo da ÁGUIA do Zangão (desenho próprio, inspirado na águia heráldica da Lazio — NÃO é o escudo do clube):
# águia branca de asas abertas, cabeça virada pro lado, bico curvo e cauda em leque, sobre um disco azul-celeste com aro branco
# e filete azul-escuro. Pixel art 64 px (PS1). Saída: material/producao/personagens/zangao/texturas/aguia.png
import os
from PIL import Image, ImageDraw
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(RAIZ, 'material/producao/personagens/zangao/texturas'); os.makedirs(OUT, exist_ok=True)
N = 256; im = Image.new('RGB', (N, N), (120, 190, 230)); d = ImageDraw.Draw(im)
CEU, CEU_E, BRANCO, AZ_E, SOMBRA = (124, 196, 236), (88, 160, 208), (246, 246, 240), (24, 52, 96), (178, 200, 214)
d.ellipse((0, 0, N - 1, N - 1), fill=AZ_E); d.ellipse((8, 8, N - 9, N - 9), fill=BRANCO); d.ellipse((22, 22, N - 23, N - 23), fill=CEU)
d.ellipse((40, 40, N - 41, N - 41), outline=CEU_E, width=3)
cx = N // 2
def asa(s):                                                        # asa aberta pra cima, com 5 penas-dedos
    base = [(cx + s * 14, 120), (cx + s * 30, 96)]
    pontas = [(cx + s * 50, 30), (cx + s * 72, 36), (cx + s * 90, 50), (cx + s * 104, 70), (cx + s * 110, 96)]
    vales = [(cx + s * 60, 58), (cx + s * 78, 64), (cx + s * 92, 80), (cx + s * 100, 98)]
    pts = base[:]
    for i, p in enumerate(pontas):
        pts.append(p)
        if i < len(vales): pts.append(vales[i])
    pts += [(cx + s * 92, 124), (cx + s * 64, 132), (cx + s * 30, 140), (cx + s * 16, 146)]
    d.polygon(pts, fill=BRANCO, outline=AZ_E)
    for k in range(4): d.line([(cx + s * (34 + k * 12), 104 + k * 2), (cx + s * (60 + k * 10), 74 + k * 10)], fill=SOMBRA, width=2)   # penas
asa(1); asa(-1)
d.polygon([(cx - 18, 110), (cx + 18, 110), (cx + 22, 150), (cx + 12, 176), (cx - 12, 176), (cx - 22, 150)], fill=BRANCO, outline=AZ_E)   # corpo
d.polygon([(cx - 12, 172), (cx + 12, 172), (cx + 30, 204), (cx + 14, 198), (cx, 210), (cx - 14, 198), (cx - 30, 204)], fill=BRANCO, outline=AZ_E)   # cauda
for k in (-14, 0, 14): d.line([(cx + k * .4, 180), (cx + k, 202)], fill=SOMBRA, width=2)
d.polygon([(cx - 12, 112), (cx - 10, 86), (cx - 2, 74), (cx + 12, 72), (cx + 20, 80), (cx + 18, 96), (cx + 10, 112)], fill=BRANCO, outline=AZ_E)   # cabeça (perfil) e pescoço
for k in range(3): d.polygon([(cx - 12 + k * 7, 112), (cx - 8 + k * 7, 122), (cx - 4 + k * 7, 112)], fill=BRANCO, outline=AZ_E)   # penas do pescoço
d.polygon([(cx + 16, 78), (cx + 40, 82), (cx + 42, 96), (cx + 34, 104), (cx + 34, 94), (cx + 18, 92)], fill=(236, 196, 70), outline=AZ_E)   # bico adunco forte (dourado)
d.line([(cx + 2, 80), (cx + 16, 78)], fill=AZ_E, width=4)                              # sobrancelha (olhar bravo)
d.ellipse((cx + 6, 82, cx + 12, 88), fill=AZ_E)                                       # olho
for s in (-1, 1): d.line([(cx + s * 8, 168), (cx + s * 16, 184), (cx + s * 22, 184)], fill=(236, 196, 70), width=4)   # garras
im = im.resize((64, 64), Image.LANCZOS)
q = im.point(lambda v: (v // 8) * 8)                               # 15 bits
q.save(os.path.join(OUT, 'aguia.png')); im.resize((256, 256), Image.NEAREST).save(os.path.join(OUT, 'aguia_preview.png'))
print('ok', os.path.join(OUT, 'aguia.png'))
