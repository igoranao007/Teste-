# DOD — farda militar MODELADA sobre a anatomia do próprio Dod (corpo = material/modelos/personagem-simples.glb).
# Fluxo de roupa de jogo: cada peça nasce da superfície do corpo (duplicar → afastar → dar espessura → cortar/inserir/extrudar),
# então segue exatamente as proporções do Dod. Pesos de osso herdados do corpo: as peças acompanham o esqueleto.
# Referências visuais (não usadas como malha): soldados PSX pesquisados no itch.io (CSAF Fort Vale rifleman, OpenGameArt low poly soldier).
# Uso: blender -b -P tools/blender/vestir_dod.py -- <saida.glb> [pasta_renders]   (COR=MATERIAL|TEXTURE pros renders)
import bpy, bmesh, sys, os, math, collections, random
from mathutils import Vector, Matrix
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
V = int(os.environ.get('VERSAO', '1'))           # 1: farda base · 2: + gola alta, poncho, alça diagonal, bolsas · 3: + paleta, costuras e detalhes
AQUI = os.path.dirname(os.path.abspath(__file__))

ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
SAIDA = ARGS[0] if ARGS else '/tmp/dod_farda.glb'
RENDERS = ARGS[1] if len(ARGS) > 1 else None
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
FONTE = os.path.join(RAIZ, 'material/modelos/personagem-simples.glb')

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=FONTE)
for o in list(bpy.data.objects):
    if o.name.startswith('Icosphere'): bpy.data.objects.remove(o)
corpo, bracos = bpy.data.objects['body'], bpy.data.objects['arms']
rig = corpo.parent
for o in bpy.data.objects: o.select_set(False)
corpo.select_set(True); bracos.select_set(True); bpy.context.view_layer.objects.active = corpo
bpy.ops.object.join()                                          # braços + corpo numa malha só (grupos casam pelo nome)
MW = corpo.matrix_world.copy(); MWi = MW.inverted(); R3 = MW.to_3x3(); R3i = R3.inverted()
ESC = MW.to_scale()[0]
def L(m): return m / ESC                                       # metros (mundo) → unidades locais
def W(v): return MW @ v                                        # ponto local → mundo
def Wn(n): return (R3 @ n).normalized()                        # direção local → mundo
def Lp(p): return MWi @ Vector(p)
def Ln(n): return (R3i @ Vector(n)).normalized()
GN = {g.index: g.name for g in corpo.vertex_groups}

# ------------------------------------------------------------------ medidas da anatomia do Dod (mundo, metros; frente = -Y, cima = +Z)
def osso(n): return rig.matrix_world @ rig.data.bones[n].head_local
QUADRIL = osso('thigh.L').z
CINTURA = QUADRIL + .10            # topo da calça / cinto
JOELHO = osso('shin.L').z
BOTA = .27                         # topo do cano do coturno
PULSO = abs(osso('hand.L').x) - .015
OMBRO = osso('upper_arm.L')        # junta do ombro esquerdo
COTOVELO = osso('forearm.L')

bm0 = bmesh.new(); bm0.from_mesh(corpo.data)
bmesh.ops.recalc_face_normals(bm0, faces=bm0.faces)
DL = bm0.verts.layers.deform.active

def tudo(bm): return bm.verts[:] + bm.edges[:] + bm.faces[:]
def geom_de(faces):
    vs, es = set(), set()
    for f in faces: vs.update(f.verts); es.update(f.edges)
    return list(vs) + list(es) + list(faces)
def cortar(bm, ponto, normal, faces=None):                     # corte plano (bisect) só nas faces dadas
    bmesh.ops.bisect_plane(bm, geom=geom_de(faces) if faces is not None else tudo(bm), plane_co=Lp(ponto), plane_no=Ln(normal))
def centro(f): return W(f.calc_center_median())
def normal(f): return Wn(f.normal)

CAMADAS = [None]
def dono(f):                                                    # osso dominante da face (serve pra qualquer bmesh desta execução)
    c = collections.Counter()
    for camada in (CAMADAS[0], DL):
        try:
            for v in f.verts:
                for gi, w in v[camada].items(): c[GN[gi]] += w
            break
        except Exception: c.clear()
    return c.most_common(1)[0][0] if c else '-'
