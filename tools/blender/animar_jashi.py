"""Passa as 10 animações do PSX Character Creator (Hips/Spine/Head/LeftArm...) pro esqueleto do Simple PSX Character
(JashiPSX: spine..spine.005, upper_arm.L, thigh.L...). Retarget em espaço de mundo: cada osso de destino recebe a
rotação que o osso de origem fez em relação à pose de descanso; o quadril recebe também o deslocamento (escalado).
Uso: blender -b personagem.blend --python animar_jashi.py -- saida.blend"""
import bpy, sys
from mathutils import Matrix, Quaternion, Vector
OUT = sys.argv[sys.argv.index('--') + 1]
sc = bpy.context.scene
T = bpy.data.objects['simple_character']
antes = set(bpy.data.objects); acoes_antes = set(bpy.data.actions)
bpy.ops.import_scene.gltf(filepath='material/modelos/itch/psx-creator/man_2.glb')
novos = [o for o in bpy.data.objects if o not in antes]
S = [o for o in novos if o.type == 'ARMATURE'][0]
for o in novos:
    if o.type == 'MESH': bpy.data.objects.remove(o, do_unlink=True)
fontes = [a for a in bpy.data.actions if a not in acoes_antes]
print('ACOES fonte', [a.name for a in fontes])
def q_rest(arm, b): return arm.matrix_world.to_quaternion() @ b.matrix_local.to_quaternion()
def q_pose(arm, pb): return arm.matrix_world.to_quaternion() @ pb.matrix.to_quaternion()
MAP = [('spine', ('Hips', None, 0)), ('spine.001', ('Hips', 'Spine', 0.35)), ('spine.002', ('Hips', 'Spine', 0.7)), ('spine.003', ('Spine', None, 0)),
       ('spine.004', ('Spine', 'Head', 0.5)), ('spine.005', ('Head', None, 0)),
       ('shoulder.L', ('Spine', None, 0)), ('upper_arm.L', ('LeftArm', None, 0)), ('forearm.L', ('LeftForeArm', None, 0)), ('hand.L', ('LeftHand', None, 0)),
       ('shoulder.R', ('Spine', None, 0)), ('upper_arm.R', ('RightArm', None, 0)), ('forearm.R', ('RightForeArm', None, 0)), ('hand.R', ('RightHand', None, 0)),
       ('pelvis.L', ('Hips', None, 0)), ('pelvis.R', ('Hips', None, 0)),
       ('thigh.L', ('LeftUpLeg', None, 0)), ('shin.L', ('LeftLeg', None, 0)), ('foot.L', ('LeftFoot', None, 0)),
       ('thigh.R', ('RightUpLeg', None, 0)), ('shin.R', ('RightLeg', None, 0)), ('foot.R', ('RightFoot', None, 0))]
MAP = [(t, f) for t, f in MAP if t in T.pose.bones]
srest = {b.name: q_rest(S, b) for b in S.data.bones}
trest = {t: q_rest(T, T.data.bones[t]) for t, _ in MAP}
hs = (S.matrix_world @ S.data.bones['Hips'].head_local).z; ht = (T.matrix_world @ T.data.bones['spine'].head_local).z
esc = ht / hs; Aq = T.matrix_world.to_quaternion(); Ainv = T.matrix_world.inverted()
hip_rest_s = S.matrix_world @ S.data.bones['Hips'].head_local
print('escala quadril', round(esc, 3))
for pb in T.pose.bones: pb.rotation_mode = 'QUATERNION'
T.animation_data_create()
for fa in fontes:
    S.animation_data.action = fa
    try:
        S.animation_data.action_slot = fa.slots[0]
    except Exception: pass
    f0, f1 = int(fa.frame_range[0]), int(fa.frame_range[1])
    nova = bpy.data.actions.new(fa.name); nova.use_fake_user = True
    T.animation_data.action = nova
    for pb in T.pose.bones: pb.matrix_basis = Matrix.Identity(4)
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        D = {b.name: q_pose(S, S.pose.bones[b.name]) @ srest[b.name].inverted() for b in S.data.bones}
        for tn, (a, b, k) in MAP:
            d = D[a] if not b else D[a].slerp(D[b], k)
            R = d @ trest[tn]
            pb = T.pose.bones[tn]
            bpy.context.view_layer.update()
            head = pb.head.copy() if tn != 'spine' else None
            if tn == 'spine':   # quadril: deslocamento da origem escalado
                desl = (S.matrix_world @ S.pose.bones['Hips'].head) - hip_rest_s
                headw = (T.matrix_world @ T.data.bones['spine'].head_local) + desl * esc
                head = Ainv @ headw
            M = Matrix.Translation(head) @ (Aq.inverted() @ R).to_matrix().to_4x4()
            pb.matrix = M
            pb.keyframe_insert('rotation_quaternion', frame=f)
            if tn == 'spine': pb.keyframe_insert('location', frame=f)
    print('ACAO', fa.name, f0, f1)
# limpa a origem
bpy.data.objects.remove(S, do_unlink=True)
for a in fontes: bpy.data.actions.remove(a)
for a in bpy.data.actions:
    if a.name.endswith('.001'): a.name = a.name[:-4]
T.animation_data.action = bpy.data.actions.get('idle')
try: T.animation_data.action_slot = T.animation_data.action.slots[0]
except Exception: pass
bpy.ops.wm.save_as_mainfile(filepath=OUT); print('ANIMADO OK', [a.name for a in bpy.data.actions])
