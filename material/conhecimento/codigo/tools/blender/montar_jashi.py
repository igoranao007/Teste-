"""Abre o Simple PSX Character (JashiPSX), troca a textura e tira os óculos (lente + armação).
Uso: blender -b --disable-autoexec base.blend --python montar_jashi.py -- textura.png saida.blend"""
import bpy, bmesh, sys, os
TEX, OUT = sys.argv[sys.argv.index('--') + 1:]
img = bpy.data.images.load(bpy.path.abspath('//') and __import__('os').path.abspath(TEX)); img.pack()
for m in bpy.data.materials:
    if m.use_nodes:
        for n in m.node_tree.nodes:
            if n.type == 'TEX_IMAGE': n.image = img; n.interpolation = 'Closest'; m.node_tree.nodes.active = n
h = bpy.data.objects['head']; bm = bmesh.new(); bm.from_mesh(h.data); uvl = bm.loops.layers.uv.active
gi = [i for i, m in enumerate(h.data.materials) if m.name == 'glass']
fora = []
for f in bm.faces:
    u = sum(l[uvl].uv.x for l in f.loops) / len(f.loops); v = 1 - sum(l[uvl].uv.y for l in f.loops) / len(f.loops)
    if f.material_index in gi or (0.42 < u < 0.80 and v > 0.90): fora.append(f)
bmesh.ops.delete(bm, geom=fora, context='FACES')
# cabelo mais curto: vértices do volume do cabelo puxados pro crânio
import mathutils
C = mathutils.Vector((0.0, -0.01, 1.875))
mw = h.matrix_world; inv = mw.inverted()
for v in (bm.verts if os.environ.get('CABELO_CURTO', '1') == '1' else []):
    w = mw @ v.co
    if w.z > 1.90 or (w.y > 0.02 and w.z > 1.80):
        d = w - C; f = 0.84 if w.z > 1.92 else (0.90 if w.z > 1.88 else 0.95)
        v.co = inv @ (C + d * f)
VOL = float(os.environ.get('CABELO_VOLUME', '1'))
if VOL != 1:   # cabelo mais cheio (cachos): só o volume de cima/trás, rosto fica
    for v in bm.verts:
        w = mw @ v.co
        if w.z > 1.93 or (w.y > 0.0 and w.z > 1.82):
            v.co = inv @ (C + (w - C) * VOL)
ROSTO_PLANO = os.environ.get('ROSTO_PLANO')     # ex.: -0.10 — achata a frente do rosto (sem nariz) pra uma placa de rosto encostar por cima (Dom)
if ROSTO_PLANO:
    yl = float(ROSTO_PLANO); n = 0
    for v in bm.verts:
        w = mw @ v.co
        if 1.70 < w.z < 1.98 and abs(w.x) < 0.08 and w.y < yl: w.y = yl; v.co = inv @ w; n += 1
    print('ROSTO_PLANO vertices:', n)
bm.to_mesh(h.data); bm.free()
print('OCULOS removidos:', len(fora))
import os
if os.environ.get('CALCA', '0') == '1':   # bermuda larga -> calça reta (perna do mesmo volume da coxa)
    b = bpy.data.objects['body']; mw = b.matrix_world; inv = mw.inverted()
    print('SHAPEKEYS', b.data.shape_keys)
    pernas = [mw @ v.co for v in b.data.vertices if 0.15 < (mw @ v.co).z < 0.45]
    cx = sum(abs(w.x) for w in pernas) / max(1, len(pernas)); cy = sum(w.y for w in pernas) / max(1, len(pernas))
    n = 0
    for v in b.data.vertices:
        w = mw @ v.co
        if abs(w.x) > 0.32 or w.z > 0.97 or w.z < 0.12: continue
        sx = 1 if w.x > 0 else -1
        if w.z <= 0.50: f = 1.0 + 0.30 * max(0.0, min(1.0, (w.z - 0.12) / 0.12))                 # canela mais grossa
        else: f = 0.74 + 0.26 * max(0.0, min(1.0, (w.z - 0.60) / 0.35)) ** 1.5                     # bermuda mais fina
        w.x = sx * (cx + (abs(w.x) - cx) * f); w.y = cy + (w.y - cy) * f
        v.co = inv @ w; n += 1
    print('CALCA', n, 'centro perna', round(cx, 3), round(cy, 3))