def tronco(f): return dono(f).startswith(('spine', 'shoulder', 'pelvis', 'breast')) and abs(centro(f).x) < .3

for z in (CINTURA, BOTA): cortar(bm0, (0, 0, z), (0, 0, 1))  # bordas retas onde uma peça encontra a outra
for s in (1, -1): cortar(bm0, (s * PULSO, 0, 0), (1, 0, 0))
TX = max(abs(W(v.co).x) for f in bm0.faces if tronco(f) and 1.3 < centro(f).z < 1.5 for v in f.verts)   # meia-largura do tronco
print('medidas: quadril %.3f cintura %.3f joelho %.3f bota %.3f pulso %.3f tronco±%.3f' % (QUADRIL, CINTURA, JOELHO, BOTA, PULSO, TX))

def regiao(f):
    b, c = dono(f), centro(f)
    if b in ('spine.004', 'spine.005'): return 'pescoco'
    if abs(c.x) > PULSO and c.z > 1.3: return 'luva'
    if b.startswith(('upper_arm', 'forearm', 'shoulder', 'spine', 'breast')): return 'camisa'
    if b.startswith('pelvis'): return 'camisa' if c.z > CINTURA else 'calca'
    if b.startswith('thigh'): return 'calca'
    if b.startswith('shin'): return 'bota' if c.z < BOTA else 'calca'
    if b.startswith(('foot', 'toe', 'heel')): return 'bota'
    return 'camisa'
REG = {f.index: regiao(f) for f in bm0.faces}
print('faces por região', dict(collections.Counter(REG.values())))

def extrair(pred, fonte=None):
    src = fonte or bm0; bm = src.copy(); bm.faces.ensure_lookup_table()
    mapa = {i: f for i, f in enumerate(bm.faces)}
    if fonte is None: fora = [mapa[f.index] for f in src.faces if not pred(f)]
    else: fora = [f for f in bm.faces if not pred(f)]
    bmesh.ops.delete(bm, geom=fora, context='FACES')
    CAMADAS[0] = bm.verts.layers.deform.active
    return bm
def afastar(bm, m, verts=None):                                # empurra a casca pra fora pela normal do vértice (m em metros)
    bm.normal_update()
    for v in (verts or bm.verts): v.co += v.normal * L(m)
def caixa(bm, rot=''):
    ps = [W(v.co) for v in bm.verts]
    if ps: print('  [%s] verts %d faces %d  x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f' % (rot, len(bm.verts), len(bm.faces), min(p.x for p in ps), max(p.x for p in ps), min(p.y for p in ps), max(p.y for p in ps), min(p.z for p in ps), max(p.z for p in ps)))
def extrudar(bm, faces, m, normal_unica=True):                 # extruda a região e empurra (volume real)
    if not faces: return []
    n = Vector()
    for f in faces: n += f.normal * f.calc_area()
    n.normalize()
    ret = bmesh.ops.extrude_face_region(bm, geom=faces)
    vs = [e for e in ret['geom'] if isinstance(e, bmesh.types.BMVert)]
    if normal_unica:
        for v in vs: v.co += n * L(m)
    else:
        bm.normal_update()
        for v in vs: v.co += v.normal * L(m)
    return [e for e in ret['geom'] if isinstance(e, bmesh.types.BMFace)]
def espessura(bm, faces, m):                                   # dá volume: casca de dentro (pela normal do vértice) + parede nas bordas
    bm.normal_update(); fs = set(faces); novo = {}
    for f in faces:
        for v in f.verts:
            if v not in novo: novo[v] = bm.verts.new(v.co - v.normal * L(m), v)
    internas, paredes = [], []
    for f in faces:
        try: internas.append(bm.faces.new([novo[v] for v in reversed(f.verts)], f))
        except ValueError: pass
    for e in {e for f in faces for e in f.edges}:
        lig = [f for f in e.link_faces if f in fs]
        if len(lig) != 1: continue
        f = lig[0]; a, b = e.verts
        for l in f.loops:                                          # mantém a ordem da face pra parede ficar virada pra fora
            if l.vert is a and l.link_loop_next.vert is b: break
            if l.vert is b and l.link_loop_next.vert is a: a, b = b, a; break
        try: paredes.append(bm.faces.new([b, a, novo[a], novo[b]], f))
        except ValueError: pass
    return internas, paredes
