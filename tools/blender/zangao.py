# ZANGÃO — duas versões SEPARADAS a partir do modelo "PlayStation 1 - South Park - Eric Cartman" (DamianToons, Sketchfab, CC BY 4.0;
# personagem © South Park Studios / Comedy Central, uso fan-made). O arquivo original fica intacto em referencia/.
# Uso: ZANGAO=original|militar blender -b -P tools/blender/zangao.py -- <saida.glb> <saida.blend>
#   original: aparência dele preservada + BIGODE estilo Chaplin (modelado) + distintivo da ÁGUIA (desenho próprio inspirado na Lazio)
#             em relevo no peito da jaqueta.
#   militar : mesmo corpo, rosto e bigode; uniforme MODELADO por cima (camisa com gola, carcela e bolsos com aba; colete com placas,
#             fileiras MOLLE, 3 porta-carregadores e 2 bolsos; cinto com fivela; calça com joelheiras; coturnos com sola; luvas; cotoveleiras;
#             gorro em verde-oliva; águia como distintivo na manga).
# Esqueleto próprio com os nomes que o motor usa (spine…, upper_arm/forearm/hand, thigh/shin/foot), nas proporções dele.
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(os.path.dirname(AQUI))
VERSAO = os.environ.get('ZANGAO', 'original')
ARGS = sys.argv[sys.argv.index('--') + 1:]; SAIDA, SAIDA_BLEND = ARGS[0], ARGS[1]
ZD = os.path.join(RAIZ, 'material/producao/personagens/zangao')
ALTURA_MOTOR = 1.30                                                # m no motor (o motor usa ×0,85)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(ZD, 'referencia/cartman_original.glb'))
base = [o for o in bpy.data.objects if o.type == 'MESH'][0]
M0 = base.matrix_world.copy()
for o in [o for o in bpy.data.objects if o is not base]: bpy.data.objects.remove(o)
me = base.data; me.transform(M0); base.matrix_world = Matrix.Identity(4)
zmax = max(v.co.z for v in me.vertices); ESC = ALTURA_MOTOR / .85 / zmax
me.transform(Matrix.Scale(ESC, 4)); base.name = 'corpo'
def U(z): return z * ESC                                            # unidades do modelo original → unidades do Blender
img0 = [n.image for n in me.materials[0].node_tree.nodes if n.type == 'TEX_IMAGE'][0]; img0.pack()
IW, IH = img0.size; PX0 = np.array(img0.pixels[:]).reshape(IH, IW, 4)[..., :3]
def classe_face(p):
    uvd = me.uv_layers.active.data                                  # lê sempre o UV atual da malha
    u = sum((uvd[i].uv for i in p.loop_indices), Vector((0, 0))) / len(p.loop_indices)
    r, g, b = PX0[min(IH - 1, int(u.y * IH)), min(IW - 1, int(u.x * IW))]
    if r > .6 and g > .6 and b < .3: return 'amarelo'
    if b > r and b > .35: return 'azul'
    if r > .45 and g < .2: return 'vermelho'
    if r > .6 and g > .5 and b > .4: return 'pele'
    if r > .8 and g > .8 and b > .8: return 'branco'
    if r < .15 and g < .15 and b < .15: return 'preto'
    return 'marrom'
CLS = {p.index: classe_face(p) for p in me.polygons}
P = np.array([tuple(v.co) for v in me.vertices])
# ---- marcos (medidos no modelo)
def media(pred): a = P[[i for i in range(len(P)) if pred(P[i])]]; return a.mean(0) if len(a) else None
MAO = media(lambda p: p[0] > U(2.0) and U(1.2) < p[2] < U(2.1))
OMB = np.array([U(1.4), 0, MAO[2] + U(.08)])
QUAD_Z, JOELHO_Z, TORN_Z = U(.55), U(.3), U(.09)
PESC_Z, CAB_Z = U(1.62), U(1.85)
print('ESC', round(ESC, 4), 'mão', MAO.round(3), 'ombro', OMB.round(3))

# ================================================================== ESQUELETO
arm = bpy.data.armatures.new('rig_zangao'); rig = bpy.data.objects.new('rig_zangao', arm); bpy.context.scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig; bpy.ops.object.mode_set(mode='EDIT')
EB = arm.edit_bones
def osso(nome, a, b, pai=None):
    e = EB.new(nome); e.head = Vector(a); e.tail = Vector(b)
    if pai: e.parent = EB[pai]; e.use_connect = False
    return e
