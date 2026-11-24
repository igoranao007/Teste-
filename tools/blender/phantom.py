"""PHANTOM (Deadpool em PSX) — converte o modelo 3D "normal" (353 mil faces, sem esqueleto, pose A, textura PBR 2048) pro estilo PS1:
1) malha reduzida (~7.000 tri), UV novo e textura 512 por BAKE no Cycles (cor + um pouco de oclusão) com cor de 15 bits;
2) esqueleto do elenco (Simple PSX Character / JashiPSX, mesmos nomes de ossos → as 10 animações do animar_jashi.py servem),
   ossos ajustados nas articulações do modelo, pesos automáticos, braços levados da pose A pra pose T e aplicados como descanso;
3) duas pistolas MALORIAN (modelo PSX do usuário, textura 128) nos coldres das coxas;
4) VERSAO=amarela: o vermelho do traje vira AMARELO FORTE (aliado do Dom), o preto continua preto.
Uso: VERSAO=classica|amarela blender -b simple-character-psx.blend --python phantom.py -- Deadpool.glb pasta_malorian saida.blend"""
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils import Vector, Matrix
from mathutils.kdtree import KDTree
a = sys.argv[sys.argv.index('--') + 1:]; DP, MAL, OUT = a[0], a[1], a[2]
VERSAO = os.environ.get('VERSAO', 'classica'); ALVO_TRI = int(os.environ.get('ALVO_TRI', '7000')); TR = 512
RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
TXD = os.path.join(RAIZ, 'material/producao/personagens/phantom/texturas'); os.makedirs(TXD, exist_ok=True)
A = bpy.data.objects['simple_character']
for n in ('body', 'arms', 'head'): bpy.data.objects.remove(bpy.data.objects[n])
def sel(objs, ativo):
    for o in bpy.data.objects:
        try: o.select_set(False)
        except Exception: pass
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = ativo

# ---------------------------------------------------------------- 1) importa, põe os pés no chão, reduz, UV, bake
antes = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=DP)
hi = [o for o in bpy.data.objects if o not in antes and o.type == 'MESH'][0]; hi.name = 'phantom_alto'
for o in [o for o in bpy.data.objects if o not in antes and o.type != 'MESH']: bpy.data.objects.remove(o)
hi.data.transform(hi.matrix_world); hi.matrix_world = Matrix.Identity(4)
zmin = min(v.co.z for v in hi.data.vertices); hi.data.transform(Matrix.Translation((0, 0, -zmin)))
lo = hi.copy(); lo.data = hi.data.copy(); lo.name = 'phantom'; bpy.context.scene.collection.objects.link(lo)
_bm = bmesh.new(); _bm.from_mesh(lo.data); nv0 = len(_bm.verts)
bmesh.ops.remove_doubles(_bm, verts=_bm.verts, dist=0.0004)               # o original vem com os vértices soltos nas costuras de UV
_bm.to_mesh(lo.data); print('SOLDA', nv0, '->', len(_bm.verts)); _bm.free()
md = lo.modifiers.new('d', 'DECIMATE'); md.ratio = ALVO_TRI / len(lo.data.polygons); md.use_collapse_triangulate = True
sel([lo], lo); bpy.ops.object.modifier_apply(modifier='d')
print('TRI', len(lo.data.polygons))
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.003, area_weight=1.0); bpy.ops.object.mode_set(mode='OBJECT')
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 16
if sc.world is None: sc.world = bpy.data.worlds.new('w')
sc.world.light_settings.distance = 0.08
mt = hi.data.materials[0]; alvo = {n: bpy.data.images.new('bk_' + n, TR, TR, alpha=False) for n in ('cor', 'ao')}
nd = mt.node_tree.nodes.new('ShaderNodeTexImage'); mt.node_tree.nodes.active = nd
sel([hi, lo], lo)
for n, tipo in (('cor', 'DIFFUSE'), ('ao', 'AO')):
    nd.image = alvo[n]; kw = dict(type=tipo, use_selected_to_active=True, cage_extrusion=0.02, max_ray_distance=0.05, margin=4)
    if tipo == 'DIFFUSE': kw['pass_filter'] = {'COLOR'}
    bpy.ops.object.bake(**kw)
