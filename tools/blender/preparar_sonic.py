"""Prepara o Sonic medium poly: aplica subsurf, vira de frente pra -Y, escala pra ALTURA m com pés no chão.
Uso: blender -b --disable-autoexec sonic.blend --python preparar_sonic.py -- saida.blend [altura]"""
import bpy, sys, math
a = sys.argv[sys.argv.index('--') + 1:]; OUT = a[0]; ALT = float(a[1]) if len(a) > 1 else 1.10
for x in list(bpy.data.objects):
    if x.type != 'MESH': bpy.data.objects.remove(x, do_unlink=True)
o = bpy.data.objects['Cube']; o.name = 'corpo'
bpy.context.view_layer.objects.active = o; o.select_set(True)
for m in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=m.name)
o.rotation_euler[2] += math.radians(-90)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
vs = [v.co for v in o.data.vertices]; zmin = min(v.z for v in vs); zmax = max(v.z for v in vs)
cx = (min(v.x for v in vs) + max(v.x for v in vs)) / 2; cy = (min(v.y for v in vs) + max(v.y for v in vs)) / 2
k = ALT / (zmax - zmin)
for v in o.data.vertices: v.co.x = (v.co.x - cx) * k; v.co.y = (v.co.y - cy) * k; v.co.z = (v.co.z - zmin) * k
o.data.update(); print('PRONTO tris', sum(len(p.vertices) - 2 for p in o.data.polygons), 'escala', round(k, 4))
bpy.ops.wm.save_as_mainfile(filepath=OUT)
