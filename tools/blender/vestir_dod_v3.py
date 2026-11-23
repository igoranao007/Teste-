# V3 do Dod: detalhes modelados + paleta (executado dentro do vestir_dod.py quando V >= 3; as funções são chamadas por cada peça).
# Regra: o que dá volume/silhueta é GEOMETRIA (bolsos, abas, reforços, fileiras MOLLE, fivelas, faixas de ajuste, sola em camadas,
# biqueira); o que é fino demais pro PS1 é TEXTURA de baixa resolução (pesponto, trama, desgaste, cadarço).

def faixa_costura(bm, pred, ponto, normal_, mat, larg=.008):      # costura "de baixo custo": dois cortes paralelos e a faixa entre eles
    n = Vector(normal_).normalized(); p = Vector(ponto)
    for k in (-.5, .5): cortar(bm, p + n * (larg * k), n, [f for f in bm.faces if pred(f)])
    for f in bm.faces:
        if pred(f) and abs((centro(f) - p).dot(n)) < larg / 2: f.material_index = mat
def uv_denso(bm, uvl, mats, dens=40.0):                           # faixas de costura: textura bem mais densa (o pesponto aparece)
    for f in bm.faces:
        if f.material_index not in mats: continue
        n = normal(f); a = max(range(3), key=lambda i: abs(n[i]))
        for l in f.loops:
            q = W(l.vert.co); l[uvl].uv = (q.y * dens, q.z * dens) if a == 0 else (q.x * dens, q.z * dens) if a == 1 else (q.x * dens, q.y * dens)
def plana(bm, uvl, faces, fu, fv):
    for f in faces:
        for l in f.loops: q = W(l.vert.co); l[uvl].uv = (fu(q), fv(q))
def eh_braco(f): return dono(f).startswith(('upper_arm', 'forearm'))

# ------------------------------------------------------------------ CAMISA: painéis em dois tons, costura do ombro e da pala,
# reforço no cotovelo, bolso na manga direita (com zíper e o patch da Toca do Anão)
BM_X0, BM_X1, BM_Y = OMBRO.x + .125, OMBRO.x + .185, .03
def camisa_v3(bm):
    for f in bm.faces:
        c = centro(f)
        if eh_braco(f) and normal(f).y > .45: f.material_index = 1          # painel de trás da manga em verde-musgo
        elif tronco(f) and c.z > 1.585: f.material_index = 1                 # pala dos ombros
    faixa_costura(bm, lambda f: tronco(f), (0, 0, 1.585), (0, 0, 1), 2)
    for s in (1, -1):
        faixa_costura(bm, lambda f, s=s: eh_braco(f) and centro(f).x * s > 0, (s * (OMBRO.x + .016), 0, 0), (1, 0, 0), 2)
        faixa_costura(bm, lambda f, s=s: eh_braco(f) and centro(f).x * s > 0, (s * (PULSO - .06), 0, 0), (1, 0, 0), 2)    # punho
        # reforço do cotovelo (peça sobreposta, levemente em relevo)
        for x in (COTOVELO.x - .045, COTOVELO.x + .045): cortar(bm, (s * x, 0, 0), (1, 0, 0), [f for f in bm.faces if eh_braco(f) and centro(f).x * s > 0])
        fs = [f for f in bm.faces if eh_braco(f) and centro(f).x * s > 0 and abs(abs(centro(f).x) - COTOVELO.x) < .045 and normal(f).y > -.35]
        for f in extrudar(bm, fs, .004, normal_unica=False): f.material_index = 3
    # bolso da manga direita (lado de fora quando o braço desce = lado de cima em T)
    na_manga_d = lambda f: eh_braco(f) and centro(f).x < -OMBRO.x and normal(f).z > .3
    for x in (-BM_X0, -BM_X1): cortar(bm, (x, 0, 0), (1, 0, 0), [f for f in bm.faces if na_manga_d(f)])
    for y in (-BM_Y, BM_Y): cortar(bm, (0, y, 0), (0, 1, 0), [f for f in bm.faces if na_manga_d(f)])
    fs = [f for f in bm.faces if na_manga_d(f) and BM_X0 < -centro(f).x < BM_X1 and abs(centro(f).y) < BM_Y]
    novos = extrudar(bm, fs, .012)
    for f in novos:
        f.material_index = 4
        if normal(f).z > .6 and -centro(f).x < BM_X0 + .02:
            for v in f.verts: v.co += f.normal * L(.003)                    # aba do bolso
    return ['farda', 'farda2', 'costura', 'reforco', 'bolso_manga']
def uv_camisa_v3(bm, uvl):
    plana(bm, uvl, [f for f in bm.faces if f.material_index == 4], lambda q: (BM_Y - q.y) / (2 * BM_Y), lambda q: 1 - (-q.x - BM_X0) / (BM_X1 - BM_X0))
    uv_denso(bm, uvl, (2,))

