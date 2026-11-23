# CORSA v2 (executado dentro do vestir_personagem.py, PERSONAGEM=corsa, CORSA=v2). Corpo HUMANOIDE com a cabeça de pardal
# LIMPA (malha nova sobre a digitalização + cores originais transferidas, ver tools/blender/corsa_cabeca.py) e uniforme próprio:
#   jaqueta de campanha marrom-oliva até o meio da coxa (gola virada, carcela de botões, costuras amarelo-oliva, cotoveleiras,
#   platinas, 2 bolsos de peito com aba e botão, 2 bolsos de baixo e 2 laterais na saia) · calça verde-oliva (bolso de coxa só
#   à esquerda, costuras, reforço nos joelhos, barra presa no coturno) · cinto de lona com fivela e passadores por cima da saia ·
#   suspensório em Y · 3 porta-munições na frente, 2 cantis e 1 bolsa de equipamento · luvas bege com palma de couro ·
#   coturno de couro marrom (sola clara + entressola, biqueira, contraforte, cadarço com ilhoses, colarinho).
# Só a CABEÇA é de pardal; o PESCOÇO é humanoide (com as cores da plumagem da garganta/nuca); a gola fica abaixo da cabeça.
import numpy as np
V = 3                                                              # funde faces coplanares no objeto()
CTX = os.path.join(RAIZ, 'material/producao/personagens/corsa/texturas')
TX = afinar_corpo(kt=(.93, .95), ka=.9, kc=.95, kn=.97)            # proporção própria: adulto de porte médio (entre o corpo base e a Entrada)
C_COST = '#a09448'
def mt(nome, w, h, fn, rep=True): material(nome, textura(nome, w, h, fn), repete=rep)
def costura_c(base):
    B = hx(base)
    def f(x, y, w, h):
        c = mix(B, (0, 0, 0), .25)
        if (y in (3, 4) and x % 4 < 2) or (x in (3, 4) and y % 4 < 2): c = mix(hx(C_COST), c, .55)   # pesponto discreto
        return c
    return f
def botoes_c(x, y, w, h):                                          # carcela: faixa dupla com botões a cada 8 px
    c = mix(hx('#54482f'), hx('#5f5238'), .4 * ruido(x, y, 201))
    if x in (0, w - 1): c = hx('#3a3222')
    if y % 8 in (3, 4) and 2 < x < w - 3: c = hx('#2a2a24') if y % 8 == 3 else hx('#4a4a40')
    return c
