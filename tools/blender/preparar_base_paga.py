"""Extrai do psx_humanoid_male.blend (Auto-Rig Pro) só a malha em T-pose e as juntas (posições dos ossos de deformação).
Uso: blender -b --disable-autoexec base.blend --python preparar_base_paga.py -- saida.blend juntas.json"""
import bpy, sys, json
OUT, JS = sys.argv[sys.argv.index('--') + 1:]
rig = bpy.data.objects['Male_rig']; o = bpy.data.objects['Male']
J = {}
for b in rig.data.bones:
    if b.use_deform or b.name in ('head.x', 'neck.x'):
        J[b.name] = {'head': list(rig.matrix_world @ b.head_local), 'tail': list(rig.matrix_world @ b.tail_local)}
json.dump(J, open(JS, 'w'), indent=1)
dg = bpy.context.evaluated_depsgraph_get()
me = bpy.data.meshes.new_from_object(o.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
me.transform(o.matrix_world)
for x in list(bpy.data.objects): bpy.data.objects.remove(x, do_unlink=True)
novo = bpy.data.objects.new('corpo', me)
for c in list(bpy.data.collections): bpy.data.collections.remove(c)
bpy.context.scene.collection.objects.link(novo)
bpy.ops.outliner.orphans_purge(do_recursive=True)
print('BASE OK tris', sum(len(p.vertices) - 2 for p in me.polygons), 'mats', [m.name for m in me.materials])
bpy.ops.wm.save_as_mainfile(filepath=OUT)
