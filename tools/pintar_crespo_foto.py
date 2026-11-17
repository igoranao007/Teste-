"""Textura crespa estilo 'foto pixelada' (como os jogos do Puppet Combo): cachinhos castanho-escuros com
brilho castanho-claro e sombra, depois reduzida e ampliada sem filtro. Uso: pintar_crespo_foto.py saida.png"""
import sys, random
from PIL import Image, ImageDraw, ImageFilter
random.seed(21); N = 512
im = Image.new('RGB', (N, N), (20, 14, 10)); d = ImageDraw.Draw(im)
for _ in range(9000):
    x, y, r = random.randint(0, N), random.randint(0, N), random.randint(2, 6)
    t = random.random()
    c = (int(30 + 70 * t), int(20 + 45 * t), int(12 + 28 * t))
    d.arc((x - r, y - r, x + r, y + r), random.randint(0, 360), random.randint(0, 360) + 200, fill=c, width=2)
im = im.filter(ImageFilter.GaussianBlur(0.8)).resize((96, 96), Image.BOX).resize((256, 256), Image.NEAREST)
im.save(sys.argv[1]); print('ok')
