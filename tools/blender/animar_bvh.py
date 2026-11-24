"""Passa animações BVH de esqueleto humanoide padrão (Motifect: Hips, Spine1, Spine2, Chest, Neck1, Head, LeftArm, LeftHandIndex1…)
pro esqueleto do elenco (Simple PSX Character / JashiPSX: spine..spine.005, upper_arm.L, f_index.01.L…), mantendo as ações
que o personagem já tem. Retarget em espaço de mundo (igual ao animar_jashi.py): cada osso de destino recebe a rotação que o
osso de origem fez em relação à pose de descanso; o quadril recebe o deslocamento escalado pela altura do quadril.
Uso: CLIPES="jab_right,front_kick" PREFIXO="luta_" blender -b personagem_anim.blend --python animar_bvh.py -- pasta_bvh saida.blend
(CLIPES vazio = todos os .bvh da pasta; o nome da ação é PREFIXO + nome do arquivo)"""
import bpy, sys, os, math
from mathutils import Matrix, Quaternion, Vector
a = sys.argv[sys.argv.index('--') + 1:]; PASTA, OUT = a[0], a[1]
CLIPES = [c for c in os.environ.get('CLIPES', '').split(',') if c]; PREF = os.environ.get('PREFIXO', '')
sc = bpy.context.scene
T = next(o for o in bpy.data.objects if o.type == 'ARMATURE' and 'spine' in o.data.bones)
MAP = [('spine', 'Hips'), ('spine.001', 'Spine1'), ('spine.002', 'Spine2'), ('spine.003', 'Chest'), ('spine.004', 'Neck1'), ('spine.005', 'Head'),
       ('pelvis.L', 'Hips'), ('pelvis.R', 'Hips')]
for s, S in (('L', 'Left'), ('R', 'Right')):
    MAP += [(f'shoulder.{s}', f'{S}Shoulder'), (f'upper_arm.{s}', f'{S}Arm'), (f'forearm.{s}', f'{S}ForeArm'), (f'hand.{s}', f'{S}Hand'),
            (f'thigh.{s}', f'{S}Leg'), (f'shin.{s}', f'{S}Shin'), (f'foot.{s}', f'{S}Foot'), (f'toe.{s}', f'{S}ToeBase'),
            (f'thumb.01.{s}', f'{S}HandThumb1'), (f'thumb.02.{s}', f'{S}HandThumb2'), (f'thumb.03.{s}', f'{S}HandThumb3')]
    for d, D in (('index', 'Index'), ('middle', 'Middle'), ('ring', 'Ring'), ('pinky', 'Pinky')):
        MAP += [(f'palm.0{["index","middle","ring","pinky"].index(d) + 1}.{s}', f'{S}Hand{D}1'),
                (f'f_{d}.01.{s}', f'{S}Hand{D}2'), (f'f_{d}.02.{s}', f'{S}Hand{D}3'), (f'f_{d}.03.{s}', f'{S}Hand{D}4')]
MAP = [(t, f) for t, f in MAP if t in T.pose.bones]
def q_rest(arm, b): return arm.matrix_world.to_quaternion() @ b.matrix_local.to_quaternion()
def q_pose(arm, pb): return arm.matrix_world.to_quaternion() @ pb.matrix.to_quaternion()
trest = {t: q_rest(T, T.data.bones[t]) for t, _ in MAP}
Aq = T.matrix_world.to_quaternion(); Ainv = T.matrix_world.inverted()
ht = (T.matrix_world @ T.data.bones['spine'].head_local).z
for pb in T.pose.bones: pb.rotation_mode = 'QUATERNION'
T.animation_data_create()
arqs = sorted(f for f in os.listdir(PASTA) if f.endswith('.bvh') and (not CLIPES or f[:-4] in CLIPES))
sc.render.fps = 30
for arq in arqs:
    nome = PREF + arq[:-4]
    antes = set(bpy.data.objects)
    bpy.ops.import_anim.bvh(filepath=os.path.join(PASTA, arq), global_scale=0.01, rotate_mode='NATIVE', axis_forward='-Z', axis_up='Y', update_scene_fps=False, update_scene_duration=False)
    S = [o for o in bpy.data.objects if o not in antes][0]
    fa = S.animation_data.action; fa.name = '_bvh_origem'; f0, f1 = int(fa.frame_range[0]), int(fa.frame_range[1])   # (o nome do BVH colidia com o da ação nova)
    srest = {b.name: q_rest(S, b) for b in S.data.bones}
    hip_rest_s = S.matrix_world @ S.data.bones['Hips'].head_local
    # o quadril do BVH fica na origem no descanso: a altura de referência é a do 1º quadro (de pé, guarda de luta)
    sc.frame_set(f0); hip0 = S.matrix_world @ S.pose.bones['Hips'].head
    esc = ht / max(1e-4, hip0.z)
    if nome in bpy.data.actions: bpy.data.actions.remove(bpy.data.actions[nome])
    nova = bpy.data.actions.new(nome); nova.use_fake_user = True
    T.animation_data.action = nova
    for pb in T.pose.bones: pb.matrix_basis = Matrix.Identity(4)
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        D = {b.name: q_pose(S, S.pose.bones[b.name]) @ srest[b.name].inverted() for b in S.data.bones}
        for tn, fn in MAP:
            R = D[fn] @ trest[tn]
            pb = T.pose.bones[tn]
            bpy.context.view_layer.update()
            if tn == 'spine':
                desl = (S.matrix_world @ S.pose.bones['Hips'].head) - hip0
                head = Ainv @ ((T.matrix_world @ T.data.bones['spine'].head_local) + desl * esc)
            else: head = pb.head.copy()
            pb.matrix = Matrix.Translation(head) @ (Aq.inverted() @ R).to_matrix().to_4x4()
            pb.keyframe_insert('rotation_quaternion', frame=f - f0 + 1)
            if tn == 'spine': pb.keyframe_insert('location', frame=f - f0 + 1)
    fa_nome = fa.name; bpy.data.objects.remove(S, do_unlink=True)
    if fa_nome in bpy.data.actions: bpy.data.actions.remove(bpy.data.actions[fa_nome])
    print('CLIPE', nome, f1 - f0 + 1, 'quadros', 'esc', round(esc, 3))
T.animation_data.action = bpy.data.actions.get('idle')
try: T.animation_data.action_slot = T.animation_data.action.slots[0]
except Exception: pass
bpy.ops.wm.save_as_mainfile(filepath=OUT); print('BVH OK', len(arqs), [x.name for x in bpy.data.actions])
