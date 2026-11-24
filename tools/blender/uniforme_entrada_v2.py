# UNIFORME DA ENTRADA v2 (executado dentro do vestir_personagem.py quando PERSONAGEM=entrada e UNIFORME=v2).
# Desenho PRÓPRIO (não é o do Dod nem o do Corsa), modelado sobre o corpo, estilo PS1:
#   camisa verde-acinzentada de manga longa (gola virada baixa, zíper, costuras de ombro/lateral/punho em amarelo-oliva,
#   cotoveleiras costuradas, bolso com aba na manga esquerda) · colete tático CÁQUI (painel da frente e de trás, faixa lateral,
#   alças acolchoadas com fivelas, fileiras MOLLE, 4 porta-carregadores INDIVIDUAIS com aba e lingueta, 2 bolsos de peito, bolso
#   chato nas costas e alça de resgate) · calça cargo marrom/cáqui (bolsos cargo BAIXOS com fole e aba, costuras laterais e do
#   joelho, reforço nos dois joelhos, bolso traseiro, barra presa no coturno) · joelheira só na esquerda · cinto bege com
#   passadores e fivela · coldre de perna direita · bolsa de descarga · luvas verde-oliva com palma de couro ·
#   coturno cáqui (sola + entressola saliente, biqueira, contraforte, cadarço com ilhoses, colarinho acolchoado).
# Regra (Puppet Combo / PS1): o que muda a silhueta é GEOMETRIA; pesponto, cadarço, trama e zíper são TEXTURA.
V = 3                                                              # liga a fusão de faces coplanares do objeto() (os cortes de costura não viram triângulos à toa)
E_COST, E_COST_E = '#a09448', '#77703a'                           # amarelo-oliva discreto (pesponto)
def mt(nome, w, h, fn, rep=True): material(nome, textura(nome, w, h, fn), repete=rep)
def costura_de(base):                                              # faixa de costura: tecido mais escuro + pesponto amarelo-oliva
    B = hx(base)
    def f(x, y, w, h):
        c = mix(B, (0, 0, 0), .25)
        if (y in (3, 4) and x % 4 < 2) or (x in (3, 4) and y % 4 < 2): c = mix(hx(E_COST), c, .2)
        return c
    return f
def placa_e(base, esc, clara, s):                                  # painel do colete (UV plana): debrum, pesponto, cantos reforçados
    def f(x, y, w, h):
        c = lona(base, esc, clara, s)(x, y, w, h); b = min(x, y, w - 1 - x, h - 1 - y)
        if b < 3: c = mix(hx(esc), c, .25)
        elif b == 4 and (x + y) % 3 != 0: c = hx(E_COST)
        return desgaste(lambda *a: c, s + 1, 1.0)(x, y, w, h)
    return f