def bordas(bm, pred=lambda e: True): return [e for e in bm.edges if e.is_boundary and pred(e)]
def extrudar_borda(bm, edges, desloc):                         # extruda uma borda aberta (gola, punho, barra) e move (vetor em metros)
    ret = bmesh.ops.extrude_edge_only(bm, edges=edges)
    vs = [e for e in ret['geom'] if isinstance(e, bmesh.types.BMVert)]
    d = R3i @ Vector(desloc)                                   # metros do mundo → local
    for v in vs: v.co += d
    extrudar_borda.faces = [e for e in ret['geom'] if isinstance(e, bmesh.types.BMFace)]
    return vs

# ------------------------------------------------------------------ texturas PSX (64 px, paleta de 15 bits, pontilhado Bayer, filtro Closest)
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
rnd = random.Random(7)
def hx(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
def mix(a, b, t): return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))
def textura(nome, w, h, fn):
    img = bpy.data.images.new(nome, w, h, alpha=False); px = []
    for y in range(h):
        for x in range(w):
            r, g, b = fn(x, y, w, h)
            d = (BAYER[y % 4][x % 4] / 16 - .5) * 8                      # pontilhado ordenado antes de cortar pra 5 bits
            px += [min(255, max(0, round((c + d) / 8) * 8)) / 255 for c in (r, g, b)] + [1]
    img.pixels = px; img.pack(); return img
def ruido(x, y, s=1):
    n = (x * 374761393 + y * 668265263 + s * 982451653) & 0xffffffff; n = (n ^ (n >> 13)) * 1274126177 & 0xffffffff
    return (n & 0xffff) / 65535
