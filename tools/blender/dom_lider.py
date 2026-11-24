"""DOM LÍDER — o que vai PRESO NO CORPO do Dom (sobre o dom.blend, depois do rosto_foto.py e antes do animar_jashi.py).
Desenho próprio do projeto (a referência de fã ao Hokage — chapéu, capa branca com chamas, 火 — continua só no que já existia):
- MEDALHÃO-REATOR dourado no peito (a fonte da tecnologia do grupo): aro dourado com 8 raios, disco escuro, núcleo aceso + aura;
- LINHAS DE ENERGIA finas do medalhão até os ombros e pelos braços até os punhos (`linhas_energia.py`);
- BRAÇADEIRAS de metal dourado nos antebraços com sulco aceso (casca da própria malha, presas no osso);
- PLACA DO EMBLEMA (Toca do Anão, `tools/dom_emblema.py`) acesa na fivela do cinto.
Materiais: '*brilho*' = luz própria no motor; '*aura*' = brilho aditivo em volta (lib/modelo.js).
Uso: blender -b dom.blend --python dom_lider.py -- saida.blend"""
import bpy, bmesh, sys, math, os
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
OUT = sys.argv[sys.argv.index('--') + 1]
RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
TX = os.path.join(RAIZ, 'material/producao/personagens/dom/texturas/')
A = bpy.data.objects['simple_character']; B = bpy.data.objects['body']; AR = bpy.data.objects['arms']
def osso(n): return A.matrix_world @ A.data.bones[n].head_local
def mat_cor(nome, rgb, brilho=False, rough=.6, metal=0.0):
    m = bpy.data.materials.new(nome); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    c = tuple((v / 255) ** (1.0 if brilho else 2.2) for v in rgb) + (1,)
    b.inputs['Base Color'].default_value = c; m.diffuse_color = c; b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if brilho: b.inputs['Emission Color'].default_value = c; b.inputs['Emission Strength'].default_value = 2.0
    return m
