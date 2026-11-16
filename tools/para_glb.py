"""Converte FBX / OBJ / BLEND em GLB (texturas embutidas) com o Blender.
uso: blender -b --disable-autoexec --python tools/para_glb.py -- <entrada> <saida.glb>
Imprime um resumo: malhas, triângulos, ossos, animações, texturas e tamanho (m).
"""
import bpy, sys, os
from mathutils import Vector
src, dst = sys.argv[sys.argv.index("--") + 1:][:2]
ext = os.path.splitext(src)[1].lower()
if ext == ".blend":
    bpy.ops.wm.open_mainfile(filepath=src, use_scripts=False)
else:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if ext == ".fbx": bpy.ops.import_scene.fbx(filepath=src)
    elif ext == ".obj": bpy.ops.wm.obj_import(filepath=src)
    else: raise SystemExit("formato não suportado: " + ext)
# câmeras e luzes não interessam
for o in list(bpy.data.objects):
    if o.type in {"CAMERA", "LIGHT"}: bpy.data.objects.remove(o, do_unlink=True)
os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB", export_apply=False, export_animations=True,
                          export_yup=True, export_image_format="AUTO")
ms = [o for o in bpy.data.objects if o.type == "MESH"]
tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in ms)
ossos = sum(len(a.bones) for a in bpy.data.armatures)
mn, mx = Vector((1e9,) * 3), Vector((-1e9,) * 3)
for o in ms:
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c)
        mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
d = mx - mn if ms else Vector((0, 0, 0))
print("RESUMO|%s|malhas=%d|tris=%d|ossos=%d|anims=%d|imgs=%d|tam=%.2fx%.2fx%.2f|%s" % (
    os.path.basename(dst), len(ms), tris, ossos, len(bpy.data.actions), len([i for i in bpy.data.images if i.size[0]]),
    d.x, d.y, d.z, ",".join(sorted(o.name for o in ms))[:300]))
