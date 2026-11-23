# Textura de cabelo "meio enrolado" do Luan (pixel art 128 px, tile): base castanho-escuro com cachos (arcos claros) e fundos escuros.
import random, math
from PIL import Image, ImageDraw
random.seed(11); N = 128
im = Image.new('RGB', (N, N), (28, 21, 17)); d = ImageDraw.Draw(im)
for _ in range(900):
    x, y = random.randint(0, N - 1), random.randint(0, N - 1); d.point((x, y), fill=random.choice([(18, 13, 11), (36, 27, 21)]))
for _ in range(230):
    x, y = random.uniform(0, N), random.uniform(0, N); r = random.uniform(2.5, 5)
    a0 = random.uniform(0, 360); cor = random.choice([(62, 46, 36), (74, 56, 44), (52, 39, 30)])
    for dx in (-N, 0, N):
        for dy in (-N, 0, N):
            d.arc((x + dx - r, y + dy - r, x + dx + r, y + dy + r), a0, a0 + 200, fill=cor, width=1)
            d.arc((x + dx - r + 1, y + dy - r + 1, x + dx + r + 1, y + dy + r + 1), a0 + 200, a0 + 330, fill=(14, 10, 9), width=1)
im.save('material/producao/personagens/luan/texturas/cachos.png'); print('ok')