# ------------------------------------------------------------------ CALÇA: bolsos cargo grandes com aba, costuras laterais e do joelho,
# reforço no joelho, costura horizontal da coxa, faixas de ajuste no tornozelo com fivela
BOLSO_CALCA_Y = {}
def calca_v3(bm, novos):
    vivos = [f for f in novos if f.is_valid]
    for f in vivos: f.material_index = 1
    for s in (1, -1):
        ys = [centro(f).y for f in vivos if centro(f).x * s > 0 and abs(normal(f).x) > .6]
        if ys: BOLSO_CALCA_Y[s] = (min(ys) - .025, max(ys) + .025)
    perna = lambda f: dono(f).startswith(('thigh', 'shin')) and f.material_index == 0
    for s in (1, -1):
        lat = lambda f, s=s: perna(f) and centro(f).x * s > 0 and abs(normal(f).x) > .5
        ys = [W(v.co).y for f in bm.faces if lat(f) for v in f.verts]
        yc = (min(ys) + max(ys)) / 2 if ys else 0
        faixa_costura(bm, lat, (0, yc, 0), (0, 1, 0), 2)                    # costura lateral (de fora e de dentro)
    for z in (JOELHO + .085, JOELHO - .085, JOELHO + .42): faixa_costura(bm, perna, (0, 0, z), (0, 0, 1), 2)
    for f in bm.faces:
        if perna(f) and abs(centro(f).z - JOELHO) < .081 and normal(f).y < -.3: f.material_index = 3   # reforço do joelho
    # faixa de ajuste no tornozelo (em relevo) + fivela do lado de fora
    canela = lambda f: dono(f).startswith('shin') and f.material_index in (0, 2)
    for z in (BOTA + .03, BOTA + .052): cortar(bm, (0, 0, z), (0, 0, 1), [f for f in bm.faces if canela(f)])
    fs = [f for f in bm.faces if canela(f) and BOTA + .03 < centro(f).z < BOTA + .052]
    faixa = extrudar(bm, fs, .005, normal_unica=False)
    for f in faixa: f.material_index = 4
    for s in (1, -1):
        fv = [f for f in faixa if f.is_valid and normal(f).x * s > .6 and centro(f).x * s > 0]
        for f in extrudar(bm, fv[:1], .004): f.material_index = 5
    return ['calca', 'bolso_calca', 'costura', 'reforco', 'fita', 'metal']
def uv_calca_v3(bm, uvl):
    for s in (1, -1):
        if s not in BOLSO_CALCA_Y: continue
        y0, y1 = BOLSO_CALCA_Y[s]
        fs = [f for f in bm.faces if f.material_index == 1 and centro(f).x * s > 0]
        plana(bm, uvl, fs, (lambda q: (q.y - y0) / (y1 - y0)) if s > 0 else (lambda q: (y1 - q.y) / (y1 - y0)), lambda q: (q.z - BZ0) / (BZ1 - BZ0))
    uv_denso(bm, uvl, (2,)); uv_denso(bm, uvl, (4,), 12)

# ------------------------------------------------------------------ COTURNO: sola em duas camadas (com borda saliente), biqueira, cadarço
def bota_v3(bm):
    cortar(bm, (0, 0, .010), (0, 0, 1))
    for f in bm.faces:
        z = centro(f).z; f.material_index = 1 if z < .010 else 2 if z < SOLA_Z else 0
    meio = [f for f in bm.faces if f.material_index == 2 and abs(normal(f).z) < .5]
    for f in extrudar(bm, meio, .004, normal_unica=False): f.material_index = 2   # entressola saliente
    for s in (1, -1):
        lado = [f for f in bm.faces if centro(f).x * s > 0]
        ymin = min(W(v.co).y for f in lado for v in f.verts)
        bico = [f for f in lado if f.material_index == 0 and centro(f).y < ymin + .06 and centro(f).z < .075]
        for f in extrudar(bm, bico, .003, normal_unica=False): f.material_index = 3
        for f in lado:
            if f.is_valid and f.material_index == 0 and normal(f).y < -.45 and .075 < centro(f).z < BOTA: f.material_index = 4
    return ['bota', 'sola', 'entressola', 'biqueira', 'cadarco']
def uv_bota_v3(bm, uvl):
    for s in (1, -1):
        fs = [f for f in bm.faces if f.material_index == 4 and centro(f).x * s > 0]
        if not fs: continue
        xc = sum(centro(f).x for f in fs) / len(fs)
        plana(bm, uvl, fs, lambda q, xc=xc: (q.x - xc) / .09 + .5, lambda q: (q.z - .075) / (BOTA - .075))

# ------------------------------------------------------------------ LUVAS: reforço da palma (couro) separado do dorso
def luva_v3(bm):
    for f in bm.faces: f.material_index = 1 if normal(f).z < -.45 else 0
    return ['luva', 'palma']

