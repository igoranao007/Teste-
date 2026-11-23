# Texturas pequenas (PS1) dos acessórios do Luan: placa de armadura (grafite com chanfro, rebites e ranhura),
# borracha da máscara de gás (preto fosco com granulado e costuras) e tampa do filtro (grade com furos).
import random
from PIL import Image, ImageDraw
random.seed(3)
D = 'material/producao/personagens/luan/texturas/'
def ruido(im, a):
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r = random.randint(-a, a); c = px[x, y]; px[x, y] = tuple(max(0, min(255, v + r)) for v in c[:3])
    return im
# placa: 64x64, tile
im = Image.new('RGB', (64, 64), (40, 40, 44)); d = ImageDraw.Draw(im)
d.rectangle((0, 0, 63, 63), outline=(62, 62, 68)); d.line((0, 63, 63, 63), fill=(22, 22, 25)); d.line((63, 0, 63, 63), fill=(22, 22, 25))
d.line((2, 1, 61, 1), fill=(74, 74, 80))
for (x, y) in ((5, 5), (58, 5), (5, 58), (58, 58)): d.rectangle((x - 1, y - 1, x + 1, y + 1), fill=(86, 86, 92)); d.point((x + 1, y + 1), fill=(20, 20, 22))
d.line((8, 32, 56, 32), fill=(26, 26, 29)); d.line((8, 33, 56, 33), fill=(58, 58, 64))
ruido(im, 5).save(D + 'armadura.png')
# máscara: borracha
im = Image.new('RGB', (64, 64), (30, 30, 33)); d = ImageDraw.Draw(im)
for y in (12, 40): d.line((0, y, 63, y), fill=(20, 20, 22)); d.line((0, y + 1, 63, y + 1), fill=(44, 44, 48))
d.line((32, 0, 32, 63), fill=(22, 22, 24))
ruido(im, 6).save(D + 'mascara.png')
# filtro: tampa com grade de furos
im = Image.new('RGB', (64, 64), (34, 34, 37)); d = ImageDraw.Draw(im)
d.ellipse((2, 2, 61, 61), fill=(46, 46, 50), outline=(70, 70, 76))
for y in range(14, 52, 7):
    for x in range(14, 52, 7):
        if (x - 32) ** 2 + (y - 32) ** 2 < 19 ** 2: d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(10, 10, 12))
ruido(im, 4).save(D + 'filtro.png'); print('ok')
