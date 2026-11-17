"""Textura crespa (black power): bolinhas/cachos pequenos pretos com leve brilho castanho. Uso: pintar_crespo.py saida.png"""
import sys, random
from PIL import Image, ImageDraw, ImageFilter
random.seed(11); N = 256
im = Image.new('RGB', (N, N), (14, 11, 10)); d = ImageDraw.Draw(im)
for _ in range(2600):
    x, y, r = random.randint(0, N), random.randint(0, N), random.randint(1, 3)
    c = random.choice([(26, 20, 17), (34, 26, 21), (8, 7, 7), (44, 33, 26)])
    d.ellipse((x - r, y - r, x + r, y + r), outline=c, width=1)
im = im.filter(ImageFilter.SMOOTH); im.save(sys.argv[1]); print('ok')
