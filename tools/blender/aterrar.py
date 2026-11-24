"""Encosta no chão as ações retargetadas (prefixos u_ e m_): mede, no clipe todo, a menor altura dos pés em relação à pose de
descanso e desce/sobe o quadril (location do osso 'spine') por essa diferença — mantém pulos e quedas, só tira o "flutuando"/"afundando".
Uso: blender -b personagem_anim_v2.blend --python aterrar.py -- saida.blend"""
import bpy, sys
from mathutils import Vector
OUT = sys.argv[sys.argv.index('--') + 1]
sc = bpy.context.scene
A = next(o for o in bpy.data.objects if o.type == 'ARMATURE' and ('spine' in o.data.bones or 'Hips' in o.data.bones))
# Esqueleto com nomes estilo Mixamo (Metalis: Hips, Spine, Head, LeftArm, LeftUpLeg…): traduz os nomes do elenco pros dele
_MIX = {'spine': 'Hips', 'spine.002': 'Spine', 'spine.005': 'Head'}
for _s, _S in (('L', 'Left'), ('R', 'Right')):
    _MIX.update({f'upper_arm.{_s}': f'{_S}Arm', f'forearm.{_s}': f'{_S}ForeArm', f'hand.{_s}': f'{_S}Hand',
                 f'thigh.{_s}': f'{_S}UpLeg', f'shin.{_s}': f'{_S}Leg', f'foot.{_s}': f'{_S}Foot'})
NB = (lambda n: n) if 'spine' in A.data.bones else (lambda n: _MIX.get(n, '-'))
RAIZ = NB('spine')
PES = [NB(n) for n in ('foot.L', 'foot.R', 'toe.L', 'toe.R') if NB(n) in A.pose.bones]
REP = {n: (A.matrix_world @ A.data.bones[n].head_local).z for n in PES}
B = A.data.bones[RAIZ]; R = (A.matrix_world.to_3x3() @ B.matrix_local.to_3x3()).inverted()   # sem normalizar: o objeto do esqueleto tem escala
def curvas(act):
    try: return list(act.fcurves)
    except Exception: return [c for l in act.layers for st in l.strips for cb in st.channelbags for c in cb.fcurves]
for act in bpy.data.actions:
    if not act.name.startswith(('u_', 'm_')): continue
    A.animation_data.action = act
    try: A.animation_data.action_slot = act.slots[0]
    except Exception: pass
    f0, f1 = int(act.frame_range[0]), int(act.frame_range[1]); zmin = 9
    for f in range(f0, f1 + 1):
        sc.frame_set(f); zmin = min(zmin, min((A.matrix_world @ A.pose.bones[n].head).z - REP[n] for n in PES))
    if abs(zmin) < 0.005: print('ATERRAR', act.name, 'ok'); continue
    d = R @ Vector((0, 0, -zmin))
    for c in curvas(act):
        if c.data_path == f'pose.bones["{RAIZ}"].location':
            for k in c.keyframe_points: k.co.y += d[c.array_index]; k.handle_left.y += d[c.array_index]; k.handle_right.y += d[c.array_index]
    print('ATERRAR', act.name, f'{-zmin * 100:+.1f} cm')
A.animation_data.action = bpy.data.actions.get('idle')
bpy.ops.wm.save_as_mainfile(filepath=OUT); print('ATERRAR OK')
