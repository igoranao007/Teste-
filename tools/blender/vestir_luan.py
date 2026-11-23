# LUAN GORDO (executado dentro do vestir_personagem.py, PERSONAGEM=luan) — aliado do DOM, 15 anos, gordo, pele "branco queimado",
# cabelo escuro meio cacheado, óculos, MÁSCARA DE GÁS (metade de baixo do rosto, filtros de aro amarelo aceso) e a CAMISA DO
# ATLÉTICO-MG da imagem enviada (preta com padrão escuro em "V", 3 listras douradas nos ombros, debrum dourado, gola em V dourada,
# escudo CAM). Calça e coturnos pretos BLINDADOS com frisos de energia amarela (tecnologia do DOM), braçadeiras e luvas táticas.
# Cabeça: tools/luan_cabeca.py (malha + textura). Materiais com "brilho" no nome = luz própria no motor (lib/modelo.js).
import numpy as np
LD = os.path.join(RAIZ, 'material/producao/personagens/luan'); LTX = os.path.join(LD, 'texturas')
V = 3
TX = afinar_corpo(kt=(1.34, 1.5), ka=1.28, kc=1.3, kn=1.15)       # GORDO: tronco largo e barrigudo, braços e coxas grossos
for v in bm0.verts:                                                # BARRIGA: volume redondo na frente (mais embaixo do peito), papada nas costas não
    p = W(v.co)
    if 0.95 < p.z < 1.5 and abs(p.x) < .32 and p.y < .02:
        k = math.exp(-((p.z - 1.2) / .16) ** 2) * max(0, 1 - (p.x / .3) ** 2)
        v.co = MWi @ (p + Vector((p.x * .15 * k, -.085 * k, -.015 * k)))
