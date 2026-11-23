# Escudo da camisa do Luan (Atlético-MG, como na camisa enviada pelo diretor): escudo com listras pretas e brancas, faixa com
# "CAM" e a estrela em cima, contorno dourado (cor da camisa). Pixel art 64 px (PS1). Uso fan-made.
# Saída: material/producao/personagens/luan/texturas/escudo_cam.png
import os
from PIL import Image, ImageDraw, ImageFont
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(RAIZ, 'material/producao/personagens/luan/texturas'); os.makedirs(OUT, exist_ok=True)
N = 256; FUNDO, OURO, PRETO, BRANCO = (22, 22, 24), (196, 150, 72), (18, 18, 18), (238, 238, 232)
im = Image.new('RGB', (N, N), FUNDO); d = ImageDraw.Draw(im)
esc = [(40, 70), (216, 70), (216, 150), (128, 246), (40, 150)]           # escudo
d.polygon(esc, fill=OURO)
dentro = [(52, 82), (204, 82), (204, 148), (128, 230), (52, 148)]
d.polygon(dentro, fill=PRETO)
for k in range(6):                                                      # listras pretas e brancas
    x0 = 52 + k * 26
    if k % 2: d.rectangle((x0, 118, x0 + 25, 240), fill=BRANCO)
mask = Image.new('L', (N, N), 0); ImageDraw.Draw(mask).polygon(dentro, fill=255)
fundo_esc = Image.new('RGB', (N, N), PRETO); fd = ImageDraw.Draw(fundo_esc)
for k in range(6):
    if k % 2: fd.rectangle((52 + k * 26, 118, 52 + k * 26 + 25, 240), fill=BRANCO)
im.paste(fundo_esc, (0, 0), mask)
d.polygon(esc, outline=OURO, width=10)
d.rectangle((52, 82, 204, 116), fill=PRETO); d.line((52, 116, 204, 116), fill=OURO, width=5)   # faixa de cima
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
d.text((128, 99), 'C A M', fill=BRANCO, font=f, anchor='mm')
cx, cy, r1, r2 = 128, 38, 26, 11                                         # estrela
import math
pts = [(cx + (r1 if i % 2 == 0 else r2) * math.sin(math.pi * i / 5), cy - (r1 if i % 2 == 0 else r2) * math.cos(math.pi * i / 5)) for i in range(10)]
d.polygon(pts, fill=OURO)
im = im.resize((64, 64), Image.LANCZOS).point(lambda v: (v // 8) * 8)
im.save(os.path.join(OUT, 'escudo_cam.png')); im.resize((256, 256), Image.NEAREST).save(os.path.join(OUT, 'escudo_cam_preview.png')); print('ok')
