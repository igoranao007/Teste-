# OLIVEIRA (executado dentro do vestir_personagem.py, PERSONAGEM=oliveira) — aliado do DOM: cabeça e pescoço do GODZILLA sobre um
# corpo humanoide encorpado com ARMADURA de tecnologia do DOM (placas pretas, frisos de energia amarela que brilham), o símbolo
# "トカ" no peito, gola blindada, ombreiras, braçadeiras, manoplas, cinto com bolsas, tabardo de tecido, coxas/joelhos/canelas
# blindados, coturnos, e o REATOR nas costas (moldura octogonal, núcleo brilhante, engrenagens).
# Cabeça: "PlayStation 3 - Godzilla - Heisei Godzilla" by Mathzilla5335 (Sketchfab), CC BY 4.0 — crédito obrigatório;
# personagem © Toho (uso fan-made). O arquivo original fica intacto em referencia/.
# Materiais com "brilho" no nome são de luz própria no motor (lib/modelo.js).
import numpy as np
OD = os.path.join(RAIZ, 'material/producao/personagens/oliveira')
V = 3
TX = afinar_corpo(kt=(1.12, 1.12), ka=1.1, kc=1.1, kn=1.05)      # mais encorpado que o corpo base
AMARELO = '#ffc21a'
def mt(nome, w, h, fn, rep=True): material(nome, textura(nome, w, h, fn), repete=rep)
def placa_o(s, base='#26262a', esc='#121214', clara='#3a3a40'):  # placa preta "de pedra/borracha": blocos e cantos gastos
    def f(x, y, w, h):
        c = mix(hx(esc), hx(base), .4 + .6 * ruido(x // 3, y // 3, s))
        if x % 16 in (0, 15) or y % 16 in (0, 15): c = mix(c, hx(esc), .6)                # junta dos blocos
        if ruido(x, y, s + 1) > .94: c = mix(c, hx(clara), .6)                          # desgaste
        return c
    return f
mt('o_placa', 64, 64, placa_o(401))
mt('o_placa2', 64, 64, placa_o(402, '#2e2e33', '#17171a', '#46464c'))
mt('o_traje', 64, 64, lambda x, y, w, h: mix(hx('#151517'), hx('#242428'), .5 * ruido(x // 2, y // 2, 403)) if (x + y) % 6 else hx('#0e0e10'))
mt('o_brilho', 8, 8, lambda x, y, w, h: mix(hx(AMARELO), hx('#fff1a8'), .35 if (x + y) % 3 == 0 else 0))
mt('o_tecido', 32, 64, lambda x, y, w, h: mix(hx('#1a1a1c'), hx('#2c2b2a'), .5 * ruido(x // 2, y // 3, 404)) if x % 8 else hx('#121213'))
mt('o_metal', 16, 16, lambda x, y, w, h: mix(hx('#3c3c40'), hx('#6a6a70'), ruido(x, y, 405)))
mt('o_bolsa', 32, 32, bolsa_f('#202022', '#111112', '#34343a', 406, aba=.6, tira=False), rep=False)
mt('o_sola', 16, 16, lambda x, y, w, h: hx('#0a0a0b') if (x + y) % 5 < 2 else hx('#1c1c1e'))
def simbolo_toka(w=64, h=48):                                       # "トカ" em amarelo sobre a placa preta (traços grossos, pixel art)
    img = bpy.data.images.new('o_toka', w, h, alpha=False); px = np.zeros((h, w, 4), np.float32); px[..., 3] = 1
    base = np.array(hx('#202024')) / 255; px[..., :3] = base
    def linha(x0, y0, x1, y1, t=3):
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        for i in range(n):
            x = x0 + (x1 - x0) * i / (n - 1); y = y0 + (y1 - y0) * i / (n - 1)
            for dx in range(-t // 2, t // 2 + 1):
                for dy in range(-t // 2, t // 2 + 1):
                    xx, yy = int(round(x + dx)), int(round(y + dy))
                    if 0 <= xx < w and 0 <= yy < h: px[h - 1 - yy, xx, :3] = np.array(hx(AMARELO)) / 255
    linha(14, 8, 14, 40); linha(14, 20, 26, 26)                    # ト
    linha(34, 16, 56, 16); linha(54, 16, 50, 40); linha(50, 40, 46, 37); linha(42, 8, 36, 40)   # カ
    img.pixels = px.ravel(); img.pack(); return img
material('o_toka_brilho', simbolo_toka(), repete=False)
def nucleo_f(x, y, w, h):                                          # núcleo do reator: círculo amarelo brilhante com anel
    d = math.hypot(x - w / 2 + .5, y - h / 2 + .5) / (w / 2)
    if d < .45: return mix(hx('#fff6c0'), hx(AMARELO), d / .45)
    if d < .6: return hx('#2a2a2e')
    if d < .8: return hx(AMARELO)
    return hx('#18181a')
mt('o_nucleo_brilho', 32, 32, nucleo_f, rep=False)

def costura_brilho(bm, pred, ponto, normal_, larg=.008):        # friso de energia: faixa de costura com o material de brilho (índice 1)
    faixa_costura(bm, pred, ponto, normal_, 1, larg=larg)

# ================================================================== TRAJE de baixo (preto, cobre o corpo todo)
bm = extrair(lambda f: REG[f.index] in ('camisa', 'calca')); afastar(bm, .008)
gola = bordas(bm, lambda e: all(W(v.co).z > 1.62 and abs(W(v.co).x) < .14 for v in e.verts))
if gola: extrudar_borda(bm, gola, (0, 0, .03))
for f in bm.faces: f.material_index = 0
traje = objeto(bm, 'traje', ['o_traje'], dens=6)
for p_ in traje.data.polygons: p_.use_smooth = True

# ================================================================== PEITORAL + COSTAS (placas com frisos de energia)
VB, PT = CINTURA + .05, 1.6
bm = extrair(lambda f: REG[f.index] == 'camisa' and tronco(f)); afastar(bm, .03)
for z in (VB, PT): cortar(bm, (0, 0, z), (0, 0, 1))
bmesh.ops.delete(bm, geom=[f for f in bm.faces if not (VB < centro(f).z < PT + .07)], context='FACES')
for f in bm.faces: f.material_index = 0
fr = lambda f: f.is_valid and normal(f).y < -.4
tr = lambda f: f.is_valid and normal(f).y > .4
costura_brilho(bm, fr, (0, 0, 1.36), (0, 0, 1)); costura_brilho(bm, fr, (0, 0, 1.22), (0, 0, 1))      # frisos horizontais (abdômen)
for s in (1, -1):
    costura_brilho(bm, lambda f, s=s: fr(f) and centro(f).z > 1.2, (s * TX * .62, 0, 0), Vector((1, 0, .35)).normalized())   # frisos diagonais do peito
    costura_brilho(bm, lambda f, s=s: f.is_valid and abs(normal(f).x) > .5 and centro(f).x * s > 0, (0, 0, 0), (0, 1, 0))     # friso lateral
    costura_brilho(bm, lambda f, s=s: tr(f) and centro(f).x * s > 0, (s * TX * .45, 0, 0), (1, 0, 0))                           # costas
INT, PAR = espessura(bm, bm.faces[:], .025)
for f in PAR + INT: f.material_index = 2 if f.is_valid else 0
peito = objeto(bm, 'peitoral', ['o_placa', 'o_brilho', 'o_placa2'], mat_de=lambda f: f.material_index, dens=6)
so_tronco(peito, ['spine', 'spine.001', 'spine.002', 'spine.003'])
SUP = bvh_de([peito])
hit = raio(SUP, Vector((0, -.2, 1.46)), F_)                         # símbolo "トカ" no peito (placa em relevo, luz própria)
b_ = bolsa_em(hit or Vector((0, -.25, 1.46)), F_, C_, .2, .14, .012, nx=2, nz=2); pesar(b_)
toka = objeto(b_, 'toka', ['o_toka_brilho'], uv=False)
so_tronco(toka, ['spine.002', 'spine.003'])

# ================================================================== GOLA blindada alta (esconde o corte do pescoço)
bm = bmesh.new(); uvl = bm.loops.layers.uv.verify(); NG = 16; an = []
for z, r in ((1.6, .16), (1.68, .14), (1.76, .125), (1.79, .135)):
    an.append([bm.verts.new(MWi @ Vector((r * math.sin(2 * math.pi * k / NG), .01 - r * .9 * math.cos(2 * math.pi * k / NG), z))) for k in range(NG)])
for j in range(len(an) - 1):
    for k in range(NG):
        f = bm.faces.new((an[j][k], an[j][(k + 1) % NG], an[j + 1][(k + 1) % NG], an[j + 1][k])); f.material_index = 1 if j == 2 and k % 4 == 0 else 0
bm.normal_update()
for f in bm.faces:
    c = W(f.calc_center_median())
    if Wn(f.normal).dot(Vector((c.x, c.y - .01, 0))) < 0: f.normal_flip()
espessura(bm, bm.faces[:], .015)
gola_o = objeto(bm, 'gola', ['o_placa2', 'o_brilho'], mat_de=lambda f: f.material_index, dens=8)
for v in gola_o.data.vertices:
    for g in list(v.groups): gola_o.vertex_groups[g.group].remove([v.index])
    z = (MW @ v.co).z; t = min(1, max(0, (z - 1.62) / .16))
    gola_o.vertex_groups['spine.003'].add([v.index], 1 - t * .6, 'REPLACE'); gola_o.vertex_groups['spine.004'].add([v.index], t * .6, 'REPLACE')

# ================================================================== OMBREIRAS, BRAÇADEIRAS e MANOPLAS
eh_braco = lambda f: dono(f).startswith(('upper_arm', 'forearm'))
for s in (1, -1):
    bm = extrair(lambda f, s=s: REG[f.index] == 'camisa' and (dono(f).startswith(('shoulder', 'upper_arm')) or tronco(f)) and centro(f).x * s > OMBRO.x - .13 and abs(centro(f).x) < OMBRO.x + .19 and normal(f).z > -.35 and centro(f).z > 1.38)
    afastar(bm, .07); espessura(bm, bm.faces[:], .04)                # ombreira grande e em blocos (como no conceito)
    for f in bm.faces: f.material_index = 0
    for f in bm.faces:
        if f.is_valid and abs(abs(centro(f).x) - (OMBRO.x + .06)) < .012 and normal(f).z > .3: f.material_index = 1
    ob = objeto(bm, 'ombreira', ['o_placa2', 'o_brilho'], mat_de=lambda f: f.material_index, dens=6)
    for xx, nome, esp_ in (((COTOVELO.x + .03, PULSO - .02), 'bracadeira', .022), ((OMBRO.x + .1, COTOVELO.x - .05), 'braco_placa', .016)):
        bm = extrair(lambda f, s=s, xx=xx: REG[f.index] == 'camisa' and eh_braco(f) and xx[0] < centro(f).x * s < xx[1])
        afastar(bm, .02); espessura(bm, bm.faces[:], esp_)
        for f in bm.faces: f.material_index = 0
        costura_brilho(bm, lambda f: f.is_valid and normal(f).z > .3, (s * (xx[0] + xx[1]) / 2, 0, 0), (1, 0, 0), .01)
        objeto(bm, nome, ['o_placa', 'o_brilho'], mat_de=lambda f: f.material_index, dens=8)
bm = extrair(lambda f: REG[f.index] == 'luva'); afastar(bm, .012)
for s in (1, -1):
    pu = bordas(bm, lambda e, s=s: all(abs(W(v.co).x - s * PULSO) < .01 for v in e.verts))
    if pu:
        vs = extrudar_borda(bm, pu, (-s * .04, 0, 0)); c0 = sum((W(v.co) for v in vs), Vector()) / len(vs)
        for v in vs: p = W(v.co); d = Vector((0, p.y - c0.y, p.z - c0.z)); v.co = MWi @ (p + d.normalized() * .015)
for f in bm.faces: f.material_index = 1 if normal(f).z > .55 and abs(abs(centro(f).x) - (PULSO + .05)) < .012 else 0
objeto(bm, 'manopla', ['o_placa2', 'o_brilho'], mat_de=lambda f: f.material_index, dens=10)

# ================================================================== CINTO + BOLSAS + TABARDO
bm = extrair(lambda f: REG[f.index] == 'calca'); afastar(bm, .02)
cortar(bm, (0, 0, CINTURA - .055), (0, 0, 1))
bmesh.ops.delete(bm, geom=[f for f in bm.faces if not (CINTURA - .055 < centro(f).z < CINTURA + .001)], context='FACES')
afastar(bm, .012); espessura(bm, bm.faces[:], .014)
for f in bm.faces: f.material_index = 0
for x in (-.035, .035): cortar(bm, (x, 0, 0), (1, 0, 0))
for f in extrudar(bm, [f for f in bm.faces if normal(f).y < -.7 and abs(centro(f).x) < .035 and centro(f).y < 0], .014): f.material_index = 1
cinto = objeto(bm, 'cinto', ['o_placa2', 'o_brilho'], mat_de=lambda f: f.material_index, dens=8); so_tronco(cinto, ['spine', 'spine.001'])
SUP = bvh_de([cinto, traje])
for x in (-.15, .15, -.1, .1):
    d_ = F_ if abs(x) < .12 else Vector((math.copysign(.8, x), -.6, 0)).normalized()
    hit = raio(SUP, Vector((x * 1.1, -.1 if abs(x) < .12 else 0, CINTURA - .06)), d_)
    b_ = bolsa_em(hit or Vector((x, -.2, CINTURA - .06)), d_, C_, .07, .08, .04); pesar(b_)
    so_tronco(objeto(b_, 'bolsa', ['o_bolsa'], uv=False), ['spine', 'spine.001'])
bm = bmesh.new(); uvl = bm.loops.layers.uv.verify(); NX, NZ = 5, 5          # tabardo: tecido da frente, do cinto até o joelho, barra rasgada
hit = raio(bvh_de([traje]), Vector((0, -.2, CINTURA - .03)), F_); y0 = (hit.y if hit else -.14) - .035
pts = [[None] * (NX + 1) for _ in range(NZ + 1)]
for j in range(NZ + 1):
    z = CINTURA - .03 - (CINTURA - .03 - (JOELHO + .03)) * j / NZ
    for i in range(NX + 1):
        x = -.085 + .17 * i / NX; rasgo = (.03 * ((i * 7) % 3) / 2) if j == NZ else 0
        pts[j][i] = bm.verts.new(MWi @ Vector((x * (1 + .15 * j / NZ), y0 - .015 * j / NZ, z + rasgo)))
for j in range(NZ):
    for i in range(NX):
        f = bm.faces.new((pts[j][i], pts[j][i + 1], pts[j + 1][i + 1], pts[j + 1][i]))
        for l, uv in zip(f.loops, ((i / NX, 1 - j / NZ), ((i + 1) / NX, 1 - j / NZ), ((i + 1) / NX, 1 - (j + 1) / NZ), (i / NX, 1 - (j + 1) / NZ))): l[uvl].uv = uv
bm.normal_update()
if sum(Wn(f.normal).y for f in bm.faces) > 0: bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
espessura(bm, bm.faces[:], .004)
tab = objeto(bm, 'tabardo', ['o_tecido'], uv=False)
for v in tab.data.vertices:                                        # metade quadril, metade coxas (cai entre as pernas ao andar)
    for g in list(v.groups): tab.vertex_groups[g.group].remove([v.index])
    p = MW @ v.co; t = min(1, max(0, (CINTURA - .03 - p.z) / (CINTURA - JOELHO)))
    tab.vertex_groups['spine'].add([v.index], 1 - t * .6, 'REPLACE')
    for s, L_ in ((1, 'L'), (-1, 'R')): tab.vertex_groups['thigh.' + L_].add([v.index], t * .3, 'REPLACE')

# ================================================================== PERNAS: coxas, joelheiras, canelas, coturnos
for s in (1, -1):
    for (z0, z1, nome, af, esp_) in ((JOELHO + .1, QUADRIL - .05, 'coxa', .025, .02), (JOELHO - .06, JOELHO + .07, 'joelheira', .04, .03), (BOTA + .02, JOELHO - .07, 'canela', .025, .02)):
        bm = extrair(lambda f, s=s, z0=z0, z1=z1: REG[f.index] == 'calca' and centro(f).x * s > 0 and z0 < centro(f).z < z1 and (normal(f).y < .3 or nome == 'canela'))
        if not bm.faces: continue
        afastar(bm, af); espessura(bm, bm.faces[:], esp_)
        for f in bm.faces: f.material_index = 0
        costura_brilho(bm, lambda f: f.is_valid and normal(f).y < -.4, (s * .1, 0, 0), (1, 0, 0), .009)
        objeto(bm, nome, ['o_placa', 'o_brilho'], mat_de=lambda f: f.material_index, dens=6)
bm = extrair(lambda f: REG[f.index] == 'bota'); afastar(bm, .022)
for v in bm.verts:
    p = W(v.co)
    if p.z < 0: v.co = MWi @ Vector((p.x, p.y, 0.0))
cortar(bm, (0, 0, .03), (0, 0, 1))
cano = bordas(bm, lambda e: all(abs(W(v.co).z - BOTA) < .01 for v in e.verts))
if cano: extrudar_borda(bm, cano, (0, 0, .03))
for f in bm.faces: f.material_index = 2 if centro(f).z < .03 else 0
for f in bm.faces:
    if f.material_index == 0 and normal(f).y < -.5 and .05 < centro(f).z < .09: f.material_index = 1
objeto(bm, 'coturno', ['o_placa2', 'o_brilho', 'o_sola'], mat_de=lambda f: f.material_index, dens=8)

# ================================================================== REATOR nas costas: moldura octogonal + núcleo + engrenagens + tubos
def cilindro(nome, c, eixo, r, comp, n, mats, mat_de=lambda k, lado: 0, pesos=('spine.002', 'spine.003'), dentes=0):
    bm = bmesh.new(); uvl = bm.loops.layers.uv.verify(); e = Vector(eixo).normalized()
    a_ = e.cross(Vector((0, 0, 1))) if abs(e.z) < .9 else e.cross(Vector((1, 0, 0))); a_.normalize(); b_ = e.cross(a_)
    an = []
    for t in (0, 1):
        anel_ = []
        for k in range(n):
            ang = 2 * math.pi * k / n; rr = r * (1.18 if dentes and k % 2 == 0 else 1)
            anel_.append(bm.verts.new(MWi @ (Vector(c) + e * comp * t + (a_ * math.cos(ang) + b_ * math.sin(ang)) * rr)))
        an.append(anel_)
    for k in range(n):
        f = bm.faces.new((an[0][k], an[0][(k + 1) % n], an[1][(k + 1) % n], an[1][k])); f.material_index = mat_de(k, 'lado')
        for l in f.loops: l[uvl].uv = (k / n, .5)
    for j, sentido in ((1, 1), (0, -1)):
        f = bm.faces.new(an[j] if sentido > 0 else an[j][::-1]); f.material_index = mat_de(0, 'tampa%d' % j)
        for l, k in zip(f.loops, range(n)): ang = 2 * math.pi * k / n; l[uvl].uv = (.5 + .5 * math.cos(ang), .5 + .5 * math.sin(ang))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    ob = objeto(bm, nome, mats, mat_de=lambda f: f.material_index, uv=False); so_tronco(ob, list(pesos)); return ob
YC = .16                                                           # costas
hit = raio(bvh_de([peito]), Vector((0, .3, 1.4)), -F_); yb = (hit.y if hit else .14)
cilindro('reator_base', (0, yb, 1.4), (0, 1, 0), .1, .05, 16, ['o_placa2'])
cilindro('reator_moldura', (0, yb + .045, 1.4), (0, 1, 0), .14, .025, 8, ['o_placa2', 'o_brilho'], mat_de=lambda k, lado: 1 if lado == 'tampa1' else 0)   # moldura octogonal com borda acesa
cilindro('reator_nucleo', (0, yb + .05, 1.4), (0, 1, 0), .065, .03, 16, ['o_placa2', 'o_nucleo_brilho'], mat_de=lambda k, lado: 1 if lado == 'tampa1' else 0)
for s in (1, -1):
    cilindro('engrenagem', (s * .15, yb + .02, 1.52), (0, 1, 0), .045, .03, 12, ['o_metal'], dentes=1)
    cilindro('tubo', (s * .17, yb, 1.25), (0, 0, 1), .028, .4, 8, ['o_placa2', 'o_brilho'], mat_de=lambda k, lado: 1 if lado == 'tampa1' else 0)
V = 1

# ================================================================== CABEÇA E PESCOÇO DO GODZILLA (recorte, redução pra PS1, olhos amarelos)
antes = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=os.path.join(OD, 'referencia/godzilla_original.glb'))
novos = [o for o in bpy.data.objects if o not in antes]
corpo_g = bpy.data.objects.get('Object_7'); olhos_g = [bpy.data.objects.get(n) for n in ('Object_8', 'Object_9')]
CORTE_Z, ESC_G = 42.0, .039
img_g = None
for nd in corpo_g.data.materials[0].node_tree.nodes:
    if nd.type == 'TEX_IMAGE': img_g = nd.image
GW, GH = img_g.size; TEXG = np.array(img_g.pixels[:], np.float32).reshape(GH, GW, 4)[..., :3]
mt('o_olho_brilho', 8, 8, lambda x, y, w, h: hx('#fff3a0') if (x, y) in ((3, 4), (4, 4)) else hx(AMARELO))
from mathutils.bvhtree import BVHTree
def cortar_original(ob):
    bm = bmesh.new(); bm.from_mesh(ob.data); bm.transform(ob.matrix_world)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, CORTE_Z - 1.0), plane_no=(0, 0, 1), clear_inner=True)
    bmesh.ops.triangulate(bm, faces=bm.faces[:]); bm.faces.ensure_lookup_table(); return bm
BM_ALTO = cortar_original(corpo_g); UV_ALTO = BM_ALTO.loops.layers.uv.active; BVH_ALTO = BVHTree.FromBMesh(BM_ALTO)
def cor_alta(p):                                                   # cor da cabeça ORIGINAL (2048 px) no ponto mais próximo
    loc, nor, i, d = BVH_ALTO.find_nearest(Vector(p))
    if i is None: return np.array([.1, .1, .1])
    f = BM_ALTO.faces[i]; a, b, c = [l.vert.co for l in f.loops]
    v0, v1, v2 = b - a, c - a, loc - a; d00, d01, d11, d20, d21 = v0.dot(v0), v0.dot(v1), v1.dot(v1), v2.dot(v0), v2.dot(v1)
    den = d00 * d11 - d01 * d01 or 1e-12; w1 = (d11 * d20 - d01 * d21) / den; w2 = (d00 * d21 - d01 * d20) / den; w0 = 1 - w1 - w2
    uv = f.loops[0][UV_ALTO].uv * w0 + f.loops[1][UV_ALTO].uv * w1 + f.loops[2][UV_ALTO].uv * w2
    x, y = min(GW - 1, max(0, int(uv.x * GW))), min(GH - 1, max(0, int(uv.y * GH)))
    return TEXG[max(0, y - 1):y + 2, max(0, x - 1):x + 2].reshape(-1, 3).mean(0)
def recorte(ob, alvo_tri, mat_i):
    me_ = ob.data.copy(); me_.transform(ob.matrix_world)
    bm = bmesh.new(); bm.from_mesh(me_)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, CORTE_Z), plane_no=(0, 0, 1), clear_inner=True)
    bm.to_mesh(me_); bm.free()
    tmp = bpy.data.objects.new('tmp', me_); bpy.context.scene.collection.objects.link(tmp)
    tri = sum(len(p.vertices) - 2 for p in me_.polygons)
    if tri > alvo_tri:
        md = tmp.modifiers.new('dec', 'DECIMATE'); md.ratio = alvo_tri / tri; md.use_collapse_triangulate = True
        bpy.context.view_layer.objects.active = tmp; bpy.ops.object.modifier_apply(modifier='dec')
    for p in tmp.data.polygons: p.material_index = mat_i
    return tmp
cabeca_g = recorte(corpo_g, 900, 0)
# UV NOVO e limpo: projeção CILÍNDRICA em volta do eixo vertical da cabeça (UMA ilha, emenda atrás) + cores da cabeça original
PB = np.array([tuple(v.co) for v in cabeca_g.data.vertices]); ZMAX = PB[:, 2].max()
CXX, CYY = PB[PB[:, 2] < CORTE_Z + 1.0][:, 0].mean(), PB[PB[:, 2] < CORTE_Z + 1.0][:, 1].mean()
uvl_ = cabeca_g.data.uv_layers.active.data
for poly in cabeca_g.data.polygons:
    us = []
    for li, vi in zip(poly.loop_indices, poly.vertices):
        p = cabeca_g.data.vertices[vi].co; th = math.atan2(p.x - CXX, -(p.y - CYY))
        us.append([.5 + th / (2 * math.pi), (p.z - CORTE_Z) / (ZMAX - CORTE_Z)])
    if max(u[0] for u in us) - min(u[0] for u in us) > .5:      # face que cruza a emenda (atrás): continua do outro lado
        for u in us:
            if u[0] < .5: u[0] += 1
    for li, u in zip(poly.loop_indices, us): uvl_[li].uv = (u[0], .02 + .96 * u[1])
TRG = 512; EXT = 64; posg = np.zeros((TRG, TRG + EXT, 3)); temg = np.zeros((TRG, TRG + EXT), bool)
uvs_ = cabeca_g.data.uv_layers.active.data
for poly in cabeca_g.data.polygons:
    vs_ = [cabeca_g.data.vertices[i].co for i in poly.vertices]; us_ = [uvs_[li].uv for li in poly.loop_indices]
    for k in range(1, len(vs_) - 1):
        T = [0, k, k + 1]; Pp = np.array([(us_[t].x * TRG, (1 - us_[t].y) * TRG) for t in T]); Q = np.array([tuple(vs_[t]) for t in T])
        x0, y0 = np.floor(Pp.min(0)).astype(int); x1, y1 = np.ceil(Pp.max(0)).astype(int)
        xs, ys = np.meshgrid(np.arange(max(x0, 0), min(x1, TRG + EXT - 1) + 1) + .5, np.arange(max(y0, 0), min(y1, TRG - 1) + 1) + .5)
        dd = (Pp[1, 1] - Pp[2, 1]) * (Pp[0, 0] - Pp[2, 0]) + (Pp[2, 0] - Pp[1, 0]) * (Pp[0, 1] - Pp[2, 1])
        if abs(dd) < 1e-9: continue
        l1 = ((Pp[1, 1] - Pp[2, 1]) * (xs - Pp[2, 0]) + (Pp[2, 0] - Pp[1, 0]) * (ys - Pp[2, 1])) / dd
        l2 = ((Pp[2, 1] - Pp[0, 1]) * (xs - Pp[2, 0]) + (Pp[0, 0] - Pp[2, 0]) * (ys - Pp[2, 1])) / dd
        l3 = 1 - l1 - l2; m = (l1 >= -.02) & (l2 >= -.02) & (l3 >= -.02)
        if not m.any(): continue
        L3 = np.stack([l1, l2, l3], -1)[m]; posg[(ys[m] - .5).astype(int), (xs[m] - .5).astype(int)] = L3 @ Q; temg[(ys[m] - .5).astype(int), (xs[m] - .5).astype(int)] = True
dobra = temg[:, TRG:] & ~temg[:, :EXT]                              # o que passou da emenda volta pro começo da textura
posg[:, :EXT][dobra] = posg[:, TRG:][dobra]; temg[:, :EXT] |= dobra
posg = posg[:, :TRG]; temg = temg[:, :TRG]
corg = np.zeros((TRG, TRG, 3), np.float32)
for Y, X in zip(*np.nonzero(temg)): corg[Y, X] = cor_alta(posg[Y, X])
lumg = corg.mean(-1, keepdims=True); corg = corg * .3 + lumg * .7               # pele cinza (tira o roxo/verde que vazava da boca)
corg = np.clip((corg * 3.4) ** .8 + .04, 0, 1)                    # a pele do original é quase preta: clareia pra escama aparecer no PS1
yy, xx = np.mgrid[0:TRG, 0:TRG]; cel = (xx + (yy // 10) % 2 * 5) // 10                     # escamas em blocos (fileiras deslocadas)
rnd_ = np.vectorize(lambda a, b: ruido(int(a), int(b), 407))(cel, yy // 10)
borda_ = ((xx + (yy // 10) % 2 * 5) % 10 == 0) | (yy % 10 == 0)
corg = corg * (.78 + .34 * rnd_[..., None]) * np.where(borda_, .62, 1.0)[..., None]   # sulco escuro entre as escamas
pre = corg.reshape(256, 2, 256, 2, 3).mean((1, 3)); m2 = temg.reshape(256, 2, 256, 2).mean((1, 3)); ok = m2 > 0
pre = np.where(ok[..., None], pre / np.maximum(m2[..., None], 1e-6), 0)
for _ in range(16):
    viz = np.zeros_like(pre); cnt = np.zeros(ok.shape)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        viz += np.roll(np.roll(pre * ok[..., None], dy, 0), dx, 1); cnt += np.roll(np.roll(ok, dy, 0), dx, 1)
    novo = (~ok) & (cnt > 0); pre[novo] = viz[novo] / cnt[novo][:, None]; ok = ok | novo
img_n = bpy.data.images.new('godzilla_cabeca', 256, 256, alpha=False); pxn = np.ones((256, 256, 4), np.float32)
pxn[..., :3] = np.round(pre[::-1] * 31) / 31; img_n.pixels.foreach_set(pxn.ravel()); img_n.pack()
img_n.filepath_raw = os.path.join(OD, 'texturas/godzilla_cabeca.png'); img_n.file_format = 'PNG'; img_n.save()
material('o_godzilla', img_n, repete=True)                         # repete: a emenda de trás continua do outro lado
partes = [cabeca_g] + [recorte(o, 40, 1) for o in olhos_g if o]
P_ = np.array([tuple(v.co) for v in partes[0].data.vertices])
base_ = P_[P_[:, 2] < CORTE_Z + .6]; cx, cy = base_[:, 0].mean(), base_[:, 1].mean()
ALVO_G = Vector((0, .0, 1.745))                                    # base do pescoço dentro da gola
ROT_G = Matrix.Rotation(math.radians(-14), 3, 'X')                 # levanta o focinho (o original olha pra baixo)
bm = bmesh.new(); uvl = bm.loops.layers.uv.verify()
for tmp in partes:
    uvs = tmp.data.uv_layers.active.data if tmp.data.uv_layers else None
    mapa = {}
    for v in tmp.data.vertices:
        p = v.co; q = ROT_G @ Vector((p.x - cx, p.y - cy, p.z - CORTE_Z))
        mapa[v.index] = bm.verts.new(MWi @ (ALVO_G + q * ESC_G))
    for p in tmp.data.polygons:
        try: f = bm.faces.new([mapa[i] for i in p.vertices])
        except ValueError: continue
        f.material_index = p.material_index
        for l, li in zip(f.loops, p.loop_indices): l[uvl].uv = uvs[li].uv if uvs else (.5, .5)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')   # vértices soltos do recorte
bm.normal_update()
BM_ALTO.free()
for o in novos + partes: bpy.data.objects.remove(o)
cab = objeto(bm, 'cabeca_godzilla', ['o_godzilla', 'o_olho_brilho'], mat_de=lambda f: f.material_index, uv=False)
for p_ in cab.data.polygons: p_.use_smooth = True
for v in cab.data.vertices:                                        # pescoço dividido: base com o pescoço, cabeça com o osso da cabeça
    for g in list(v.groups): cab.vertex_groups[g.group].remove([v.index])
    z = (MW @ v.co).z; t = min(1, max(0, (z - 1.76) / .08))
    cab.vertex_groups['spine.004'].add([v.index], 1 - t, 'REPLACE'); cab.vertex_groups['spine.005'].add([v.index], t, 'REPLACE')
print('GODZILLA: tri', sum(len(p.vertices) - 2 for p in cab.data.polygons), 'centro do corte', round(cx, 2), round(cy, 2))
for m in MATS.values(): m.use_backface_culling = True
bpy.data.objects.remove(corpo)
