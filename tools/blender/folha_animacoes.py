"""Folha de conferência visual: 4 quadros de cada ação (u_* e m_*, ou todas com TODAS=1), câmera 3/4 que acompanha o quadril.
Uso: blender -b personagem_anim.blend --python folha_animacoes.py -- pasta_saida"""
import bpy, sys, os
from mathutils import Vector
OUT = sys.argv[sys.argv.index('--') + 1]; os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; sc.render.engine = 'BLENDER_WORKBENCH'; sh = sc.display.shading
sh.light = 'STUDIO'; sh.color_type = 'TEXTURE'; sh.background_type = 'VIEWPORT'; sh.background_color = (.13, .13, .14)
for m in bpy.data.materials:
    if m.use_nodes:
        for n in m.node_tree.nodes:
            if n.type == 'TEX_IMAGE': n.interpolation = 'Closest'
A = next(o for o in bpy.data.objects if o.type == 'ARMATURE' and 'spine' in o.data.bones)
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0)); chao = bpy.context.object
mt = bpy.data.materials.new('chao'); mt.diffuse_color = (.32, .33, .31, 1); chao.data.materials.append(mt)
cam = bpy.data.objects.new('c', bpy.data.cameras.new('c')); sc.collection.objects.link(cam); sc.camera = cam
sc.render.resolution_x, sc.render.resolution_y = 300, 420; cam.data.lens = 35
todas = os.environ.get('TODAS') == '1'
for act in sorted(bpy.data.actions, key=lambda a: a.name):
    if not todas and not act.name.startswith(('u_', 'm_')): continue
    A.animation_data.action = act
    try: A.animation_data.action_slot = act.slots[0]
    except Exception: pass
    f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
    for k, t in enumerate((0.0, 0.33, 0.66, 0.99)):
        sc.frame_set(int(f0 + (f1 - f0) * t))
        h = A.matrix_world @ A.pose.bones['spine'].head; alvo = Vector((h.x, h.y, .85))
        cam.location = alvo + Vector((2.3, -3.0, .45)); cam.rotation_euler = (alvo - cam.location).to_track_quat('-Z', 'Y').to_euler()
        sc.render.filepath = f'{OUT}/{act.name}__{k}.png'; bpy.ops.render.render(write_still=True)
print('FOLHA OK')