osso('spine', (0, 0, QUAD_Z), (0, 0, U(.9)))
osso('spine.001', (0, 0, U(.9)), (0, 0, U(1.2)), 'spine'); osso('spine.002', (0, 0, U(1.2)), (0, 0, U(1.45)), 'spine.001')
osso('spine.003', (0, 0, U(1.45)), (0, 0, PESC_Z), 'spine.002'); osso('spine.004', (0, 0, PESC_Z), (0, 0, CAB_Z), 'spine.003')
osso('spine.005', (0, 0, CAB_Z), (0, 0, U(3.9)), 'spine.004')
for s, L in ((1, 'L'), (-1, 'R')):
    osso('shoulder.' + L, (s * U(.3), 0, OMB[2]), (s * OMB[0], 0, OMB[2]), 'spine.003')
    cot = (s * (OMB[0] + MAO[0]) / 2 * 1.02, 0, (OMB[2] + MAO[2]) / 2)
    osso('upper_arm.' + L, (s * OMB[0], 0, OMB[2]), cot, 'shoulder.' + L)
    osso('forearm.' + L, cot, (s * MAO[0] * .93, 0, MAO[2]), 'upper_arm.' + L)
    osso('hand.' + L, (s * MAO[0] * .93, 0, MAO[2]), (s * (MAO[0] + U(.25)), 0, MAO[2] - U(.02)), 'forearm.' + L)
    osso('f_middle.01.' + L, (s * (MAO[0] + U(.25)), 0, MAO[2] - U(.02)), (s * (MAO[0] + U(.35)), 0, MAO[2] - U(.03)), 'hand.' + L)
    osso('thigh.' + L, (s * U(.6), 0, QUAD_Z), (s * U(.6), 0, JOELHO_Z), 'spine')
    osso('shin.' + L, (s * U(.6), 0, JOELHO_Z), (s * U(.6), 0, TORN_Z), 'thigh.' + L)
    osso('foot.' + L, (s * U(.6), 0, TORN_Z), (s * U(.6), -U(.5), U(.02)), 'shin.' + L)
bpy.ops.object.mode_set(mode='OBJECT')
OSSOS = [b.name for b in arm.bones]

def ss(e0, e1, x): t = min(1, max(0, (x - e0) / (e1 - e0))); return t * t * (3 - 2 * t)
VCLS = {}
for p in me.polygons:
    for v in p.vertices: VCLS.setdefault(v, set()).add(CLS[p.index])
def pesos_de(p, cls=None):                                         # pesos por região (com transições suaves)
    x, y, z = p; ax = abs(x); L = 'L' if x > 0 else 'R'; w = {}
    cab = cls is not None and cls <= {'pele', 'azul', 'branco', 'preto'} and z > U(1.5) or z > U(2.3) or (cls and 'azul' in cls)
    if cab and z > U(1.5): return {'spine.005': 1.0}
    braco = ax > OMB[0] + U(.06) and U(1.0) < z < U(2.2)               # só o toco do braço (o corpo redondo não é puxado)
    if braco:
        t = (ax - OMB[0] - U(.06)) / (MAO[0] - OMB[0] - U(.06))
        if t < .15: w['spine.003'] = 1 - ss(-.1, .15, t); w['upper_arm.' + L] = ss(-.1, .15, t)
        elif t < .55: w['upper_arm.' + L] = 1 - ss(.35, .55, t); w['forearm.' + L] = ss(.35, .55, t)
        elif t < .85: w['forearm.' + L] = 1 - ss(.7, .85, t); w['hand.' + L] = ss(.7, .85, t)
        else: w['hand.' + L] = 1
        return w
    if z < QUAD_Z + U(.12) and ax > U(.08):
        if z > JOELHO_Z: k = ss(QUAD_Z - U(.05), QUAD_Z + U(.12), z); w['thigh.' + L] = 1 - k; w['spine'] = k
        elif z > TORN_Z: k = ss(JOELHO_Z - U(.06), JOELHO_Z + U(.06), z); w['shin.' + L] = 1 - k; w['thigh.' + L] = k
        else: w['foot.' + L] = 1
        return w
    for nome, z0, z1 in (('spine', -U(9), U(.9)), ('spine.001', U(.9), U(1.2)), ('spine.002', U(1.2), U(1.45)), ('spine.003', U(1.45), U(9))):
        if z0 <= z < z1: w[nome] = 1
    return w
def prender(ob, pesos_fn):
    for n in OSSOS: ob.vertex_groups.new(name=n)
    for v in ob.data.vertices:
        for n, wt in pesos_fn(v).items():
            if wt > 1e-4: ob.vertex_groups[n].add([v.index], wt, 'REPLACE')
    ob.parent = rig; md = ob.modifiers.new('rig', 'ARMATURE'); md.object = rig
