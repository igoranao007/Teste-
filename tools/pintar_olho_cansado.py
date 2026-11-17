"""Textura do olho cansado (estilo da referência): branco, pálpebra azul com linha reta e lisa, íris verde pequena
encostada embaixo da pálpebra olhando de lado. u=0 lado de fora, u=1 lado do nariz; v=0 embaixo.
Uso: pintar_olho_cansado.py saida.png [altura_palpebra 0..1]"""
import sys
from PIL import Image, ImageDraw
OUT = sys.argv[1]; LID = float(sys.argv[2]) if len(sys.argv) > 2 else 0.52
S = 4; N = 128 * S
im = Image.new('RGB', (N, N), (232, 228, 214)); d = ImageDraw.Draw(im)
def Y(v): return N - v * N
# íris + pupila (olhando pro lado do nariz, um pouco pra cima)
cx, cy, r = 0.60 * N, Y(LID - 0.08), float(__import__('os').environ.get('IRIS', '0.14')) * N
d.ellipse((cx - r, cy - r * 1.25, cx + r, cy + r * 1.25), fill=(30, 140, 60))
d.ellipse((cx - r * 0.55, cy - r * 0.8, cx + r * 0.55, cy + r * 0.8), fill=(8, 10, 8))
d.ellipse((cx - r * 0.55, cy - r * 0.95, cx - r * 0.15, cy - r * 0.55), fill=(240, 240, 240))   # brilho
# pálpebra: tudo acima de uma linha quase reta (cai um pouquinho pro lado de fora)
y_fora, y_dentro = Y(LID - 0.03), Y(LID + 0.02)
d.polygon([(0, 0), (N, 0), (N, y_dentro), (0, y_fora)], fill=(52, 70, 130))
d.line([(0, y_fora), (N, y_dentro)], fill=(22, 28, 58), width=3 * S)            # borda escura da pálpebra
d.line([(0, y_fora - 6 * S), (N, y_dentro - 6 * S)], fill=(70, 92, 160), width=2 * S)  # dobra clara
im.resize((128, 128), Image.LANCZOS).save(OUT); print('ok', OUT)
