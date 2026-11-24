# Emblema PRÓPRIO do grupo do Dom — "Toca do Anão" (小人の隠れ家): porta em arco de toca com luz saindo, 3 pedras no alto,
# dentro de um hexágono dourado com filete. Desenho original do projeto (não é símbolo de nenhuma obra).
# Saídas: texturas/emblema.png (128, pra placa acesa) e emblema_capa.png (256, bordado pras costas do capote).
import math
from PIL import Image, ImageDraw
D = 'material/producao/personagens/dom/texturas/'
def emblema(N, fundo=(18, 16, 14), transp=False):
    im = Image.new('RGBA', (N, N), (0, 0, 0, 0) if transp else fundo + (255,)); d = ImageDraw.Draw(im)
    c = N / 2; OURO, OURO2, LUZ, LUZ2 = (214, 170, 62, 255), (150, 110, 34, 255), (255, 222, 60, 255), (255, 246, 170, 255)
    hexa = lambda r: [(c + r * math.cos(math.pi / 6 + k * math.pi / 3), c + r * math.sin(math.pi / 6 + k * math.pi / 3)) for k in range(6)]
    d.polygon(hexa(N * .48), fill=OURO2); d.polygon(hexa(N * .44), fill=OURO); d.polygon(hexa(N * .38), fill=(26, 22, 18, 255))
    d.line(hexa(N * .345) + [hexa(N * .345)[0]], fill=LUZ, width=max(1, N // 64))                          # filete aceso
    # porta em arco (a toca): moldura dourada, vão aceso, chão
    w, h = N * .30, N * .34; x0, y1 = c - w / 2, c + N * .2
    d.rectangle((x0 - N * .03, y1 - h * .55, x0 + w + N * .03, y1), fill=OURO); d.pieslice((x0 - N * .03, y1 - h - N * .03, x0 + w + N * .03, y1 - h * .1 + N * .03), 180, 360, fill=OURO)
    d.rectangle((x0, y1 - h * .55, x0 + w, y1), fill=LUZ); d.pieslice((x0, y1 - h, x0 + w, y1 - h * .1), 180, 360, fill=LUZ)
    d.rectangle((c - w * .18, y1 - h * .55, c + w * .18, y1), fill=LUZ2); d.pieslice((c - w * .18, y1 - h * .78, c + w * .18, y1 - h * .32), 180, 360, fill=LUZ2)   # luz mais forte no meio
    d.rectangle((c - N * .25, y1, c + N * .25, y1 + N * .035), fill=OURO)                                                         # chão/degrau
    for k, (dx, dy) in enumerate(((-.12, -.26), (0, -.3), (.12, -.26))):                                                           # 3 pedras (as 3 da toca)
        r = N * (.035 if k != 1 else .045); d.polygon([(c + dx * N, c + dy * N - r), (c + dx * N + r, c + dy * N), (c + dx * N, c + dy * N + r), (c + dx * N - r, c + dy * N)], fill=LUZ)
    return im
e = emblema(128); e.convert('RGB').point(lambda v: (v // 8) * 8).save(D + 'emblema.png')
emblema(256, transp=True).save(D + 'emblema_capa.png'); e.resize((256, 256), Image.NEAREST).save(D + 'emblema_preview.png'); print('ok')