prender(base, lambda v: pesos_de(v.co, VCLS.get(v.index)))
for p in me.polygons: p.use_smooth = False
KD_BASE = [tuple(v.co) for v in me.vertices]
from mathutils.kdtree import KDTree
KD = KDTree(len(me.vertices))
for v in me.vertices: KD.insert(v.co, v.index)
KD.balance()
def pesos_perto(v):                                                # peça presa: copia os pesos do vértice mais próximo do corpo
    _, i, _ = KD.find(v.co); return pesos_de(me.vertices[i].co, VCLS.get(i))
bm_b = bmesh.new(); bm_b.from_mesh(me); BVH = BVHTree.FromBMesh(bm_b)
def ponto_frente(x, z, dirv=(0, 1, 0), orig_y=-5.0):              # raio na superfície do corpo
    o_ = Vector((x, orig_y, z)) if dirv == (0, 1, 0) else Vector((x, 0, z)) - Vector(dirv) * 5
    loc, nor, i, d = BVH.ray_cast(o_, Vector(dirv), 20)
    return (loc, nor) if loc is not None else (None, None)

# ================================================================== materiais e texturas PSX
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
def ruido(x, y, s=1):
    n = (x * 374761393 + y * 668265263 + s * 982451653) & 0xffffffff; n = (n ^ (n >> 13)) * 1274126177 & 0xffffffff
    return (n & 0xffff) / 65535
def hx(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
def mix(a, b, t): return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))
def textura(nome, w, h, fn):
    img = bpy.data.images.new(nome, w, h, alpha=False); px = []
    for y in range(h):
        for x in range(w):
            r, g, b = fn(x, y, w, h); d = (BAYER[y % 4][x % 4] / 16 - .5) * 8
            px += [min(255, max(0, round((c + d) / 8) * 8)) / 255 for c in (r, g, b)] + [1]
    img.pixels = px; img.pack(); return img
MATS = {}
def material(nome, img, repete=True):
    m = bpy.data.materials.new(nome); m.use_nodes = True; nt = m.node_tree
    p = nt.nodes['Principled BSDF']; p.inputs['Roughness'].default_value = 1; p.inputs['Specular IOR Level'].default_value = 0
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = img; t.interpolation = 'Closest'; t.extension = 'REPEAT' if repete else 'EXTEND'
    nt.links.new(t.outputs[0], p.inputs['Base Color']); m.use_backface_culling = True; MATS[nome] = m; return m