mt.node_tree.nodes.remove(nd)
C = np.array(alvo['cor'].pixels[:], np.float32).reshape(TR, TR, 4)[..., :3]; AO = np.array(alvo['ao'].pixels[:], np.float32).reshape(TR, TR, 4)[..., 0]
cor = C * (0.62 + 0.38 * np.clip(AO, 0, 1))[..., None]                     # um pouco de oclusão (dobras e costuras marcadas)
cor = np.clip(cor ** 0.9 * 1.08, 0, 1)
def amarelo(c):
    """vermelho do traje -> amarelo forte (mantém a sombra/luz pela luminância); preto, couro e olhos ficam"""
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    verm = (r > 0.12) & (r > g * 1.7) & (r > b * 1.5)
    k = np.clip((r - np.maximum(g, b)) / np.maximum(r, 1e-4), 0, 1)       # quão "vermelho" (transição suave nas bordas)
    med = float(np.median(r[verm])) if verm.any() else 0.5
    lum = np.clip(r / med * 0.78, 0, 1.25)                                  # o vermelho médio vira ~78% de luz
    y = np.stack([np.clip(lum * 1.22 + 0.10, 0, 1), np.clip(lum * 1.02 + 0.06, 0, 1), np.clip(lum * 0.10, 0, 1)], -1)   # amarelo forte (255, 214, 20 no meio)
    out = c.copy(); w = (k * verm)[..., None]; out = out * (1 - w) + y * w; return out
if VERSAO == 'amarela': cor = amarelo(cor)
cor = np.round(cor * 31) / 31                                              # 15 bits
img = bpy.data.images.new('phantom_' + VERSAO, TR, TR, alpha=False); px = np.ones((TR, TR, 4), np.float32); px[..., :3] = cor
img.pixels.foreach_set(px.ravel()); img.filepath_raw = os.path.join(TXD, f'phantom_{VERSAO}.png'); img.file_format = 'PNG'; img.save(); img.pack()
M = bpy.data.materials.new('phantom'); M.use_nodes = True; nt = M.node_tree; ti = nt.nodes.new('ShaderNodeTexImage'); ti.image = img; ti.interpolation = 'Closest'
nt.links.new(ti.outputs['Color'], nt.nodes['Principled BSDF'].inputs['Base Color']); nt.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.8; nt.nodes.active = ti
lo.data.materials.clear(); lo.data.materials.append(M)
for p in lo.data.polygons: p.use_smooth = True
bpy.data.objects.remove(hi)

# ---------------------------------------------------------------- 2) esqueleto nas articulações do modelo (pose A)
P = np.array([tuple(v.co) for v in lo.data.vertices])
def centro(x, z, rx=0.07, rz=0.03, lado=None):
    m = (np.abs(P[:, 2] - z) < rz) & (np.abs(P[:, 0] - x) < rx)
    if not m.any(): return Vector((x, 0.0, z))
    s = P[m]; return Vector((float(s[:, 0].mean()) if lado else x, float((s[:, 1].min() + s[:, 1].max()) / 2), z))
