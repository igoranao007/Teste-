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
