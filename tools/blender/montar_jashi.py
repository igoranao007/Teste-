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
bpy.ops.wm.save_as_mainfile(filepath=OUT)
