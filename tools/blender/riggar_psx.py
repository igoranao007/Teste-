"""Liga uma malha em T-pose ('corpo' num .blend) ao esqueleto do PSX Character Creator (10 animações), com juntas dadas.
Uso: blender -b --python riggar_psx.py -- malha.blend textura.png juntas.json saida.blend"""
import bpy, sys, json
a = sys.argv[sys.argv.index('--') + 1:]; MALHA, TEX, JS, OUT = a
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(MALHA) as (src, dst): dst.objects = [n for n in src.objects]
for x in dst.objects: bpy.context.scene.collection.objects.link(x)
o = bpy.data.objects['corpo']; pecas = [x for x in dst.objects if x.type == 'MESH' and x.name != 'corpo']
# material simples estilo PS1: textura sem filtro, sem brilho
m = bpy.data.materials.new('mat_corpo'); m.use_nodes = True; nt = m.node_tree; bs = nt.nodes['Principled BSDF']
ti = nt.nodes.new('ShaderNodeTexImage'); ti.image = bpy.data.images.load(TEX); ti.image.pack(); ti.interpolation = 'Closest'
nt.links.new(ti.outputs['Color'], bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = 1.0
try: bs.inputs['Specular IOR Level'].default_value = 0.0
except KeyError: pass
nt.nodes.active = ti
for x in [o] + [p for p in pecas if not p.get('proprio')]: x.data.materials.clear(); x.data.materials.append(m)
J = json.load(open(JS))
# roupa com volume: terno e calça um pouco mais largos que o corpo (cabeça, pescoço, mãos e pés ficam)
import os
INF = float(os.environ.get('INFLAR', '0.012'))
mao_x = J['hand.l']['head'][0] - 0.015
for v in o.data.vertices:
    x, y, z = v.co
    if z > 1.53 or abs(x) > mao_x or z < 0.10: continue
    k = INF * (0.7 if z < 0.93 else 1.0)
    v.co = v.co + v.normal * k
def h(n): return J[n]['head']
antes = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath='material/modelos/itch/psx-creator/man_2.glb')
for x in [x for x in bpy.data.objects if x not in antes]:
    if x.type == 'MESH': bpy.data.objects.remove(x, do_unlink=True)
arm = [x for x in bpy.data.objects if x.type == 'ARMATURE'][0]; arm.name = 'rig'
bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active = arm; arm.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
SH = J['arm_stretch.l']['head'][0] - 0.11; EL = J['forearm_stretch.l']['head'][0]; WR = J['hand.l']['head'][0]; HE = J['hand.l']['tail'][0] + 0.04
AZ = J['arm_stretch.l']['head'][2]; HX = J['thigh_stretch.l']['head'][0]
HIP = J['root.x']['tail'][2]; KN = J['leg_stretch.l']['head'][2]; AN = J['foot.l']['head'][2]
P = {'Hips': ((0, 0.03, HIP), (0, 0.03, J['spine_01.x']['head'][2])), 'Spine': ((0, 0.03, J['spine_01.x']['head'][2]), (0, 0.04, J['neck.x']['head'][2])),
     'Head': ((0, 0.03, J['neck.x']['head'][2] + 0.01), (0, 0.03, J['head.x']['tail'][2]))}
for s, L, l in ((1, 'Left', 'l'), (-1, 'Right', 'r')):
    P[L + 'Arm'] = ((s * SH, 0.04, AZ), (s * EL, 0.03, AZ)); P[L + 'ForeArm'] = ((s * EL, 0.03, AZ), (s * WR, 0.0, AZ)); P[L + 'Hand'] = ((s * WR, 0.0, AZ), (s * HE, -0.01, AZ))
    P[L + 'UpLeg'] = ((s * HX, 0.01, HIP - 0.04), (s * HX, 0.0, KN)); P[L + 'Leg'] = ((s * HX, 0.0, KN), (s * HX, 0.01, AN))
    P[L + 'Foot'] = ((s * HX, 0.01, AN), (s * HX, -0.15, 0.0))
print('JUNTAS', {k: [round(x, 3) for x in v[0]] for k, v in P.items()})
bpy.ops.object.mode_set(mode='EDIT')
for b in arm.data.edit_bones:
    if b.name in P:
        r = b.roll; b.use_connect = False; b.head = P[b.name][0]; b.tail = P[b.name][1]; b.roll = r
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
# peças (roupa, cabelo): pesos copiados do corpo (seguem o corpo sem atravessar)
for x in pecas:
    for g in o.vertex_groups: x.vertex_groups.new(name=g.name)
    dt = x.modifiers.new('pesos', 'DATA_TRANSFER'); dt.object = o; dt.use_vert_data = True
    dt.data_types_verts = {'VGROUP_WEIGHTS'}; dt.vert_mapping = 'NEAREST'
    bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active = x; x.select_set(True)
    bpy.ops.object.datalayout_transfer(modifier='pesos'); bpy.ops.object.modifier_apply(modifier='pesos')
    # limpa pesos absurdos: osso longe demais do vértice (> 0,22 m) não pode mexer nele
    from mathutils.geometry import intersect_point_line
    seg = {b.name: (b.head_local, b.tail_local) for b in arm.data.bones}
    def dseg(p, n):
        h, t = seg[n]; q, f = intersect_point_line(p, h, t); f = max(0, min(1, f)); return (p - (h + (t - h) * f)).length
    for v in x.data.vertices:
        gs = [(x.vertex_groups[g.group].name, g.weight) for g in v.groups if x.vertex_groups[g.group].name in seg]
        ruins = [n for n, w in gs if w > 0 and dseg(v.co, n) > 0.22]
        for n in ruins: x.vertex_groups[n].remove([v.index])
        if ruins and not any(n not in ruins and w > 0 for n, w in gs):
            perto = min(seg, key=lambda n: dseg(v.co, n)); x.vertex_groups[perto].add([v.index], 1.0, 'REPLACE')
    if x.name == 'paleto':   # barra do paletó presa no quadril (não rasga quando a perna anda)
        hips = x.vertex_groups['Hips']
        for v in x.data.vertices:
            if v.co.z < 1.0:
                f = max(0.0, min(1.0, (1.0 - v.co.z) / 0.10))
                for g in v.groups:
                    nome = x.vertex_groups[g.group].name
                    if 'Leg' in nome: x.vertex_groups[nome].add([v.index], g.weight * (1 - f), 'REPLACE')
                hips.add([v.index], f, 'ADD')
    am = x.modifiers.new('Armature', 'ARMATURE'); am.object = arm; x.parent = arm
    print('PECA', x.name, 'sem peso:', sum(1 for v in x.data.vertices if not v.groups))
print('PESOS sem osso:', sum(1 for v in o.data.vertices if not v.groups), 'de', len(o.data.vertices))
for ac in bpy.data.actions: ac.use_fake_user = True
arm.animation_data_create(); arm.animation_data.action = bpy.data.actions.get('idle')
print('ACOES', [x.name for x in bpy.data.actions], 'TRIS', sum(len(p.vertices) - 2 for p in o.data.polygons))
bpy.ops.wm.save_as_mainfile(filepath=OUT)