def mat_tex(nome, arq, brilho=False):
    m = bpy.data.materials.new(nome); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    ti = nt.nodes.new('ShaderNodeTexImage'); ti.image = bpy.data.images.load(arq); ti.image.pack(); ti.interpolation = 'Closest'
    nt.links.new(ti.outputs['Color'], b.inputs['Base Color']); nt.nodes.active = ti
    if brilho: nt.links.new(ti.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 1.5
    return m
M_OURO = mat_cor('d_ouro', (214, 170, 62), rough=.35, metal=.8)
M_OURO2 = mat_cor('d_ouro_escuro', (140, 102, 34), rough=.45, metal=.7)
M_ESC = mat_cor('d_escuro', (24, 22, 20), rough=.7)
M_BR = mat_cor('d_linha_brilho', (255, 224, 20), True)
M_NU = mat_cor('d_nucleo_brilho', (255, 246, 170), True)
M_AU = mat_cor('d_aura', (255, 190, 0), True)
M_EM = mat_tex('d_emblema_brilho', TX + 'emblema.png', True)
MATS = [M_OURO, M_OURO2, M_ESC, M_BR, M_NU, M_AU, M_EM]
bmP = bmesh.new()
for o in (B, AR):
    t = bmesh.new(); t.from_mesh(o.data); t.transform(o.matrix_world); me = bpy.data.meshes.new('t'); t.to_mesh(me); t.free(); bmP.from_mesh(me); bpy.data.meshes.remove(me)
PELE = BVHTree.FromBMesh(bmP)
def na_pele(o_, d_):
    h = PELE.ray_cast(Vector(o_), Vector(d_).normalized(), 1.0); return h[0], h[1]
GR = {}
def acum(n):
    if n not in GR: bm = bmesh.new(); bm.loops.layers.uv.new('UVMap'); GR[n] = bm
    return GR[n]
def juntar(dst, src):
    me = bpy.data.meshes.new('t'); src.to_mesh(me); dst.from_mesh(me); bpy.data.meshes.remove(me); src.free()
def disco(bm, uvl, c, n_, r0, r1, z0, z1, seg, mat, tampa=False, uvmap=None):
    """anel (r0..r1) com espessura z0..z1 ao longo da normal n_; tampa=True fecha o lado de fora (z1)"""
    n_ = n_.normalized(); R = n_.to_track_quat('Z', 'Y').to_matrix()
    def v(r, z, a): return bm.verts.new(c + R @ Vector((r * math.cos(a), r * math.sin(a), z)))
    A_ = [[v(r, z, 2 * math.pi * k / seg) for k in range(seg)] for r, z in ((r1, z0), (r1, z1), (r0, z1), (r0, z0))]
    for j in range(4 if r0 > 0 else 2):
        for k in range(seg):
            q = (A_[j][k], A_[j][(k + 1) % seg], A_[(j + 1) % 4][(k + 1) % seg], A_[(j + 1) % 4][k])
            try:
                f = bm.faces.new(q); f.material_index = mat
                for l in f.loops: l[uvl].uv = (0.5, 0.5)
            except ValueError: pass
    if tampa:
        f = bm.faces.new(A_[1] if r0 == 0 else A_[2]); f.material_index = mat
        for l in f.loops:
            p = R.inverted() @ (l.vert.co - c); l[uvl].uv = (0.5 + p.x / (2 * r1), 0.5 + p.y / (2 * r1)) if uvmap else (0.5, 0.5)
    return A_
FR = Vector((0, -1, 0))
# ---------------------------------------------------------------- MEDALHÃO-REATOR no peito
ZM = 1.395
hit, nrm = na_pele((0, -0.6, ZM), (0, 1, 0))
CM = hit + Vector((0, -0.012, 0)); NM = Vector((0, -1, 0.12)).normalized()
bm = bmesh.new(); uv = bm.loops.layers.uv.new('UVMap')
disco(bm, uv, CM, NM, 0.0, 0.062, 0.0, 0.010, 24, 2, tampa=True)                       # disco escuro de fundo
disco(bm, uv, CM, NM, 0.048, 0.066, 0.0, 0.022, 24, 0)                                  # aro dourado
disco(bm, uv, CM, NM, 0.044, 0.048, 0.010, 0.020, 24, 3)                                # filete aceso por dentro do aro
disco(bm, uv, CM, NM, 0.0, 0.026, 0.008, 0.026, 16, 4, tampa=True)                      # núcleo aceso
disco(bm, uv, CM, NM, 0.026, 0.034, 0.008, 0.022, 16, 1)                                # anel escuro do núcleo
R = NM.to_track_quat('Z', 'Y').to_matrix()
for k in range(8):                                                                       # 8 raios dourados saindo do aro
    a = 2 * math.pi * k / 8 + math.pi / 8; d = R @ Vector((math.cos(a), math.sin(a), 0)); L = 0.030 if k % 2 else 0.044
    p0 = CM + d * 0.064; t = bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=0.010, radius2=0.0, depth=L)['verts']
    M_ = Matrix.Translation(p0 + d * L / 2 + NM * 0.008) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    for v in t: v.co = M_ @ v.co
    for f in {f for v in t for f in v.link_faces}:
        f.material_index = 0
        for l in f.loops: l[uv].uv = (0.5, 0.5)
juntar(acum('spine.003'), bm)
# ---------------------------------------------------------------- LINHAS DE ENERGIA (finas): medalhão -> ombros -> braços -> punhos
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'linhas_energia.py')).read())
OMB_Z = 1.60
CAM = []
for s in (1, -1):
    CAM.append(('frente', [(s * 0.06, ZM + 0.03), (s * 0.10, 1.47), (s * 0.15, 1.55), (s * 0.20, OMB_Z)]))
    CAM.append(('frente', [(s * 0.05, ZM - 0.05), (s * 0.08, 1.30), (s * 0.08, 1.16)]))
lt = linhas('dom_linhas_tronco', [B], CAM, M_BR, A, larg=0.006, alto=0.003, afasta=0.003, passo=0.010)
CB = []
for s in (1, -1):
    CB.append(('cima', [(s * x, 0.035 - 0.05 * (x - 0.22) / 0.55) for x in (0.22, 0.30, 0.40, 0.50, 0.60, 0.70, 0.77)]))