if os.environ.get('AFRO'):   # black power: volume grande e fofo em volta da cabeça, sem cobrir o rosto
    import math, random
    from mathutils import Vector
    random.seed(5)
    A = bpy.data.objects['simple_character']
    hb = max(A.data.bones, key=lambda b: (A.matrix_world @ b.head_local).z if b.use_deform else -9)
    ESC = float(os.environ.get('AFRO_TAM', '1.0'))
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1, location=(0, 0, 0))
    o = bpy.context.object; o.name = 'afro'
    bm = bmesh.new(); bm.from_mesh(o.data)
    C = Vector([float(v) for v in os.environ.get('AFRO_C', '0,0.03,1.96').split(',')]); R = Vector([float(v) for v in os.environ.get('AFRO_R', '0.25,0.23,0.21').split(',')]) * ESC
    for v in bm.verts:
        n = v.co.normalized(); j = 1 + float(os.environ.get('AFRO_JIT', '0.10')) * (random.random() - 0.5)          # contorno fofo/irregular
        afina = 1 - float(os.environ.get('AFRO_AFINA', '0')) * max(0.0, -n.z)       # mais estreito embaixo (formato de cogumelo/cúpula)
        v.co = C + Vector((n.x * R.x * afina, n.y * R.y * afina, n.z * R.z)) * j
    LINHA = float(os.environ.get('AFRO_LINHA', '1.975'))
    def corta(c):
        if c.z < 1.79: return True                                                   # pescoço
        if c.y < 0.0 and c.z < LINHA + 0.01 and abs(c.x) < 0.17: return True        # janela do rosto
        if c.y < 0.03 and c.z < 1.86 and abs(c.x) < 0.13: return True                 # queixo/bochecha
        return False
    fora = [f for f in bm.faces if corta(f.calc_center_median())]
    bmesh.ops.delete(bm, geom=fora, context='FACES')
    for v in bm.verts:   # frente do cabelo curva pra dentro até a testa (sem aba e sem dentes)
        if v.co.y < 0.03:
            t = max(0.0, min(1.0, (2.08 - v.co.z) / 0.12)) * max(0.0, min(1.0, (0.20 - abs(v.co.x)) / 0.08))
            v.co = C + (v.co - C) * (1 - 0.32 * t)
        if v.co.y < 0.02 and abs(v.co.x) < 0.15 and v.co.z < LINHA: v.co.z = LINHA
    # borda da abertura encosta na cabeça (fecha o 'capacete' oco)
    H = Vector((0.0, -0.02, 1.90))
    def encostar(v, k):
        d = Vector((v.co.x - H.x, v.co.y - H.y, 0)); r = d.length
        alvo = 0.115 if v.co.y > -0.02 else 0.135
        if r > alvo: v.co = Vector((H.x + d.x * (1 - k + k * alvo / r), H.y + d.y * (1 - k + k * alvo / r), v.co.z))
    borda = {v for e in bm.edges if e.is_boundary for v in e.verts}
    viz = {w for v in borda for e in v.link_edges for w in e.verts} - borda
    for v in borda: encostar(v, 1.0)
    for v in viz: encostar(v, 0.45)
    # tufos: bolinhas irregulares de tamanhos variados por cima da base (quebra o contorno de capacete)
    TUFOS = int(os.environ.get('AFRO_TUFOS', '48'))
    base = [f for f in bm.faces]
    pts = []
    for f in random.sample(base, min(len(base), TUFOS * 3)):
        c = f.calc_center_median(); n = (c - C).normalized()
        if c.y < 0.04 and c.z < 2.02 and abs(c.x) < 0.19: continue      # não cobre a testa/rosto
        if c.z < 1.83: continue
        if any((c - q).length < 0.055 for q in pts): continue
        pts.append(c)
        if len(pts) >= TUFOS: break
    for c in pts:
        n = (c - C).normalized(); r = random.uniform(0.038, 0.062) * ESC
        g = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
        for v in g['verts']:
            v.co = v.co * (1 + 0.22 * (random.random() - 0.5)) + c - n * (r * 0.30)
    print('TUFOS', len(pts))
    # sombra pintada por vértice: claro em cima, escuro embaixo e no fundo entre os tufos
    ca = bm.loops.layers.color.new('sombra')
    for f in bm.faces:
        for l in f.loops:
            p = l.vert.co; up = max(0.0, min(1.0, (p.z - 1.80) / 0.40)); dist = (p - C).length / 0.30
            k = 0.45 + 0.55 * up; k *= 0.75 + 0.25 * min(1.0, dist)
            l[ca] = (k, k, k, 1.0)
    uvl = bm.loops.layers.uv.new('UVMap')
    for f in bm.faces:
        for l in f.loops:
            p = l.vert.co - C; l[uvl].uv = ((math.atan2(p.x, p.y) / math.pi + 1) * 2, (p.z / 0.2 + 1) * 2)
    bm.to_mesh(o.data); bm.free()
    for p in o.data.polygons: p.use_smooth = True
    mt = bpy.data.materials.new('afro'); mt.use_nodes = True; nt = mt.node_tree; b = nt.nodes['Principled BSDF']
    ti = nt.nodes.new('ShaderNodeTexImage'); ti.image = bpy.data.images.load(os.path.abspath(os.environ['AFRO'])); ti.image.pack(); ti.interpolation = 'Closest'
    vc = nt.nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'sombra'
    mx = nt.nodes.new('ShaderNodeMixRGB'); mx.blend_type = 'MULTIPLY'; mx.inputs['Fac'].default_value = 1.0
    nt.links.new(ti.outputs['Color'], mx.inputs['Color1']); nt.links.new(vc.outputs['Color'], mx.inputs['Color2'])
    nt.links.new(mx.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = 1.0; nt.nodes.active = ti
    o.data.materials.append(mt)
    vg = o.vertex_groups.new(name=hb.name); vg.add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')
    m = o.modifiers.new('Armature', 'ARMATURE'); m.object = A; o.parent = A; o.matrix_parent_inverse = A.matrix_world.inverted()
    print('AFRO tris', sum(len(p.vertices) - 2 for p in o.data.polygons), 'osso', hb.name)
if os.environ.get('ESPINHOS', '0') == '1':   # espinhos e orelhas (personagem ouriço), presos no osso da cabeça
    import math
    from mathutils import Vector, Matrix
    A = bpy.data.objects['simple_character']
    hb = max(A.data.bones, key=lambda b: (A.matrix_world @ b.head_local).z if b.use_deform else -9)
    print('OSSO CABECA', hb.name)
    azul = bpy.data.materials.new('espinho'); azul.use_nodes = True
    bs = azul.node_tree.nodes['Principled BSDF']; bs.inputs['Base Color'].default_value = (0.0, 0.03, 0.55, 1); bs.inputs['Roughness'].default_value = 0.9
    pele = bpy.data.materials.new('orelha'); pele.use_nodes = True
    bp = pele.node_tree.nodes['Principled BSDF']; bp.inputs['Base Color'].default_value = (0.75, 0.45, 0.25, 1); bp.inputs['Roughness'].default_value = 0.9
    C = Vector((0.0, 0.02, 1.90))
    def cone(base, ponta, r, mat, nome):
        bpy.ops.mesh.primitive_cone_add(vertices=5, radius1=r, radius2=0, depth=1)
        o = bpy.context.object; o.name = nome
        d = ponta - base; o.scale = (1, 1, d.length); o.location = base + d / 2
        o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        o.data.materials.append(mat)
        vg = o.vertex_groups.new(name=hb.name); vg.add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')
        m = o.modifiers.new('Armature', 'ARMATURE'); m.object = A; o.parent = A; o.matrix_parent_inverse = A.matrix_world.inverted()
        for p in o.data.polygons: p.use_smooth = False
    # 3 espinhos grandes pra trás + 2 menores
    for i, (dz, dx, L, r) in enumerate([(0.06, 0, 0.22, 0.055), (-0.01, 0, 0.24, 0.06), (-0.08, 0, 0.20, 0.05), (0.02, 0.06, 0.17, 0.045), (0.02, -0.06, 0.17, 0.045)]):
        base = C + Vector((dx, 0.02, dz)); ponta = base + Vector((dx * 1.2, L, -0.05 - dz * 0.3))
        cone(base, ponta, r, azul, 'espinho%d' % i)
    for s in (1, -1):   # orelhas
        base = C + Vector((s * 0.075, -0.0, 0.07)); cone(base, base + Vector((s * 0.04, 0.01, 0.09)), 0.035, pele, 'orelha')
bpy.ops.wm.save_as_mainfile(filepath=OUT)