J = {}
for n, z in (('spine', 0.95), ('spine.001', 1.08), ('spine.002', 1.22), ('spine.003', 1.38), ('spine.004', 1.58), ('spine.005', 1.66)): J[n] = centro(0.0, z, 0.10)
J['topo'] = Vector((0, J['spine.005'].y, 1.88))
for s, sfx in ((1, 'L'), (-1, 'R')):
    J[f'shoulder.{sfx}'] = Vector((s * 0.05, J['spine.003'].y, 1.50))
    J[f'upper_arm.{sfx}'] = centro(s * 0.19, 1.46, 0.05, lado=1)
    J[f'forearm.{sfx}'] = centro(s * 0.345, 1.13, 0.06, lado=1)
    J[f'hand.{sfx}'] = centro(s * 0.35, 0.94, 0.06, lado=1)
    J[f'dedos.{sfx}'] = centro(s * 0.335, 0.80, 0.06, lado=1)
    J[f'pelvis.{sfx}'] = Vector((0, J['spine'].y + 0.03, 0.95))
    J[f'thigh.{sfx}'] = centro(s * 0.11, 0.92, 0.06, lado=1)
    J[f'shin.{sfx}'] = centro(s * 0.19, 0.48, 0.07, lado=1)
    J[f'foot.{sfx}'] = centro(s * 0.19, 0.10, 0.07, lado=1)
    f = J[f'foot.{sfx}']; J[f'toe.{sfx}'] = Vector((f.x, f.y - 0.12, 0.03)); J[f'dedao.{sfx}'] = Vector((f.x, f.y - 0.20, 0.02)); J[f'heel.02.{sfx}'] = Vector((f.x, f.y + 0.06, 0.02))
for k, v in J.items(): print('JUNTA', k, tuple(round(x, 3) for x in v))
A = bpy.data.objects['simple_character']                                    # (re-busca: a referência some depois do import)
sel([A], A); bpy.ops.object.mode_set(mode='EDIT'); eb = A.data.edit_bones; inv = A.matrix_world.inverted()
for b in list(eb):
    if b.name.startswith(('palm', 'f_', 'thumb')): eb.remove(b)
for b in eb: b.use_connect = False
CAD = [('spine', 'spine', 'spine.001'), ('spine.001', 'spine.001', 'spine.002'), ('spine.002', 'spine.002', 'spine.003'), ('spine.003', 'spine.003', 'spine.004'),
       ('spine.004', 'spine.004', 'spine.005'), ('spine.005', 'spine.005', 'topo')]
for sfx in ('L', 'R'):
    CAD += [(f'shoulder.{sfx}', f'shoulder.{sfx}', f'upper_arm.{sfx}'), (f'upper_arm.{sfx}', f'upper_arm.{sfx}', f'forearm.{sfx}'), (f'forearm.{sfx}', f'forearm.{sfx}', f'hand.{sfx}'),
            (f'hand.{sfx}', f'hand.{sfx}', f'dedos.{sfx}'), (f'pelvis.{sfx}', f'pelvis.{sfx}', f'thigh.{sfx}'), (f'thigh.{sfx}', f'thigh.{sfx}', f'shin.{sfx}'),
            (f'shin.{sfx}', f'shin.{sfx}', f'foot.{sfx}'), (f'foot.{sfx}', f'foot.{sfx}', f'toe.{sfx}'), (f'toe.{sfx}', f'toe.{sfx}', f'dedao.{sfx}')]
for nome, h, t in CAD:
    if nome in eb: eb[nome].head = inv @ J[h]; eb[nome].tail = inv @ J[t]
for sfx in ('L', 'R'):
    if f'heel.02.{sfx}' in eb: eb[f'heel.02.{sfx}'].head = inv @ J[f'foot.{sfx}']; eb[f'heel.02.{sfx}'].tail = inv @ J[f'heel.02.{sfx}']
for nome in ('IK.L', 'IK.R', 'PullTarget.L', 'PullTarget.R'):
    if nome in eb: eb.remove(eb[nome])
bpy.ops.object.mode_set(mode='OBJECT')
print('OSSOS', [b.name for b in A.data.bones])
# pesos automáticos
sel([lo, A], A)
try:
    bpy.ops.object.parent_set(type='ARMATURE_AUTO'); print('PESOS automáticos')
except Exception as e:
    print('AUTO falhou', e); bpy.ops.object.parent_set(type='ARMATURE_ENVELOPE')
