"""Metalis = Sonic medium poly (solowotanks, CC BY) vestido de mendigo com os trapos da folha do responsável,
ligado ao esqueleto do PSX Character Creator (10 animações).
Uso: blender -b --python montar_metalis.py -- sonic_base.blend folha.png saida.blend"""
import bpy, bmesh, sys, math
from mathutils import Vector
BASE, FOLHA, OUT = sys.argv[sys.argv.index('--') + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(BASE) as (src, dst): dst.objects = ['corpo']
corpo = dst.objects[0]; bpy.context.scene.collection.objects.link(corpo)
img = bpy.data.images.load(bpy.path.abspath(FOLHA)); img.pack()
W, H = img.size
# ---- materiais do corpo: sujar luva e tênis (mendigo)
SUJO = {'Material.004': (0.62, 0.58, 0.50), 'Material.006': (0.55, 0.52, 0.45), 'Material.005': (0.16, 0.18, 0.32)}
for m in corpo.data.materials:
    b = m.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Roughness'].default_value = 1.0
        try: b.inputs['Specular IOR Level'].default_value = 0.0
        except KeyError: pass
        if m.name in SUJO: b.inputs['Base Color'].default_value = SUJO[m.name] + (1,)
# ---- material de trapo (recorte da folha, buracos = preto da folha)
def mat_trapo(nome):
    m = bpy.data.materials.new(nome); m.use_nodes = True; nt = m.node_tree; bs = nt.nodes['Principled BSDF']
    ti = nt.nodes.new('ShaderNodeTexImage'); ti.image = img; ti.interpolation = 'Closest'
    nt.links.new(ti.outputs['Color'], bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = 1.0
    try: bs.inputs['Specular IOR Level'].default_value = 0.0
    except KeyError: pass
    sep = nt.nodes.new('ShaderNodeRGBToBW'); nt.links.new(ti.outputs['Color'], sep.inputs[0])
    mr = nt.nodes.new('ShaderNodeMath'); mr.operation = 'GREATER_THAN'; mr.inputs[1].default_value = 0.025
    nt.links.new(sep.outputs[0], mr.inputs[0]); nt.links.new(mr.outputs[0], bs.inputs['Alpha'])
    try: m.blend_method = 'CLIP'
    except Exception: pass
    m.use_backface_culling = False; nt.nodes.active = ti
    return m
def ss(a, b, v): return max(0.0, min(1.0, (v - a) / (b - a)))
def casca(nome, escolhe, desloc, uvfun, extra=None):
    bm = bmesh.new(); bm.from_mesh(corpo.data); bm.faces.ensure_lookup_table()
    fora = [f for f in bm.faces if not escolhe(f.calc_center_median(), f.normal)]
    bmesh.ops.delete(bm, geom=fora, context='FACES'); bm.normal_update()
    for v in bm.verts: v.co = v.co + v.normal * desloc(v.co)
    if extra: extra(bm)
    uvl = bm.loops.layers.uv.new('UVMap') if not bm.loops.layers.uv else bm.loops.layers.uv.active
    for f in bm.faces:
        cs = [uvfun(l.vert.co) for l in f.loops]
        us = [c[0] for c in cs]
        if max(us) - min(us) > 0.5:   # emenda do cilindro
            cs = [(u + 1 if u < 0.5 else u, v) for u, v in cs]
        for l, (u, v) in zip(f.loops, cs): l[uvl].uv = (u, v)
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(nome, me); bpy.context.scene.collection.objects.link(o)
    me.materials.append(mat_trapo('trapo_' + nome))
    print('CASCA', nome, 'tris', sum(len(p.vertices) - 2 for p in me.polygons)); return o
def cil(cx, cy, x0, x1, y0, y1, z0, z1, alcance=1.0):
    """projeção cilíndrica: frente (ângulo 0) no meio do retângulo da folha [x0..x1, y0..y1] (px), z0 embaixo z1 em cima"""
    def f(p):
        a = math.atan2(p.x - cx, -(p.y - cy)) / math.pi            # -1..1, 0 = frente
        u = (x0 + (x1 - x0) * (0.5 + 0.5 * a / alcance)) / W
        v = 1 - (y0 + (y1 - y0) * (1 - ss(z0, z1, p.z))) / H
        return (u % 1.0 if alcance >= 1 else u, v)
    return f
# folha 1254 px: trapo da frente 10..525 x 10..490 | costas 535..860 | bermuda 10..725 x 500..780
F = 1254 / W if W else 1
def px(v): return v / F
# poncho: tronco + ombro, mais largo e caindo até 0,30 m (franja)
def e_poncho(c, n): return 0.36 < c.z < 0.76 and abs(c.x) < 0.17 and not (c.z > 0.70 and abs(c.x) < 0.06 and c.y < -0.02)
def d_poncho(p): return 0.028 + 0.025 * ss(0.62, 0.40, p.z)
def barra(bm):
    ed = [e for e in bm.edges if e.is_boundary and all(v.co.z < 0.42 for v in e.verts)]
    r = bmesh.ops.extrude_edge_only(bm, edges=ed)
    for v in [g for g in r['geom'] if isinstance(g, bmesh.types.BMVert)]:
        d = Vector((v.co.x, v.co.y, 0)); d = d.normalized() if d.length else d
        v.co.z -= 0.11; v.co += d * 0.035
poncho = casca('poncho', e_poncho, d_poncho, cil(0, 0.01, px(10), px(860), px(10), px(490), 0.30, 0.77), barra)
# bermuda de trapo nas coxas
def e_bermuda(c, n): return 0.24 < c.z < 0.44 and abs(c.x) < 0.16
def d_bermuda(p): return 0.022 + 0.014 * ss(0.36, 0.25, p.z)
bermuda = casca('bermuda', e_bermuda, d_bermuda, cil(0, 0.0, px(10), px(725), px(500), px(780), 0.24, 0.44))
# ---- esqueleto PSX com as juntas do Sonic
antes = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath='material/modelos/itch/psx-creator/man_2.glb')
for x in [x for x in bpy.data.objects if x not in antes]:
    if x.type == 'MESH': bpy.data.objects.remove(x, do_unlink=True)
arm = [x for x in bpy.data.objects if x.type == 'ARMATURE'][0]; arm.name = 'rig'
bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active = arm; arm.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
P = {'Hips': ((0, 0.0, 0.40), (0, 0.0, 0.46)), 'Spine': ((0, 0.0, 0.46), (0, 0.0, 0.72)), 'Head': ((0, 0.0, 0.73), (0, 0.0, 1.05))}
for s, L in ((1, 'Left'), (-1, 'Right')):
    P[L + 'Arm'] = ((s * 0.11, 0, 0.695), (s * 0.24, 0, 0.695)); P[L + 'ForeArm'] = ((s * 0.24, 0, 0.695), (s * 0.34, 0, 0.695))
    P[L + 'Hand'] = ((s * 0.34, 0, 0.695), (s * 0.55, 0, 0.695))
    P[L + 'UpLeg'] = ((s * 0.075, 0, 0.40), (s * 0.075, 0, 0.26)); P[L + 'Leg'] = ((s * 0.075, 0, 0.26), (s * 0.075, 0, 0.12))
    P[L + 'Foot'] = ((s * 0.075, 0, 0.12), (s * 0.075, -0.18, 0.0))
bpy.ops.object.mode_set(mode='EDIT')
for b in arm.data.edit_bones:
    if b.name in P:
        r = b.roll; b.use_connect = False; b.head = P[b.name][0]; b.tail = P[b.name][1]; b.roll = r
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT'); corpo.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
from mathutils.geometry import intersect_point_line
seg = {b.name: (b.head_local, b.tail_local) for b in arm.data.bones}
def dseg(p, n):
    h, t = seg[n]; q, f = intersect_point_line(p, h, t); f = max(0, min(1, f)); return (p - (h + (t - h) * f)).length
for v in corpo.data.vertices:
    if not v.groups:
        n = 'Head' if v.co.z > 0.72 else min(seg, key=lambda k: dseg(v.co, k))
        corpo.vertex_groups[n].add([v.index], 1.0, 'REPLACE')
print('PESOS sem osso', sum(1 for v in corpo.data.vertices if not v.groups), 'de', len(corpo.data.vertices))
for x in (poncho, bermuda):
    for g in corpo.vertex_groups: x.vertex_groups.new(name=g.name)
    dt = x.modifiers.new('pesos', 'DATA_TRANSFER'); dt.object = corpo; dt.use_vert_data = True
    dt.data_types_verts = {'VGROUP_WEIGHTS'}; dt.vert_mapping = 'NEAREST'
    bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active = x; x.select_set(True)
    bpy.ops.object.datalayout_transfer(modifier='pesos'); bpy.ops.object.modifier_apply(modifier='pesos')
    if x is poncho:   # barra do poncho presa no quadril/tronco (não acompanha a perna)
        for v in x.data.vertices:
            for g in list(v.groups):
                nm = x.vertex_groups[g.group].name
                if 'Leg' in nm or 'Arm' in nm or 'Hand' in nm: x.vertex_groups[nm].remove([v.index])
            if not v.groups: x.vertex_groups['Spine' if v.co.z > 0.46 else 'Hips'].add([v.index], 1.0, 'REPLACE')
    m = x.modifiers.new('Armature', 'ARMATURE'); m.object = arm; x.parent = arm
for ac in bpy.data.actions: ac.use_fake_user = True
arm.animation_data_create(); arm.animation_data.action = bpy.data.actions.get('idle')
for o in bpy.data.objects:
    if o.type == 'MESH':
        for p in o.data.polygons: p.use_smooth = True
bpy.ops.wm.save_as_mainfile(filepath=OUT); print('METALIS OK')
