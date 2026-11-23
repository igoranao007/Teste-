"""LUAN GORDO sobre o Simple PSX Character (JashiPSX), depois do montar_jashi.py (textura ROUPA=luan, OCULOS=1, AFRO...).
1) engorda o corpo com UMA função de escala por altura aplicada no tronco, pescoço e cabeça (a costura pescoço-corpo continua
   fechada porque os dois lados recebem a mesma escala), barriga pra frente, braços e pernas mais grossos em volta do próprio eixo;
2) máscara de gás (metade de baixo do rosto) moldada por raios na própria cabeça + válvula + 2 filtros com aro amarelo luminoso + tiras;
3) peças de armadura feitas a partir da própria malha (cópia das faces da região, afastada pela normal e com espessura): ombreiras,
   braçadeiras, cinto, coxa, joelheira, caneleira e cano da bota. A borda (espessura) de cada placa é a linha de energia ('*brilho*').
Tudo com os mesmos grupos de vértices do corpo (as peças copiadas) ou presas no osso da cabeça (máscara) — mexem junto nas animações.
Uso: blender -b luan_base.blend --python luan_jashi.py -- saida.blend"""
import bpy, bmesh, sys, math, os
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
OUT = sys.argv[sys.argv.index('--') + 1]
A = bpy.data.objects['simple_character']
CAB_OSSO = 'spine.005'
def interp(pts, v):
    if v <= pts[0][0]: return pts[0][1]
    for (a, fa), (b, fb) in zip(pts, pts[1:]):
        if v <= b: return fa + (fb - fa) * (v - a) / (b - a)
    return pts[-1][1]
def ss(a, b, v): t = max(0.0, min(1.0, (v - a) / (b - a))); return t * t * (3 - 2 * t)

# ---------------------------------------------------------------- 1) engordar
LARG = [(0.80, 1.16), (0.92, 1.26), (1.02, 1.34), (1.15, 1.38), (1.30, 1.32), (1.45, 1.18), (1.56, 1.08), (1.64, 1.03), (1.80, 1.0)]   # largura do tronco
FRENTE = [(0.88, 1.15), (0.98, 1.45), (1.10, 1.75), (1.22, 1.80), (1.34, 1.55), (1.46, 1.25), (1.56, 1.08), (1.64, 1.0)]              # barriga/peito pra frente
COSTAS = [(0.90, 1.10), (1.05, 1.22), (1.30, 1.22), (1.50, 1.10), (1.64, 1.0)]
PESCOCO = [(1.62, 1.0), (1.67, 1.22), (1.73, 1.30), (1.77, 1.24), (1.81, 1.08), (1.84, 1.0)]   # pescoço grosso / papada
BOCHECHA = [(1.72, 1.22), (1.76, 1.24), (1.80, 1.20), (1.84, 1.13), (1.87, 1.06), (1.90, 1.0)]  # rosto mais largo embaixo
YC = 0.0
def escala_tronco(w):
    x, y, z = w
    r = math.hypot(x, y - 0.01)
    # pescoço/cabeça (r pequeno) x ombros (r grande): mistura pelo raio, mesma regra pros dois objetos
    kp = 1 - ss(0.085, 0.15, r)
    sx = interp(LARG, z) * (1 - kp) + interp(PESCOCO, z) * kp
    sy_f = interp(FRENTE, z) * (1 - kp) + interp(PESCOCO, z) * kp
    sy_b = interp(COSTAS, z) * (1 - kp) + interp(PESCOCO, z) * kp
    sy = sy_f if y < YC else sy_b
    return Vector((x * sx, YC + (y - YC) * sy, z))
def engordar_corpo(o):
    mw = o.matrix_world; inv = mw.inverted(); n = 0
    for v in o.data.vertices:
        w = mw @ v.co; x, y, z = w
        if z > 0.97:
            nw = escala_tronco(w)
        else:   # pernas: em volta do centro de cada perna, misturando com o tronco no quadril
            c = 0.153 if x > 0 else -0.153; cy = 0.02
            f = interp([(0.08, 1.06), (0.2, 1.14), (0.45, 1.20), (0.65, 1.26), (0.85, 1.30)], z)
            perna = Vector((c + (x - c) * f, cy + (y - cy) * f, z))
            k = ss(0.84, 0.97, z)
            nw = perna * (1 - k) + escala_tronco(Vector((x, y, 0.97))) * k; nw.z = z
            if z > 0.84 and y < 0: nw.y -= 0.02 * k                      # pança caindo por cima do cós
        v.co = inv @ nw; n += 1
    return n
