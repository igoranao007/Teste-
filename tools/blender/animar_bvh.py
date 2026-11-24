"""Passa animações BVH de esqueleto humanoide padrão (Motifect: Hips, Spine1, Spine2, Chest, Neck1, Head, LeftArm, LeftHandIndex1…)
pro esqueleto do elenco (Simple PSX Character / JashiPSX: spine..spine.005, upper_arm.L, f_index.01.L…), mantendo as ações
que o personagem já tem. Retarget em espaço de mundo (igual ao animar_jashi.py): cada osso de destino recebe a rotação que o
osso de origem fez em relação à pose de descanso; o quadril recebe o deslocamento escalado pela altura do quadril.
Uso: CLIPES="jab_right,front_kick" PREFIXO="luta_" blender -b personagem_anim.blend --python animar_bvh.py -- pasta_bvh saida.blend
     ou com a biblioteca Quaternius (UAL, GLB com várias ações):  ... animar_bvh.py -- UAL1_Standard.glb saida.blend  (SEM_DESLOC=1 trava o quadril no lugar)
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
MAP_UAL = [('spine', 'pelvis'), ('spine.001', 'spine_01'), ('spine.002', 'spine_02'), ('spine.003', 'spine_03'), ('spine.004', 'neck_01'), ('spine.005', 'Head'),
           ('pelvis.L', 'pelvis'), ('pelvis.R', 'pelvis')]
for s, u in (('L', 'l'), ('R', 'r')):
    MAP_UAL += [(f'shoulder.{s}', f'clavicle_{u}'), (f'upper_arm.{s}', f'upperarm_{u}'), (f'forearm.{s}', f'lowerarm_{u}'), (f'hand.{s}', f'hand_{u}'),
                (f'thigh.{s}', f'thigh_{u}'), (f'shin.{s}', f'calf_{u}'), (f'foot.{s}', f'foot_{u}'), (f'toe.{s}', f'ball_{u}'),
                (f'thumb.01.{s}', f'thumb_01_{u}'), (f'thumb.02.{s}', f'thumb_02_{u}'), (f'thumb.03.{s}', f'thumb_03_{u}')]
    for d in ('index', 'middle', 'ring', 'pinky'):
        MAP_UAL += [(f'f_{d}.01.{s}', f'{d}_01_{u}'), (f'f_{d}.02.{s}', f'{d}_02_{u}'), (f'f_{d}.03.{s}', f'{d}_03_{u}')]
MAP_UAL = [(t, f) for t, f in MAP_UAL if t in T.pose.bones]
MAP = [(t, f) for t, f in MAP if t in T.pose.bones]
def q_rest(arm, b): return arm.matrix_world.to_quaternion() @ b.matrix_local.to_quaternion()
def q_pose(arm, pb): return arm.matrix_world.to_quaternion() @ pb.matrix.to_quaternion()
Aq = T.matrix_world.to_quaternion(); Ainv = T.matrix_world.inverted()
ht = (T.matrix_world @ T.data.bones['spine'].head_local).z
for pb in T.pose.bones: pb.rotation_mode = 'QUATERNION'
T.animation_data_create()
def retarget(nome, S, fa, mapa, quadril):
    try: S.animation_data.action_slot = fa.slots[0]
    except Exception: pass
    f0, f1 = int(fa.frame_range[0]), int(fa.frame_range[1])
    srest = {b.name: q_rest(S, b) for b in S.data.bones}
    sc.frame_set(f0); hip0 = S.matrix_world @ S.pose.bones[quadril].head
    # escala pelo comprimento da PERNA em repouso (não pelo 1º quadro: clipes que começam sentados/agachados ficavam flutuando)
    perna = lambda arm, a_, b_: ((arm.matrix_world @ arm.data.bones[a_].head_local) - (arm.matrix_world @ arm.data.bones[b_].head_local)).length
    coxa_s, pe_s = ('LeftLeg', 'LeftFoot') if quadril == 'Hips' else ('thigh_l', 'foot_l')
    esc = perna(T, 'thigh.L', 'foot.L') / max(1e-4, perna(S, coxa_s, pe_s))
    if nome in bpy.data.actions: bpy.data.actions.remove(bpy.data.actions[nome])
    nova = bpy.data.actions.new(nome); nova.use_fake_user = True
    T.animation_data.action = nova
    for pb in T.pose.bones: pb.matrix_basis = Matrix.Identity(4)
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        D = {b.name: q_pose(S, S.pose.bones[b.name]) @ srest[b.name].inverted() for b in S.data.bones}
        for tn, fn in mapa:
            R = D[fn] @ trest_de[tn]
            pb = T.pose.bones[tn]
            bpy.context.view_layer.update()
            if tn == 'spine':
                hp = S.matrix_world @ S.pose.bones[quadril].head                 # altura do quadril ABSOLUTA (chão = 0), deslocamento no chão relativo ao 1º quadro
                dx, dy = (hp.x - hip0.x) * esc, (hp.y - hip0.y) * esc
                if os.environ.get('SEM_DESLOC') == '1': dx = dy = 0.0
                base = T.matrix_world @ T.data.bones['spine'].head_local
                head = Ainv @ Vector((base.x + dx, base.y + dy, hp.z * esc))
            else: head = pb.head.copy()
            pb.matrix = Matrix.Translation(head) @ (Aq.inverted() @ R).to_matrix().to_4x4()
            pb.keyframe_insert('rotation_quaternion', frame=f - f0 + 1)
            if tn == 'spine': pb.keyframe_insert('location', frame=f - f0 + 1)
    print('CLIPE', nome, f1 - f0 + 1, 'quadros', 'esc', round(esc, 3))
trest_de = {t: q_rest(T, T.data.bones[t]) for t in T.data.bones.keys()}
if PASTA.lower().endswith('.glb'):                                   # biblioteca num GLB só (Quaternius UAL): um esqueleto, várias ações
    antes = set(bpy.data.objects); acoes_antes = set(bpy.data.actions)
    bpy.ops.import_scene.gltf(filepath=PASTA)
    novos = [o for o in bpy.data.objects if o not in antes]; S = next(o for o in novos if o.type == 'ARMATURE')
    for o in novos:
        if o.type == 'MESH': bpy.data.objects.remove(o, do_unlink=True)
    fontes = [x for x in bpy.data.actions if x not in acoes_antes and (not CLIPES or x.name in CLIPES)]
    for fa in fontes: fa.name = '_src_' + fa.name
    for fa in fontes:
        S.animation_data.action = fa; retarget(PREF + fa.name[5:], S, fa, MAP_UAL, 'pelvis')
    bpy.data.objects.remove(S, do_unlink=True)
    for x in [x for x in bpy.data.actions if x in acoes_antes or x.name.startswith('_src_')]: pass
    for x in [x for x in list(bpy.data.actions) if x not in acoes_antes and not x.use_fake_user]: bpy.data.actions.remove(x)   # ações da biblioteca não escolhidas
    arqs = fontes
else:
    arqs = sorted(f for f in os.listdir(PASTA) if f.endswith('.bvh') and (not CLIPES or f[:-4] in CLIPES))
    for arq in arqs:
        antes = set(bpy.data.objects)
        bpy.ops.import_anim.bvh(filepath=os.path.join(PASTA, arq), global_scale=0.01, rotate_mode='NATIVE', axis_forward='-Z', axis_up='Y', update_scene_fps=False, update_scene_duration=False)
        S = [o for o in bpy.data.objects if o not in antes][0]
        fa = S.animation_data.action; fa.name = '_bvh_origem'
        retarget(PREF + arq[:-4], S, fa, MAP, 'Hips')
        fa_nome = fa.name; bpy.data.objects.remove(S, do_unlink=True)
        if fa_nome in bpy.data.actions: bpy.data.actions.remove(bpy.data.actions[fa_nome])
T.animation_data.action = bpy.data.actions.get('idle')
try: T.animation_data.action_slot = T.animation_data.action.slots[0]
except Exception: pass
bpy.ops.wm.save_as_mainfile(filepath=OUT); print('BVH OK', len(arqs), [x.name for x in bpy.data.actions])
