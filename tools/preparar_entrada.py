# Prepara as texturas da ENTRADA a partir da foto (o rosto é o da pessoa da foto, com autorização): rosto PS1 (128 px de largura,
# cor de 15 bits), mecha de cabelo e cor da pele medida na bochecha/testa. Grava material/producao/personagens/entrada/texturas/.
import json
from PIL import Image, ImageEnhance
D = 'material/producao/personagens/entrada/'
foto = Image.open(D + 'referencia_foto.jpg').convert('RGB')
REC = (380, 0, 1840, 1900)                                         # recorte da cabeça inteira (cabelo, orelha, queixo)
TW = 128; TH = round(TW * (REC[3] - REC[1]) / (REC[2] - REC[0]))
def q(im): return im.point(lambda v: round(v / 8) * 8)
rosto = ImageEnhance.Contrast(foto.crop(REC)).enhance(1.12).resize((TW, TH), Image.LANCZOS)
q(rosto).save(D + 'texturas/rosto.png')
cab = foto.crop((760, 120, 1400, 440)).resize((64, 32), Image.LANCZOS)
q(ImageEnhance.Contrast(cab).enhance(1.25)).save(D + 'texturas/cabelo.png')
def media(box):
    r = foto.crop(box).resize((1, 1), Image.BOX).getpixel((0, 0)); return r
pele = media((1180, 1150, 1360, 1300)); testa = media((900, 680, 1300, 780))
json.dump({'rec': REC, 'tw': TW, 'th': TH, 'pele': pele, 'testa': testa, 'tamanho': foto.size,
           'olhos': [[920, 1040], [1414, 1073]], 'nariz': [1159, 1312], 'boca': [1108, 1517], 'queixo': [1108, 1772], 'linha_cabelo': 630},
          open(D + 'texturas/rosto.json', 'w'), indent=1)
print('ok', TW, TH, pele, testa)
