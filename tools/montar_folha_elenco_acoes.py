# Junta os quadros de tools/blender/folha_elenco_acoes.py: uma linha por personagem, uma coluna por ação, com o resultado do QA.
# Uso: python3 tools/montar_folha_elenco_acoes.py pasta "pre1:Nome 1:qa1.json,pre2:Nome 2:qa2.json" "rotulo1,rotulo2,..." saida.jpg "TÍTULO"
import sys, os, json, glob
from PIL import Image, ImageDraw, ImageFont
P, LIN, ROT, OUT, TIT = sys.argv[1:6]
F = lambda t: ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', t)
linhas = [x.split(':') for x in LIN.split(',')]; rot = ROT.split(',')
W, H, ESQ = 240, 320, 230
fo = Image.new('RGB', (ESQ + len(rot) * (W + 4) + 10, 110 + len(linhas) * (H + 8)), (16, 16, 18)); d = ImageDraw.Draw(fo)
d.text((16, 14), TIT, font=F(34), fill=(240, 196, 50))
for j, r in enumerate(rot): d.text((ESQ + j * (W + 4) + 6, 72), r, font=F(17), fill=(200, 200, 200))
for i, (pre, nome, qa) in enumerate(linhas):
    y = 104 + i * (H + 8)
    q = json.load(open(qa)) if os.path.exists(qa) else {}
    ok = sum(1 for v in q.values() if not v.get('problemas')); tot = len(q)
    d.text((14, y + 10), nome, font=F(24), fill=(240, 240, 240))
    d.text((14, y + 46), f'QA: {ok}/{tot} ok', font=F(18), fill=(120, 220, 120) if ok >= tot - 2 else (240, 150, 90))
    ruins = [k for k, v in q.items() if v.get('problemas')]
    for k, nm in enumerate(ruins[:8]): d.text((14, y + 76 + k * 22), '· ' + nm, font=F(15), fill=(240, 150, 90))
    for j in range(len(rot)):
        f = glob.glob(f'{P}/{pre}__{j:02d}__*.png')
        if f: fo.paste(Image.open(f[0]).convert('RGB').resize((W, H)), (ESQ + j * (W + 4), y))
fo.save(OUT, quality=90); print('ok', OUT, fo.size)
