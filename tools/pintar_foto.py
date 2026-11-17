"""Prepara a foto pro rosto: pele lisa (sem poro/granulado), cor menos avermelhada, olhos e boca nítidos.
Uso: pintar_foto.py foto.jpg saida.png"""
import sys
from PIL import Image, ImageFilter, ImageEnhance
ENT, SAI = sys.argv[1:3]
im = Image.open(ENT).convert('RGB')
p = im.filter(ImageFilter.MedianFilter(3)).filter(ImageFilter.GaussianBlur(0.7))
p = ImageEnhance.Color(p).enhance(0.82)
r, g, b = p.split(); r = r.point(lambda v: int(v * 0.95)); p = Image.merge('RGB', (r, g, b))   # tira o vermelho do pôster
p = ImageEnhance.Contrast(p).enhance(1.05)
p.save(SAI)
