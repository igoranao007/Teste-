# VEGETTI — etapa A (Blender): base, separa a cabeça, UV novo da cabeça (cilíndrico, rosto no centro), UV dos olhos, casca do cabelo.
# Salva o .blend de trabalho e um JSON com as posições do rosto no espaço UV (pra pintar a textura na etapa B).
import bpy, bmesh, sys, json, math
from mathutils import Vector
OUT = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='material/modelos/itch/gente/csaf/sy_boss.glb')
for o in list(bpy.data.objects):
    if o.name.startswith('Icosphere'): bpy.data.objects.remove(o, do_unlink=True)
arm = bpy.data.objects['sy_boss_rig']; corpo = bpy.data.objects['sy_boss']; corpo.name = 'vegetti_corpo'; arm.name = 'vegetti_rig'
hg = corpo.vertex_groups['DEF-head'].index
def peso(v, gi): return sum(g.weight for g in v.groups if g.group == gi)
# ── separa a cabeça (faces com todos os vértices presos ao osso da cabeça) ──
bpy.context.view_layer.objects.active = corpo; corpo.select_set(True)
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='DESELECT'); bpy.ops.object.mode_set(mode='OBJECT')
for p in corpo.data.polygons: p.select = all(peso(corpo.data.vertices[i], hg) > .5 for i in p.vertices)
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.separate(type='SELECTED'); bpy.ops.object.mode_set(mode='OBJECT')
cab = [o for o in bpy.data.objects if o.type == 'MESH' and o != corpo][0]; cab.name = 'vegetti_cabeca'
me = cab.data; uv = me.uv_layers.active.data; W = cab.matrix_world
# ── olhos: faces que liam os losangos do atlas (u<.16, v .55–.64 no Blender) ──
olho_faces = [p.index for p in me.polygons if all(uv[l].uv.x < .16 and .54 < uv[l].uv.y < .64 for l in p.loop_indices)]
cents = {}
for fi in olho_faces:
    c = W @ me.polygons[fi].center; s = 'E' if c.x > 0 else 'D'; cents.setdefault(s, []).append((fi, c))
olhos = {}
for s, L in cents.items():
    pts = [W @ me.vertices[i].co for fi, _ in L for i in me.polygons[fi].vertices]
    mn = Vector([min(p[k] for p in pts) for k in range(3)]); mx = Vector([max(p[k] for p in pts) for k in range(3)]); olhos[s] = {'min': list(mn), 'max': list(mx), 'faces': [fi for fi, _ in L]}
# ── UV novo: cabeça cilíndrica (frente = −Y no centro da textura), olhos planos num canto ──
vs = [W @ v.co for v in me.vertices]; zmin = min(v.z for v in vs); zmax = max(v.z for v in vs); ymin = min(v.y for v in vs); ymax = max(v.y for v in vs)
CY = (ymin + ymax) / 2 + .01
def cil(p): th = math.atan2(p.x, -(p.y - CY)); return [.5 + th / (2 * math.pi), (p.z - zmin) / (zmax - zmin)]
olho_set = set(olho_faces)
for p in me.polygons:
    if p.index in olho_set:
        s = 'E' if (W @ p.center).x > 0 else 'D'; o = olhos[s]; x0 = 0 if s == 'E' else .5
        for l in p.loop_indices:
            q = W @ me.vertices[me.loops[l].vertex_index].co
            uv[l].uv = (x0 + .5 * (q.x - o['min'][0]) / (o['max'][0] - o['min'][0] + 1e-6), (q.z - o['min'][2]) / (o['max'][2] - o['min'][2] + 1e-6))
    else:
        us = [cil(W @ me.vertices[me.loops[l].vertex_index].co) for l in p.loop_indices]
        if max(u[0] for u in us) - min(u[0] for u in us) > .5:                      # face na costura de trás
            for u in us:
                if u[0] < .5: u[0] += 1
        for l, u in zip(p.loop_indices, us): uv[l].uv = u
# materiais: 0 = pele/cabelo da cabeça, 1 = olhos
me.materials.clear(); me.materials.append(bpy.data.materials.new('vegetti_cabeca')); me.materials.append(bpy.data.materials.new('vegetti_olhos'))
for p in me.polygons: p.material_index = 1 if p.index in olho_set else 0
# ── pontos do rosto (no espaço do mundo e no UV da cabeça) ──
frente = [v for v in vs if v.y < CY - .06]
nariz = min(vs, key=lambda v: v.y)
queixo = min([v for v in vs if abs(v.x) < .02 and v.y < CY - .05], key=lambda v: v.z)
ec = {s: (Vector(o['min']) + Vector(o['max'])) / 2 for s, o in olhos.items()}
boca = Vector((0, nariz.y + .012, nariz.z - .62 * (nariz.z - queixo.z)))
orelha = max(vs, key=lambda v: abs(v.x) if abs(v.z - (nariz.z + .005)) < .03 else 0)
pts = {'olhoE': ec['E'], 'olhoD': ec['D'], 'nariz': nariz, 'boca': boca, 'queixo': queixo, 'orelhaE': Vector((abs(orelha.x), orelha.y, orelha.z)), 'orelhaD': Vector((-abs(orelha.x), orelha.y, orelha.z))}
info = {'zmin': zmin, 'zmax': zmax, 'CY': CY, 'pts': {k: {'mundo': list(v), 'uv': cil(v)} for k, v in pts.items()}, 'olhos': {s: {k: o[k] for k in ('min', 'max')} for s, o in olhos.items()},
        'tris': [[list(uv[l].uv) for l in p.loop_indices] for p in me.polygons if p.index not in olho_set]}
json.dump(info, open(OUT + '/cabeca_uv.json', 'w'))
print('CABECA', len(me.vertices), 'verts', len(me.polygons), 'faces; olhos', {s: len(o['faces']) for s, o in olhos.items()}, 'z', round(zmin, 3), round(zmax, 3))
for k, v in pts.items(): print('  ', k, [round(a, 3) for a in v], 'uv', [round(a, 3) for a in cil(v)])
bpy.ops.wm.save_as_mainfile(filepath=OUT + '/vegetti_trabalho.blend')