def mt(nome, w, h, fn, rep=True): return material(nome, textura(nome, w, h, fn), rep)
def tecido(base_, esc, clara, s):
    B, E, C = hx(base_), hx(esc), hx(clara)
    def f(x, y, w, h):
        k = ruido(x // 2, y // 2, s); dobra = .5 + .5 * math.sin(x * .35 + math.sin(y * .19) * 2.4) * math.sin(y * .11 + x * .04)
        c = mix(E, B, .55 + .45 * dobra); c = mix(c, C, .25) if k > .9 else c
        if (x + y * 3) % 7 == 0 and k > .5: c = mix(c, E, .4)
        return c
    return f
def lona(base_, esc, clara, s):
    B, E, C = hx(base_), hx(esc), hx(clara)
    def f(x, y, w, h):
        m = ruido(x // 3, y // 3, s) * .6 + ruido(x // 6, y // 6, s + 1) * .4; c = mix(E, B, .35 + .65 * m)
        if ruido(x, y, s + 2) > .93: c = mix(c, C, .5)
        return c
    return f
COST = '#a09448'
def bolso_f(base_, esc, s, aba=.62):
    def f(x, y, w, h):
        v = y / (h - 1); c = lona(base_, esc, base_, s)(x, y, w, h)
        if v > aba: c = mix(c, hx(esc), .35)
        if abs(v - aba) < .04: c = mix(hx(esc), c, .2)
        if (x in (1, w - 2) or y in (1, h - 2)) and (x + y) % 2 == 0: c = mix(hx(COST), c, .45)
        if abs(x - w // 2) < 2 and abs(v - (aba + .12)) < .05: c = hx('#5a5a50')   # botão/pressão
        return c
    return f

# ---- helpers de malha
def novo_obj(nome, bm, mats, pesos=None):
    me_ = bpy.data.meshes.new(nome); bm.to_mesh(me_); bm.free()
    for p in me_.polygons: p.use_smooth = False
    for m in mats: me_.materials.append(MATS[m])
    ob = bpy.data.objects.new(nome, me_); bpy.context.scene.collection.objects.link(ob)
    prender(ob, pesos or pesos_perto); return ob
def remendo(nome, centro, eixo_u, eixo_v, raio_, mat, dirv, n=12, afasta=.006, esp=.004, uv_circ=True, plano=False):
    """disco (12 lados) apoiado na superfície do corpo por raios, com espessura e borda — distintivo/joelheira/etc."""
    bm = bmesh.new(); uvl = bm.loops.layers.uv.verify(); eu, ev = Vector(eixo_u).normalized(), Vector(eixo_v).normalized()
    pts = [(0.0, 0.0)] + [(math.cos(2 * math.pi * k / n), math.sin(2 * math.pi * k / n)) for k in range(n)]
    top, bot = [], []
    c0, _, _, _ = BVH.ray_cast(Vector(centro) - Vector(dirv) * .5, Vector(dirv), 2)
    for a, b in pts:
        q = Vector(centro) + eu * a * raio_ + ev * b * raio_
        if plano and c0 is not None: loc = c0 + eu * a * raio_ + ev * b * raio_       # distintivo plano, encostado no ponto central
        else:
            loc, nor, i, d = BVH.ray_cast(q - Vector(dirv) * .5, Vector(dirv), 2)
            if loc is None: loc, nor = q, -Vector(dirv)
        top.append(bm.verts.new(loc - Vector(dirv) * (afasta + esp))); bot.append(bm.verts.new(loc - Vector(dirv) * afasta))
    for k in range(n):
        k1, k2 = 1 + k, 1 + (k + 1) % n
        f = bm.faces.new((top[0], top[k1], top[k2]))
        for l, (a, b) in zip(f.loops, (pts[0], pts[k1], pts[k2])): l[uvl].uv = (.5 + .5 * a, .5 + .5 * b)
        f = bm.faces.new((top[k2], top[k1], bot[k1], bot[k2]))
        for l in f.loops: l[uvl].uv = (.02, .5)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')   # o centro de baixo não é usado
    bm.normal_update(); bm.faces.ensure_lookup_table()
    if sum(f.normal.dot(-Vector(dirv)) for f in bm.faces[:n]) < 0: bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    return novo_obj(nome, bm, [mat])

def anel(nome, z, h, afasta, mat, a0=-180, a1=180, n=20, esp=0.0, pesos=None, dens=8):
    """faixa que contorna o corpo na altura z (cinto, fileira MOLLE, barra da calça): cada ponto vem de um raio de fora pra dentro"""
    bm = bmesh.new(); uvl = bm.loops.layers.uv.verify(); fech = (a1 - a0) >= 359.9
    angs = [a0 + (a1 - a0) * k / (n if fech else n - 1) for k in range(n)]
    linhas = []
    for zz in (z - h / 2, z + h / 2):
        lin = []
        for a in angs:
            d = Vector((math.sin(math.radians(a)), -math.cos(math.radians(a)), 0)); o_ = Vector((0, 0, zz)) + d * 5
            loc, nor, _, _ = BVH.ray_cast(o_, -d, 10)
            p_ = (loc if loc is not None else Vector((0, 0, zz)) + d * U(1.3)) + d * afasta
            lin.append(bm.verts.new(p_))
        linhas.append(lin)
    m = n if fech else n - 1
    for k in range(m):
        k2 = (k + 1) % n; f = bm.faces.new((linhas[0][k], linhas[0][k2], linhas[1][k2], linhas[1][k]))
        for l, uv in zip(f.loops, ((k / m * 6, 0), ((k + 1) / m * 6, 0), ((k + 1) / m * 6, 1), (k / m * 6, 1))): l[uvl].uv = uv
    bm.normal_update()
    for f in bm.faces:
        c = f.calc_center_median()
        if f.normal.dot(Vector((c.x, c.y, 0))) < 0: f.normal_flip()
    if esp:
        ret = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:]); vs = [g for g in ret['geom'] if isinstance(g, bmesh.types.BMVert)]
        for v in vs: v.co += Vector((v.co.x, v.co.y, 0)).normalized() * esp
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return novo_obj(nome, bm, [mat], pesos)
def caixa_obj(nome, c, tam, mats, pesos, sola=0.0, chanfro=.25):
    """caixa chanfrada (coturno, fivela): base no chão, bico arredondado na frente (-Y); sola = altura da faixa de borracha"""
    bm = bmesh.new(); uvl = bm.loops.layers.uv.verify(); cx, cy, cz = c; sx, sy, sz = tam
    def secao(z, enc):
        k = chanfro * sx; return [(cx - sx / 2 + k * enc, cy - sy / 2, z), (cx + sx / 2 - k * enc, cy - sy / 2, z), (cx + sx / 2, cy - sy / 2 + k, z), (cx + sx / 2, cy + sy / 2, z), (cx - sx / 2, cy + sy / 2, z), (cx - sx / 2, cy - sy / 2 + k, z)]
    niveis = [(cz, 1), (cz + sola, 1), (cz + sola + .001, 1.15), (cz + sz, 1.6)] if sola else [(cz, 1), (cz + sz, 1.4)]
    an = [[bm.verts.new(p) for p in secao(z, e)] for z, e in niveis]
    for j in range(len(an) - 1):
        for k in range(6):
            f = bm.faces.new((an[j][k], an[j][(k + 1) % 6], an[j + 1][(k + 1) % 6], an[j + 1][k])); f.material_index = 1 if (sola and j == 0) else 0
            for l in f.loops: l[uvl].uv = (l.vert.co.x * 10 + l.vert.co.y * 10, l.vert.co.z * 10)
    f = bm.faces.new(an[-1]); f.material_index = 0
    for l in f.loops: l[uvl].uv = (l.vert.co.x * 10, l.vert.co.y * 10)
    f = bm.faces.new(an[0][::-1]); f.material_index = 1 if sola else 0
    for l in f.loops: l[uvl].uv = (l.vert.co.x * 10, l.vert.co.y * 10)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return novo_obj(nome, bm, mats, pesos)

# ================================================================== BIGODE estilo Chaplin (as duas versões)
# fica no meio do rosto, logo acima da boca: um bloco curto e retangular (largura do "nariz"), bem escuro, com volume
mt('z_bigode', 16, 8, lambda x, y, w, h: mix(hx('#141210'), hx('#2c2620'), .6 * ruido(x, y // 2, 301)) if x % 3 else hx('#0c0b0a'))
FACE = [p for p in me.polygons if CLS[p.index] == 'pele']
Z_BIGODE = U(2.375)                                                 # medido no modelo: boca em 2,15–2,31 e olhos a partir de 2,64 → bigode logo acima da boca
def bigode():
    """bigode estilo Chaplin: bloco curto e escuro COLADO no rosto — cada vértice vem de um raio na superfície do rosto e
    cresce pela normal da pele (acompanha a curvatura; sem vão nem inclinação). Peça fechada (frente, verso, bordas)."""
    bm = bmesh.new(); uvl = bm.loops.layers.uv.verify(); NC, NR = 4, 3; H_ = U(.1); D_ = U(.045)
    zc = Z_BIGODE; frente, tras = [], []
    for r in range(NR):
        z = zc - H_ / 2 + H_ * r / (NR - 1); W_ = U(.105) - U(.015) * r / (NR - 1)    # estreito como o do Chaplin (largura do nariz)
        lf, lt = [], []
        for c in range(NC):
            x = -W_ + 2 * W_ * c / (NC - 1)
            loc, nor, _, _ = BVH.ray_cast(Vector((x, -5, z)), Vector((0, 1, 0)), 20)
            if loc is None: loc, nor = Vector((x, -U(1.2), z)), Vector((0, -1, 0))
            n_ = (nor if nor.dot(Vector((0, -1, 0))) > 0 else -nor).normalized()
            n_ = (n_ + Vector((0, -1, 0))).normalized()                # puxa a direção pra frente (o bloco não "escorre" de lado)
            lt.append(bm.verts.new(loc + n_ * U(.003))); lf.append(bm.verts.new(loc + n_ * D_))
        frente.append(lf); tras.append(lt)
    def quad(vs, uvs):
        f = bm.faces.new(vs)
        for l, u_ in zip(f.loops, uvs): l[uvl].uv = u_
    for r in range(NR - 1):
        for c in range(NC - 1):
            u0, u1, v0, v1 = c / (NC - 1), (c + 1) / (NC - 1), r / (NR - 1), (r + 1) / (NR - 1)
            quad((frente[r][c], frente[r][c + 1], frente[r + 1][c + 1], frente[r + 1][c]), ((u0, v0), (u1, v0), (u1, v1), (u0, v1)))
            quad((tras[r][c + 1], tras[r][c], tras[r + 1][c], tras[r + 1][c + 1]), ((0, 0),) * 4)
    borda = [(0, c) for c in range(NC)] + [(r, NC - 1) for r in range(1, NR)] + [(NR - 1, c) for c in range(NC - 2, -1, -1)] + [(r, 0) for r in range(NR - 2, 0, -1)]
    for k in range(len(borda)):
        (r0, c0), (r1, c1) = borda[k], borda[(k + 1) % len(borda)]
        quad((tras[r0][c0], tras[r1][c1], frente[r1][c1], frente[r0][c0]), ((0, .5),) * 4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])          # peça fechada: normais pra fora
    return novo_obj('bigode', bm, ['z_bigode'], lambda v: {'spine.005': 1.0})
bigode_ob = bigode()

# ================================================================== VERSÃO ORIGINAL: águia no peito
aguia = bpy.data.images.load(os.path.join(ZD, 'texturas/aguia.png')); aguia.pack()
material('z_aguia', aguia, repete=False)
if VERSAO == 'original':
    # peito esquerdo do personagem (+X), na frente da jaqueta vermelha
    remendo('aguia_peito', (U(.62), 0, U(1.2)), (1, 0, 0), (0, 0, 1), U(.36), 'z_aguia', (0, 1, 0), afasta=U(.05), esp=U(.03))

# ================================================================== VERSÃO MILITAR: uniforme modelado por cima
if VERSAO == 'militar':
    # paleta própria: verde-musgo (camisa), verde-militar escuro (calça), cáqui-marrom (colete), couro marrom (cinto), preto (coturno),
    # oliva (luvas, gorro), amarelo-oliva (pesponto), metal
    mt('zm_camisa', 64, 64, tecido('#56603e', '#3a4229', '#6e7a52', 311))
    mt('zm_calca', 64, 64, tecido('#3f4630', '#2a2f20', '#555e40', 312))
    mt('zm_colete', 64, 64, lona('#7d6b4a', '#574a33', '#968360', 313))
    mt('zm_molle', 32, 8, lambda x, y, w, h: mix(hx('#6c5c3e'), hx('#4c412c'), .7 if y in (0, h - 1) or x % 10 < 2 else .2 * ruido(x, y, 314)))
    mt('zm_bolso', 32, 32, bolso_f('#857252', '#5e5038', 315), rep=False)
    mt('zm_carregador', 32, 32, bolso_f('#7a6848', '#544730', 316, aba=.68), rep=False)
    mt('zm_couro', 32, 8, lambda x, y, w, h: mix(hx('#5b4130'), hx('#7a5a40'), .5 * ruido(x // 2, y, 317)) if y not in (1, h - 2) or x % 2 else mix(hx(COST), hx('#5b4130'), .4))
    mt('zm_metal', 8, 8, lambda x, y, w, h: mix(hx('#777770'), hx('#b8b6aa'), ruido(x, y, 318)))
    mt('zm_bota', 32, 32, lambda x, y, w, h: mix(hx('#151516'), hx('#38383a'), .5 * ruido(x // 2, y // 2, 319) ** 2) if y % 9 else hx('#5a5a5c') if x % 4 < 2 else hx('#1d1d1f'))
    mt('zm_sola', 16, 16, lambda x, y, w, h: hx('#0f0f10') if (x + y) % 5 < 2 else hx('#262628'))
    mt('zm_luva', 32, 32, lambda x, y, w, h: mix(hx('#47502f'), hx('#5f6a42'), .5 * ruido(x // 2, y // 2, 320)) if y % 8 else hx('#353c23'))
    mt('zm_joelheira', 32, 32, lambda x, y, w, h: mix(hx('#2e302a'), hx('#4a4c44'), .5 * ruido(x // 2, y // 2, 321) ** 2) if not 13 < y < 18 else hx('#1e201b'))
    mt('zm_costura', 8, 8, lambda x, y, w, h: mix(hx(COST), hx('#3a4229'), .45) if (y in (3, 4) and x % 4 < 2) else hx('#3a4229'))
    mt('zm_gorro', 32, 32, lambda x, y, w, h: mix(hx('#4b5534'), hx('#5f6b43'), .5 * ruido(x, y // 2, 322)) if x % 3 else hx('#3f482b'))
    mt('zm_gorro_faixa', 32, 32, lambda x, y, w, h: mix(hx('#2f3520'), hx('#3d4429'), .5 * ruido(x, y // 2, 323)) if x % 3 else hx('#262b19'))
    def casca(classes, afasta, pred=lambda c: True, sub=0):
        bm = bmesh.new(); bm.from_mesh(me)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if not (CLS[f.index] in classes and pred(f.calc_center_median()))], context='FACES')
        if sub: bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=sub, use_grid_fill=True)
        bm.normal_update()
        for v in bm.verts: v.co += v.normal * afasta
        return bm
    def uv_caixa(bm, dens):
        uvl = bm.loops.layers.uv.verify()
        for f in bm.faces:
            n = f.normal; a = max(range(3), key=lambda i: abs(n[i]))
            for l in f.loops:
                p = l.vert.co; l[uvl].uv = (p.y * dens, p.z * dens) if a == 0 else (p.x * dens, p.z * dens) if a == 1 else (p.x * dens, p.y * dens)
    def espessura(bm, d):
        ret = bmesh.ops.duplicate(bm, geom=bm.faces[:]); dentro = [g for g in ret['geom'] if isinstance(g, bmesh.types.BMFace)]
        for v in {v for f in dentro for v in f.verts}: v.co -= v.normal * 0 + Vector(v.normal) * d
        bmesh.ops.reverse_faces(bm, faces=dentro)
    # ---- CAMISA (a jaqueta vermelha some; a camisa é uma casca própria com gola, carcela, bolsos com aba e costuras)
    bm = casca({'vermelho'}, U(.02), sub=1)
    for f in bm.faces:
        c = f.calc_center_median(); f.material_index = 0
        if abs(c.x) < U(.06) and f.normal.y < -.4 and c.z > U(.6): f.material_index = 1          # carcela (costura dupla)
        if c.z > U(1.95) and f.normal.z > .2: f.material_index = 1                                # pala dos ombros
    uv_caixa(bm, 6); camisa = novo_obj('camisa', bm, ['zm_camisa', 'zm_costura'])
    for p_ in camisa.data.polygons: p_.use_smooth = True                 # tecido com sombreamento suave
    for s in (1, -1):                                              # gola: anel em volta do pescoço (entre o corpo e a cabeça)
        pass
    bm = bmesh.new(); uvl = bm.loops.layers.uv.verify(); NG = 16; an = []
    for j, (z, r) in enumerate(((U(1.88), U(1.25)), (U(2.02), U(1.12)), (U(1.93), U(1.42)))):
        an.append([bm.verts.new((r * math.sin(2 * math.pi * k / NG), -r * .95 * math.cos(2 * math.pi * k / NG), z)) for k in range(NG)])
    for j in range(2):
        for k in range(NG):
            f = bm.faces.new((an[j][k], an[j][(k + 1) % NG], an[j + 1][(k + 1) % NG], an[j + 1][k]))
            for l in f.loops: l[uvl].uv = (l.vert.co.x * 6, l.vert.co.z * 6)
    bm.normal_update()
    for f in bm.faces:
        c = f.calc_center_median()
        if f.normal.dot(Vector((c.x, c.y, 0))) < 0: f.normal_flip()
    novo_obj('gola', bm, ['zm_camisa'], lambda v: {'spine.003': .6, 'spine.004': .4})
    # ---- COLETE (placa da frente e de trás, com espessura) + fileiras MOLLE + porta-carregadores + bolsos + ombreiras
    bm = casca({'vermelho'}, U(.12), pred=lambda c: U(.85) < c.z < U(1.75) and abs(c.x) < U(1.35))
    uv_caixa(bm, 5); espessura(bm, U(.05))
    for f in bm.faces: f.material_index = 0
    colete = novo_obj('colete', bm, ['zm_colete'], lambda v: {'spine.001': .5, 'spine.002': .5})
    for z in (U(1.40), U(1.52)): anel('molle', z, U(.07), U(.19), 'zm_molle', -60, 60, n=9, pesos=lambda v: {'spine.002': 1.0})   # fileiras MOLLE na frente
    for z in (U(1.2), U(1.32), U(1.44)): anel('molle_costas', z, U(.07), U(.19), 'zm_molle', 120, 240, n=9, pesos=lambda v: {'spine.002': 1.0})
    def bolsa(nome, x, z, w, h, prof, mat, dirv=(0, 1, 0)):
        """bolsa/porta-carregador: caixa apoiada no colete (frente achatada), com aba que sai 1 cm e cobre o terço de cima"""
        bm = bmesh.new(); uvl = bm.loops.layers.uv.verify(); dv = Vector(dirv)
        trs = []
        for (a, b) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            q = Vector((x + a * w / 2, 0, z + b * h / 2)); loc, nor, _, _ = BVH.ray_cast(q - dv * 5, dv, 20)
            trs.append((loc if loc is not None else q - dv * U(1.2)) - dv * U(.17))
        yf = min(p.y for p in trs) - prof
        frente = [Vector((p.x, yf, p.z)) for p in trs]
        VT = [bm.verts.new(p) for p in trs]; VF = [bm.verts.new(p) for p in frente]
        f = bm.faces.new(VF)
        for l, uv in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): l[uvl].uv = uv
        for k in range(4):
            f = bm.faces.new((VT[k], VT[(k + 1) % 4], VF[(k + 1) % 4], VF[k]))
            for l in f.loops: l[uvl].uv = (.05, .3)
        topo = [VF[3].co + Vector((0, -U(.02), U(.015))), VF[2].co + Vector((0, -U(.02), U(.015)))]   # aba
        baixo = [VF[3].co + Vector((0, -U(.02), -h * .36)), VF[2].co + Vector((0, -U(.02), -h * .36))]
        A = [bm.verts.new(p) for p in topo]; B_ = [bm.verts.new(p) for p in baixo]
        f = bm.faces.new((B_[0], B_[1], A[1], A[0]))
        for l, uv in zip(f.loops, ((0, .64), (1, .64), (1, 1), (0, 1))): l[uvl].uv = uv
        f = bm.faces.new((A[0], A[1], VT[2], VT[3]))
        for l in f.loops: l[uvl].uv = (.5, .98)
        bm.normal_update()
        for f in bm.faces:
            c = f.calc_center_median()
            if f.normal.dot(c - Vector((x, frente[0].y + prof * .5 + U(.3), z))) < 0: f.normal_flip()
        return novo_obj(nome, bm, [mat], lambda v: {'spine.001': .5, 'spine.002': .5})
    for x in (-U(.58), 0, U(.58)): bolsa('carregador', x, U(1.06), U(.46), U(.46), U(.2), 'zm_carregador')
    for x in (-U(.62), U(.62)): bolsa('bolso_peito', x, U(1.6), U(.42), U(.2), U(.08), 'zm_bolso')
    # ---- CINTO de couro com fivela de metal
    anel('cinto', U(.7), U(.14), U(.07), 'zm_couro', n=22, esp=U(.03), pesos=lambda v: {'spine': 1.0})
    bolsa('fivela', 0, U(.71), U(.22), U(.16), U(.04), 'zm_metal')
    # ---- CALÇA (casca das pernas) + JOELHEIRAS
    anel('calca', U(.33), U(.5), U(.05), 'zm_calca', n=22, pesos=lambda v: pesos_de(v.co))           # barra da calça em volta da base
    for s in (1, -1):
        remendo('joelheira', (s * U(.62), 0, U(.3)), (1, 0, 0), (0, 0, 1), U(.2), 'zm_joelheira', (0, 1, 0), afasta=U(.1), esp=U(.06))
    # ---- COTURNOS (casca do pé com sola grossa)
    L_ = 'L'
    for s in (1, -1):                                              # COTURNOS: par com sola grossa e bico pra frente, saindo debaixo do corpo
        caixa_obj('coturno', (s * U(.62), -U(.35), 0), (U(.75), U(1.45), U(.3)), ['zm_bota', 'zm_sola'], lambda v, s=s: {'foot.' + ('L' if s > 0 else 'R'): 1.0}, sola=U(.07))
    # ---- LUVAS (casca da mão) + COTOVELEIRAS (no meio do braço)
    bm = casca({'amarelo'}, U(.035), pred=lambda c: abs(c.x) > U(1.75) and c.z < U(2.2))
    uv_caixa(bm, 10); novo_obj('luvas', bm, ['zm_luva'])
    for s in (1, -1):
        remendo('cotoveleira', (s * (OMB[0] + MAO[0]) / 2, 0, (OMB[2] + MAO[2]) / 2), (1, 0, 0), (0, 0, 1), U(.14), 'zm_joelheira', (0, -1, 0), afasta=U(.03), esp=U(.04))
    # ---- GORRO em verde-oliva (mesma forma: continua reconhecível) — troca só o material do gorro do corpo
    material('zm_gorro_base', textura('zm_gorro_base', 32, 32, lambda x, y, w, h: (0, 0, 0)))
    # ---- ÁGUIA como distintivo na manga esquerda (em cima do braço, perto do ombro)
    remendo('aguia_manga', (OMB[0] + U(.2), 0, OMB[2] + U(.01)), (1, 0, 0), (0, 0, 1), U(.13), 'z_aguia', (0, 1, 0), afasta=U(.1), esp=U(.015), plano=True)   # plano, encostado no braço
    # o corpo: some a jaqueta vermelha, as luvas amarelas e as pernas marrons (cobertas); o gorro vira oliva
    bm = bmesh.new(); bm.from_mesh(me)
    tira = [f for f in bm.faces if CLS[f.index] == 'vermelho' or (CLS[f.index] == 'amarelo' and abs(f.calc_center_median().x) > U(1.75)) or (f.calc_center_median().z < U(.6) and CLS[f.index] in ('marrom', 'preto'))]
    bmesh.ops.delete(bm, geom=tira, context='FACES')
    bm.to_mesh(me); bm.free()
    me.materials.append(MATS['zm_gorro']); me.materials.append(MATS['zm_gorro_faixa'])
    for p in me.polygons:
        c = classe_face(p)
        if c == 'azul': p.material_index = 1
        elif c == 'amarelo' and p.center.z > U(2.2): p.material_index = 2
    # pesos do corpo (os vértices restantes mantêm os grupos)

for o in bpy.data.objects:
    if o.type == 'MESH':
        for m in o.data.materials:
            if m: m.use_backface_culling = True
tris = {o.name: sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.type == 'MESH'}
print('TRIANGULOS', tris, 'total', sum(tris.values()))
for o in bpy.data.objects: o.select_set(o.type in ('MESH', 'ARMATURE'))
bpy.ops.export_scene.gltf(filepath=SAIDA, export_format='GLB', use_selection=True, export_skins=True, export_animations=False, export_apply=False)
bpy.ops.file.pack_all(); bpy.ops.wm.save_as_mainfile(filepath=SAIDA_BLEND, compress=True)
print('ZANGAO OK', VERSAO, SAIDA)
