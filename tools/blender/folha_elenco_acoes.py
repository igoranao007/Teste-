"""Folha de aprovação: UM quadro de cada ação escolhida, câmera 3/4 que acompanha o quadril e se ajusta à altura do personagem.
Uso: ACOES="u_Walk_Loop@.3,m_turn_180@.5" blender -b X_anim_v2.blend --python folha_elenco_acoes.py -- pasta_saida prefixo
Gera pasta_saida/prefixo__NN__acao.png (Workbench com textura, filtro 'closest' como no motor)."""
import bpy, sys, os
from mathutils import Vector
a = sys.argv[sys.argv.index('--') + 1:]; OUT, PRE = a[0], a[1]; os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; sc.render.engine = 'BLENDER_WORKBENCH'; sh = sc.display.shading
sh.light = 'STUDIO'; sh.color_type = 'TEXTURE'; sh.background_type = 'VIEWPORT'; sh.background_color = (.13, .13, .14)
for m in bpy.data.materials:
    if m.use_nodes:
        for n in m.node_tree.nodes:
            if n.type == 'TEX_IMAGE': n.interpolation = 'Closest'
A = next(o for o in bpy.data.objects if o.type == 'ARMATURE' and ('spine' in o.data.bones or 'Hips' in o.data.bones))
RAIZ = 'spine' if 'spine' in A.data.bones else 'Hips'
MALHAS = [o for o in bpy.data.objects if o.type == 'MESH' and o.visible_get()]
for o in bpy.data.objects:                               # esconde a esfera de referência dos modelos antigos
    if o.type == 'MESH' and o.name.startswith('Icosphere'): o.hide_render = True
def altura():
    dg = bpy.context.evaluated_depsgraph_get(); zs = []
    for o in MALHAS:
        if o.hide_render: continue
        e = o.evaluated_get(dg); zs += [(e.matrix_world @ v.co).z for v in e.data.vertices]
    return max(zs) - min(zs) if zs else 1.8
A.animation_data_create(); A.animation_data.action = bpy.data.actions.get('idle') or bpy.data.actions[0]
try: A.animation_data.action_slot = A.animation_data.action.slots[0]
except Exception: pass
sc.frame_set(1); H = altura()
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0)); chao = bpy.context.object
mt = bpy.data.materials.new('chao'); mt.diffuse_color = (.32, .33, .31, 1); chao.data.materials.append(mt)
cam = bpy.data.objects.new('c', bpy.data.cameras.new('c')); sc.collection.objects.link(cam); sc.camera = cam
sc.render.resolution_x, sc.render.resolution_y = 360, 480; cam.data.lens = 35
for i, item in enumerate(x for x in os.environ.get('ACOES', '').split(',') if x):
    nome, fr = (item.split('@') + ['.5'])[:2]
    act = bpy.data.actions.get(nome)
    if not act: print('FALTA', nome); continue
    A.animation_data.action = act
    try: A.animation_data.action_slot = act.slots[0]
    except Exception: pass
    f0, f1 = int(act.frame_range[0]), int(act.frame_range[1]); sc.frame_set(int(f0 + (f1 - f0) * float(fr)))
    h = A.matrix_world @ A.pose.bones[RAIZ].head; alvo = Vector((h.x, h.y, H * .5))
    d = H / 1.8
    cam.location = alvo + Vector((2.0, -2.7, .35)) * d; cam.rotation_euler = (alvo - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = f'{OUT}/{PRE}__{i:02d}__{nome}.png'; bpy.ops.render.render(write_still=True)
print('FOLHA OK', PRE, round(H, 2))