def molle_e(base, esc, s):                                         # fileira MOLLE: fita com travetes verticais
    def f(x, y, w, h):
        c = mix(hx(base), hx(esc), .3 * ruido(x, y // 2, s))
        if y in (0, h - 1): c = mix(hx(base), hx(esc), .7)
        if x % 10 in (0, 1): c = mix(hx(esc), c, .3)
        return c
    return f
def bota_e(x, y, w, h):                                            # camurça cáqui com painéis e costura
    c = mix(hx('#8a7853'), hx('#a8966c'), .55 * ruido(x // 2, y // 2, 131) ** 1.5)
    if y % 16 == 0 or x % 21 == 0: c = hx('#6b5b3d')
    if y % 16 == 2 and x % 2 == 0: c = mix(hx(E_COST), c, .4)
    return c
def cadarco_e(x, y, w, h):                                         # língua + cadarço cruzado marrom + ilhoses de metal (UV plana)
    u, v = x / (w - 1), y / (h - 1)
    c = hx('#7c6a48') if abs(u - .5) < .28 else hx('#8f7d57')
    yy = y % 6
    if abs(u - .5) < .3 and abs((u - .5) * 10) - abs(yy - 3) < 1.2 and abs(u - .5) * 10 > abs(yy - 3) - 1.0: c = hx('#4e3d29')
    if abs(abs(u - .5) - .3) < .05 and yy == 3: c = hx('#9d9a8c')
    return c
def luva_e(x, y, w, h):                                            # luva tática PRETA-grafite (contrasta com a manga verde): nós dos dedos e costuras
    c = mix(hx('#1c1d1f'), hx('#34363a'), .5 * ruido(x // 2, y // 2, 141) ** 2)
    if y % 8 == 0: c = hx('#121314')
    if x % 8 == 4 and y % 2 == 0: c = mix(hx('#55575c'), c, .5)
    if 10 <= y % 16 <= 13 and x % 8 in (1, 2, 5, 6): c = hx('#4a4c52')   # protetor dos nós (borracha)
    return c
def ziper_e(x, y, w, h): return hx('#8d8b80') if (x + y) % 2 == 0 else hx('#3b4036')
def coldre_e(x, y, w, h): return bolsa_f('#3d3c2e', '#26261d', '#545240', 151, aba=.72, tira=False)(x, y, w, h)

# ---- materiais (paleta própria: verde-acinzentado · verde-musgo · cáqui · marrom · bege · amarelo-oliva · couro · metal · borracha)
mt('e2_camisa', 64, 64, desgaste(tecido('#5d6553', '#3e4537', '#7a8270', 101), 102, .6))
mt('e2_painel', 64, 64, desgaste(tecido('#4f5a3c', '#353d28', '#66704f', 103), 104, .6))
mt('e2_costura', 8, 8, costura_de('#4a5143'))
mt('e2_cotov', 32, 32, lona('#4a5340', '#30372a', '#606a52', 105))
mt('e2_bolso_manga', 32, 32, bolsa_f('#59614f', '#3b4235', '#737b68', 106, aba=.6, tira=False), rep=False)
mt('e2_ziper', 4, 4, ziper_e)
mt('e2_calca', 64, 64, desgaste(lona('#7a6548', '#5f4e37', '#8c775a', 107), 108, .8))
mt('e2_bolso_calca', 32, 32, bolsa_f('#7f6a4b', '#594a34', '#98815d', 109, aba=.6, tira=False), rep=False)
mt('e2_costura_c', 8, 8, costura_de('#6a5840'))
mt('e2_reforco', 32, 32, lona('#6a563c', '#4b3d2a', '#806a4c', 110))
mt('e2_fita', 32, 8, fita_f('#6d5f44', '#4a3f2d', 111))
mt('e2_metal', 8, 8, preto_f('#6f6e66', '#b0aea2', 112))
mt('e2_joelheira', 32, 32, lambda x, y, w, h: (mix(hx('#3d3529'), hx('#5e533f'), .5 * ruido(x // 2, y // 2, 113) ** 2) if not (13 < y < 18) else hx('#2c271f')))
mt('e2_bota', 32, 32, bota_e)
mt('e2_sola', 16, 16, lambda x, y, w, h: hx('#2a2219') if (x + y) % 5 < 2 else hx('#3f3326'))
mt('e2_entressola', 16, 16, lambda x, y, w, h: hx('#5a4c38') if y % 8 not in (0, 7) else hx('#463a2a'))
mt('e2_biqueira', 16, 16, lambda x, y, w, h: mix(hx('#6a5a3d'), hx('#86744f'), ruido(x // 2, y // 2, 114) ** 3))
mt('e2_cadarco', 32, 32, cadarco_e, rep=False)
mt('e2_colarinho', 16, 16, lambda x, y, w, h: mix(hx('#4d3f2b'), hx('#66553b'), .5 * ruido(x, y, 115)))
mt('e2_luva', 32, 32, luva_e)
mt('e2_palma', 16, 16, lambda x, y, w, h: hx('#6e6450') if (x in (1, w - 2) or y in (1, h - 2)) and (x + y) % 2 == 0 else mix(hx('#4f4232'), hx('#6a5a44'), .5 * ruido(x // 2, y // 2, 116)))
mt('e2_placa', 64, 64, placa_e('#8f7f58', '#655939', '#a8976e', 117), rep=False)
mt('e2_lateral', 32, 32, lambda x, y, w, h: molle_e('#857551', '#5c5037', 118)(x, y % 8, w, 8) if y % 16 < 8 else lona('#8f7f58', '#655939', '#a8976e', 119)(x, y, w, h))
mt('e2_molle', 32, 8, molle_e('#7a6a46', '#54482f', 120))
mt('e2_alca', 32, 32, lambda x, y, w, h: mix(lona('#86764f', '#5c5037', '#9e8d66', 121)(x, y, w, h), hx('#5c5037'), .35 if x % 16 in (0, 15) else 0))
mt('e2_borda', 16, 16, lambda x, y, w, h: mix(hx('#5a4f35'), hx('#6f6242'), .4 * ruido(x, y, 122)))
mt('e2_bolso_colete', 32, 32, bolsa_f('#958459', '#685b3c', '#ad9c70', 123, aba=.64), rep=False)
mt('e2_cinto', 32, 8, fita_f('#b1a27a', '#857853', 124))
mt('e2_coldre', 32, 32, coldre_e, rep=False)
mt('e2_couro', 16, 16, lambda x, y, w, h: mix(hx('#5b4632'), hx('#7a6046'), .5 * ruido(x // 2, y // 2, 125)))
pele_mat('e_pele', PELE, 94)

# ================================================================== CAMISA (manga longa)
bm = extrair(lambda f: REG[f.index] == 'camisa'); afastar(bm, .010)
gola = bordas(bm, lambda e: all(W(v.co).z > 1.62 and abs(W(v.co).x) < .14 for v in e.verts))
GOLA_F = []
if gola:                                                           # gola virada baixa: sobe 1,4 cm e dobra pra fora/baixo
    vs = extrudar_borda(bm, gola, (0, 0, .014)); GOLA_F += extrudar_borda.faces
    c0 = sum((W(v.co) for v in vs), Vector()) / len(vs)
    vs2 = extrudar_borda(bm, [e for e in bm.edges if e.is_boundary and all(v in vs for v in e.verts)], (0, 0, 0)); GOLA_F += extrudar_borda.faces
    for v in vs2:
        p = W(v.co); d = Vector((p.x - c0.x, p.y - c0.y, 0))
        if d.length > 1e-6: v.co = MWi @ (p + d.normalized() * .022 + Vector((0, 0, -.026)))
for f in bm.faces:
    f.material_index = 1 if f in GOLA_F else 0
    if f.material_index == 0 and dono(f).startswith(('upper_arm', 'forearm')) and normal(f).z < -.55: f.material_index = 1   # painel de baixo da manga (musgo)
eh_braco = lambda f: dono(f).startswith(('upper_arm', 'forearm'))
for s in (1, -1):
    faixa_costura(bm, lambda f, s=s: eh_braco(f) and centro(f).x * s > 0 and normal(f).z > .5, (0, 0, 0), (0, 1, 0), 2, larg=.007)     # costura de cima da manga
    faixa_costura(bm, lambda f, s=s: eh_braco(f) and centro(f).x * s > 0, (s * (OMBRO.x + .02), 0, 0), (1, 0, 0), 2)                  # cava
    faixa_costura(bm, lambda f, s=s: eh_braco(f) and centro(f).x * s > 0, (s * (PULSO - .05), 0, 0), (1, 0, 0), 2)                    # punho
    faixa_costura(bm, lambda f, s=s: tronco(f) and centro(f).x * s > 0 and abs(normal(f).x) > .6, (s * TX, 0, 0), (0, 1, 0), 2)       # lateral
    for x in (COTOVELO.x - .05, COTOVELO.x + .05): cortar(bm, (s * x, 0, 0), (1, 0, 0), [f for f in bm.faces if eh_braco(f) and centro(f).x * s > 0])
    fs = [f for f in bm.faces if eh_braco(f) and centro(f).x * s > 0 and abs(abs(centro(f).x) - COTOVELO.x) < .05 and normal(f).y > -.2]
    for f in extrudar(bm, fs, .005, normal_unica=False): f.material_index = 3                                                        # cotoveleira costurada
faixa_costura(bm, lambda f: tronco(f) and normal(f).y < -.5 and centro(f).z > 1.42, (0, 0, 0), (1, 0, 0), 4, larg=.012)              # zíper da frente
EBX0, EBX1, EBY = OMBRO.x + .07, OMBRO.x + .135, .032              # bolso da manga ESQUERDA (lado de fora do braço)
na_manga_e = lambda f: eh_braco(f) and centro(f).x > OMBRO.x and normal(f).z > .3
for x in (EBX0, EBX1): cortar(bm, (x, 0, 0), (1, 0, 0), [f for f in bm.faces if na_manga_e(f)])
for y in (-EBY, EBY): cortar(bm, (0, y, 0), (0, 1, 0), [f for f in bm.faces if na_manga_e(f)])
for f in extrudar(bm, [f for f in bm.faces if na_manga_e(f) and EBX0 < centro(f).x < EBX1 and abs(centro(f).y) < EBY], .011):
    f.material_index = 5
    if normal(f).z > .6 and centro(f).x < EBX0 + .022:
        for v in f.verts: v.co += f.normal * L(.003)                # aba
def uv_camisa(bm, uvl):
    plana(bm, uvl, [f for f in bm.faces if f.material_index == 5], lambda q: (q.y + EBY) / (2 * EBY), lambda q: 1 - (q.x - EBX0) / (EBX1 - EBX0))
    uv_denso(bm, uvl, (2,)); uv_denso(bm, uvl, (4,), 60)
camisa = objeto(bm, 'camisa', ['e2_camisa', 'e2_painel', 'e2_costura', 'e2_cotov', 'e2_ziper', 'e2_bolso_manga'], mat_de=lambda f: f.material_index, uv_extra=uv_camisa)

# ================================================================== CALÇA cargo (bolsos baixos com fole), costuras, reforços, barra presa no coturno
bm = extrair(lambda f: REG[f.index] == 'calca'); afastar(bm, .014)
barra = bordas(bm, lambda e: all(abs(W(v.co).z - BOTA) < .01 for v in e.verts))
if barra: extrudar_borda(bm, barra, (0, 0, -.032))
CZ0, CZ1, CPROF = JOELHO + .05, JOELHO + .27, .03                  # bolsos cargo BAIXOS (marca da Entrada)
NOVOS_C = []; YB = {}
for s in (1, -1):
    lado = lambda f, s=s: dono(f).startswith('thigh') and normal(f).x * s > .55 and centro(f).x * s > 0
    for z in (CZ0, CZ1): cortar(bm, (0, 0, z), (0, 0, 1), [f for f in bm.faces if lado(f)])
    fs = [f for f in bm.faces if lado(f) and CZ0 < centro(f).z < CZ1]
    ys = [W(v.co).y for f in fs for v in f.verts]
    if ys: YB[s] = (min(ys), max(ys))
    novos = extrudar(bm, fs, CPROF); NOVOS_C += novos
    for v in {v for f in novos if abs(normal(f).x) > .6 for v in f.verts}:     # fole: estufa no meio
        z = W(v.co).z
        if CZ0 + .03 < z < CZ1 - .07: v.co += R3i @ Vector((s * .006, 0, 0))
    for f in [f for f in novos if centro(f).z > CZ1 - .065 and abs(normal(f).x) > .5]:
        for v in f.verts: v.co += f.normal * L(.004)               # aba
for f in bm.faces: f.material_index = 1 if f in NOVOS_C else 0
perna = lambda f: f.is_valid and dono(f).startswith(('thigh', 'shin')) and f.material_index == 0
for s in (1, -1):
    lat = lambda f, s=s: perna(f) and centro(f).x * s > 0 and abs(normal(f).x) > .5
    ys = [W(v.co).y for f in bm.faces if lat(f) for v in f.verts]
    if ys: faixa_costura(bm, lat, (0, (min(ys) + max(ys)) / 2, 0), (0, 1, 0), 2)           # costuras laterais (fora e dentro)
for z in (JOELHO + .09, JOELHO - .08, JOELHO + .45): faixa_costura(bm, perna, (0, 0, z), (0, 0, 1), 2)
for f in bm.faces:
    if perna(f) and abs(centro(f).z - JOELHO) < .086 and normal(f).y < -.3: f.material_index = 3   # reforço dos dois joelhos
tras = lambda f: f.is_valid and f.material_index in (0, 2) and normal(f).y > .45 and centro(f).y > 0
bt = lambda f: tras(f) and centro(f).x < 0                         # bolso traseiro DIREITO (o Dod tem o esquerdo)
for x in (-.13, -.05): cortar(bm, (x, 0, 0), (1, 0, 0), [f for f in bm.faces if bt(f)])
for z in (QUADRIL - .005, QUADRIL + .08): cortar(bm, (0, 0, z), (0, 0, 1), [f for f in bm.faces if bt(f)])
BTRAS = []
for f in extrudar(bm, [f for f in bm.faces if bt(f) and -.13 < centro(f).x < -.05 and QUADRIL - .005 < centro(f).z < QUADRIL + .08], .007):
    f.material_index = 1; BTRAS.append(f)
def uv_calca(bm, uvl):
    for s in (1, -1):
        if s not in YB: continue
        y0, y1 = YB[s][0] - .02, YB[s][1] + .02
        fs = [f for f in bm.faces if f.material_index == 1 and centro(f).x * s > 0 and f not in BTRAS]
        plana(bm, uvl, fs, (lambda q: (q.y - y0) / (y1 - y0)) if s > 0 else (lambda q: (y1 - q.y) / (y1 - y0)), lambda q: (q.z - CZ0) / (CZ1 - CZ0))
    plana(bm, uvl, [f for f in BTRAS if f.is_valid], lambda q: (q.x + .13) / .08, lambda q: (q.z - QUADRIL + .005) / .085)
    uv_denso(bm, uvl, (2,))
calca = objeto(bm, 'calca', ['e2_calca', 'e2_bolso_calca', 'e2_costura_c', 'e2_reforco'], mat_de=lambda f: f.material_index, uv_extra=uv_calca)
# joelheira só na ESQUERDA: casca com espessura + tira atrás do joelho
bm = extrair(lambda f: REG[f.index] == 'calca'); afastar(bm, .014)
bmesh.ops.delete(bm, geom=[f for f in bm.faces if not (abs(centro(f).z - JOELHO) < .065 and centro(f).x > 0 and (normal(f).y < -.3 or (abs(centro(f).z - JOELHO) < .016)))], context='FACES')
afastar(bm, .008); extrudar(bm, bm.faces[:], .016, normal_unica=False)
objeto(bm, 'joelheira', ['e2_joelheira'], dens=12)

# ================================================================== COTURNO cáqui
bm = extrair(lambda f: REG[f.index] == 'bota'); afastar(bm, .017)
for v in bm.verts:
    p = W(v.co)
    if p.z < 0: v.co = MWi @ Vector((p.x, p.y, 0.0))
ESOLA = .024
for z in (.010, ESOLA): cortar(bm, (0, 0, z), (0, 0, 1))
cano = bordas(bm, lambda e: all(abs(W(v.co).z - BOTA) < .01 for v in e.verts))
COLAR = []
if cano:                                                           # colarinho acolchoado no topo do cano
    vs = extrudar_borda(bm, cano, (0, 0, .012)); COLAR += extrudar_borda.faces
    for s in (1, -1):
        lado_v = [v for v in vs if W(v.co).x * s > 0]
        if not lado_v: continue
        c0 = sum((W(v.co) for v in lado_v), Vector()) / len(lado_v)
        for v in lado_v: p = W(v.co); d = Vector((p.x - c0.x, p.y - c0.y, 0)); v.co = MWi @ (p + (d.normalized() * .005 if d.length > 1e-6 else Vector()))
for f in bm.faces:
    z = centro(f).z; f.material_index = 1 if z < .010 else 2 if z < ESOLA else 0
    if f in COLAR: f.material_index = 6
for f in extrudar(bm, [f for f in bm.faces if f.material_index == 2 and abs(normal(f).z) < .5], .004, normal_unica=False): f.material_index = 2   # entressola saliente
for s in (1, -1):
    lado = [f for f in bm.faces if centro(f).x * s > 0]
    ymin = min(W(v.co).y for f in lado for v in f.verts); ymax = max(W(v.co).y for f in lado for v in f.verts)
    bico = [f for f in lado if f.material_index == 0 and centro(f).y < ymin + .06 and centro(f).z < .07]
    for f in extrudar(bm, bico, .003, normal_unica=False): f.material_index = 3                                      # biqueira
    calc = [f for f in lado if f.is_valid and f.material_index == 0 and centro(f).y > ymax - .045 and centro(f).z < .08]
    for f in extrudar(bm, calc, .003, normal_unica=False): f.material_index = 3                                      # contraforte
    for f in lado:
        if f.is_valid and f.material_index == 0 and normal(f).y < -.45 and .07 < centro(f).z < BOTA: f.material_index = 4   # cadarço
def uv_bota(bm, uvl):
    for s in (1, -1):
        fs = [f for f in bm.faces if f.material_index == 4 and centro(f).x * s > 0]
        if not fs: continue
        xc = sum(centro(f).x for f in fs) / len(fs)
        plana(bm, uvl, fs, lambda q, xc=xc: (q.x - xc) / .09 + .5, lambda q: (q.z - .07) / (BOTA - .07))
objeto(bm, 'bota', ['e2_bota', 'e2_sola', 'e2_entressola', 'e2_biqueira', 'e2_cadarco', 'e2_bota', 'e2_colarinho'], mat_de=lambda f: f.material_index, uv_extra=uv_bota)

# ================================================================== LUVAS táticas pretas (punho largo por cima da manga, palma de couro)
bm = extrair(lambda f: REG[f.index] == 'luva'); afastar(bm, .010)
for v in bm.verts:                                                   # mão mais cheia (a do corpo base é fina e sumia dentro da manga)
    p = W(v.co); s_ = 1 if p.x > 0 else -1; ax = osso('hand.L' if s_ > 0 else 'hand.R')
    d = Vector((0, p.y - ax.y, p.z - ax.z)); v.co = MWi @ Vector((p.x + s_ * .012, ax.y + d.y * 1.28, ax.z + d.z * 1.28))
for s in (1, -1):
    pu = bordas(bm, lambda e, s=s: all(abs(W(v.co).x - s * PULSO) < .01 for v in e.verts))
    if pu:
        vs = extrudar_borda(bm, pu, (-s * .045, 0, 0)); c0 = sum((W(v.co) for v in vs), Vector()) / len(vs)
        for v in vs: p = W(v.co); d = Vector((0, p.y - c0.y, p.z - c0.z)); v.co = MWi @ (p + d.normalized() * .016)   # punho largo por cima da manga
for f in bm.faces: f.material_index = 1 if normal(f).z < -.45 else 0
objeto(bm, 'luva', ['e2_luva', 'e2_palma'], mat_de=lambda f: f.material_index, dens=8)

# ================================================================== COLETE tático cáqui (painel da frente e de trás, faixa lateral, alças)
EVB, EVT, EPT = CINTURA + .06, 1.385, 1.57
EPX, ESX0, ESX1 = TX * .72, TX * .24, TX * .64
bm = extrair(lambda f: REG[f.index] == 'camisa' and tronco(f)); afastar(bm, .012)
for z in (EVB, EVT, EPT): cortar(bm, (0, 0, z), (0, 0, 1))
for x in (EPX, -EPX, ESX0, -ESX0, ESX1, -ESX1): cortar(bm, (x, 0, 0), (1, 0, 0))
def no_colete_e(f):
    c = centro(f); ax = abs(c.x)
    if c.z < EVB: return False
    if c.z < EVT: return True
    if c.z < EPT: return ax < EPX
    return ESX0 < ax < ESX1
bmesh.ops.delete(bm, geom=[f for f in bm.faces if not no_colete_e(f)], context='FACES')
afastar(bm, .024)
FIL_F = [EVB + .155 + .026 * i for i in range(2)]                  # MOLLE na frente: entre os carregadores e os bolsos de peito
FIL_T = [EVB + .17 + .026 * i for i in range(4)]                   # MOLLE nas costas: acima do bolso chato
INT, PAR = espessura(bm, bm.faces[:], .016)
I_, P_ = set(INT), set(PAR)
fora_ = lambda f: f not in I_ and f not in P_
for f in bm.faces:
    c = centro(f)
    f.material_index = 3 if not fora_(f) else 2 if c.z >= EPT - .002 else 0 if abs(c.x) < EPX else 1
frente_f = lambda f: fora_(f) and f.material_index == 0 and normal(f).y < -.6 and centro(f).y < 0
tras_f = lambda f: fora_(f) and f.material_index == 0 and normal(f).y > .6 and centro(f).y > 0
for lado_, pred, fils in (('frente', frente_f, FIL_F), ('tras', tras_f, FIL_T)):
    for x in (EPX - .015, -(EPX - .015)): cortar(bm, (x, 0, 0), (1, 0, 0), [f for f in bm.faces if pred(f)])
    for z0 in fils:
        for z in (z0, z0 + .014): cortar(bm, (0, 0, z), (0, 0, 1), [f for f in bm.faces if pred(f)])
    for z0 in fils:
        for f in extrudar(bm, [f for f in bm.faces if pred(f) and z0 < centro(f).z < z0 + .014 and abs(centro(f).x) < EPX - .015], .004): f.material_index = 4
alca_f = lambda f: fora_(f) and f.material_index == 2 and centro(f).y < 0 and normal(f).y < -.3
for z in (EPT + .008, EPT + .024): cortar(bm, (0, 0, z), (0, 0, 1), [f for f in bm.faces if alca_f(f)])
for f in extrudar(bm, [f for f in bm.faces if alca_f(f) and EPT + .008 < centro(f).z < EPT + .024], .005): f.material_index = 5   # fivelas das alças
lat_f = lambda f: fora_(f) and f.material_index == 1 and normal(f).y < -.3 and EPX < abs(centro(f).x) < EPX + .035
for x in (EPX + .035, -(EPX + .035)): cortar(bm, (x, 0, 0), (1, 0, 0), [f for f in bm.faces if fora_(f) and f.material_index == 1])
for z in (EVB + .05, EVB + .068, EVB + .12, EVB + .138): cortar(bm, (0, 0, z), (0, 0, 1), [f for f in bm.faces if lat_f(f)])
for z0 in (EVB + .05, EVB + .12):
    for f in extrudar(bm, [f for f in bm.faces if lat_f(f) and z0 < centro(f).z < z0 + .018], .004): f.material_index = 5   # fivelas laterais (só na emenda com o painel da frente)
def uv_colete(bm, uvl):
    plana(bm, uvl, [f for f in bm.faces if f.material_index == 0 and centro(f).y < 0], lambda q: (q.x + EPX) / (2 * EPX), lambda q: (q.z - EVB) / (EPT - EVB))
    plana(bm, uvl, [f for f in bm.faces if f.material_index == 0 and centro(f).y >= 0], lambda q: (EPX - q.x) / (2 * EPX), lambda q: (q.z - EVB) / (EPT - EVB))
    uv_denso(bm, uvl, (3,), 20); uv_denso(bm, uvl, (4, 2), 14)
colete_e = objeto(bm, 'colete', ['e2_placa', 'e2_lateral', 'e2_alca', 'e2_borda', 'e2_molle', 'e2_metal'], mat_de=lambda f: f.material_index, dens=6, uv_extra=uv_colete)
SUP = bvh_de([colete_e, camisa, calca])
BOLSOS_E = []
for k, x in enumerate((-.105, -.035, .035, .105)):                 # 4 porta-carregadores INDIVIDUAIS (aba + lingueta de couro na textura)
    xx = x * TX / .2; hit = raio(SUP, Vector((xx, -.1, EVB + .088)), F_)
    b_ = bolsa_em(hit or Vector((xx, -.2, EVB + .088)), F_, C_, .062 * TX / .2, .13, .036, nx=2, nz=3); pesar(b_)
    BOLSOS_E.append(objeto(b_, 'carregador', ['e2_bolso_colete'], uv=False))
for s in (1, -1):                                                  # 2 bolsos de peito com aba
    xx = s * .072 * TX / .2; hit = raio(SUP, Vector((xx, -.1, EPT - .07)), F_)
    b_ = bolsa_em(hit or Vector((xx, -.2, EPT - .07)), F_, C_, .095 * TX / .2, .075, .02, nx=2, nz=2); pesar(b_)
    BOLSOS_E.append(objeto(b_, 'bolso_peito', ['e2_bolso_colete'], uv=False))
hit = raio(SUP, Vector((0, .1, EVB + .085)), T_)                    # bolso chato nas costas
b_ = bolsa_em(hit or Vector((0, .2, EVB + .085)), T_, C_, .26 * TX / .2, .13, .022, nx=3, nz=2); pesar(b_)
BOLSOS_E.append(objeto(b_, 'bolso_costas', ['e2_bolso_colete'], uv=False))
g_ = [(Vector((-.04, .12, EPT - .01)), T_), (Vector((0, .135, EPT + .012)), (T_ + C_).normalized()), (Vector((.04, .12, EPT - .01)), T_)]   # alça de resgate
SUP = bvh_de([colete_e])
bms, fs_, _ = faixa(g_, .03, .012, passos=3); espessura(bms, fs_, .004); pesar(bms)
BOLSOS_E.append(objeto(bms, 'alca_resgate', ['e2_fita'], dens=10))
for o in [colete_e] + BOLSOS_E: so_tronco(o, ['spine', 'spine.001', 'spine.002', 'spine.003'])

# ================================================================== CINTO bege (passadores + fivela) · COLDRE de perna · BOLSA DE DESCARGA
bm = extrair(lambda f: REG[f.index] == 'calca'); afastar(bm, .014)
cortar(bm, (0, 0, CINTURA - .042), (0, 0, 1))
bmesh.ops.delete(bm, geom=[f for f in bm.faces if not (CINTURA - .042 < centro(f).z < CINTURA + .001)], context='FACES')
afastar(bm, .008); espessura(bm, bm.faces[:], .009)
for f in bm.faces: f.material_index = 0
for x in (-.026, .026): cortar(bm, (x, 0, 0), (1, 0, 0))
for f in extrudar(bm, [f for f in bm.faces if normal(f).y < -.7 and abs(centro(f).x) < .026 and centro(f).y < 0], .01): f.material_index = 1
fr_ = lambda f: f.is_valid and normal(f).y < -.6 and centro(f).y < 0 and f.material_index == 0
for x in (.075, .092, -.075, -.092): cortar(bm, (x, 0, 0), (1, 0, 0), [f for f in bm.faces if fr_(f)])
for f in extrudar(bm, [f for f in bm.faces if fr_(f) and .075 < abs(centro(f).x) < .092], .003): f.material_index = 2   # passadores
cinto = objeto(bm, 'cinto', ['e2_cinto', 'e2_metal', 'e2_fita'], mat_de=lambda f: f.material_index, dens=8); so_tronco(cinto, ['spine', 'spine.001'])
SUP = bvh_de([calca, cinto])
hit = raio(SUP, Vector((-.16, 0, QUADRIL - .17)), -E_)
b_ = bolsa_em(hit or Vector((-.2, 0, QUADRIL - .17)), -E_, C_, .075, .15, .045); pesar(b_)
objeto(b_, 'coldre', ['e2_coldre'], uv=False)
bm = extrair(lambda f: REG[f.index] == 'calca'); afastar(bm, .014)
perna_d = lambda f: dono(f).startswith('thigh') and centro(f).x < 0
for z in (QUADRIL - .13, QUADRIL - .108, QUADRIL - .235, QUADRIL - .213): cortar(bm, (0, 0, z), (0, 0, 1), [f for f in bm.faces if perna_d(f)])
bmesh.ops.delete(bm, geom=[f for f in bm.faces if not (perna_d(f) and (QUADRIL - .13 < centro(f).z < QUADRIL - .108 or QUADRIL - .235 < centro(f).z < QUADRIL - .213))], context='FACES')
afastar(bm, .006); objeto(bm, 'tiras_coldre', ['e2_fita'], dens=10)
hit = raio(SUP, Vector((.1, .12, CINTURA - .07)), Vector((.5, .86, 0)).normalized())
b_ = bolsa_em(hit or Vector((.1, .15, CINTURA - .07)), Vector((.5, .86, 0)).normalized(), C_, .1, .09, .04); pesar(b_)
so_tronco(objeto(b_, 'bolsa_descarga', ['e2_bolso_calca'], uv=False), ['spine', 'spine.001'])

for o in (camisa, calca):                                          # tecido com sombreamento suave (Gouraud, como os NPCs da Puppet Combo); equipamento facetado
    for p_ in o.data.polygons: p_.use_smooth = True
V = 1
