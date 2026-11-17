"""Deixa o Metalis mais mendigo: pelo sujo (cor por vértice), pálpebra caída, cobertor xadrez nos ombros,
luvas/tênis furados e encardidos, corda nos tênis, lata, garrafa, trouxa nas costas, papelão no chão, postura curvada.
Uso: blender -b metalis_v2.blend --python mendigar_metalis.py -- xadrez.png saida.blend"""
import bpy, bmesh, sys, math, random
from mathutils import Vector, Quaternion, Matrix
XAD, OUT = sys.argv[sys.argv.index('--') + 1:]
random.seed(3)
corpo = bpy.data.objects['corpo']; arm = bpy.data.objects['rig']; me = corpo.data
def hsh(v, s=1): return ((int(v.x * 997 * s) * 73856093) ^ (int(v.y * 991 * s) * 19349663) ^ (int(v.z * 983 * s) * 83492791)) % 1000 / 1000
# ---------- materiais: olho separado da luva; cores encardidas
def nova_mat(nome, cor, vcol=True):
    m = bpy.data.materials.new(nome); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = 1.0
    try: b.inputs['Specular IOR Level'].default_value = 0.0
    except KeyError: pass
    if vcol:
        ca = nt.nodes.new('ShaderNodeVertexColor'); ca.layer_name = 'sujeira'
        mx = nt.nodes.new('ShaderNodeMixRGB'); mx.blend_type = 'MULTIPLY'; mx.inputs['Fac'].default_value = 1.0
        mx.inputs['Color1'].default_value = cor + (1,); nt.links.new(ca.outputs['Color'], mx.inputs['Color2']); nt.links.new(mx.outputs['Color'], b.inputs['Base Color'])
    else: b.inputs['Base Color'].default_value = cor + (1,)
    return m
M = {'pelo': nova_mat('pelo_sujo', (0.05, 0.08, 0.26)), 'pele': nova_mat('pele_suja', (0.55, 0.36, 0.24)), 'luva': nova_mat('luva_suja', (0.60, 0.55, 0.46)),
     'olho': nova_mat('olho', (0.80, 0.78, 0.68), False), 'tenis': nova_mat('tenis_sujo', (0.22, 0.20, 0.30)), 'preto': nova_mat('preto', (0.02, 0.02, 0.02), False),
     'verde': nova_mat('iris', (0.0, 0.12, 0.02), False)}
ant = [m.name for m in me.materials]; mi0 = [p.material_index for p in me.polygons]; me.materials.clear()
for k in ('pelo', 'pele', 'luva', 'olho', 'tenis', 'preto', 'verde'): me.materials.append(M[k])
idx = {k: i for i, k in enumerate(('pelo', 'pele', 'luva', 'olho', 'tenis', 'preto', 'verde'))}
MAP = {'Material.001': 'pelo', 'Material.003': 'pele', 'Material.004': 'luva', 'Material.006': 'luva', 'Material.005': 'tenis', 'Material.002': 'preto', 'Material.007': 'verde'}
pi = {}
for p in me.polygons:
    k = MAP.get(ant[mi0[p.index]], 'pelo')
    if k == 'luva' and p.center.z > 0.80: k = 'olho'
    if k == 'luva' and p.center.z < 0.22: k = 'tenis'
    p.material_index = idx[k]; pi[p.index] = k
import collections; print('MATS', ant, collections.Counter(pi.values()))
# ---------- sujeira por vértice (manchas, encardido embaixo, furos escuros na ponta dos dedos e no tênis)
ca = me.color_attributes.new('sujeira', 'BYTE_COLOR', 'CORNER')
for p in me.polygons:
    k = pi[p.index]
    for li in p.loop_indices:
        v = me.vertices[me.loops[li].vertex_index].co
        n = hsh(v, 1); n2 = hsh(v, 3)
        f = 0.72 + 0.35 * n                                   # manchas
        f *= 0.75 + 0.25 * min(1.0, v.z / 0.6) if k != 'olho' else 1.0   # mais sujo embaixo
        c = [f, f * 0.97, f * 0.92]
        if n2 > 0.86 and k in ('pelo', 'pele'): c = [c[0] * 1.15, c[1] * 0.85, c[2] * 0.55]   # barro
        if k == 'luva' and abs(v.x) > 0.49 and n2 > 0.45: c = [0.9, 0.62, 0.42]              # dedo aparecendo (furo)
        if k == 'tenis' and n2 > 0.80: c = [0.15, 0.13, 0.12]                                 # furo no tênis
        ca.data[li].color = (c[0], c[1], c[2], 1.0)
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name in ('poncho', 'bermuda'):
        m = o.data.materials[0]; b = m.node_tree.nodes['Principled BSDF']
        for n in m.node_tree.nodes:
            if n.type == 'TEX_IMAGE': n.image = bpy.data.images.load(bpy.path.abspath(sys.argv[sys.argv.index('--') + 1].replace('cobertor_xadrez', 'metalis_trapos_remendos')))
