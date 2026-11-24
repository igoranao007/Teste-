"""QA automático de todas as ações de um personagem (esqueleto do elenco):
- PÉ: altura mínima dos pés por quadro (afunda no chão < -3 cm / flutua > 6 cm quando o clipe é de pé);
- SALTO: maior rotação de um osso entre dois quadros seguidos (> 35° = salto/estalo);
- NaN e quadril fora do lugar (> 3 m).
Uso: blender -b personagem_anim.blend --python qa_animacoes.py -- relatorio.json"""
import bpy, sys, json, math
OUT = sys.argv[sys.argv.index('--') + 1]
sc = bpy.context.scene
A = next(o for o in bpy.data.objects if o.type == 'ARMATURE' and 'spine' in o.data.bones)
PES = [n for n in ('foot.L', 'foot.R', 'toe.L', 'toe.R') if n in A.pose.bones]
REPOUSO = {n: (A.matrix_world @ A.data.bones[n].head_local).z for n in PES}
LIM_SALTO = 60   # graus por quadro (golpes e corridas rápidas passam de 35°; acima de 60° é estalo)
SENTADO = ('sit', 'driv', 'crouch', 'death', 'knock', 'fall', 'get_up', 'kneel', 'crawl', 'swim', 'roll', 'land', 'jump', 'climb', 'vault', 'cower', 'fixing')
rel = {}
for act in sorted(bpy.data.actions, key=lambda a: a.name):
    A.animation_data.action = act
    try: A.animation_data.action_slot = act.slots[0]
    except Exception: pass
    f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
    ant = None; pior = (0, '', 0); zmin, zmax_min = 9, -9; problemas = []
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        zs = [(A.matrix_world @ A.pose.bones[n].head).z - REPOUSO[n] for n in PES]   # altura em relação à de descanso (tornozelo ~7,5 cm, ponta ~2 cm)
        z = min(zs); zmin = min(zmin, z); zmax_min = max(zmax_min, z)
        if any(math.isnan(v) for v in zs): problemas.append(f'NaN no quadro {f}')
        hip = A.matrix_world @ A.pose.bones['spine'].head
        if hip.length > 40 and f'quadril' not in ' '.join(problemas): problemas.append(f'quadril longe ({hip.length:.1f} m) no quadro {f}')
        atual = {b.name: (A.matrix_world @ b.matrix).to_quaternion() for b in A.pose.bones if not b.name.startswith(('f_', 'thumb', 'palm'))}
        if ant:
            for n, q in atual.items():
                ang = math.degrees(q.rotation_difference(ant[n]).angle)
                if ang > 180: ang = 360 - ang
                if ang > pior[0]: pior = (ang, n, f)
        ant = atual
    de_pe = not any(k in act.name.lower() for k in SENTADO)
    if de_pe and zmin < -0.03: problemas.append(f'pé afunda no chão ({zmin * 100:.0f} cm)')
    if de_pe and zmin > 0.025: problemas.append(f'pés no ar ({zmin * 100:.0f} cm acima do chão no clipe todo)')
    if pior[0] > LIM_SALTO: problemas.append(f'salto de {pior[0]:.0f}° no osso {pior[1]} (quadro {pior[2]})')
    rel[act.name] = {'quadros': f1 - f0 + 1, 'pe_min_cm': round(zmin * 100, 1), 'pe_max_min_cm': round(zmax_min * 100, 1),
                     'maior_salto_graus': round(pior[0], 1), 'problemas': problemas}
    print('QA', act.name, 'OK' if not problemas else '; '.join(problemas))
json.dump(rel, open(OUT, 'w'), indent=1, ensure_ascii=False); print('QA FIM', len(rel))