def engordar_cabeca(o):
    mw = o.matrix_world; inv = mw.inverted()
    for v in o.data.vertices:
        w = mw @ v.co; x, y, z = w
        nw = escala_tronco(w) if z < 1.84 else Vector(w)
        if 1.70 < z < 1.90 and y < 0.06:                                 # bochecha/queixo (frente) mais largos
            b = interp(BOCHECHA, z) * ss(0.06, -0.04, y) + 1 * (1 - ss(0.06, -0.04, y))
            nw.x *= b
        if 1.72 < z < 1.79 and y < -0.02: nw.z -= 0.012 * ss(1.79, 1.74, z); nw.y -= 0.01   # papada
        v.co = inv @ nw
EIXO_B = [(0.20, Vector((0.20, 0.039, 1.610))), (0.223, Vector((0.223, 0.039, 1.607))), (0.451, Vector((0.451, 0.039, 1.561))), (0.80, Vector((0.80, -0.01, 1.533))), (1.1, Vector((1.1, -0.03, 1.52)))]
def eixo_braco(ax):
    for (a, pa), (b, pb) in zip(EIXO_B, EIXO_B[1:]):
        if ax <= b: t = max(0.0, (ax - a) / (b - a)); return pa.lerp(pb, t)
    return EIXO_B[-1][1]
def engordar_bracos(o):
    mw = o.matrix_world; inv = mw.inverted()
    for v in o.data.vertices:
        w = mw @ v.co; s = 1 if w.x > 0 else -1; ax = abs(w.x)
        e = eixo_braco(ax); e = Vector((s * e.x, e.y, e.z))
        f = interp([(0.20, 1.10), (0.27, 1.34), (0.40, 1.36), (0.47, 1.28), (0.62, 1.24), (0.76, 1.14), (0.81, 1.06), (0.90, 1.04)], ax)
        d = Vector((0, w.y - e.y, w.z - e.z)) * f
        v.co = inv @ Vector((w.x, e.y + d.y, e.z + d.z))
print('ENGORDAR corpo', engordar_corpo(bpy.data.objects['body']))
engordar_cabeca(bpy.data.objects['head']); engordar_bracos(bpy.data.objects['arms'])
if 'afro' in bpy.data.objects:   # o cabelo acompanha o rosto mais largo só um pouco
    pass

# ---------------------------------------------------------------- materiais
def mat_cor(nome, rgb, brilho=False):
    m = bpy.data.materials.new(nome); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    c = tuple((v / 255) ** (1.0 if brilho else 2.2) for v in rgb) + (1,)   # brilho: cor direta (o motor usa o fator como cor de tela)
    b.inputs['Base Color'].default_value = c; b.inputs['Roughness'].default_value = 0.85; m.diffuse_color = c
    if brilho:
        b.inputs['Emission Color'].default_value = c; b.inputs['Emission Strength'].default_value = 2.0
    return m
