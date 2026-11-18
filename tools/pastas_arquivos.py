"""Fichas das pastas (Plano 12): papel envelhecido, foto com faixa preta nos olhos (estilo procurado/confidencial),
campos datilografados, carimbo. Gera a ficha em alta e a textura PS1 (256x192, 15 bits + pontilhado).
uso: python3 tools/pastas_arquivos.py"""
import os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R = 'material/cenarios/sala-igor/ref/pastas/'; OUT = 'material/cenarios/sala-igor/pastas/'; os.makedirs(OUT, exist_ok=True)
MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'; SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FICHAS = [
 ('piolho', 'PIOLHO', [('IDADE', '??'), ('CLASSE', 'SIMULADOR'), ('POTENCIAL', '67%')], (222, 182, 400, 262), -12),
 ('roraima', 'RORAIMA', [('IDADE', '16-17 ANOS'), ('CLASSE', 'SIMULADOR'), ('POTENCIAL', 'VAGABUNDO')], (175, 212, 525, 335), 0),
 ('jv', 'JV', [('IDADE', '17 ANOS'), ('CUIDADO', 'GAY GULOSO')], (262, 190, 450, 280), 8),
 ('phantom', 'PHANTOM', [('IDADE', '19 ANOS'), ('POTENCIAL', '100%')], (110, 250, 480, 350), -6),
]
def psx(im, W, H):
    im = im.resize((W, H), Image.LANCZOS); P = im.load()
    B = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
    for y in range(H):
        for x in range(W):
            d = (B[y % 4][x % 4] / 16 - .5) * 8; P[x, y] = tuple(max(0, min(255, (int(c + d) >> 3) << 3)) for c in P[x, y])
    return im
for chave, nome, campos, olho, ang in FICHAS:
    random.seed(chave)
    W, H = 1200, 900
    pap = Image.new('RGB', (W, H), (214, 200, 168)); d = ImageDraw.Draw(pap)
    for _ in range(4000):   # manchas e textura do papel
        x, y = random.randint(0, W), random.randint(0, H); c = random.randint(-22, 10)
        d.point((x, y), fill=(214 + c, 200 + c, 168 + c))
    pap = pap.filter(ImageFilter.GaussianBlur(1.2)); d = ImageDraw.Draw(pap)
    d.rectangle((0, 0, W, 70), fill=(30, 40, 34)); d.text((30, 14), 'TOCA DO ANÃO  //  ARQUIVO DE MEMBROS', font=ImageFont.truetype(MONO, 34), fill=(57, 255, 106))
    d.text((W - 260, 18), 'Nº %04d' % random.randint(1, 9999), font=ImageFont.truetype(MONO, 30), fill=(160, 220, 170))
    # foto com faixa nos olhos
    f = Image.open(R + chave + '.jpg').convert('RGB'); s = min(f.size); f = f.crop((0, 0, s, s)) if f.size[0] != f.size[1] else f
    fd = ImageDraw.Draw(f)
    x0, y0, x1, y1 = olho; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    barra = Image.new('RGBA', (int((x1 - x0) * 1.15), int(y1 - y0)), (8, 8, 8, 255)).rotate(ang, expand=True)
    f.paste(barra, (int(cx - barra.width / 2), int(cy - barra.height / 2)), barra)
    f = f.resize((440, 440)); foto = Image.new('RGB', (470, 470), (240, 236, 226)); foto.paste(f, (15, 15))
    foto = foto.rotate(random.uniform(-3, 3), expand=True, fillcolor=(214, 200, 168)); pap.paste(foto, (50, 140))
    d.rectangle((150, 120, 260, 150), fill=(150, 150, 150))   # clipe
    d.text((50, 640), nome, font=ImageFont.truetype(SANS, 92), fill=(28, 26, 24))
    y = 160
    for k, v in campos:
        d.text((580, y), k + ':', font=ImageFont.truetype(MONO, 38), fill=(70, 60, 50))
        d.text((580, y + 48), v, font=ImageFont.truetype(MONO, 58 if len(v) < 12 else 46), fill=(20, 20, 20)); y += 150
    # carimbo
    car = Image.new('RGBA', (520, 130), (0, 0, 0, 0)); cd = ImageDraw.Draw(car)
    txt = 'PROCURADO' if chave != 'phantom' else 'PRIORIDADE'
    cd.rectangle((4, 4, 515, 125), outline=(170, 20, 24, 220), width=8); cd.text((26, 24), txt, font=ImageFont.truetype(SANS, 70), fill=(170, 20, 24, 220))
    car = car.rotate(random.uniform(8, 16), expand=True); pap.paste(car, (600, 640), car)
    pap.save(OUT + chave + '_ficha.png')
    psx(pap, 256, 192).save(OUT + chave + '_psx_256.png'); print('ok', chave)
c = Image.new('RGB', (2 * 768, 2 * 576), (12, 14, 12))
for i, (chave, *_ ) in enumerate(FICHAS):
    c.paste(Image.open(OUT + chave + '_psx_256.png').resize((768, 576), Image.NEAREST), ((i % 2) * 768, (i // 2) * 576))
c.save(OUT + 'previa_pastas.jpg', quality=92)