# ------------------------------------------------------------------ COLETE: painel frontal/traseiro, laterais, alças, debrum, 4 fileiras MOLLE
# em relevo, fita de nome, fivelas de ajuste nas alças e nas laterais
NOME_X0, NOME_X1, NOME_Z0, NOME_Z1 = -.17, -.075, 1.468, 1.494
def colete_v3(bm, internas, paredes):
    I, Pa = set(internas), set(paredes)
    fora_ = lambda f: f not in I and f not in Pa
    for f in bm.faces:
        c = centro(f)
        if f in Pa or f in I: f.material_index = 3
        elif c.z >= PT - .002: f.material_index = 2
        elif abs(c.x) < PX: f.material_index = 0
        else: f.material_index = 1
    frente_f = lambda f: fora_(f) and f.material_index == 0 and normal(f).y < -.6 and centro(f).y < 0
    tras_f = lambda f: fora_(f) and f.material_index == 0 and normal(f).y > .6 and centro(f).y > 0
    FILEIRAS = {'frente': [PZ1 + .01 + .026 * i for i in range(4)], 'tras': [VB + .03 + .026 * i for i in range(4)]}
    for lado, pred in (('frente', frente_f), ('tras', tras_f)):
        for x in (PX - .015, -(PX - .015)): cortar(bm, (x, 0, 0), (1, 0, 0), [f for f in bm.faces if pred(f)])
        for z0 in FILEIRAS[lado]:
            for z in (z0, z0 + .014): cortar(bm, (0, 0, z), (0, 0, 1), [f for f in bm.faces if pred(f)])
        for z0 in FILEIRAS[lado]:
            fs = [f for f in bm.faces if pred(f) and z0 < centro(f).z < z0 + .014 and abs(centro(f).x) < PX - .015]
            for f in extrudar(bm, fs, .004): f.material_index = 4
    # fita de nome "DOD" no peito direito
    for x in (NOME_X0, NOME_X1): cortar(bm, (x, 0, 0), (1, 0, 0), [f for f in bm.faces if frente_f(f)])
    for z in (NOME_Z0, NOME_Z1): cortar(bm, (0, 0, z), (0, 0, 1), [f for f in bm.faces if frente_f(f)])
    fs = [f for f in bm.faces if frente_f(f) and NOME_X0 < centro(f).x < NOME_X1 and NOME_Z0 < centro(f).z < NOME_Z1]
    for f in extrudar(bm, fs, .003): f.material_index = 5
    # fivelas: nas alças (logo acima da placa) e nas laterais
    alca_f = lambda f: fora_(f) and f.material_index == 2 and centro(f).y < 0 and normal(f).y < -.3
    for z in (PT + .007, PT + .022): cortar(bm, (0, 0, z), (0, 0, 1), [f for f in bm.faces if alca_f(f)])
    fs = [f for f in bm.faces if alca_f(f) and PT + .007 < centro(f).z < PT + .022]
    for f in extrudar(bm, fs, .004): f.material_index = 6
    lat_f = lambda f: fora_(f) and f.material_index == 1 and normal(f).y < -.3
    for z in (1.285, 1.305): cortar(bm, (0, 0, z), (0, 0, 1), [f for f in bm.faces if lat_f(f)])
    fs = [f for f in bm.faces if lat_f(f) and 1.285 < centro(f).z < 1.305 and PX < abs(centro(f).x) < PX + .035]
    for f in extrudar(bm, fs, .004): f.material_index = 6
    return ['placa', 'lateral', 'alca', 'borda', 'fita', 'nome', 'metal']
def uv_colete_v3(bm, uvl):
    plana(bm, uvl, [f for f in bm.faces if f.material_index == 0 and centro(f).y < 0], lambda q: (q.x + PX) / (2 * PX), lambda q: (q.z - VB) / (PT - VB))
    plana(bm, uvl, [f for f in bm.faces if f.material_index == 0 and centro(f).y >= 0], lambda q: (PX - q.x) / (2 * PX), lambda q: (q.z - VB) / (PT - VB))
    plana(bm, uvl, [f for f in bm.faces if f.material_index == 5], lambda q: (q.x - NOME_X0) / (NOME_X1 - NOME_X0), lambda q: (q.z - NOME_Z0) / (NOME_Z1 - NOME_Z0))
    uv_denso(bm, uvl, (3,)); uv_denso(bm, uvl, (4, 2), 14)

# ------------------------------------------------------------------ CINTO: passadores de fita
def cinto_v3(bm):
    fr = lambda f: normal(f).y < -.6 and centro(f).y < 0 and f.material_index == 0
    for x in (.085, .105, -.085, -.105): cortar(bm, (x, 0, 0), (1, 0, 0), [f for f in bm.faces if fr(f)])
    fs = [f for f in bm.faces if fr(f) and .085 < abs(centro(f).x) < .105]
    for f in extrudar(bm, fs, .003): f.material_index = 2
    return ['cinto', 'metal', 'fita']