def mat_tex(nome, arq):
    m = bpy.data.materials.new(nome); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    ti = nt.nodes.new('ShaderNodeTexImage'); ti.image = bpy.data.images.load(os.path.abspath(arq)); ti.image.pack(); ti.interpolation = 'Closest'
    nt.links.new(ti.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = 0.8; nt.nodes.active = ti
    m.diffuse_color = (0.03, 0.03, 0.035, 1)
    return m
TEXD = 'material/producao/personagens/luan/texturas/'
M_ARM = mat_tex('armadura', TEXD + 'armadura.png')
M_BRI = mat_cor('linha_brilho', (255, 212, 36), True)
M_MASC = mat_tex('mascara', TEXD + 'mascara.png')
M_FILT = mat_tex('filtro', TEXD + 'filtro.png')
M_ESC = mat_cor('mascara_escuro', (14, 14, 16))

def prender_cabeca(o):
    vg = o.vertex_groups.new(name=CAB_OSSO); vg.add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')
    m = o.modifiers.new('Armature', 'ARMATURE'); m.object = A; o.parent = A; o.matrix_parent_inverse = A.matrix_world.inverted()

# ---------------------------------------------------------------- 2) máscara de gás (por raios na cabeça já engordada)
H = bpy.data.objects['head']
dg = bpy.context.evaluated_depsgraph_get()
bmH = bmesh.new(); bmH.from_mesh(H.data); bmH.transform(H.matrix_world); bvh = BVHTree.FromBMesh(bmH)
def raio(a, z):   # a: ângulo em volta do eixo vertical da cabeça (0 = frente)
    o_ = Vector((0.4 * math.sin(a), -0.4 * math.cos(a) + 0.0, z)); d_ = Vector((-math.sin(a), math.cos(a), 0)).normalized()
    hit, nrm, i, dist = bvh.ray_cast(o_, d_)
    return hit, nrm
NA, NZ = 22, 12
AMAX = math.radians(78)
def borda_z(a):   # contorno da máscara: alto no nariz, desce pras laterais; embaixo segue o queixo
    t = abs(a) / AMAX
    return 1.722 + 0.018 * t, 1.866 - 0.062 * t ** 1.4
bm = bmesh.new(); grade = []
for i in range(NA + 1):
    a = -AMAX + 2 * AMAX * i / NA; z0, z1 = borda_z(a); linha = []
    for j in range(NZ + 1):
        z = z0 + (z1 - z0) * j / NZ
        hit, nrm = raio(a, z)
        if hit is None: hit = Vector((0.12 * math.sin(a), -0.12 * math.cos(a), z)); nrm = Vector((math.sin(a), -math.cos(a), 0))
        fora = Vector((math.sin(a), -math.cos(a), 0))
        # focinho: mais volume no meio (boca/nariz), menos nas bordas
        bojo = 0.010 + 0.030 * math.cos(a * 1.15) ** 2 * math.sin(math.pi * j / NZ) ** 0.7
        p = hit + fora * bojo
        linha.append(bm.verts.new(p))
    grade.append(linha)
fs = []
for i in range(NA):
    for j in range(NZ): fs.append(bm.faces.new((grade[i][j], grade[i + 1][j], grade[i + 1][j + 1], grade[i][j + 1])))
# espessura (casca de borracha) com borda
r = bmesh.ops.extrude_face_region(bm, geom=fs)
novos = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
centro = Vector((0, 0.0, 1.80))
for v in novos:
    d = Vector((v.co.x - centro.x, v.co.y - centro.y, 0)).normalized(); v.co -= d * 0.010
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
uv = bm.loops.layers.uv.new('UVMap')
for f in bm.faces:
    for l in f.loops:
        p = l.vert.co; l[uv].uv = ((math.atan2(p.x, -p.y) / AMAX) * 0.5 + 0.5, (p.z - 1.72) / 0.15)
me = bpy.data.meshes.new('mascara'); bm.to_mesh(me); bm.free()
masc = bpy.data.objects.new('mascara', me); bpy.context.scene.collection.objects.link(masc); me.materials.append(M_MASC)
for p in me.polygons: p.use_smooth = False
prender_cabeca(masc)
def frente_da_mascara(a, z, extra=0.0):
    hit, nrm = raio(a, z)
    fora = Vector((math.sin(a), -math.cos(a), 0))
    bojo = 0.010 + 0.030 * math.cos(a * 1.15) ** 2 * 0.95
    return hit + fora * (bojo + extra), fora
def cilindro(nome, base, eixo, r1, r2, comp, nseg, mats, tampa_brilho=False):
    bm = bmesh.new(); eixo = eixo.normalized()
    q = eixo.to_track_quat('Z', 'Y'); R = q.to_matrix()
    an = []
    for k, (rr, zz) in enumerate(((r1, 0.0), (r2, comp), (r2 * 0.82, comp), (r2 * 0.82, comp - 0.006))):
        an.append([bm.verts.new(base + R @ Vector((rr * math.cos(2 * math.pi * s / nseg), rr * math.sin(2 * math.pi * s / nseg), zz))) for s in range(nseg)])
    lado = []
    for k in range(3):
        for s in range(nseg):
            f = bm.faces.new((an[k][s], an[k][(s + 1) % nseg], an[k + 1][(s + 1) % nseg], an[k + 1][s])); f.material_index = 1 if (k == 1 and tampa_brilho) else 0; lado.append(f)
    f = bm.faces.new(an[3]); f.material_index = 2
    uv = bm.loops.layers.uv.new('UVMap')
    for f in bm.faces:
        for l in f.loops:
            p = R.inverted() @ (l.vert.co - base); l[uv].uv = (0.5 + p.x / (2 * r2 * 1.05), 0.5 + p.y / (2 * r2 * 1.05)) if f.material_index == 2 else (math.atan2(p.y, p.x) / math.pi * 0.5 + 0.5, p.z / comp)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(nome, me); bpy.context.scene.collection.objects.link(o)
    for m in mats: me.materials.append(m)
    prender_cabeca(o); return o
# válvula central (na frente da boca)
p, fora = frente_da_mascara(0.0, 1.785, -0.004)
cilindro('valvula', p, fora + Vector((0, 0, -0.25)), 0.026, 0.022, 0.022, 10, [M_ESC, M_BRI, M_FILT])
# filtros nas bochechas (aro amarelo luminoso, como no conceito)
for s in (-1, 1):
    a = s * math.radians(50); p, fora = frente_da_mascara(a, 1.79, -0.006)
    eixo = (fora + Vector((0, -0.35, -0.12))).normalized()
    cilindro(f'filtro_{"E" if s > 0 else "D"}', p, eixo, 0.026, 0.031, 0.026, 12, [M_ESC, M_BRI, M_FILT], tampa_brilho=True)
# tiras (de cada lado da máscara até a nuca, acima e abaixo da orelha)
for nome, z0, z1 in (('tira_cima', 1.845, 1.905), ('tira_baixo', 1.765, 1.775)):
    bm = bmesh.new(); pts = []
    a0 = math.radians(66); N = 18
    for k in range(N + 1):
        a = a0 + (2 * math.pi - 2 * a0) * k / N; z = z0 + (z1 - z0) * math.sin(math.pi * k / N)
        hit, nrm = raio(a, z)
        if hit is None: continue
        fora = Vector((math.sin(a), -math.cos(a), 0)); pts.append((hit + fora * 0.006, fora))
    vs = [(bm.verts.new(p + Vector((0, 0, 0.007))), bm.verts.new(p - Vector((0, 0, 0.007)))) for p, f in pts]
    for (a1, b1), (a2, b2) in zip(vs, vs[1:]): bm.faces.new((a1, a2, b2, b1))
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(nome, me); bpy.context.scene.collection.objects.link(o); me.materials.append(M_ESC)
    prender_cabeca(o)
bmH.free()

# ---------------------------------------------------------------- 3) armadura: cascas da própria malha
B, AR = bpy.data.objects['body'], bpy.data.objects['arms']
def casca2(fonte, nome, filtro, afasta, esp):
    o = fonte.copy(); o.data = fonte.data.copy(); o.name = nome; bpy.context.scene.collection.objects.link(o)
    o.data.materials.clear(); o.data.materials.append(M_ARM); o.data.materials.append(M_BRI)
    mw = o.matrix_world; R3 = mw.to_3x3()
    bm = bmesh.new(); bm.from_mesh(o.data)
    fora_ = [f for f in bm.faces if not filtro(mw @ f.calc_center_median(), (R3 @ f.normal).normalized())]
    bmesh.ops.delete(bm, geom=fora_, context='FACES')
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    if not bm.faces: bm.free(); bpy.data.objects.remove(o); print('CASCA vazia', nome); return None
    bm.normal_update()
    for f in bm.faces: f.material_index = 0
    orig = list(bm.verts); nrm = {v: v.normal.copy() for v in orig}
    for v in orig: v.co += nrm[v] * (afasta + esp)
    # parede de dentro: cópia das faces, um pouco pra dentro, invertida; borda costurada com faces de linha
    dentro = {v: bm.verts.new(v.co - nrm[v] * esp) for v in orig}
    deform = bm.verts.layers.deform.active
    if deform:
        for v in orig: dentro[v][deform] = v[deform]
    fs = list(bm.faces); borda = [e for e in bm.edges if e.is_boundary]
    for f in fs:
        try: nf = bm.faces.new([dentro[v] for v in reversed(f.verts)]); nf.material_index = 0
        except ValueError: pass
    for e in borda:
        a, b = e.verts
        try: nf = bm.faces.new((a, b, dentro[b], dentro[a])); nf.material_index = 1
        except ValueError: pass
    uvl = bm.loops.layers.uv.active or bm.loops.layers.uv.new('UVMap')
    for f in bm.faces:
        nn = f.normal; ax = max(range(3), key=lambda i: abs(nn[i]))
        for l in f.loops:
            p = l.vert.co; u, v = [(p.y, p.z), (p.x, p.z), (p.x, p.y)][ax]; l[uvl].uv = (u * 3, v * 3)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data); bm.free()
    for p in o.data.polygons: p.use_smooth = False
    print('CASCA', nome, len(o.data.polygons)); return o
casca2(AR, 'ombreiras', lambda c, n: 0.20 < abs(c.x) < 0.34 and n.z > 0.15, 0.012, 0.012)
casca2(AR, 'bracadeiras', lambda c, n: 0.53 < abs(c.x) < 0.77, 0.010, 0.010)
casca2(B, 'cinto', lambda c, n: 0.90 < c.z < 0.99, 0.010, 0.010)
casca2(B, 'joelheiras', lambda c, n: 0.42 < c.z < 0.57 and n.y < -0.25, 0.014, 0.012)
casca2(B, 'caneleiras', lambda c, n: 0.16 < c.z < 0.40 and n.y < 0.1, 0.010, 0.010)
casca2(B, 'cano_bota', lambda c, n: 0.06 < c.z < 0.15, 0.008, 0.008)
bpy.ops.wm.save_as_mainfile(filepath=OUT); print('LUAN OK', OUT)
