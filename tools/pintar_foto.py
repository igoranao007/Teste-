"""Transforma a foto em 'pintura de jogo' leve: tira poro/granulado (pele lisa), junta cores em tons chapados,
mantém olho, sobrancelha e boca. Uso: pintar_foto.py foto.jpg saida.png [cores]"""
import sys
from PIL import Image, ImageFilter, ImageEnhance
ENT, SAI = sys.argv[1:3]; NC = int(sys.argv[3]) if len(sys.argv) > 3 else 64
im = Image.open(ENT).convert('RGB')
p = im.filter(ImageFilter.MedianFilter(3)).filter(ImageFilter.MedianFilter(3))
p = p.filter(ImageFilter.GaussianBlur(0.8))
p = ImageEnhance.Contrast(p).enhance(1.08)
q = p.quantize(colors=NC, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB')
Image.blend(q, p, 0.35).save(SAI)