vazios = sum(1 for v in lo.data.vertices if not v.groups); print('VERTICES SEM PESO', vazios)
# limpeza: na pose A a mão fica encostada no coldre/coxa -> tira o peso de braço do que não é braço (longe do osso da mão/antebraço)
def dist_seg(p, a, b):
    ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared)); return (p - (a + ab * t)).length
BR = {}
for sfx in ('L', 'R'):
    for n in (f'upper_arm.{sfx}', f'forearm.{sfx}', f'hand.{sfx}'):
        bn = A.data.bones[n]; BR[n] = (A.matrix_world @ bn.head_local, A.matrix_world @ bn.tail_local)
idx = {g.name: g.index for g in lo.vertex_groups}; limpos = 0
for v in lo.data.vertices:
    p = v.co
    if p.z > 1.05: continue
    if abs(p.x) > 0.287: continue                                           # na pose A a mão fica pra fora de |x| 0,29 (vão medido nas fatias)
    tira = [g for g in v.groups if lo.vertex_groups[g.group].name in BR]
    if not tira: continue
    for g in tira: lo.vertex_groups[g.group].remove([v.index])
    if not v.groups:
        sfx = 'L' if p.x > 0 else 'R'; lo.vertex_groups[f'thigh.{sfx}'].add([v.index], 1.0, 'REPLACE')
    limpos += 1
print('PESOS DE BRACO LIMPOS', limpos)

# ---------------------------------------------------------------- 3) pose A -> pose T (aplicada como descanso)
sel([A], A); bpy.ops.object.mode_set(mode='POSE')
for sfx, s in (('L', 1), ('R', -1)):
    alvo_d = Vector((s, 0.0, -0.18)).normalized()
    for n in (f'upper_arm.{sfx}', f'forearm.{sfx}', f'hand.{sfx}'):
        pb = A.pose.bones[n]; bpy.context.view_layer.update()
        cab = pb.head.copy(); d = (pb.tail - pb.head).normalized()
        R = d.rotation_difference(alvo_d).to_matrix().to_4x4()
        pb.matrix = Matrix.Translation(cab) @ R @ Matrix.Translation(-cab) @ pb.matrix
        bpy.context.view_layer.update()
bpy.ops.object.mode_set(mode='OBJECT')
CO_A = [v.co.copy() for v in lo.data.vertices]                              # posição na pose A (pra achar o que esticou)
sel([lo], lo); mdA = next(m for m in lo.modifiers if m.type == 'ARMATURE'); bpy.ops.object.modifier_apply(modifier=mdA.name)
sel([A], A); bpy.ops.object.mode_set(mode='POSE'); bpy.ops.pose.select_all(action='SELECT'); bpy.ops.pose.armature_apply(selected=False); bpy.ops.object.mode_set(mode='OBJECT')
_bm = bmesh.new(); _bm.from_mesh(lo.data)                                  # tira as "pontes": faces que ligavam a mão ao coldre (esticaram na pose T)
_bm.verts.ensure_lookup_table()
def estica(f):
    return max(e.calc_length() / max(1e-5, (CO_A[e.verts[0].index] - CO_A[e.verts[1].index]).length) for e in f.edges)
ponte = [f for f in _bm.faces if estica(f) > 2.2 and max(e.calc_length() for e in f.edges) > 0.05]
bmesh.ops.delete(_bm, geom=ponte, context='FACES'); bmesh.ops.delete(_bm, geom=[v for v in _bm.verts if not v.link_faces], context='VERTS')
_bm.to_mesh(lo.data); _bm.free(); print('PONTES REMOVIDAS', len(ponte))
m2 = lo.modifiers.new('Armature', 'ARMATURE'); m2.object = A
print('POSE T aplicada')