def peca(nome, bm, mat, ossos):
    mesh = bpy.data.meshes.new(nome); bm.to_mesh(mesh); bm.free()
    o = bpy.data.objects.new(nome, mesh); bpy.context.scene.collection.objects.link(o); mesh.materials.append(mat)
    if ossos:
        if isinstance(ossos, str):
            g = o.vertex_groups.new(name=ossos); g.add(list(range(len(mesh.vertices))), 1.0, 'REPLACE')
        else:
            for g in corpo.vertex_groups: o.vertex_groups.new(name=g.name)
            dt = o.modifiers.new('p', 'DATA_TRANSFER'); dt.object = corpo; dt.use_vert_data = True; dt.data_types_verts = {'VGROUP_WEIGHTS'}; dt.vert_mapping = 'NEAREST'
            bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active = o; o.select_set(True)
            bpy.ops.object.datalayout_transfer(modifier='p'); bpy.ops.object.modifier_apply(modifier='p')
        am = o.modifiers.new('Armature', 'ARMATURE'); am.object = arm; o.parent = arm
    print('PECA', nome, sum(len(p.vertices) - 2 for p in mesh.polygons)); return o
# ---------- pálpebras caídas: metade de cima do branco do olho coberta de pelo
bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
olhos = [f for f in bm.faces if f.material_index == idx['olho']]
lims = {}
for f in olhos:
    s = 1 if f.calc_center_median().x > 0 else -1
    for v in f.verts: lo, hi = lims.get(s, (9, -9)); lims[s] = (min(lo, v.co.z), max(hi, v.co.z))
fora = [f for f in bm.faces if not (f.material_index in (idx['olho'], idx['verde'], idx['preto']) and f.calc_center_median().z > 0.82
        and f.calc_center_median().z > lims[1 if f.calc_center_median().x > 0 else -1][0] + 0.52 * (lims[1 if f.calc_center_median().x > 0 else -1][1] - lims[1 if f.calc_center_median().x > 0 else -1][0]))]
bmesh.ops.delete(bm, geom=fora, context='FACES'); bm.normal_update()
for v in bm.verts: v.co += v.normal * 0.006
for f in bm.faces: f.material_index = 0
palp = peca('palpebras', bm, M['pelo'], 'Head')
# ---------- cobertor xadrez nos ombros (tipo capa curta com capuz caído)
img = bpy.data.images.load(bpy.path.abspath(XAD)); img.pack()
mx = bpy.data.materials.new('cobertor'); mx.use_nodes = True; nt = mx.node_tree; b = nt.nodes['Principled BSDF']
ti = nt.nodes.new('ShaderNodeTexImage'); ti.image = img; ti.interpolation = 'Closest'; nt.links.new(ti.outputs['Color'], b.inputs['Base Color'])
bw = nt.nodes.new('ShaderNodeRGBToBW'); nt.links.new(ti.outputs['Color'], bw.inputs[0]); gt = nt.nodes.new('ShaderNodeMath'); gt.operation = 'GREATER_THAN'; gt.inputs[1].default_value = 0.03
nt.links.new(bw.outputs[0], gt.inputs[0]); nt.links.new(gt.outputs[0], b.inputs['Alpha']); b.inputs['Roughness'].default_value = 1.0
try: mx.blend_method = 'CLIP'
except Exception: pass
mx.use_backface_culling = False; nt.nodes.active = ti
bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
def e_cob(c):
    if abs(c.x) > 0.21: return False
    if 0.58 < c.z < 0.78: return not (c.y < -0.06 and abs(c.x) < 0.09)      # ombros e costas (frente aberta)
    if 0.78 <= c.z < 0.86 and c.y > 0.06: return True                        # capuz caído na nuca
    return False
bmesh.ops.delete(bm, geom=[f for f in bm.faces if not e_cob(f.calc_center_median())], context='FACES'); bm.normal_update()
for v in bm.verts: v.co += v.normal * (0.045 + 0.02 * random.random())
ed = [e for e in bm.edges if e.is_boundary and all(v.co.z < 0.64 for v in e.verts)]
r = bmesh.ops.extrude_edge_only(bm, edges=ed)
for v in [g for g in r['geom'] if isinstance(g, bmesh.types.BMVert)]:
    d = Vector((v.co.x, v.co.y, 0)); d = d.normalized() if d.length else d; v.co.z -= 0.07 + 0.04 * random.random(); v.co += d * 0.02
uvl = bm.loops.layers.uv.new('UVMap')
for f in bm.faces:
    for l in f.loops:
        p = l.vert.co; a = math.atan2(p.x, -(p.y - 0.02)) / math.pi
        l[uvl].uv = ((a * 0.5 + 0.5) * 2.0 % 1.0, (p.z - 0.45) / 0.45)
