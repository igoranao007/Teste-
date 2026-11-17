# VEGETTI — etapa A (Blender): base, separa a cabeça, UV novo da cabeça (cilíndrico, rosto no centro), UV dos olhos, casca do cabelo.
# Salva o .blend de trabalho e um JSON com as posições do rosto no espaço UV (pra pintar a textura na etapa B).
import bpy, bmesh, sys, json, math
from mathutils import Vector, Matrix
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
for s_, o in olhos.items():                                           # globo do olho: sai da órbita e cresce um pouco
    c = (Vector(o['min']) + Vector(o['max'])) / 2; vids = {i for fi in o['faces'] for i in me.polygons[fi].vertices}
    for i in vids:
        p = W @ me.vertices[i].co; p = c + (p - c) * 1.04 + Vector((0, -.0072, 0)); me.vertices[i].co = W.inverted() @ p
    o['min'] = list(c + (Vector(o['min']) - c) * 1.04 + Vector((0, -.0072, 0))); o['max'] = list(c + (Vector(o['max']) - c) * 1.04 + Vector((0, -.0072, 0)))
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
# MÃOS NOVAS: a mão do modelo base era presa inteira a um osso só e tinha dedos finos e pontudos (virava garra).
# A malha antiga da mão sai e entra uma mão modelada aqui: palma, 4 dedos de 3 falanges com curva relaxada e polegar,
# na mesma posição (pose de bind), presa ao osso da mão e com a cor de pele do atlas.
cm = corpo.data; CW = corpo.matrix_world; CWi = CW.inverted(); gi = {g.index: g.name for g in corpo.vertex_groups}
uvd = cm.uv_layers.active.data
def anel(c, ex, ey, ez, ry, rz, n=6): return [c + ey * (math.cos(2 * math.pi * k / n) * ry) + ez * (math.sin(2 * math.pi * k / n) * rz) for k in range(n)]
def tubo(bm, pts, raios, ex_fn, n=6):
    aneis = []
    for i, (c, r) in enumerate(zip(pts, raios)):
        ex = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized(); ez = ex_fn(ex); ey = ez.cross(ex).normalized(); ez = ex.cross(ey).normalized()
        aneis.append([bm.verts.new(p) for p in anel(c, ex, ey, ez, r[0], r[1], n)])
    for a1, a2 in zip(aneis, aneis[1:]):
        for k in range(n): bm.faces.new((a1[k], a1[(k + 1) % n], a2[(k + 1) % n], a2[k]))
    ponta = bm.verts.new(pts[-1] + (pts[-1] - pts[-2]).normalized() * raios[-1][0] * .9)                  # ponta arredondada
    for k in range(n): bm.faces.new((aneis[-1][k], aneis[-1][(k + 1) % n], ponta))
    bm.faces.new(list(reversed(aneis[0])))