def tecido(base, esc, clara, s):
    B, E, C = hx(base), hx(esc), hx(clara)
    def f(x, y, w, h):
        k = ruido(x // 2, y // 2, s); dobra = .5 + .5 * math.sin(x * .35 + math.sin(y * .19) * 2.4) * math.sin(y * .11 + x * .04)
        c = mix(E, B, .55 + .45 * dobra); c = mix(c, C, .25) if k > .9 else c
        if (x + y * 3) % 7 == 0 and k > .5: c = mix(c, E, .4)                # trama
        return c
    return f
def colete_f(x, y, w, h):                                         # MOLLE: faixas horizontais de fita com costuras verticais
    B, E, C = hx('#3b4629'), hx('#262e1a'), hx('#56613c')
    c = mix(B, C, .3 * ruido(x // 2, y // 2, 4))
    yy = y % 8
    if yy in (0, 1): c = mix(E, B, .25)                               # vão entre as fitas
    if yy == 2: c = mix(C, B, .4)                                     # borda de cima da fita (luz)
    if yy in (3, 4, 5, 6) and x % 10 == 0: c = mix(E, B, .45)         # costura (bartack)
    return c
def bolso_f(x, y, w, h):                                          # um bolso inteiro: costura na borda, aba escura em cima com a borda clara, fecho
    B, E, C = hx('#5a6340'), hx('#353c25'), hx('#737d52')
    v = y / (h - 1)                                                # 0 embaixo, 1 em cima (no Blender a linha 0 do pixel é a de baixo)
    c = mix(B, C, .35 * ruido(x // 2, y // 2, 5))
    if v > .68: c = mix(c, E, .35)                                 # aba
    if abs(v - .68) < .04: c = mix(E, B, .2)                       # borda da aba (sombra)
    if x in (1, w - 2) or y in (1, h - 2): c = mix(E, B, .4)       # costura
    if abs(x - w / 2) < 2 and .6 < v < .76: c = hx('#1c1d18')       # fecho (presilha)
    return c
def preto_f(base, luz, s):
    B, C = hx(base), hx(luz)
    return lambda x, y, w, h: mix(B, C, .5 * ruido(x // 2, y // 2, s) ** 2)
def cinto_f(x, y, w, h):
    B, C = hx('#1d1e1b'), hx('#3a3b36')
    c = mix(B, C, .3 * ruido(x, y // 2, 8))
    if y % 16 in (2, 13): c = mix(C, B, .3)                           # costura dupla da fita
    return c
def sola_f(x, y, w, h):
    B, E = hx('#2c2c2e'), hx('#101012')
    return E if (x + y) % 6 < 2 else B                               # cravo do solado
def bandeira_f(x, y, w, h):                                       # Israel: branco, 2 faixas azuis, estrela de Davi; costura verde-oliva
    if x in (0, w - 1) or y in (0, h - 1): return hx('#3a4529')
    v = (h - 1 - y) / (h - 1); u = x / (w - 1)
    A, Br = hx('#1b3f9c'), hx('#ecebe6')
    if .12 < v < .25 or .75 < v < .88: return A
    cx, cy, r = .5, .5, .19; px_, py_ = (u - cx) * w / h, v - cy
    def lado(ax, ay, bx, by, x0, y0): return (bx - ax) * (y0 - ay) - (by - ay) * (x0 - ax)
    def dentro(tri, x0, y0):
        a, b, c = tri; s1, s2, s3 = lado(*a, *b, x0, y0), lado(*b, *c, x0, y0), lado(*c, *a, x0, y0)
        return (s1 >= 0 and s2 >= 0 and s3 >= 0) or (s1 <= 0 and s2 <= 0 and s3 <= 0)
    def tri(rr, k): return [(rr * math.cos(math.pi / 2 + k * math.pi + i * 2 * math.pi / 3), rr * math.sin(math.pi / 2 + k * math.pi + i * 2 * math.pi / 3)) for i in range(3)]
    fora = dentro(tri(r, 0), px_, py_) or dentro(tri(r, 1), px_, py_)
    dent = dentro(tri(r * .62, 0), px_, py_) or dentro(tri(r * .62, 1), px_, py_)
    return A if fora and not dent else Br

MATS = {}
def material(nome, img, repete=True):
    m = bpy.data.materials.new(nome); m.use_nodes = True; nt = m.node_tree
    p = nt.nodes['Principled BSDF']; p.inputs['Roughness'].default_value = 1; p.inputs['Specular IOR Level'].default_value = 0
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = img; t.interpolation = 'Closest'; t.extension = 'REPEAT' if repete else 'EXTEND'
    nt.links.new(t.outputs['Color'], p.inputs['Base Color'])
    px = img.pixels[:]; n = len(px) // 4                                # cor média (pros renders sem textura)
    m.diffuse_color = (sum(px[0::4]) / n, sum(px[1::4]) / n, sum(px[2::4]) / n, 1)
    m.use_backface_culling = V >= 2                                   # V2/V3: face única (a casca interna não briga com a externa)
    MATS[nome] = m; return m
material('farda', textura('farda', 64, 64, tecido('#414e2e', '#2c361f', '#5a6840', 1)))
material('calca', textura('calca', 64, 64, tecido('#3d4a2b', '#29331d', '#56633d', 2)))
material('colete', textura('colete', 64, 64, colete_f))
material('bolso', textura('bolso', 32, 32, bolso_f))
material('cinto', textura('cinto', 32, 32, cinto_f))
material('metal', textura('metal', 8, 8, preto_f('#6b6857', '#9a9680', 9)))
material('bota', textura('bota', 32, 32, preto_f('#151516', '#3a3a3c', 10)))
material('sola', textura('sola', 16, 16, sola_f))
material('luva', textura('luva', 32, 32, preto_f('#1a1b18', '#3d3f38', 11)))
material('joelheira', textura('joelheira', 16, 16, preto_f('#222820', '#3e4637', 12)))
material('bandeira', textura('bandeira', 48, 32, bandeira_f), repete=False)
if V >= 2: exec(open(os.path.join(AQUI, 'vestir_dod_mat.py')).read())     # paleta e texturas da V2/V3
if V >= 3: exec(open(os.path.join(AQUI, 'vestir_dod_v3.py')).read())      # funções de detalhe da V3

# pesos pra geometria nova (alças, bolsas): os do vértice do corpo mais próximo
bm0.verts.ensure_lookup_table(); KD = KDTree(len(bm0.verts))
for i, v in enumerate(bm0.verts): KD.insert(W(v.co), i)
KD.balance()
def pesar(bm):
    dl = bm.verts.layers.deform.verify()
    for v in bm.verts:
        _, i, _ = KD.find(W(v.co)); dv = v[dl]; dv.clear()
        for gi, w in bm0.verts[i][DL].items(): dv[gi] = w

def uv_caixa(bm, dens=4.0):                                      # projeção de caixa no mundo: 1 repetição a cada 1/dens metros
    uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = normal(f); a = max(range(3), key=lambda i: abs(n[i]))
        for l in f.loops:
            p = W(l.vert.co)
            l[uv].uv = (p.y * dens, p.z * dens) if a == 0 else (p.x * dens, p.z * dens) if a == 1 else (p.x * dens, p.y * dens)

def objeto(bm, nome, mats, mat_de=None, dens=4.0, uv=True, uv_extra=None):   # malha final presa ao esqueleto do Dod (mesmos grupos de vértice)
    if uv: uv_caixa(bm, dens)
    if uv_extra: uv_extra(bm, bm.loops.layers.uv.verify())
    for f in bm.faces: f.material_index = mat_de(f) if mat_de else 0
    if V >= 3:                                                     # funde faces coplanares do mesmo material (os cortes deixam lascas); a forma não muda
        antes = len(bm.faces)
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(1.5), use_dissolve_boundaries=False, verts=bm.verts[:], edges=bm.edges[:], delimit={'MATERIAL', 'UV'})
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
        print('  %s: %d -> %d faces' % (nome, antes, len(bm.faces)))
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = False
    for m in mats: me.materials.append(MATS[m])
    ob = bpy.data.objects.new(nome, me); bpy.context.scene.collection.objects.link(ob)
    ob.parent = rig; ob.matrix_world = MW
    for g in corpo.vertex_groups: ob.vertex_groups.new(name=g.name)
    md = ob.modifiers.new('rig', 'ARMATURE'); md.object = rig
    return ob

# ================================================================== PEÇAS
# ---------- CAMISA de combate (manga comprida) + GOLA
bm = extrair(lambda f: REG[f.index] == 'camisa'); afastar(bm, .010)
gola = bordas(bm, lambda e: all(W(v.co).z > 1.62 and abs(W(v.co).x) < .14 for v in e.verts))
if gola:
    vs = extrudar_borda(bm, gola, (0, 0, .035))                 # gola em pé
    c0 = sum((W(v.co) for v in vs), Vector()) / len(vs)
    for v in vs: p = W(v.co); d = Vector((p.x - c0.x, p.y - c0.y, 0)); v.co = MWi @ (p + d.normalized() * .012 if d.length > 1e-6 else p)
# BANDEIRA: recorte da própria manga esquerda, no lado de fora do braço (em T: o lado de cima), logo abaixo do ombro
BX0, BX1 = OMBRO.x + .075, OMBRO.x + .075 + .045                  # vertical da bandeira (ao longo do braço)
BY0, BY1 = -.033, .033                                             # horizontal (frente → trás)
def na_manga(f): return dono(f).startswith(('upper_arm.L', 'shoulder.L')) and centro(f).x > OMBRO.x - .01 and normal(f).z > .3
for x in (BX0, BX1): cortar(bm, (x, 0, 0), (1, 0, 0), [f for f in bm.faces if na_manga(f)])
for y in (BY0, BY1): cortar(bm, (0, y, 0), (0, 1, 0), [f for f in bm.faces if na_manga(f)])
patch = [f for f in bm.faces if na_manga(f) and BX0 < centro(f).x < BX1 and BY0 < centro(f).y < BY1]
print('bandeira: faces na manga', len(patch))
bmb = bm.copy(); bmb.faces.ensure_lookup_table(); idx = {f.index for f in patch}
idx = {f.index for f in patch}
bmesh.ops.delete(bmb, geom=[f for f in bmb.faces if f.index not in idx], context='FACES')
afastar(bmb, .003)
uvb = bmb.loops.layers.uv.verify()
for f in bmb.faces:
    for l in f.loops:
        p = W(l.vert.co); l[uvb].uv = ((p.y - BY0) / (BY1 - BY0), 1 - (p.x - BX0) / (BX1 - BX0))   # arco do braço → bandeira acompanha a curva da manga
bandeira = objeto(bmb, 'bandeira', ['bandeira'], uv=False)
if V >= 3: camisa = objeto(bm, 'camisa', camisa_v3(bm), mat_de=lambda f: f.material_index, uv_extra=uv_camisa_v3)
else: camisa = objeto(bm, 'camisa', ['farda'])

# ---------- CALÇA (com barra por cima do cano) + BOLSOS CARGO + JOELHEIRAS
bm = extrair(lambda f: REG[f.index] == 'calca'); afastar(bm, .013)
barra = bordas(bm, lambda e: all(abs(W(v.co).z - BOTA) < .01 for v in e.verts))
if barra:                                                          # a barra desce por cima do coturno (sem vão)
    vs = extrudar_borda(bm, barra, (0, 0, -.035))
    bm.normal_update()
BZ0, BZ1, BPROF = (JOELHO + .13, JOELHO + .36, .028) if V >= 3 else (JOELHO + .17, JOELHO + .33, .022)
BOLSOS_CALCA = []
for s in (1, -1):                                                  # bolso cargo na lateral de fora da coxa
    lado = lambda f, s=s: dono(f).startswith('thigh') and normal(f).x * s > .55 and centro(f).x * s > 0
    for z in (BZ0, BZ1): cortar(bm, (0, 0, z), (0, 0, 1), [f for f in bm.faces if lado(f)])
    fs = [f for f in bm.faces if lado(f) and BZ0 < centro(f).z < BZ1]
    novos = extrudar(bm, fs, BPROF); BOLSOS_CALCA += novos
    tampa = [f for f in novos if centro(f).z > BZ1 - .06 and abs(normal(f).x) > .5]
    for f in tampa:
        for v in f.verts: v.co += f.normal * L(.004)
if V >= 3: calca = objeto(bm, 'calca', calca_v3(bm, BOLSOS_CALCA), mat_de=lambda f: f.material_index, uv_extra=uv_calca_v3)
else: calca = objeto(bm, 'calca', ['calca'])
bm = extrair(lambda f: REG[f.index] == 'calca'); afastar(bm, .013)     # joelheiras: casca da frente do joelho, com espessura
fs = [f for f in bm.faces if abs(centro(f).z - JOELHO) < .065 and normal(f).y < -.35]
bmesh.ops.delete(bm, geom=[f for f in bm.faces if f not in fs], context='FACES')
afastar(bm, .010); extrudar(bm, bm.faces[:], .018, normal_unica=False)
joelheira = objeto(bm, 'joelheira', ['joelheira'])

# ---------- COTURNO com solado e cano
bm = extrair(lambda f: REG[f.index] == 'bota'); afastar(bm, .018)
for v in bm.verts:                                                 # a casca afastada passaria do chão: o solado fica rente ao chão (z = 0)
    p = W(v.co)
    if p.z < 0: v.co = MWi @ Vector((p.x * 1.0, p.y, 0.0))
SOLA_Z = .022                                                      # faixa do solado (borracha) até 2,2 cm
cortar(bm, (0, 0, SOLA_Z), (0, 0, 1))
def mat_bota(f): return 1 if centro(f).z < SOLA_Z else 0
cano = bordas(bm, lambda e: all(abs(W(v.co).z - BOTA) < .01 for v in e.verts))
if cano: extrudar_borda(bm, cano, (0, 0, .012))
if V >= 3: bota = objeto(bm, 'bota', bota_v3(bm), mat_de=lambda f: f.material_index, uv_extra=uv_bota_v3)
else: bota = objeto(bm, 'bota', ['bota', 'sola'], mat_de=mat_bota)

# ---------- LUVAS com punho
bm = extrair(lambda f: REG[f.index] == 'luva'); afastar(bm, .006)
for s in (1, -1):
    pu = bordas(bm, lambda e, s=s: all(abs(W(v.co).x - s * PULSO) < .01 for v in e.verts))
    if pu:
        vs = extrudar_borda(bm, pu, (-s * .035, 0, 0))           # o punho sobe pelo antebraço por cima da manga
        c0 = sum((W(v.co) for v in vs), Vector()) / len(vs)
        for v in vs: p = W(v.co); d = Vector((0, p.y - c0.y, p.z - c0.z)); v.co = MWi @ (p + d.normalized() * .009)
if V >= 3: luva = objeto(bm, 'luva', luva_v3(bm), mat_de=lambda f: f.material_index, dens=8)
else: luva = objeto(bm, 'luva', ['luva'], dens=8)

# ---------- COLETE porta-placas (placa da frente e de trás, faixa lateral, alças nos ombros), com espessura
VB, VT, PT = CINTURA + .07, 1.40, 1.585                            # base do colete, topo da faixa lateral, topo das placas
PX, SX0, SX1 = TX * .74, TX * .26, TX * .62                        # meia-largura da placa · alças
bm = extrair(lambda f: REG[f.index] == 'camisa' and tronco(f)); afastar(bm, .010)
for z in (VB, VT, PT): cortar(bm, (0, 0, z), (0, 0, 1))
for x in (PX, -PX, SX0, -SX0, SX1, -SX1): cortar(bm, (x, 0, 0), (1, 0, 0))
def no_colete(f):
    c = centro(f); ax = abs(c.x)
    if c.z < VB: return False
    if c.z < VT: return True                                       # faixa em volta do tronco
    if c.z < PT: return ax < PX                                    # placas
    return SX0 < ax < SX1                                          # alças
bmesh.ops.delete(bm, geom=[f for f in bm.faces if not no_colete(f)], context='FACES'); caixa(bm, 'colete recortado')
afastar(bm, .022); caixa(bm, 'colete afastado')
# porta-carregadores (3 na frente) e bolso administrativo no peito: extrudados da própria placa
PZ0, PZ1 = VB + .03, (VB + .15 if V >= 3 else VB + .17)
for x in (-.115, -.045, -.035, .035, .045, .115, -.06, .06): cortar(bm, (x * TX / .2, 0, 0), (1, 0, 0), [f for f in bm.faces if normal(f).y < -.6])
for z in (PZ0, PZ1, PT - .11, PT - .04, PT - .13, PT - .06): cortar(bm, (0, 0, z), (0, 0, 1), [f for f in bm.faces if normal(f).y < -.6])
bm.normal_update(); caixa(bm, 'colete cortado')
frente = lambda f: normal(f).y < -.6
# BOLSOS: peças próprias tiradas da frente da placa (frente achatada e rígida, como um porta-carregador de verdade), com aba
REGIOES = [((-.115, -.045), (PZ0, PZ1), .034), ((-.035, .035), (PZ0, PZ1), .034), ((.045, .115), (PZ0, PZ1), .034), ((-.06, .06), (PT - .13, PT - .06) if V >= 2 else (PT - .11, PT - .04), .02)]
bmp = bm.copy(); grupos = []
for (x0, x1), (z0, z1), prof in REGIOES:
    x0, x1 = x0 * TX / .2, x1 * TX / .2
    grupos.append(([f for f in bmp.faces if frente(f) and z0 < centro(f).z < z1 and x0 < centro(f).x < x1], z1, prof, (x0, x1, z0)))
usadas = {f for g in grupos for f in g[0]}
bmesh.ops.delete(bmp, geom=[f for f in bmp.faces if f not in usadas], context='FACES')
for fs, z1, prof, _ in grupos:
    fs = [f for f in fs if f.is_valid]
    if not fs: continue
    vs = {v for f in fs for v in f.verts}; yf = min(W(v.co).y for v in vs)
    for v in vs: p_ = W(v.co); v.co = MWi @ Vector((p_.x, yf, p_.z))      # frente plana
    bmp.normal_update()
    novos = extrudar(bmp, fs, prof)
    for f in novos:                                                # aba: degrau na parte de cima da frente
        if normal(f).y < -.6 and centro(f).z > z1 - .05:
            for v in f.verts: v.co += f.normal * L(.005)
uv_caixa(bmp, 5); uvp = bmp.loops.layers.uv.verify()
for fs, z1, prof, (x0, x1, z0) in grupos:                         # frente de cada bolso: a textura inteira (costura na borda, aba em cima)
    for f in bmp.faces:
        c = centro(f)
        if normal(f).y < -.6 and x0 - .005 < c.x < x1 + .005 and z0 - .005 < c.z < z1 + .01:
            for l in f.loops: p_ = W(l.vert.co); l[uvp].uv = ((p_.x - x0) / (x1 - x0), (p_.z - z0) / (z1 - z0))
bolsos = objeto(bmp, 'bolsos', ['bolso'], uv=False)
# espessura do colete (placas de verdade)
INT, PAR = espessura(bm, bm.faces[:], .016)
caixa(bm, 'colete solido')
if V >= 3: colete = objeto(bm, 'colete', colete_v3(bm, INT, PAR), mat_de=lambda f: f.material_index, dens=5, uv_extra=uv_colete_v3)
else: colete = objeto(bm, 'colete', ['colete'], dens=5)

# ---------- CINTO de guarnição com fivela
bm = extrair(lambda f: REG[f.index] == 'calca'); afastar(bm, .013)
cortar(bm, (0, 0, CINTURA - .045), (0, 0, 1))
bmesh.ops.delete(bm, geom=[f for f in bm.faces if not (CINTURA - .045 < centro(f).z < CINTURA + .001)], context='FACES')
afastar(bm, .008); espessura(bm, bm.faces[:], .008)
cortar(bm, (-.03, 0, 0), (1, 0, 0)); cortar(bm, (.03, 0, 0), (1, 0, 0))
fiv = [f for f in bm.faces if normal(f).y < -.7 and abs(centro(f).x) < .03 and centro(f).y < 0]
for f in extrudar(bm, fiv, .008): f.material_index = 1
cinto = objeto(bm, 'cinto', cinto_v3(bm) if V >= 3 else ['cinto', 'metal'], mat_de=lambda f: f.material_index, dens=6)

# ---------- o corpo do Dod fica só com o que a roupa não cobre (pescoço); a cabeça de gato entra no motor
bmc = extrair(lambda f: REG[f.index] == 'pescoco'); bmc.to_mesh(corpo.data); bmc.free()

# ------------------------------------------------------------------ pesos: cada peça herda os do corpo; o colete e o cinto ficam presos ao tronco
def so_tronco(ob, ossos):
    keep = {ob.vertex_groups[n].index for n in ossos if n in ob.vertex_groups}
    for v in ob.data.vertices:
        gs = [(g.group, g.weight) for g in v.groups]
        tot = sum(w for gi, w in gs if gi in keep)
        for gi, w in gs:
            if gi not in keep: ob.vertex_groups[gi].remove([v.index])
        if tot > 0:
            for gi, w in gs:
                if gi in keep: ob.vertex_groups[gi].add([v.index], w / tot, 'REPLACE')
        else: ob.vertex_groups['spine.002'].add([v.index], 1, 'REPLACE')
so_tronco(colete, ['spine', 'spine.001', 'spine.002', 'spine.003']); so_tronco(bolsos, ['spine', 'spine.001', 'spine.002', 'spine.003'])
so_tronco(cinto, ['spine', 'spine.001'])
if V >= 2: exec(open(os.path.join(AQUI, 'vestir_dod_v2.py')).read())   # gola alta, poncho, alça diagonal, bolsas

tris = {o.name: sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.type == 'MESH' and o.name != 'head'}
print('TRIANGULOS', tris, 'total', sum(tris.values()))

if RENDERS: exec(open(os.path.join(os.path.dirname(__file__), 'vestir_dod_render.py')).read())
for o in bpy.data.objects: o.select_set(o.type in ('MESH', 'ARMATURE'))
bpy.ops.export_scene.gltf(filepath=SAIDA, export_format='GLB', use_selection=True, export_skins=True, export_animations=False, export_apply=False)
print('VESTIR OK', SAIDA)
