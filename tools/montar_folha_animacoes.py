# Junta os quadros de tools/blender/folha_animacoes.py numa folha (linha = ação, 4 quadros) com o nome e o resultado do QA.
# Uso: python3 tools/montar_folha_animacoes.py pasta_quadros qa.json saida.jpg "TÍTULO"
import sys, os, json, glob
from PIL import Image, ImageDraw, ImageFont
P, QA, OUT, TIT = sys.argv[1:5]
qa = json.load(open(QA)) if os.path.exists(QA) else {}
F = lambda t: ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', t)
acoes = sorted({os.path.basename(f).split('__')[0] for f in glob.glob(P + '/*__0.png')})
W, H, COL = 150, 210, 2          # 2 ações por linha
lin = (len(acoes) + COL - 1) // COL
fo = Image.new('RGB', (COL * (4 * W + 200) + 20, 70 + lin * (H + 6)), (16, 16, 18)); d = ImageDraw.Draw(fo)
d.text((16, 14), TIT, font=F(34), fill=(240, 196, 50))
for i, a in enumerate(acoes):
    x0 = 10 + (i % COL) * (4 * W + 200); y0 = 66 + (i // COL) * (H + 6)
    pr = qa.get(a, {}).get('problemas', []); cor = (120, 220, 120) if not pr else (240, 110, 90)
    d.text((x0, y0 + 6), a.replace('u_', '').replace('m_', ''), font=F(17), fill=(230, 230, 230))
    d.text((x0, y0 + 30), 'OK' if not pr else 'ATENÇÃO', font=F(16), fill=cor)
    for k, t in enumerate(pr[:3]): d.text((x0, y0 + 52 + 20 * k), t[:26], font=F(12), fill=cor)
    for k in range(4):
        p = f'{P}/{a}__{k}.png'
        if os.path.exists(p): fo.paste(Image.open(p).convert('RGB').resize((W, H)), (x0 + 190 + k * W, y0))
fo.save(OUT, quality=88); print(OUT, fo.size)