def bota_c(x, y, w, h):
    c = mix(hx('#4a3020'), hx('#6e4a30'), .55 * ruido(x // 2, y // 2, 202) ** 1.5)
    if y % 16 == 0 or x % 21 == 0: c = hx('#33210f')
    if y % 16 == 2 and x % 2 == 0: c = mix(hx('#8a7a55'), c, .5)
    return c
def cadarco_c(x, y, w, h):
    u = x / (w - 1); c = hx('#5a3c26') if abs(u - .5) < .28 else hx('#6e4a30')
    yy = y % 6
    if abs(u - .5) < .3 and abs((u - .5) * 10) - abs(yy - 3) < 1.2 and abs(u - .5) * 10 > abs(yy - 3) - 1.0: c = hx('#8f7d5a')
    if abs(abs(u - .5) - .3) < .05 and yy == 3: c = hx('#a7a397')
    return c
def luva_c(x, y, w, h):
    c = mix(hx('#8f7c58'), hx('#b09c74'), .5 * ruido(x // 2, y // 2, 203))
    if y % 8 == 0: c = hx('#7a6a4a')
    if x % 8 == 4 and y % 2 == 0: c = mix(hx('#6a5c40'), c, .5)
    return c
# ---- paleta própria: marrom-oliva · verde-oliva · verde-musgo · cáqui · couro marrom · bege · amarelo-oliva
mt('c2_jaqueta', 64, 64, desgaste(tecido('#5f5238', '#403725', '#776a4c', 211), 212, .8))
mt('c2_painel', 64, 64, desgaste(tecido('#55492f', '#3a3020', '#6d6042', 213), 214, .6))
mt('c2_costura', 8, 8, costura_c('#4c412c'))
mt('c2_cotov', 32, 32, lona('#4f4a33', '#353122', '#665f43', 215))
mt('c2_botoes', 8, 32, botoes_c)
mt('c2_bolso', 32, 32, bolsa_f('#665840', '#463c2a', '#7e7052', 216, aba=.62, tira=False), rep=False)
mt('c2_calca', 64, 64, desgaste(lona('#4d5336', '#363b26', '#62694a', 217), 218, .7))
mt('c2_bolso_calca', 32, 32, bolsa_f('#4a5034', '#323722', '#5f6646', 219, aba=.6, tira=False), rep=False)
mt('c2_costura_c', 8, 8, costura_c('#41472f'))
mt('c2_reforco', 32, 32, lona('#3f4530', '#2b301f', '#555c40', 220))
mt('c2_fita', 32, 8, fita_f('#41472f', '#2b301f', 221, ponto=False))
mt('c2_cinto', 32, 8, fita_f('#4b5038', '#30331f', 222, ponto=False))
mt('c2_metal', 8, 8, preto_f('#77766c', '#b3b1a4', 223))
mt('c2_bota', 32, 32, bota_c)
mt('c2_sola', 16, 16, lambda x, y, w, h: hx('#6b5c48') if (x + y) % 5 < 2 else hx('#4c4234'))
mt('c2_entressola', 16, 16, lambda x, y, w, h: hx('#8a7a60') if y % 8 not in (0, 7) else hx('#6b5c48'))
mt('c2_biqueira', 16, 16, lambda x, y, w, h: mix(hx('#3d2717'), hx('#5c3d27'), ruido(x // 2, y // 2, 224) ** 3))
mt('c2_cadarco', 32, 32, cadarco_c, rep=False)
mt('c2_colarinho', 16, 16, lambda x, y, w, h: mix(hx('#2e1e12'), hx('#45301e'), .5 * ruido(x, y, 225)))
mt('c2_luva', 32, 32, luva_c)
mt('c2_palma', 16, 16, lambda x, y, w, h: hx('#9c8a6a') if (x in (1, w - 2) or y in (1, h - 2)) and (x + y) % 2 == 0 else mix(hx('#6e5a40'), hx('#86704f'), .5 * ruido(x // 2, y // 2, 226)))
mt('c2_cantil', 32, 32, bolsa_f('#4b5038', '#30331f', '#626a49', 227, aba=.7, tira=False), rep=False)
mt('c2_municao', 32, 32, bolsa_f('#5a5038', '#3e3726', '#71664a', 228, aba=.6), rep=False)
mt('c2_equip', 32, 32, bolsa_f('#4f4a33', '#353122', '#665f43', 229, aba=.66), rep=False)

# ================================================================== JAQUETA de campanha
bm = extrair(lambda f: REG[f.index] == 'camisa'); afastar(bm, .016)
barra_j = bordas(bm, lambda e: all(abs(W(v.co).z - CINTURA) < .012 and abs(W(v.co).x) < .3 for v in e.verts))
SAIA = []
if barra_j:                                                        # saia até o meio da coxa, abrindo um pouco
    vs = extrudar_borda(bm, barra_j, (0, 0, -.11)); SAIA += extrudar_borda.faces
    c0 = sum((W(v.co) for v in vs), Vector()) / len(vs)
    for v in vs: p = W(v.co); d = Vector((p.x - c0.x, p.y - c0.y, 0)); v.co = MWi @ (p + d.normalized() * .012)
    vs2 = extrudar_borda(bm, [e for e in bm.edges if e.is_boundary and all(v in vs for v in e.verts)], (0, 0, -.12)); SAIA += extrudar_borda.faces
    for v in vs2: p = W(v.co); d = Vector((p.x - c0.x, p.y - c0.y, 0)); v.co = MWi @ (p + d.normalized() * .014)
GOLA = []
gola_ = bordas(bm, lambda e: all(W(v.co).z > 1.62 and abs(W(v.co).x) < .14 for v in e.verts))
if gola_:                                                          # gola virada: sobe 1,8 cm e dobra pra fora/baixo (não encosta na cabeça)
    vs = extrudar_borda(bm, gola_, (0, 0, .018)); GOLA += extrudar_borda.faces
    c0 = sum((W(v.co) for v in vs), Vector()) / len(vs)
    vs2 = extrudar_borda(bm, [e for e in bm.edges if e.is_boundary and all(v in vs for v in e.verts)], (0, 0, 0)); GOLA += extrudar_borda.faces
    for v in vs2:
        p = W(v.co); d = Vector((p.x - c0.x, p.y - c0.y, 0))
        if d.length > 1e-6: v.co = MWi @ (p + d.normalized() * .03 + Vector((0, 0, -.032)))
SS = set(SAIA)
for f in bm.faces:
    f.material_index = 1 if f in GOLA else 0
    if f.material_index == 0 and dono(f).startswith(('upper_arm', 'forearm')) and normal(f).y > .5: f.material_index = 1   # painel de trás da manga
eh_braco = lambda f: dono(f).startswith(('upper_arm', 'forearm'))
for s in (1, -1):
    faixa_costura(bm, lambda f, s=s: eh_braco(f) and centro(f).x * s > 0, (s * (OMBRO.x + .02), 0, 0), (1, 0, 0), 2)
    faixa_costura(bm, lambda f, s=s: eh_braco(f) and centro(f).x * s > 0, (s * (PULSO - .05), 0, 0), (1, 0, 0), 2)
    for x in (COTOVELO.x - .05, COTOVELO.x + .05): cortar(bm, (s * x, 0, 0), (1, 0, 0), [f for f in bm.faces if eh_braco(f) and centro(f).x * s > 0])
    fs = [f for f in bm.faces if eh_braco(f) and centro(f).x * s > 0 and abs(abs(centro(f).x) - COTOVELO.x) < .05 and normal(f).y > -.2]
    for f in extrudar(bm, fs, .005, normal_unica=False): f.material_index = 3
frente_j = lambda f: f.is_valid and normal(f).y < -.5 and centro(f).y < 0 and (tronco(f) or f in SS) and f not in GOLA
faixa_costura(bm, frente_j, (0, 0, 0), (1, 0, 0), 4, larg=.022)    # carcela de botões no meio da frente
faixa_costura(bm, lambda f: f.is_valid and tronco(f) and f not in GOLA, (0, 0, 1.585), (0, 0, 1), 2)   # pala
ombro_t = lambda f: f.is_valid and tronco(f) and normal(f).z > .6 and .08 < abs(centro(f).x) < .21 and f not in GOLA
for f in extrudar(bm, [f for f in bm.faces if ombro_t(f)], .005): f.material_index = 1   # platinas
def uv_jaq(bm, uvl):
    plana(bm, uvl, [f for f in bm.faces if f.material_index == 4], lambda q: (q.x + .011) / .022, lambda q: q.z * 6)
    uv_denso(bm, uvl, (2,))
jaqueta = objeto(bm, 'jaqueta', ['c2_jaqueta', 'c2_painel', 'c2_costura', 'c2_cotov', 'c2_botoes'], mat_de=lambda f: f.material_index, uv_extra=uv_jaq)
def pesos_saia(ob):                                                # a saia (e o que está preso nela) segue meio quadril, meio coxa
    for v in ob.data.vertices:
        if (MW @ v.co).z < CINTURA + .01:
            gs = [(ob.vertex_groups[g.group].name, g.weight) for g in v.groups]
            for n_, w_ in gs:
                if n_.startswith('shin'): ob.vertex_groups[n_].remove([v.index])
                elif n_.startswith('thigh'): ob.vertex_groups[n_].add([v.index], w_ * .5, 'REPLACE')
            ob.vertex_groups['spine'].add([v.index], .5, 'ADD')
pesos_saia(jaqueta)
SUP = bvh_de([jaqueta])
for s in (1, -1):                                                  # bolsos de peito (aba + botão) e bolsos de baixo e laterais na saia
    hit = raio(SUP, Vector((s * .085 * TX / .2, -.1, 1.47)), F_)
    b_ = bolsa_em(hit or Vector((s * .085, -.2, 1.47)), F_, C_, .085 * TX / .2, .1, .016, nx=2, nz=2); pesar(b_)
    so_tronco(objeto(b_, 'bolso_peito', ['c2_bolso'], uv=False), ['spine.001', 'spine.002', 'spine.003'])
    hit = raio(SUP, Vector((s * .09, -.1, CINTURA - .13)), F_)
    b_ = bolsa_em(hit or Vector((s * .09, -.2, CINTURA - .13)), F_, C_, .11, .1, .016, nx=2, nz=2); pesar(b_)
    pesos_saia(objeto(b_, 'bolso_saia', ['c2_bolso'], uv=False))
    d_ = Vector((s, -.15, 0)).normalized(); hit = raio(SUP, Vector((s * .1, 0, CINTURA - .12)), d_)
    b_ = bolsa_em(hit or Vector((s * .2, 0, CINTURA - .12)), d_, C_, .08, .1, .014, nx=2, nz=2); pesar(b_)
    pesos_saia(objeto(b_, 'bolso_lateral', ['c2_bolso'], uv=False))

# ================================================================== CALÇA verde-oliva
bm = extrair(lambda f: REG[f.index] == 'calca'); afastar(bm, .013)
barra = bordas(bm, lambda e: all(abs(W(v.co).z - BOTA) < .01 for v in e.verts))
if barra: extrudar_borda(bm, barra, (0, 0, -.03))
CZ0, CZ1 = JOELHO + .1, JOELHO + .24
lado = lambda f: dono(f).startswith('thigh') and normal(f).x > .55 and centro(f).x > 0
for z in (CZ0, CZ1): cortar(bm, (0, 0, z), (0, 0, 1), [f for f in bm.faces if lado(f)])
fsb = [f for f in bm.faces if lado(f) and CZ0 < centro(f).z < CZ1]
YB = (min(W(v.co).y for f in fsb for v in f.verts), max(W(v.co).y for f in fsb for v in f.verts)) if fsb else (-.05, .05)
NOV = extrudar(bm, fsb, .022)
for f in bm.faces: f.material_index = 1 if f in NOV else 0
for f in [f for f in NOV if centro(f).z > CZ1 - .05 and normal(f).x > .5]:
    for v in f.verts: v.co += f.normal * L(.004)
perna = lambda f: f.is_valid and dono(f).startswith(('thigh', 'shin')) and f.material_index == 0
for s in (1, -1):
    lat = lambda f, s=s: perna(f) and centro(f).x * s > 0 and normal(f).x * s > .5
    ys = [W(v.co).y for f in bm.faces if lat(f) for v in f.verts]
    if ys: faixa_costura(bm, lat, (0, (min(ys) + max(ys)) / 2, 0), (0, 1, 0), 2)
for z in (JOELHO + .09, JOELHO - .08): faixa_costura(bm, perna, (0, 0, z), (0, 0, 1), 2)
for f in bm.faces:
    if perna(f) and abs(centro(f).z - JOELHO) < .086 and normal(f).y < -.3: f.material_index = 3
def uv_calca_c(bm, uvl):
    y0, y1 = YB[0] - .02, YB[1] + .02
    plana(bm, uvl, [f for f in bm.faces if f.material_index == 1], lambda q: (q.y - y0) / (y1 - y0), lambda q: (q.z - CZ0) / (CZ1 - CZ0))
    uv_denso(bm, uvl, (2,))
calca = objeto(bm, 'calca', ['c2_calca', 'c2_bolso_calca', 'c2_costura_c', 'c2_reforco'], mat_de=lambda f: f.material_index, uv_extra=uv_calca_c)

# ================================================================== COTURNO de couro marrom
bm = extrair(lambda f: REG[f.index] == 'bota'); afastar(bm, .017)
for v in bm.verts:
    p = W(v.co)
    if p.z < 0: v.co = MWi @ Vector((p.x, p.y, 0.0))
CSOLA = .024
for z in (.010, CSOLA): cortar(bm, (0, 0, z), (0, 0, 1))
cano = bordas(bm, lambda e: all(abs(W(v.co).z - BOTA) < .01 for v in e.verts))
COLAR = []
if cano:
    vs = extrudar_borda(bm, cano, (0, 0, .014)); COLAR += extrudar_borda.faces
    for s in (1, -1):
        lv = [v for v in vs if W(v.co).x * s > 0]
        if not lv: continue
        c0 = sum((W(v.co) for v in lv), Vector()) / len(lv)
        for v in lv: p = W(v.co); d = Vector((p.x - c0.x, p.y - c0.y, 0)); v.co = MWi @ (p + (d.normalized() * .005 if d.length > 1e-6 else Vector()))
for f in bm.faces:
    z = centro(f).z; f.material_index = 1 if z < .010 else 2 if z < CSOLA else 0
    if f in COLAR: f.material_index = 6
for f in extrudar(bm, [f for f in bm.faces if f.material_index == 2 and abs(normal(f).z) < .5], .004, normal_unica=False): f.material_index = 2
for s in (1, -1):
    ld = [f for f in bm.faces if centro(f).x * s > 0]
    ymin = min(W(v.co).y for f in ld for v in f.verts); ymax = max(W(v.co).y for f in ld for v in f.verts)
    for f in extrudar(bm, [f for f in ld if f.material_index == 0 and centro(f).y < ymin + .06 and centro(f).z < .07], .003, normal_unica=False): f.material_index = 3
    for f in extrudar(bm, [f for f in ld if f.is_valid and f.material_index == 0 and centro(f).y > ymax - .045 and centro(f).z < .08], .003, normal_unica=False): f.material_index = 3
    for f in ld:
        if f.is_valid and f.material_index == 0 and normal(f).y < -.45 and .07 < centro(f).z < BOTA: f.material_index = 4
def uv_bota_c(bm, uvl):
    for s in (1, -1):
        fs = [f for f in bm.faces if f.material_index == 4 and centro(f).x * s > 0]
        if not fs: continue
        xc = sum(centro(f).x for f in fs) / len(fs)
        plana(bm, uvl, fs, lambda q, xc=xc: (q.x - xc) / .09 + .5, lambda q: (q.z - .07) / (BOTA - .07))
objeto(bm, 'bota', ['c2_bota', 'c2_sola', 'c2_entressola', 'c2_biqueira', 'c2_cadarco', 'c2_bota', 'c2_colarinho'], mat_de=lambda f: f.material_index, uv_extra=uv_bota_c)

# ================================================================== LUVAS bege (palma de couro)
bm = extrair(lambda f: REG[f.index] == 'luva'); afastar(bm, .006)
for s in (1, -1):
    pu = bordas(bm, lambda e, s=s: all(abs(W(v.co).x - s * PULSO) < .01 for v in e.verts))
    if pu:
        vs = extrudar_borda(bm, pu, (-s * .03, 0, 0)); c0 = sum((W(v.co) for v in vs), Vector()) / len(vs)
        for v in vs: p = W(v.co); d = Vector((0, p.y - c0.y, p.z - c0.z)); v.co = MWi @ (p + d.normalized() * .012)
for f in bm.faces: f.material_index = 1 if normal(f).z < -.45 else 0
objeto(bm, 'luva', ['c2_luva', 'c2_palma'], mat_de=lambda f: f.material_index, dens=8)

# ================================================================== CINTO de lona (por cima da saia) + SUSPENSÓRIO em Y + equipamento
bm = extrair(lambda f: REG[f.index] == 'calca'); afastar(bm, .013)
cortar(bm, (0, 0, CINTURA - .05), (0, 0, 1))
bmesh.ops.delete(bm, geom=[f for f in bm.faces if not (CINTURA - .05 < centro(f).z < CINTURA - .005)], context='FACES')
afastar(bm, .03); espessura(bm, bm.faces[:], .008)
for f in bm.faces: f.material_index = 0
for x in (-.022, .022): cortar(bm, (x, 0, 0), (1, 0, 0))
for f in extrudar(bm, [f for f in bm.faces if normal(f).y < -.7 and abs(centro(f).x) < .022 and centro(f).y < 0], .008): f.material_index = 1
cinto = objeto(bm, 'cinto', ['c2_cinto', 'c2_metal'], mat_de=lambda f: f.material_index, dens=8); so_tronco(cinto, ['spine', 'spine.001'])
SUP = bvh_de([jaqueta, cinto, calca])
for s in (1, -1):
    g_ = [(Vector((s * .1, -.1, CINTURA - .02)), F_), (Vector((s * .11, -.1, 1.35)), F_), (Vector((s * .11, -.1, 1.56)), F_),
          (Vector((s * .1, -.04, 1.66)), (F_ + C_).normalized()), (Vector((s * .09, .03, 1.70)), C_), (Vector((s * .07, .1, 1.62)), T_), (Vector((0, .1, 1.52)), T_)]
    bms, fs_, _ = faixa(g_, .036, .008, passos=4); espessura(bms, fs_, .004)
    for f in extrudar(bms, [fs_[int(len(fs_) * .3)]], .006): f.material_index = 1
    pesar(bms); so_tronco(objeto(bms, 'suspensorio', ['c2_fita', 'c2_metal'], mat_de=lambda f: f.material_index, dens=10), ['spine', 'spine.001', 'spine.002', 'spine.003'])
bms, fs_, _ = faixa([(Vector((0, .1, 1.53)), T_), (Vector((0, .1, 1.35)), T_), (Vector((0, .1, CINTURA - .02)), T_)], .04, .008, passos=4)
espessura(bms, fs_, .004); pesar(bms); so_tronco(objeto(bms, 'suspensorio_tras', ['c2_fita'], dens=10), ['spine', 'spine.001', 'spine.002'])
SUP = bvh_de([jaqueta, cinto, calca])
for s in (1, -1):
    d_ = Vector((s * .65, .76, 0)).normalized(); hit = raio(SUP, Vector((s * .13, .1, CINTURA - .07)), d_)
    b_ = bolsa_em(hit or Vector((s * .15, .15, CINTURA - .07)), d_, C_, .1, .13, .07, nx=2, nz=3); pesar(b_)
    so_tronco(objeto(b_, 'cantil', ['c2_cantil'], uv=False), ['spine', 'spine.001'])
for x in (-.15, -.085, .12):                                       # porta-munições: dois à direita, um à esquerda
    hit = raio(SUP, Vector((x, -.1, CINTURA - .065)), F_)
    b_ = bolsa_em(hit or Vector((x, -.2, CINTURA - .065)), F_, C_, .055, .07, .035); pesar(b_)
    so_tronco(objeto(b_, 'porta_municao', ['c2_municao'], uv=False), ['spine', 'spine.001'])
d_ = Vector((-1, .2, 0)).normalized(); hit = raio(SUP, Vector((-.12, .02, CINTURA - .07)), d_)   # bolsa de equipamento (lado direito)
b_ = bolsa_em(hit or Vector((-.2, .02, CINTURA - .07)), d_, C_, .09, .11, .05, nx=2, nz=3); pesar(b_)
so_tronco(objeto(b_, 'bolsa_equip', ['c2_equip'], uv=False), ['spine', 'spine.001'])
for o in (jaqueta, calca):
    for p_ in o.data.polygons: p_.use_smooth = True                 # tecido com sombreamento suave; equipamento facetado
V = 1

# ================================================================== CABEÇA DE PARDAL (nova) + PESCOÇO humanoide
CJ = json.load(open(os.path.join(CTX, 'cabeca_corsa.json')))
img_p = bpy.data.images.load(os.path.join(CTX, 'pardal_cabeca.png')); img_p.pack()
material('c2_pardal', img_p, repete=False)
mt('c2_olho', 8, 8, lambda x, y, w, h: hx('#d8d8d0') if (x, y) in ((4, 4), (5, 4)) else hx('#0b0b0e'))
ESC_P = 10.0; ALVO_P = Vector((0, -.01, 1.885))
bm = bmesh.new(); uvl = bm.loops.layers.uv.verify()
vs_ = [bm.verts.new(MWi @ (ALVO_P + Vector(p) * ESC_P)) for p in CJ['v']]
for f, uv, m in zip(CJ['f'], CJ['uv'], CJ['mat']):
    try: fa = bm.faces.new([vs_[i] for i in f])
    except ValueError: continue
    fa.material_index = m
    for l, u in zip(fa.loops, uv): l[uvl].uv = u
bm.normal_update()
cab = objeto(bm, 'cabeca_pardal', ['c2_pardal', 'c2_olho'], mat_de=lambda f: f.material_index, uv=False)
tudo_no_osso(cab, 'spine.005')
g_, n_ = CJ['garganta'], CJ['nuca']
PESC_F, PESC_T = tuple(int(c * .95) for c in g_), (104, 84, 60)     # frente: babador escuro do pardal · trás: nuca marrom
def pesc_f(x, y, w, h):                                            # u = .5 é a frente; v (y) sobe do ombro pra cabeça
    a = (x / w) * 2 * math.pi; fr = max(0, math.cos(a - math.pi)) ** 1.3
    c = mix(PESC_T, PESC_F, fr)
    k = ruido(x // 3, y // 2, 231) * .6 + ruido(x // 6, y // 4, 232) * .4
    c = mix(c, (0, 0, 0), .1 + .12 * k)
    sombra = max(0, (y / h - .7) / .3)                              # sombra embaixo da cabeça
    return mix(c, (20, 16, 12), .35 * sombra)
mt('c2_pescoco', 32, 32, pesc_f)
# PESCOÇO humanoide de verdade: oval (mais largo de lado que de frente), afina do ombro (base larga, some sob a gola) até
# debaixo da cabeça, garganta um pouco à frente e nuca atrás; o topo entra na cabeça. Plumagem marrom (só a cabeça é de pardal).
bm = bmesh.new(); uvl = bm.loops.layers.uv.verify(); NP = 14; an = []
ANEIS_P = [(1.615, .088, .072, .005), (1.665, .06, .056, .004), (1.71, .051, .049, .002), (1.75, .054, .053, .004), (1.785, .066, .06, .008), (1.815, .07, .062, .008)]   # afina no meio, abre embaixo da cabeça (encaixa no contorno dela)
for j, (z, a_, b_, yc) in enumerate(ANEIS_P):
    anel_ = []
    for k in range(NP):
        t = 2 * math.pi * k / NP; x = a_ * math.sin(t); y = yc - b_ * math.cos(t)
        if j in (0, 1) and math.cos(t) < -.3: z_ = z + .012 * (-math.cos(t)) * (1 - j * .5)                 # nuca: base mais alta atrás (trapézio)
        else: z_ = z
        anel_.append(bm.verts.new(MWi @ Vector((x, y, z_))))
    an.append(anel_)
for j in range(len(an) - 1):
    for k in range(NP):
        k2 = (k + 1) % NP; f = bm.faces.new((an[j][k], an[j][k2], an[j + 1][k2], an[j + 1][k]))
        u0 = (.5 + k / NP) % 1; u1 = u0 + 1 / NP
        for l, uv in zip(f.loops, ((u0, j / 5), (u1, j / 5), (u1, (j + 1) / 5), (u0, (j + 1) / 5))): l[uvl].uv = uv
bm.normal_update()
if sum(Wn(f.normal).dot((W(f.calc_center_median()) - Vector((0, -.01, W(f.calc_center_median()).z))).normalized()) for f in bm.faces) < 0: bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
pesc = objeto(bm, 'pescoco', ['c2_pescoco'], uv=False)
for p_ in pesc.data.polygons: p_.use_smooth = True                 # pescoço liso (sem cara de caixa)
for v in pesc.data.vertices:                                       # base no pescoço, topo junto com a cabeça
    for g in list(v.groups): pesc.vertex_groups[g.group].remove([v.index])
    z = (MW @ v.co).z; t = min(1, max(0, (z - 1.65) / .17))       # base presa no tronco, topo acompanha a cabeça
    if z < 1.64: pesc.vertex_groups['spine.003'].add([v.index], 1.0, 'REPLACE'); continue
    pesc.vertex_groups['spine.004'].add([v.index], 1 - t * .7, 'REPLACE'); pesc.vertex_groups['spine.005'].add([v.index], t * .7, 'REPLACE')
for m in MATS.values(): m.use_backface_culling = True
bpy.data.objects.remove(corpo)                                     # o corpo base fica todo coberto (roupa, luvas, pescoço)