for s_, sx in (('L', 1), ('R', -1)):
    cm = corpo.data; uvd = cm.uv_layers.active.data; gi = {g.index: g.name for g in corpo.vertex_groups}
    idx = [v.index for v in cm.vertices if v.groups and gi[max(v.groups, key=lambda g: g.weight).group] == 'DEF-hand.' + s_]
    P = [CW @ cm.vertices[i].co for i in idx]; x0 = min(p.x * sx for p in P)
    pulso_pts = [p for p in P if p.x * sx < x0 + .012]; pulso = sum(pulso_pts, Vector()) / len(pulso_pts)
    si = set(idx); luv = [uvd[l].uv.copy() for poly in cm.polygons if all(i in si for i in poly.vertices) for l in poly.loop_indices]
    uvp = sum(luv, Vector((0, 0))) / len(luv)                                                         # cor de pele do atlas
    # apaga a mão antiga
    bm = bmesh.new(); bm.from_mesh(cm); bm.verts.ensure_lookup_table(); bmesh.ops.delete(bm, geom=[bm.verts[i] for i in idx], context='VERTS'); bm.to_mesh(cm); bm.free()
    # mão nova (espaço do mundo, pose de bind em T: dedos ao longo de ±X, palma pra baixo, polegar pra frente −Y)
    X = Vector((sx, 0, 0)); Y = Vector((0, -1, 0)); Z = Vector((0, 0, 1)); o = pulso + X * -.008
    bm = bmesh.new()
    palma = [o + X * t for t in (0, .03, .06, .088)]
    tubo(bm, palma, [(.03, .012), (.037, .014), (.04, .0135), (.039, .012)], lambda ex: Z, 8)
    for k, (dy, L) in enumerate(((.026, .066), (.009, .074), (-.009, .07), (-.026, .057))):         # indicador (lado do polegar) … mínimo
        base = o + X * .086 + Y * dy * 1 + Z * .002; ang = 0; pts = [base]; seg = [L * .42, L * .32, L * .26]; d = X.copy()
        for j, sg in enumerate(seg):
            ang += (.16, .26, .2)[j]; d = (X * math.cos(ang) - Z * math.sin(ang) + Y * dy * .6).normalized(); pts.append(pts[-1] + d * sg)
        r = (.0092 if k < 3 else .0078); tubo(bm, pts, [(r, r * .85), (r * .95, r * .8), (r * .88, r * .75), (r * .8, r * .7)], lambda ex: Z, 6)
    tb = o + X * .028 + Y * .03 - Z * .004; td = (X * .72 + Y * .48 - Z * .5).normalized(); td2 = (X * .9 + Y * .15 - Z * .4).normalized()
    tubo(bm, [tb, tb + td * .03, tb + td * .03 + td2 * .028, tb + td * .03 + td2 * .05], [(.012, .01), (.011, .009), (.0098, .0085), (.009, .008)], lambda ex: Z, 6)
    nm = bpy.data.meshes.new('mao_' + s_); bm.normal_update(); bm.to_mesh(nm); bm.free()
    nm.uv_layers.new(name=cm.uv_layers.active.name)
    for l in nm.uv_layers.active.data: l.uv = uvp
    mo = bpy.data.objects.new('mao_' + s_, nm); bpy.context.scene.collection.objects.link(mo)
    for v in nm.vertices: v.co = v.co                                                                  # já está no mundo
    mo.data.materials.append(cm.materials[0]) if cm.materials else None
    vg = mo.vertex_groups.new(name='DEF-hand.' + s_); vg.add([v.index for v in nm.vertices], 1.0, 'REPLACE')
    for g in corpo.vertex_groups:
        if g.name not in mo.vertex_groups: mo.vertex_groups.new(name=g.name)
    bpy.ops.object.select_all(action='DESELECT'); mo.select_set(True); corpo.select_set(True); bpy.context.view_layer.objects.active = corpo
    mo.matrix_world = Matrix(); bpy.ops.object.join()
    print('MAO nova', s_, 'pulso', [round(c, 3) for c in pulso])
# (os globos dos olhos são apagados no fim: os olhos ficam pintados na textura da órbita)
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
        'tris': [[list(uv[l].uv) for l in p.loop_indices] for p in me.polygons if p.index not in olho_set],
        'tris3d': [[list(W @ me.vertices[me.loops[l].vertex_index].co) for l in p.loop_indices] for p in me.polygons if p.index not in olho_set]}
json.dump(info, open(OUT + '/cabeca_uv.json', 'w'))
print('CABECA', len(me.vertices), 'verts', len(me.polygons), 'faces; olhos', {s: len(o['faces']) for s, o in olhos.items()}, 'z', round(zmin, 3), round(zmax, 3))
for k, v in pts.items(): print('  ', k, [round(a, 3) for a in v], 'uv', [round(a, 3) for a in cil(v)])
bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm, geom=[bm.faces[i] for i in olho_faces], context='FACES'); bm.to_mesh(me); bm.free()
bpy.ops.wm.save_as_mainfile(filepath=OUT + '/vegetti_trabalho.blend')
