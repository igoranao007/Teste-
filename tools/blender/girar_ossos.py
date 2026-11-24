"""Põe giro contínuo em ossos extras em TODAS as ações (loop sem emenda: número inteiro de voltas por clipe).
Uso: GIROS="halo:0.25,engr_a:-0.6,engr_b:0.8" PULSO="halo:0.03" blender -b arq.blend --python girar_ossos.py -- saida.blend
(voltas por segundo; o eixo é o Y local do osso; PULSO = escala que pulsa, 2 vezes por volta)"""
import bpy, sys, math, os
from mathutils import Quaternion
OUT = sys.argv[sys.argv.index('--') + 1]
A = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
fps = bpy.context.scene.render.fps / bpy.context.scene.render.fps_base
GIROS = {k: float(v) for k, v in (x.split(':') for x in os.environ.get('GIROS', 'halo:0.25').split(','))}
PULSO = {k: float(v) for k, v in (x.split(':') for x in os.environ.get('PULSO', '').split(',') if x)}
A.animation_data_create()
for act in bpy.data.actions:
    A.animation_data.action = act
    try: A.animation_data.action_slot = act.slots[0]
    except Exception: pass
    f0, f1 = act.frame_range; dur = (f1 - f0) / fps
    for nome, vps in GIROS.items():
        pb = A.pose.bones.get(nome)
        if not pb: continue
        pb.rotation_mode = 'QUATERNION'
        n = max(1, round(abs(vps) * dur)) * (1 if vps > 0 else -1)          # voltas inteiras no clipe
        passos = 8 * abs(n)
        for k in range(passos + 1):
            f = f0 + (f1 - f0) * k / passos; ang = 2 * math.pi * n * k / passos
            pb.rotation_quaternion = Quaternion((0, 1, 0), ang); pb.keyframe_insert('rotation_quaternion', frame=f)
            if nome in PULSO:
                e = 1 + PULSO[nome] * math.sin(4 * math.pi * k / 8); pb.scale = (e, e, e); pb.keyframe_insert('scale', frame=f)
    # interpolação linear (giro constante)
    try: curvas = act.fcurves
    except Exception: curvas = [c for l in act.layers for s in l.strips for b in s.channelbags for c in b.fcurves]
    for c in curvas:
        if any(f'"{n}"' in c.data_path for n in GIROS):
            for kp in c.keyframe_points: kp.interpolation = 'LINEAR'
    print('GIRO', act.name, round(dur, 2), 's')
A.animation_data.action = bpy.data.actions.get('idle')
bpy.ops.wm.save_as_mainfile(filepath=OUT); print('GIROS OK')