lb = linhas('dom_linhas_bracos', [AR], CB, M_BR, A, larg=0.006, alto=0.003, afasta=0.003, passo=0.010)
# ---------------------------------------------------------------- BRAÇADEIRAS douradas (antebraço) com sulco aceso
def bracadeira(s, sfx):
    o = AR.copy(); o.data = AR.data.copy(); bpy.context.scene.collection.objects.link(o)
    mw = o.matrix_world; bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if not (0.56 < s * (mw @ f.calc_center_median()).x < 0.74)], context='FACES')
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    bm.normal_update(); orig = list(bm.verts); nrm = {v: v.normal.copy() for v in orig}
    for v in orig: v.co += nrm[v] * 0.016
    dentro = {v: bm.verts.new(v.co - nrm[v] * 0.008) for v in orig}
    fs = list(bm.faces); borda = [e for e in bm.edges if e.is_boundary]
    for f in fs: f.material_index = 0
    for f in fs:
        try: bm.faces.new([dentro[v] for v in reversed(f.verts)]).material_index = 1
        except ValueError: pass
    for e in borda:
        a_, b_ = e.verts
        try: bm.faces.new((a_, b_, dentro[b_], dentro[a_])).material_index = 3      # borda acesa
        except ValueError: pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data); bm.free(); o.data.materials.clear()
    for m in MATS: o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth = False
    o.name = f'dom_bracadeira_{sfx}'
    for g in list(o.vertex_groups): o.vertex_groups.remove(g)
    vg = o.vertex_groups.new(name=f'forearm.{sfx}'); vg.add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')
    for md in list(o.modifiers): o.modifiers.remove(md)
    m_ = o.modifiers.new('Armature', 'ARMATURE'); m_.object = A
bracadeira(1, 'L'); bracadeira(-1, 'R')
# ---------------------------------------------------------------- PLACA DO EMBLEMA na fivela
ZF = 1.24
hit, nrm = na_pele((0, -0.6, ZF), (0, 1, 0))
CF = hit + Vector((0, -0.010, 0))
bm = bmesh.new(); uv = bm.loops.layers.uv.new('UVMap')
t = bmesh.ops.create_cube(bm, size=1.0)['verts']
for v in t: v.co = Matrix.Translation(CF) @ Matrix.Diagonal((0.085, 0.014, 0.085, 1)) @ v.co
for f in bm.faces:
    f.material_index = 6 if f.normal.y < -0.9 else 1
    for l in f.loops: l[uv].uv = (0.5 - (l.vert.co.x - CF.x) / 0.085, 0.5 + (l.vert.co.z - CF.z) / 0.085) if f.normal.y < -0.9 else (0.5, 0.5)
juntar(acum('spine.001'), bm)
# ---------------------------------------------------------------- objetos por osso + aura
AURA = 0.006
for n, bm in GR.items():
    acesas = [f for f in bm.faces if f.material_index in (3, 4)]
    if acesas:
        dup = bmesh.ops.duplicate(bm, geom=acesas); fs = [g for g in dup['geom'] if isinstance(g, bmesh.types.BMFace)]; vs = [g for g in dup['geom'] if isinstance(g, bmesh.types.BMVert)]
        for f in fs: f.material_index = 5
        bm.normal_update(); S = set(fs)
        for v in vs:
            nn = sum((f.normal for f in v.link_faces if f in S), Vector())
            if nn.length: v.co += nn.normalized() * AURA
    me = bpy.data.meshes.new('dom_' + n); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('dom_peca_' + n, me); bpy.context.scene.collection.objects.link(o)
    for m in MATS: me.materials.append(m)
    for p in me.polygons: p.use_smooth = False
    g = o.vertex_groups.new(name=n); g.add(list(range(len(me.vertices))), 1.0, 'REPLACE')
    md = o.modifiers.new('Armature', 'ARMATURE'); md.object = A; o.parent = A; o.matrix_parent_inverse = A.matrix_world.inverted()
bmP.free()
bpy.ops.wm.save_as_mainfile(filepath=OUT); print('DOM LIDER OK', OUT)