bm0.normal_update()
OURO, AMARELO = '#c49648', '#ffc21a'
PELE_L = (206, 166, 136)
def mt(nome, w, h, fn, rep=True): material(nome, textura(nome, w, h, fn), repete=rep)
def camisa_cam(x, y, w, h):                                        # preto com o padrão em "V" grafite da camisa (chevrons em colunas)
    col = x // 8; yy = (y + abs((x % 8) - 4)) % 6
    c = hx('#1b1b1d') if col % 2 else hx('#202023')
    if yy in (0, 1): c = mix(c, hx('#3c3c42'), .7)
    return mix(c, hx('#000000'), .15 * ruido(x // 2, y // 2, 501))
mt('l_camisa', 64, 64, camisa_cam)
mt('l_ouro', 8, 8, lambda x, y, w, h: mix(hx(OURO), hx('#e0b860'), .4 * ruido(x, y, 502)))
mt('l_listras', 16, 16, lambda x, y, w, h: hx(OURO) if (y % 6) in (1, 2) else hx('#1b1b1d'))   # 3 listras douradas
escudo = bpy.data.images.load(os.path.join(LTX, 'escudo_cam.png')); escudo.pack(); material('l_escudo', escudo, repete=False)
mt('l_calca', 64, 64, lambda x, y, w, h: mix(hx('#151517'), hx('#26262a'), .5 * ruido(x // 2, y // 2, 503)) if (x + y) % 7 else hx('#0f0f11'))
mt('l_placa', 64, 64, lambda x, y, w, h: (mix(hx('#121214'), hx('#2a2a2f'), .45 + .55 * ruido(x // 3, y // 3, 504)) if x % 16 not in (0, 15) and y % 16 not in (0, 15) else hx('#0d0d0e')))
mt('l_brilho', 8, 8, lambda x, y, w, h: mix(hx(AMARELO), hx('#fff1a8'), .35 if (x + y) % 3 == 0 else 0))
mt('l_sola', 16, 16, lambda x, y, w, h: hx('#0a0a0b') if (x + y) % 5 < 2 else hx('#1c1c1e'))
mt('l_luva', 32, 32, lambda x, y, w, h: mix(hx('#141416'), hx('#2e2e33'), .5 * ruido(x // 2, y // 2, 505) ** 2) if y % 8 else hx('#0c0c0d'))
mt('l_pele', 16, 16, lambda x, y, w, h: mix(tuple(int(c * .9) for c in PELE_L), PELE_L, .6 + .4 * ruido(x // 2, y // 2, 506)))

# ================================================================== CAMISA do Atlético-MG (manga curta, gola em V dourada)
MANGA_L = COTOVELO.x - .03
bm = extrair(lambda f: REG[f.index] == 'camisa'); manga_curta(bm, MANGA_L); afastar(bm, .012)
for f in bm.faces: f.material_index = 0
gola = bordas(bm, lambda e: all(W(v.co).z > 1.62 and abs(W(v.co).x) < .14 for v in e.verts))
GOLA = []
if gola:                                                           # gola em V: a frente desce num "V" e ganha um filete dourado
    vs = extrudar_borda(bm, gola, (0, 0, .012)); GOLA += extrudar_borda.faces
    for v in vs:
        p = W(v.co)
        if p.y < 0: v.co = MWi @ Vector((p.x, p.y, p.z - .07 * max(0, 1 - abs(p.x) / .07)))
for v in bm.verts:                                                 # o decote da frente desce em V
    p = W(v.co)
    if p.y < -.02 and p.z > 1.6 and abs(p.x) < .08: v.co = MWi @ Vector((p.x, p.y, p.z - .06 * (1 - abs(p.x) / .08)))
for f in GOLA: f.material_index = 1
eh_braco = lambda f: dono(f).startswith(('upper_arm', 'forearm'))
for s in (1, -1):
    faixa_costura(bm, lambda f, s=s: eh_braco(f) and centro(f).x * s > 0, (s * (MANGA_L - .012), 0, 0), (1, 0, 0), 1, larg=.012)   # punho dourado
    faixa_costura(bm, lambda f, s=s: tronco(f) and centro(f).x * s > 0 and abs(normal(f).x) > .55, (s * TX, 0, 0), (0, 1, 0), 1, larg=.008)   # debrum lateral
    for yy in (-.018, 0, .018):                                    # 3 listras douradas em cima do ombro e da manga
        faixa_costura(bm, lambda f, s=s: (eh_braco(f) or dono(f).startswith('shoulder')) and centro(f).x * s > .08 and normal(f).z > .55, (0, yy, 0), (0, 1, 0), 1, larg=.008)
camisa = objeto(bm, 'camisa', ['l_camisa', 'l_ouro'], mat_de=lambda f: f.material_index, dens=5)
for p_ in camisa.data.polygons: p_.use_smooth = True
SUP = bvh_de([camisa])
hit = raio(SUP, Vector((.09 * TX / .2, -.2, 1.5)), F_)              # ESCUDO no peito esquerdo (relevo bordado)
b_ = bolsa_em(hit or Vector((.12, -.3, 1.5)), F_, C_, .075, .085, .006, nx=2, nz=2); pesar(b_)
so_tronco(objeto(b_, 'escudo', ['l_escudo'], uv=False), ['spine.002', 'spine.003'])
# ================================================================== CALÇA blindada + JOELHEIRAS/CANELEIRAS + CINTO + COTURNOS
bm = extrair(lambda f: REG[f.index] == 'calca'); afastar(bm, .015)
barra = bordas(bm, lambda e: all(abs(W(v.co).z - BOTA) < .01 for v in e.verts))
if barra: extrudar_borda(bm, barra, (0, 0, -.03))
for f in bm.faces: f.material_index = 0
perna = lambda f: f.is_valid and dono(f).startswith(('thigh', 'shin'))
for s in (1, -1):
    faixa_costura(bm, lambda f, s=s: perna(f) and centro(f).x * s > 0 and normal(f).y < -.4, (s * .11, 0, 0), (1, 0, 0), 1, larg=.009)   # friso de energia na frente da coxa
calca = objeto(bm, 'calca', ['l_calca', 'l_brilho'], mat_de=lambda f: f.material_index)
for p_ in calca.data.polygons: p_.use_smooth = True
for s in (1, -1):
    for (z0, z1, nome, af, esp_) in ((JOELHO + .12, QUADRIL - .06, 'coxa', .03, .02), (JOELHO - .06, JOELHO + .07, 'joelheira', .045, .03), (BOTA + .02, JOELHO - .07, 'caneleira', .03, .02)):
        bm = extrair(lambda f, s=s, z0=z0, z1=z1: REG[f.index] == 'calca' and centro(f).x * s > 0 and z0 < centro(f).z < z1 and normal(f).y < .2)
        if not bm.faces: continue
        afastar(bm, af); espessura(bm, bm.faces[:], esp_)
        for f in bm.faces: f.material_index = 0
        faixa_costura(bm, lambda f: f.is_valid and normal(f).y < -.4, (0, 0, (z0 + z1) / 2), (0, 0, 1), 1, larg=.009)
        objeto(bm, nome, ['l_placa', 'l_brilho'], mat_de=lambda f: f.material_index, dens=6)
bm = extrair(lambda f: REG[f.index] == 'calca'); afastar(bm, .015)
cortar(bm, (0, 0, CINTURA - .05), (0, 0, 1))
bmesh.ops.delete(bm, geom=[f for f in bm.faces if not (CINTURA - .05 < centro(f).z < CINTURA + .001)], context='FACES')
afastar(bm, .012); espessura(bm, bm.faces[:], .012)
for f in bm.faces: f.material_index = 0
for x in (-.03, .03): cortar(bm, (x, 0, 0), (1, 0, 0))
for f in extrudar(bm, [f for f in bm.faces if normal(f).y < -.7 and abs(centro(f).x) < .03 and centro(f).y < 0], .012): f.material_index = 1
so_tronco(objeto(bm, 'cinto', ['l_placa', 'l_brilho'], mat_de=lambda f: f.material_index, dens=8), ['spine', 'spine.001'])
bm = extrair(lambda f: REG[f.index] == 'bota'); afastar(bm, .022)
for v in bm.verts:
    p = W(v.co)
    if p.z < 0: v.co = MWi @ Vector((p.x, p.y, 0.0))
cortar(bm, (0, 0, .03), (0, 0, 1))
cano = bordas(bm, lambda e: all(abs(W(v.co).z - BOTA) < .01 for v in e.verts))
if cano: extrudar_borda(bm, cano, (0, 0, .025))
for f in bm.faces: f.material_index = 2 if centro(f).z < .03 else 0
for f in bm.faces:
    if f.material_index == 0 and normal(f).y < -.5 and .05 < centro(f).z < .09: f.material_index = 1
objeto(bm, 'coturno', ['l_placa', 'l_brilho', 'l_sola'], mat_de=lambda f: f.material_index, dens=8)
# ================================================================== BRAÇADEIRAS + LUVAS táticas (antebraço à mostra entre a manga e a braçadeira)
for s in (1, -1):
    bm = extrair(lambda f, s=s: REG[f.index] == 'camisa' and eh_braco(f) and PULSO - .14 < centro(f).x * s < PULSO - .01)
    afastar(bm, .018); espessura(bm, bm.faces[:], .015)
    for f in bm.faces: f.material_index = 0
    faixa_costura(bm, lambda f: f.is_valid and normal(f).z > .3, (s * (PULSO - .075), 0, 0), (1, 0, 0), 1, larg=.01)
    objeto(bm, 'bracadeira', ['l_placa', 'l_brilho'], mat_de=lambda f: f.material_index, dens=8)
bm = extrair(lambda f: REG[f.index] == 'luva'); afastar(bm, .008)
for f in bm.faces: f.material_index = 0
objeto(bm, 'luva', ['l_luva'], dens=8)
V = 1
# o corpo fica só com os ANTEBRAÇOS de fora (manga curta), na cor da pele
corpo_visivel(lambda f: dono(f).startswith(('forearm', 'upper_arm')) and abs(centro(f).x) > MANGA_L + .005 and REG[f.index] != 'luva', 'l_pele')

# ================================================================== CABEÇA (tools/luan_cabeca.py): rosto, cabelo cacheado, óculos e máscara
TEXD = LTX
def img_png(n): i = bpy.data.images.load(os.path.join(TEXD, n)); i.pack(); return i
material('l_rosto', img_png('rosto_v2.png'), repete=False)
material('l_cabelo', img_png('cabelo_v2.png'))
mt('l_armacao', 8, 8, lambda x, y, w, h: mix(hx('#0c0c0d'), hx('#2a2a2c'), .3 * ruido(x, y, 507)))
mt('l_lente', 16, 16, lambda x, y, w, h: hx('#9fb4c0') if (x - y) in (3, 4) else mix(hx('#3a4650'), hx('#56646e'), y / 15))
mt('l_mascara', 32, 32, lambda x, y, w, h: mix(hx('#121214'), hx('#2a2a2e'), .4 * ruido(x // 2, y // 2, 508)) if (x + y) % 9 else hx('#0a0a0b'))
def filtro_f(x, y, w, h):                                          # tampa do filtro: aro amarelo aceso, centro escuro com furos
    d = math.hypot(x - w / 2 + .5, y - h / 2 + .5) / (w / 2)
    if d > .72: return hx(AMARELO)
    if (x + y) % 4 == 0: return hx('#3a3a3e')
    return hx('#151517')
mt('l_filtro_brilho', 16, 16, filtro_f, rep=False)
mt('l_filtro', 16, 16, lambda x, y, w, h: mix(hx('#1a1a1c'), hx('#34343a'), .5 if y % 4 == 0 else .1))
CJ = json.load(open(os.path.join(TEXD, 'cabeca.json')))
def peca_json(nome, i0, i1, mats, mat_de):
    bm = bmesh.new(); uvl = bm.loops.layers.uv.verify(); mapa = {}
    for i in range(i0, i1):
        f = CJ['f'][i]
        for v in f:
            if v not in mapa: mapa[v] = bm.verts.new(MWi @ Vector(CJ['v'][v]))
        try: face = bm.faces.new([mapa[v] for v in f])
        except ValueError: continue
        face.material_index = mat_de(CJ['mat'][i])
        for l, uv in zip(face.loops, CJ['uv'][i]): l[uvl].uv = uv
    bm.normal_update(); bm.verts.index_update(); inv = {b.index: k for k, b in mapa.items()}
    ob = objeto(bm, nome, mats, mat_de=lambda f: f.material_index, uv=False)
    for v in ob.data.vertices:
        for osso_, w in CJ['peso'][inv[v.index]].items(): ob.vertex_groups[osso_].add([v.index], w, 'REPLACE')
    return ob
a, b = CJ['pecas']['cabeca']; peca_json('cabeca', a, b, ['l_rosto'], lambda m: 0)
a, b = CJ['pecas']['cabelo']; peca_json('cabelo', a, b, ['l_cabelo'], lambda m: 0)
a, b = CJ['pecas']['acessorios']; peca_json('oculos_mascara', a, b, ['l_armacao', 'l_lente', 'l_mascara', 'l_filtro_brilho', 'l_filtro'], lambda m: {3: 0, 4: 1, 5: 2, 6: 3, 7: 4}[m])
for m in MATS.values(): m.use_backface_culling = True
