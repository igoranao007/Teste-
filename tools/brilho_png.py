# Bloom simples (PIL) nas partes acesas de um render: pega o que é amarelo/claro saturado, desfoca e soma. Uso: brilho_png.py arquivos...
import sys
from PIL import Image, ImageFilter, ImageChops
import numpy as np
for f in sys.argv[1:]:
    im = Image.open(f).convert('RGB'); a = np.asarray(im).astype(np.float32)
    m = ((a[..., 0] > 170) & (a[..., 1] > 120) & (a[..., 0] - a[..., 2] > 70)).astype(np.float32)[..., None] * a
    g = Image.fromarray(m.astype('uint8'))
    b = np.asarray(g.filter(ImageFilter.GaussianBlur(6))).astype(np.float32) * 0.9 + np.asarray(g.filter(ImageFilter.GaussianBlur(18))).astype(np.float32) * 0.7
    Image.fromarray(np.clip(a + b, 0, 255).astype('uint8')).save(f)