peca('cobertor', bm, mx, True)
# ---------- corda nos tênis
corda = bpy.data.materials.new('corda'); corda.use_nodes = True; corda.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.32, 0.20, 0.09, 1)
def anel(nome, c, R, r, rot, osso):
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, segments=8, radius=1)
    bm.free()
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=10, minor_segments=4, location=c, rotation=rot)
    o = bpy.context.object; o.name = nome; o.data.materials.append(corda)
    bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.transform(bm, matrix=o.matrix_world, verts=bm.verts); bpy.data.objects.remove(o, do_unlink=True)
    return peca(nome, bm, corda, osso)
for s, L in ((1, 'Left'), (-1, 'Right')):
    anel('corda_tornozelo', (s * 0.075, -0.02, 0.15), 0.068, 0.009, (0, 0, 0), L + 'Foot')
    anel('corda_peito_pe', (s * 0.075, -0.12, 0.06), 0.07, 0.009, (math.radians(70), 0, 0), L + 'Foot')
# ---------- objetos: lata (mão direita), garrafa (mão esquerda), trouxa nas costas, papelão no chão
def cilindro(nome, c, r, h, cor, osso, seg=8, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=r, depth=h, location=c, rotation=rot)
    o = bpy.context.object; m = bpy.data.materials.new(nome); m.use_nodes = True
    bb = m.node_tree.nodes['Principled BSDF']; bb.inputs['Base Color'].default_value = cor + (1,); bb.inputs['Roughness'].default_value = 0.6
    bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.transform(bm, matrix=o.matrix_world, verts=bm.verts); bpy.data.objects.remove(o, do_unlink=True)
    return peca(nome, bm, m, osso)
cilindro('lata', (-0.46, -0.05, 0.695), 0.032, 0.075, (0.45, 0.45, 0.44), 'RightHand')
cilindro('garrafa', (0.46, -0.05, 0.70), 0.026, 0.12, (0.06, 0.22, 0.08), 'LeftHand')
cilindro('gargalo', (0.46, -0.05, 0.78), 0.010, 0.05, (0.06, 0.22, 0.08), 'LeftHand')
cilindro('vara', (0.0, 0.17, 0.66), 0.008, 0.62, (0.30, 0.20, 0.10), 'Spine', 6, (0, math.radians(50), 0))
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.10, location=(-0.22, 0.18, 0.88))
o = bpy.context.object; o.scale = (1, 0.8, 0.85); bpy.ops.object.transform_apply(scale=True)
bm = bmesh.new(); bm.from_mesh(o.data); bpy.data.objects.remove(o, do_unlink=True)
for v in bm.verts: v.co *= 1 + 0.08 * (random.random() - 0.5)
uvl = bm.loops.layers.uv.new('UVMap')
for f in bm.faces:
    for l in f.loops: l[uvl].uv = ((l.vert.co.x + 0.3) * 3, (l.vert.co.z - 0.7) * 3)
peca('trouxa', bm, mx, 'Spine')
bpy.ops.mesh.primitive_cube_add(size=1, location=(0.36, 0.05, 0.006)); o = bpy.context.object; o.name = 'papelao_cena'
o.scale = (0.42, 0.30, 0.01); bpy.ops.object.transform_apply(scale=True); o.rotation_euler[2] = 0.15
mp = bpy.data.materials.new('papelao'); mp.use_nodes = True; mp.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.42, 0.28, 0.14, 1); o.data.materials.append(mp)
# ---------- postura curvada: soma inclinação no Spine e Head em todas as ações
import os
CURVA = float(os.environ.get('CURVA', '22')); CAB = float(os.environ.get('CAB', '14'))
def canais(a):
    try:
        for lay in a.layers:
            for st in lay.strips:
                for cb in st.channelbags: yield from cb.fcurves
    except AttributeError:
        yield from a.fcurves
def curvar(osso, graus):
    off = Quaternion((1, 0, 0), math.radians(graus))
    for a in bpy.data.actions:
        fcs = {fc.array_index: fc for fc in canais(a) if fc.data_path == 'pose.bones["%s"].rotation_quaternion' % osso}
        if len(fcs) < 4: continue
        frames = sorted(set(round(k.co[0], 3) for fc in fcs.values() for k in fc.keyframe_points))
        novos = {}
        for fr in frames:
            q = Quaternion([fcs[i].evaluate(fr) for i in range(4)]); novos[fr] = q @ off
        for i in range(4):
            fc = fcs[i]
            for fr, q in novos.items(): fc.keyframe_points.insert(fr, q[i], options={'REPLACE', 'FAST'})
            fc.update()
curvar('Spine', CURVA); curvar('Head', -CAB * 0.3)
arm.animation_data.action = bpy.data.actions.get('idle')
bpy.ops.wm.save_as_mainfile(filepath=OUT); print('MENDIGO OK')
