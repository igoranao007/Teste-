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
# --- correções de forma (corpo do 'dude' vestia bermuda, meia/bota e manga dobrada) ---
import os
for v in o.data.vertices:
    x, y, z = v.co; sx = 1 if x >= 0 else -1; ax = abs(x)
    if 0.24 <= z <= 0.60 and ax < 0.30:                    # perna nua -> perna de calça (um pouco mais grossa)
        f = 1.16
        c = 0.112; v.co.x = sx * (c + (ax - c) * f); v.co.y = 0.01 + (y - 0.01) * f
    if 0.60 < z < 0.98 and ax < 0.30:                      # bermuda larga -> calça reta
        f = 0.66 + 0.34 * max(0.0, min(1.0, (z - 0.66) / 0.30)) ** 1.5
        c = 0.112; v.co.x = sx * (c + (ax - c) * f); v.co.y = 0.01 + (y - 0.01) * f
    if 0.05 < z < 0.24 and ax < 0.30:                      # cano da bota/meia -> tornozelo fino
        f = 0.80 if z > 0.10 else 0.9
        c = 0.112; v.co.x = sx * (c + (ax - c) * f); v.co.y = -0.02 + (y + 0.02) * f
    if 0.44 < ax < 0.665 and z > 1.25:                     # manga inchada no antebraço
        f = 0.82
        v.co.y = y * f; v.co.z = 1.40 + (z - 1.40) * f
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
SH, EL, WR, HE = 0.15, 0.415, 0.66, 0.85; AZ = 1.41
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
# pesos automáticos (calor dos ossos) do Blender; se falhar, cai no osso mais próximo
bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
vazios = sum(1 for v in o.data.vertices if not v.groups)
print('PESOS auto, vertices sem osso:', vazios, 'de', len(o.data.vertices))
if vazios > len(o.data.vertices) * 0.05:
    ossos = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in arm.data.bones}
    def dist(p, n):
        h, t = ossos[n]; q, f = intersect_point_line(p, h, t); f = max(0, min(1, f)); return (p - (h + (t - h) * f)).length
    for v in o.data.vertices:
        if v.groups: continue
        n1 = min(ossos, key=lambda n: dist(v.co, n)); o.vertex_groups[n1].add([v.index], 1.0, 'REPLACE')
for ac in bpy.data.actions: ac.use_fake_user = True
arm.animation_data_create(); arm.animation_data.action = bpy.data.actions.get('idle')
print('ACOES', [x.name for x in bpy.data.actions], 'TRIS', sum(len(p.vertices) - 2 for p in o.data.polygons))
bpy.ops.wm.save_as_mainfile(filepath=OUT)
