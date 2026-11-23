# CORSA (executado dentro do vestir_personagem.py): corpo HUMANOIDE com a CABEÇA 3D do pardal (só a cabeça, recortada da
# digitalização "22_23 House Sparrow.glb": bico, olhos, plumagem e cores originais) + uniforme próprio:
# jaqueta de campanha comprida (até o meio da coxa) com bolsos de peito e de baixo, platinas; calça verde-oliva com bolso de coxa
# só à esquerda; suspensório em Y com cinto de lona, cantis atrás e porta-munição na frente; lenço militar quadriculado no
# pescoço (transição natural cabeça → corpo); coturno de couro marrom; luvas bege.
import numpy as np
PARDAL = os.environ.get('PARDAL_GLB', '')
# ---------------- paleta própria
material('c_jaqueta', textura('c_jaqueta', 64, 64, desgaste(tecido('#5f5238', '#403725', '#776a4c', 101), 102, .8)))
material('c_calca', textura('c_calca', 64, 64, desgaste(tecido('#4d5336', '#343924', '#656c48', 103), 104, .7)))
material('c_bolso', textura('c_bolso', 32, 32, bolsa_f('#665840', '#463c2a', '#7e7052', 105, aba=.62, tira=False)), repete=False)
material('c_fita', textura('c_fita', 32, 8, fita_f('#41472f', '#2b301f', 106, ponto=False)))
material('c_cinto', textura('c_cinto', 32, 8, fita_f('#4b5038', '#30331f', 107, ponto=False)))
material('c_bota', textura('c_bota', 32, 32, lambda x, y, w, h: mix(hx('#4a3020'), hx('#6e4a30'), .55 * ruido(x // 2, y // 2, 108)) if y % 13 else hx('#3a2618')))
material('c_sola', textura('c_sola', 16, 16, lambda x, y, w, h: hx('#6b5c48') if (x + y) % 5 < 2 else hx('#4c4234')))
material('c_luva', textura('c_luva', 32, 32, lambda x, y, w, h: mix(hx('#8f7c58'), hx('#b09c74'), .5 * ruido(x // 2, y // 2, 109)) if y % 8 else hx('#7a6a4a')))
def lenco_f(x, y, w, h):                                           # lenço militar quadriculado (caqui e verde-oliva)
    c = mix(hx('#b3a37b'), hx('#9e8e68'), .4 * ruido(x // 2, y // 2, 110))
    if x % 8 in (0, 1) or y % 8 in (0, 1): c = mix(hx('#4c5236'), c, .3)
    if x % 8 in (0, 1) and y % 8 in (0, 1): c = hx('#3a3f29')
    return c
material('c_lenco', textura('c_lenco', 32, 32, lenco_f))
material('c_cantil', textura('c_cantil', 32, 32, bolsa_f('#4b5038', '#30331f', '#626a49', 111, aba=.7, tira=False)), repete=False)
material('c_metal', textura('c_metal', 8, 8, preto_f('#77766c', '#b3b1a4', 112)))
material('c_pena', textura('c_pena', 16, 16, lambda x, y, w, h: mix(hx('#5a4634'), hx('#8a7456'), .6 * ruido(x // 2, y, 113)) if (x + 2 * y) % 5 else hx('#3e3024')))

# ---------------- JAQUETA de campanha: manga comprida, saia até o meio da coxa, bolsos de peito e de baixo, platinas
bm = extrair(lambda f: REG[f.index] == 'camisa'); afastar(bm, .016)
barra_j = bordas(bm, lambda e: all(abs(W(v.co).z - CINTURA) < .012 and abs(W(v.co).x) < .3 for v in e.verts))
saia = []
if barra_j:
    vs = extrudar_borda(bm, barra_j, (0, 0, -.11)); saia += extrudar_borda.faces
    c0 = sum((W(v.co) for v in vs), Vector()) / len(vs)
    for v in vs: p = W(v.co); d = Vector((p.x - c0.x, p.y - c0.y, 0)); v.co = MWi @ (p + d.normalized() * .012)
    vs2 = extrudar_borda(bm, [e for e in bm.edges if e.is_boundary and all(v in vs for v in e.verts)], (0, 0, -.12)); saia += extrudar_borda.faces
    for v in vs2: p = W(v.co); d = Vector((p.x - c0.x, p.y - c0.y, 0)); v.co = MWi @ (p + d.normalized() * .014)
gola_ = bordas(bm, lambda e: all(W(v.co).z > 1.62 and abs(W(v.co).x) < .14 for v in e.verts))
if gola_:                                                          # gola virada (dobrada pra fora)
    vs = extrudar_borda(bm, gola_, (0, 0, .02)); c0 = sum((W(v.co) for v in vs), Vector()) / len(vs)
    for v in vs: p = W(v.co); d = Vector((p.x - c0.x, p.y - c0.y, 0)); v.co = MWi @ (p + (d.normalized() * .02 if d.length > 1e-6 else Vector()))
frente_t = lambda f: tronco(f) and normal(f).y < -.6 and centro(f).y < 0
for s in (1, -1):                                                  # bolsos do peito (abas) e bolsos de baixo (na saia)
    for x in (s * .045, s * .135): cortar(bm, (x, 0, 0), (1, 0, 0), [f for f in bm.faces if frente_t(f)])
for z in (1.43, 1.54): cortar(bm, (0, 0, z), (0, 0, 1), [f for f in bm.faces if frente_t(f)])
for s in (1, -1):
    fs = [f for f in bm.faces if frente_t(f) and 1.43 < centro(f).z < 1.54 and .045 < centro(f).x * s < .135]
    for f in extrudar(bm, fs, .012): f.material_index = 1
fr_saia = lambda f: f in set(saia) and normal(f).y < -.5
for f in bm.faces:
    if f.is_valid and fr_saia(f): f.material_index = 1
ombro_t = lambda f: tronco(f) and normal(f).z > .6 and .08 < abs(centro(f).x) < .21
for f in extrudar(bm, [f for f in bm.faces if ombro_t(f)], .005): f.material_index = 2   # platinas
jaqueta = objeto(bm, 'jaqueta', ['c_jaqueta', 'c_bolso', 'c_fita'], mat_de=lambda f: f.material_index)
for v in jaqueta.data.vertices:                                     # a saia da jaqueta segue o quadril (não rasga entre as pernas)
    p = MW @ v.co
    if p.z < CINTURA + .01:                                         # metade quadril, metade coxa: a saia cai por cima da perna ao sentar e andar
        gs = [(jaqueta.vertex_groups[g.group].name, g.weight) for g in v.groups]
        for n_, w_ in gs:
            if n_.startswith('shin'): jaqueta.vertex_groups[n_].remove([v.index])
            elif n_.startswith('thigh'): jaqueta.vertex_groups[n_].add([v.index], w_ * .5, 'REPLACE')
        jaqueta.vertex_groups['spine'].add([v.index], .5, 'ADD')

# ---------------- CALÇA verde-oliva, reta, barra dentro do coturno; bolso de coxa só na esquerda (aba inclinada)
bm = extrair(lambda f: REG[f.index] == 'calca'); afastar(bm, .013)
barra = bordas(bm, lambda e: all(abs(W(v.co).z - BOTA) < .01 for v in e.verts))
if barra: extrudar_borda(bm, barra, (0, 0, -.025))
lado = lambda f: dono(f).startswith('thigh') and normal(f).x > .55 and centro(f).x > 0
for z in (JOELHO + .1, JOELHO + .22): cortar(bm, (0, 0, z), (0, 0, 1), [f for f in bm.faces if lado(f)])
for f in extrudar(bm, [f for f in bm.faces if lado(f) and JOELHO + .1 < centro(f).z < JOELHO + .22], .018): f.material_index = 1
calca = objeto(bm, 'calca', ['c_calca', 'c_bolso'], mat_de=lambda f: f.material_index)
# ---------------- COTURNO de couro marrom, sola clara
bm = extrair(lambda f: REG[f.index] == 'bota'); afastar(bm, .017)
for v in bm.verts:
    p = W(v.co)
    if p.z < 0: v.co = MWi @ Vector((p.x, p.y, 0.0))
cortar(bm, (0, 0, .02), (0, 0, 1))
cano = bordas(bm, lambda e: all(abs(W(v.co).z - BOTA) < .01 for v in e.verts))
if cano: extrudar_borda(bm, cano, (0, 0, .015))
objeto(bm, 'bota', ['c_bota', 'c_sola'], mat_de=lambda f: 1 if centro(f).z < .02 else 0)
# ---------------- LUVAS bege
bm = extrair(lambda f: REG[f.index] == 'luva'); afastar(bm, .006)
for s in (1, -1):
    pu = bordas(bm, lambda e, s=s: all(abs(W(v.co).x - s * PULSO) < .01 for v in e.verts))
    if pu:
        vs = extrudar_borda(bm, pu, (-s * .03, 0, 0)); c0 = sum((W(v.co) for v in vs), Vector()) / len(vs)
        for v in vs: p = W(v.co); d = Vector((0, p.y - c0.y, p.z - c0.z)); v.co = MWi @ (p + d.normalized() * .012)
objeto(bm, 'luva', ['c_luva'], dens=8)
# ---------------- CINTO de lona com fivela
bm = extrair(lambda f: REG[f.index] == 'calca'); afastar(bm, .013)
cortar(bm, (0, 0, CINTURA - .05), (0, 0, 1))
bmesh.ops.delete(bm, geom=[f for f in bm.faces if not (CINTURA - .05 < centro(f).z < CINTURA - .005)], context='FACES')
afastar(bm, .03); espessura(bm, bm.faces[:], .008)                 # por cima da saia da jaqueta
for x in (-.022, .022): cortar(bm, (x, 0, 0), (1, 0, 0))
for f in extrudar(bm, [f for f in bm.faces if normal(f).y < -.7 and abs(centro(f).x) < .022 and centro(f).y < 0], .008): f.material_index = 1
cinto = objeto(bm, 'cinto', ['c_cinto', 'c_metal'], mat_de=lambda f: f.material_index, dens=8); so_tronco(cinto, ['spine', 'spine.001'])
# ---------------- SUSPENSÓRIO EM Y: dois na frente (cinto → ombros), juntam atrás no meio das costas e descem até o cinto
SUP = bvh_de([jaqueta, cinto, calca])
for s in (1, -1):
    g_ = [(Vector((s * .1, -.1, CINTURA - .02)), F_), (Vector((s * .11, -.1, 1.35)), F_), (Vector((s * .11, -.1, 1.58)), F_),
          (Vector((s * .1, -.04, 1.70)), (F_ + C_).normalized()), (Vector((s * .09, .03, 1.76)), C_), (Vector((s * .07, .1, 1.64)), T_), (Vector((0, .1, 1.52)), T_)]
    bms, fs_, _ = faixa(g_, .036, .008, passos=4); espessura(bms, fs_, .004)
    for t in (.3,):                                                # fivela de ajuste na frente
        for f in extrudar(bms, [fs_[int(len(fs_) * t)]], .006): f.material_index = 1
    pesar(bms); so_tronco(objeto(bms, 'suspensorio', ['c_fita', 'c_metal'], mat_de=lambda f: f.material_index, dens=10), ['spine', 'spine.001', 'spine.002', 'spine.003'])
bms, fs_, _ = faixa([(Vector((0, .1, 1.53)), T_), (Vector((0, .1, 1.35)), T_), (Vector((0, .1, CINTURA - .02)), T_)], .04, .008, passos=4)
espessura(bms, fs_, .004); pesar(bms); so_tronco(objeto(bms, 'suspensorio_tras', ['c_fita'], dens=10), ['spine', 'spine.001', 'spine.002'])
# cantis nos dois lados de trás + porta-munição na frente (assimétrico: dois à direita, um à esquerda)
SUP = bvh_de([jaqueta, cinto, calca])
for s in (1, -1):
    d_ = Vector((s * .65, .76, 0)).normalized(); hit = raio(SUP, Vector((s * .13, .1, CINTURA - .07)), d_)
    b_ = bolsa_em(hit or Vector((s * .15, .15, CINTURA - .07)), d_, C_, .1, .13, .07, nx=2, nz=3); pesar(b_)
    so_tronco(objeto(b_, 'cantil', ['c_cantil'], uv=False), ['spine', 'spine.001'])
for x in (-.15, -.085, .12):
    hit = raio(SUP, Vector((x, -.1, CINTURA - .065)), F_)
    b_ = bolsa_em(hit or Vector((x, -.2, CINTURA - .065)), F_, C_, .055, .07, .035); pesar(b_)
    so_tronco(objeto(b_, 'porta_municao', ['c_bolso'], uv=False), ['spine', 'spine.001'])

# ---------------- CABEÇA DO PARDAL (só a cabeça: recorte por um cilindro no eixo bico → nuca; corpo, asas, pernas e cauda ficam de fora)
antes = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=PARDAL)
pd = [o for o in bpy.data.objects if o not in antes and o.type == 'MESH'][0]; PM = pd.matrix_world.copy()
for o in [o for o in bpy.data.objects if o not in antes and o != pd]: bpy.data.objects.remove(o)
BICO = Vector((-.0171, -.0284, -.0223)); NUCA = Vector((-.013, -.045, -.002)); LC, RC = .036, .016
EIXO = (NUCA - BICO).normalized()
bmh = bmesh.new(); bmh.from_mesh(pd.data)
def fora_cab(v):
    p = PM @ v.co; t = (p - BICO).dot(EIXO); r = ((p - BICO) - EIXO * t).length
    return t < -.002 or t > LC or r > RC * (.55 + .45 * min(1, t / .012))
bmesh.ops.delete(bmh, geom=[v for v in bmh.verts if fora_cab(v)], context='VERTS')
# pedaços soltos (pontas de pena que caíram no cilindro mas não são da cabeça): fica só a maior ilha
ilhas, vis = [], set()
for v in bmh.verts:
    if v in vis: continue
    pilha, ilha = [v], []
    while pilha:
        a = pilha.pop()
        if a in vis: continue
        vis.add(a); ilha.append(a); pilha += [e.other_vert(a) for e in a.link_edges]
    ilhas.append(ilha)
fiapos = [i for i in ilhas if len(i) < 8]                         # a digitalização tem várias ilhas: só os fiapos (< 8 vértices) saem
bmesh.ops.delete(bmh, geom=[v for i in fiapos for v in i], context='VERTS'); ilhas = [i for i in ilhas if len(i) >= 8] + [None] * len(fiapos)
antes_f = len(bmh.faces); bmesh.ops.holes_fill(bmh, edges=bmh.edges[:], sides=9)          # fecha os furos pequenos da digitalização (a nuca aberta, maior, fica)
print('pardal: furos fechados', len(bmh.faces) - antes_f)
print('pardal: cabeça com', len(bmh.verts), 'vértices,', len(bmh.faces), 'faces; fiapos descartados', len(fiapos))
# orientação: bico pra frente (-Y), alto da cabeça pra cima; escala de cabeça humana; centro sobre o pescoço
CEN_P = sum((PM @ v.co for v in bmh.verts), Vector()) / len(bmh.verts)          # centro da cabeça (média dos vértices)
# a digitalização já tem a cabeça DE PÉ: bico pra -Y, alto da cabeça pra +Z, olhos nos lados (±X) → só escala e posição (sem girar)
CEN_P = sum((PM @ v.co for v in bmh.verts), Vector()) / len(bmh.verts)
PONTA = min((PM @ v.co for v in bmh.verts), key=lambda p: p.y)       # ponta do bico (o ponto mais à frente)
print('pardal: ponta do bico', [round(c, 4) for c in PONTA], 'centro', [round(c, 4) for c in CEN_P])
lado_p, frente_p, cima_p = Vector((1, 0, 0)), Vector((0, -1, 0)), Vector((0, 0, 1))
# tampa da nuca: o recorte deixa a parte de trás aberta → fecha o buraco grande (a tampa herda as cores da plumagem em volta)
bmesh.ops.holes_fill(bmh, edges=bmh.edges[:], sides=200)
R_src = Matrix((lado_p, frente_p, cima_p))                          # linhas: eixos do pardal
ESC_P = float(os.environ.get('PARDAL_ESC', '10.5')); CENTRO_P = CEN_P
ALVO_C = Vector((0, -.005, 1.86))
uvp = bmh.loops.layers.uv.active
for v in bmh.verts:
    q = R_src @ (PM @ v.co - CENTRO_P)                                # coordenadas do pardal: (lado, frente, cima)
    v.co = MWi @ (ALVO_C + Vector((q.x, -q.y, q.z)) * ESC_P)          # frente do pardal → -Y do personagem
bmesh.ops.recalc_face_normals(bmh, faces=bmh.faces)
# textura original do pardal, reduzida pra PS1 e clareada (a digitalização é escura)
img0 = None
for m in pd.data.materials:
    if m and m.use_nodes:
        for n in m.node_tree.nodes:
            if n.type == 'TEX_IMAGE' and n.image and img0 is None: img0 = n.image
img = img0.copy(); img.scale(128, 128)
px = np.empty(128 * 128 * 4, dtype=np.float32); img.pixels.foreach_get(px)
px = px.reshape(-1, 4); px[:, :3] = np.clip(px[:, :3] * 1.55 + .03, 0, 1); px[:, :3] = np.round(px[:, :3] * 31) / 31
img.pixels.foreach_set(px.ravel()); img.pack()
material('c_pardal', img, repete=False)
bmesh.ops.delete(bmh, geom=[v for v in bmh.verts if not v.link_faces], context="VERTS")   # vértices soltos da digitalização
me = bpy.data.meshes.new('cabeca_pardal'); bmh.to_mesh(me); bmh.free()
for p in me.polygons: p.use_smooth = False
me.materials.append(MATS['c_pardal'])
cab = bpy.data.objects.new('cabeca_pardal', me); bpy.context.scene.collection.objects.link(cab); cab.parent = rig; cab.matrix_world = MW
md = cab.modifiers.new('rig', 'ARMATURE'); md.object = rig
tudo_no_osso(cab, 'spine.005')
bpy.data.objects.remove(pd)
# PESCOÇO emplumado (fecha a nuca aberta do recorte e liga a cabeça ao corpo) + LENÇO por cima da junção
bmn = bmesh.new(); N_ = 10; aneis_ = []
for j, (z, r) in enumerate(((1.70, .072), (1.745, .066), (1.79, .058))):
    aneis_.append([bmn.verts.new(MWi @ Vector((r * math.cos(2 * math.pi * k / N_), -.005 + r * .95 * math.sin(2 * math.pi * k / N_), z))) for k in range(N_)])
for j in range(len(aneis_) - 1):
    for k in range(N_): bmn.faces.new((aneis_[j][k], aneis_[j][(k + 1) % N_], aneis_[j + 1][(k + 1) % N_], aneis_[j + 1][k]))
bmesh.ops.recalc_face_normals(bmn, faces=bmn.faces)
pesc_ = objeto(bmn, 'pescoco_penas', ['c_pena'], dens=20); tudo_no_osso(pesc_, 'spine.004')
bml = bmesh.new(); N_ = 14; aneis_ = []                             # lenço: dois anéis frouxos + nó com as pontas caindo no peito
for j, (z, r) in enumerate(((1.665, .105), (1.705, .097), (1.735, .086))):
    aneis_.append([bml.verts.new(MWi @ Vector(((r + .006 * math.sin(k * 2.3 + j)) * math.cos(2 * math.pi * k / N_), -.005 + (r + .006 * math.sin(k * 2.3 + j)) * math.sin(2 * math.pi * k / N_), z))) for k in range(N_)])
for j in range(len(aneis_) - 1):
    for k in range(N_): bml.faces.new((aneis_[j][k], aneis_[j][(k + 1) % N_], aneis_[j + 1][(k + 1) % N_], aneis_[j + 1][k]))
k_fr = min(range(N_), key=lambda k: abs(math.sin(2 * math.pi * k / N_) + 1))
topo_ = MW @ aneis_[0][k_fr].co
for dx, dz, ln in ((-.02, -.1, .03), (.025, -.085, .028)):           # duas pontas do nó, de comprimentos diferentes
    q = [topo_ + Vector((dx - ln / 2, -.01, 0)), topo_ + Vector((dx + ln / 2, -.01, 0)), topo_ + Vector((dx + .004, -.03, dz)), topo_ + Vector((dx - .006, -.028, dz + .01))]
    bml.faces.new([bml.verts.new(MWi @ p) for p in q])
bmesh.ops.recalc_face_normals(bml, faces=bml.faces)
espessura(bml, bml.faces[:], .006)
lenco = objeto(bml, 'lenco', ['c_lenco'], dens=8); tudo_no_osso(lenco, 'spine.003')
# o corpo base fica sem nada à mostra (a roupa e o pescoço emplumado cobrem tudo)
bpy.data.objects.remove(corpo)                                     # o corpo base fica todo coberto (roupa + pescoço emplumado): sai do arquivo
for m in MATS.values(): m.use_backface_culling = True
MATS['c_pardal'].use_backface_culling = False                       # a digitalização tem normais desencontradas: as duas faces aparecem
