# Costas da camisa do Atlético-MG a partir da própria foto (referencia/camisa_atletico.jpg): entre os debruns dourados
# da parte de cima, o padrão é trocado pelo de 300 px abaixo (mesmas colunas, período vertical ~300 px) — some gola em V,
# escudo e logo; ombros/listras e debruns ficam. Gola redonda preta com filete dourado. Saída: texturas/camisa_costas.png
from PIL import Image, ImageDraw
import numpy as np
D = 'material/producao/personagens/luan/'
im = Image.open(D + 'referencia/camisa_atletico.jpg').convert('RGB'); a = np.asarray(im).astype(int); b = a.copy()
ouro = (a[:, :, 0] > 140) & (a[:, :, 0] - a[:, :, 2] > 45)
def borda(y):                                                         # debrum raglan (lado esquerdo da foto), medido à mão
    pts = [(20, 312), (40, 296), (70, 250), (100, 224), (150, 210), (300, 204)]
    for (y0, x0), (y1, x1) in zip(pts, pts[1:]):
        if y0 <= y <= y1: return x0 + (x1 - x0) * (y - y0) / (y1 - y0)
    return 204
for y in range(20, 300):
    L = int(borda(y)) + 4; R = 736 - L
    b[y, L:R] = a[y + 300, L:R]
out = Image.fromarray(b.astype('uint8')); d = ImageDraw.Draw(out)
d.chord((262, -40, 474, 62), 0, 180, fill=(26, 26, 28)); d.arc((262, -40, 474, 62), 0, 180, fill=(196, 150, 72), width=5)
out.save(D + 'texturas/camisa_costas.png'); print('ok')
