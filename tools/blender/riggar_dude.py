"""Liga um modelo 'dudes 3D' (T-pose, espelhado, sem esqueleto) ao esqueleto do PSX Character Creator (10 animações).
Uso: blender -b --python riggar_dude.py -- dudes.blend "dude 2" textura.png saida.blend"""
import bpy, sys, math
from mathutils import Vector
from mathutils.geometry import intersect_point_line
a = sys.argv[sys.argv.index('--') + 1:]; FONTE, NOME, TEX, OUT = a
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(FONTE) as (src, dst): dst.objects = [NOME]
o = dst.objects[0]; bpy.context.scene.collection.objects.link(o)
bpy.context.view_layer.objects.active = o; o.select_set(True)
for m in list(o.modifiers):
    if m.type == 'ARMATURE': o.modifiers.remove(m)
bpy.ops.object.modifier_apply(modifier='Mirror')
o.vertex_groups.clear()
cx = o.location.x; o.location.x = 0; o.name = 'corpo'
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for n in o.active_material.node_tree.nodes:
    if n.type == 'TEX_IMAGE': n.image = bpy.data.images.load(TEX); n.image.pack(); n.interpolation = 'Closest'
# esqueleto + animações da base PSX
antes = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath='material/modelos/itch/psx-creator/man_2.glb')
for x in [x for x in bpy.data.objects if x not in antes]:
    if x.type == 'MESH': bpy.data.objects.remove(x, do_unlink=True)
arm = [x for x in bpy.data.objects if x.type == 'ARMATURE'][0]; arm.name = 'rig'
print('RIG transf', tuple(arm.location), tuple(arm.rotation_euler), tuple(arm.scale))
bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active = arm; arm.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
# juntas medidas no modelo (m)
SH, EL, WR, HE = 0.17, 0.415, 0.66, 0.85; AZ = 1.40
HX, HIP, KN, AN = 0.112, 0.90, 0.50, 0.09
J = {'Hips': ((0, 0, 0.92), (0, 0, 1.00)), 'Spine': ((0, 0, 1.00), (0, 0.01, 1.46)), 'Head': ((0, 0.01, 1.47), (0, 0.01, 1.80))}
for s, L in ((1, 'Left'), (-1, 'Right')):
    J[L + 'Arm'] = ((s * SH, 0, AZ), (s * EL, 0, AZ)); J[L + 'ForeArm'] = ((s * EL, 0, AZ), (s * WR, 0, AZ)); J[L + 'Hand'] = ((s * WR, 0, AZ), (s * HE, 0, AZ))
    J[L + 'UpLeg'] = ((s * HX, 0, HIP), (s * HX, 0, KN)); J[L + 'Leg'] = ((s * HX, 0, KN), (s * HX, 0, AN))
    J[L + 'Foot'] = ((s * HX, 0, AN), (s * HX, -0.16, 0.0))
bpy.ops.object.mode_set(mode='EDIT')
for b in arm.data.edit_bones:
    if b.name in J:
        r = b.roll; b.use_connect = False; b.head = J[b.name][0]; b.tail = J[b.name][1]; b.roll = r
bpy.ops.object.mode_set(mode='OBJECT')
# pesos: osso mais próximo (com zonas), mistura suave perto das juntas
ossos = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in arm.data.bones}
def dist(p, n):
    h, t = ossos[n]; q, f = intersect_point_line(p, h, t); f = max(0, min(1, f)); return (p - (h + (t - h) * f)).length
def candidatos(p):
    ax = abs(p.x); lado = 'Left' if p.x > 0 else 'Right'
    if p.z > 1.47 and ax < 0.16: return ['Head', 'Spine']
    if ax > SH - 0.02 and p.z > 1.25: return [lado + 'Arm', lado + 'ForeArm', lado + 'Hand', 'Spine']
    if p.z < 0.93: return [lado + 'UpLeg', lado + 'Leg', lado + 'Foot', 'Hips']
    return ['Spine', 'Hips', lado + 'Arm', 'Head']
G = {n: o.vertex_groups.new(name=n) for n in ossos}
for v in o.data.vertices:
    p = v.co; ds = sorted((dist(p, n), n) for n in candidatos(p))
    (d1, n1), (d2, n2) = ds[0], ds[1]
    w2 = max(0.0, 0.5 - (d2 - d1) / 0.06) if d2 - d1 < 0.03 else 0.0
    G[n1].add([v.index], 1 - w2, 'REPLACE')
    if w2 > 0: G[n2].add([v.index], w2, 'REPLACE')
md = o.modifiers.new('Armature', 'ARMATURE'); md.object = arm; o.parent = arm
for ac in bpy.data.actions: ac.use_fake_user = True
arm.animation_data_create(); arm.animation_data.action = bpy.data.actions.get('idle')
print('ACOES', [x.name for x in bpy.data.actions], 'TRIS', sum(len(p.vertices) - 2 for p in o.data.polygons))
bpy.ops.wm.save_as_mainfile(filepath=OUT)