# ---------------------------------------------------------------- 4) Malorian nos coldres das coxas
def importar_malorian():
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=os.path.join(MAL, 'Malorian.fbx'))
    ns = [o for o in bpy.data.objects if o not in antes]
    ms = [o for o in ns if o.type == 'MESH']
    for o in ns:
        if o.type != 'MESH': bpy.data.objects.remove(o)
    sel(ms, ms[0])
    if len(ms) > 1: bpy.ops.object.join()
    g = ms[0]; g.data.transform(g.matrix_world); g.matrix_world = Matrix.Identity(4); g.parent = None
    for m in g.data.materials:                                              # liga as texturas PS1 (128 px) que o FBX não trouxe
        arq = os.path.join(MAL, 'Textures', 'Malorian_Ammo.png' if 'Ammo' in m.name else 'Malorian_Base.png')
        m.use_nodes = True; t = m.node_tree; b = t.nodes.get('Principled BSDF')
        ti = t.nodes.new('ShaderNodeTexImage'); ti.image = bpy.data.images.load(arq); ti.image.pack(); ti.interpolation = 'Closest'
        t.links.new(ti.outputs['Color'], b.inputs['Base Color']); t.nodes.active = ti
        for n in list(t.nodes):
            if n.type == 'NORMAL_MAP': t.nodes.remove(n)
    return g
base = importar_malorian()
# eixo do cano = maior dimensão (y no FBX); boca do cano pro lado -y; coronha embaixo (-z)
Pm = np.array([tuple(v.co) for v in base.data.vertices]); comp = Pm[:, 1].max() - Pm[:, 1].min()
ESC = 0.30 / comp                                                           # pistola de ~30 cm
base.data.transform(Matrix.Diagonal((ESC, ESC, ESC, 1)))
base.data.transform(Matrix.Translation(-Vector(np.array([tuple(v.co) for v in base.data.vertices]).mean(0))))
# arma solta (pra pôr na mão nas cenas): exportada separada
arma = base.copy(); arma.data = base.data.copy(); arma.name = 'malorian'; bpy.context.scene.collection.objects.link(arma)
for s, sfx in ((1, 'L'), (-1, 'R')):
    g = base.copy(); g.data = base.data.copy(); g.name = f'malorian_coldre_{sfx}'; bpy.context.scene.collection.objects.link(g)
    # no coldre: cano pra baixo, coronha pra cima e pra trás, colada na lateral da coxa
    R = Matrix.Rotation(math.radians(-90), 4, 'X') @ Matrix.Rotation(math.radians(180 if s > 0 else 0), 4, 'Z')
    g.data.transform(R)
    th = A.matrix_world @ A.data.bones[f'thigh.{sfx}'].head_local; sh = A.matrix_world @ A.data.bones[f'shin.{sfx}'].head_local
    alvo = th.lerp(sh, 0.38); Pl = P[(np.abs(P[:, 2] - alvo.z) < 0.03) & (P[:, 0] * s > 0)]
    xo = float(np.abs(Pl[:, 0]).max()) if len(Pl) else 0.27
    g.data.transform(Matrix.Translation(Vector((s * (xo + 0.025), alvo.y + 0.01, alvo.z))))
    vg = g.vertex_groups.new(name=f'thigh.{sfx}'); vg.add(list(range(len(g.data.vertices))), 1.0, 'REPLACE')
    m_ = g.modifiers.new('Armature', 'ARMATURE'); m_.object = A; g.parent = A; g.matrix_parent_inverse = A.matrix_world.inverted()
bpy.data.objects.remove(base)
sel([arma], arma)                                                           # Malorian solta (PSX) pra pôr na mão: exporta e tira do personagem
bpy.ops.export_scene.gltf(filepath=os.path.join(RAIZ, 'material/producao/personagens/phantom/malorian.glb'), export_format='GLB', use_selection=True, export_animations=False)
bpy.data.objects.remove(arma)
lo.parent = A; lo.matrix_parent_inverse = A.matrix_world.inverted()
bpy.ops.wm.save_as_mainfile(filepath=OUT); print('PHANTOM OK', VERSAO, OUT)
