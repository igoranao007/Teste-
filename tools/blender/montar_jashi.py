"""Abre o Simple PSX Character (JashiPSX), troca a textura e tira os óculos (lente + armação).
Uso: blender -b --disable-autoexec base.blend --python montar_jashi.py -- textura.png saida.blend"""
import bpy, bmesh, sys
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
for v in bm.verts:
    w = mw @ v.co
    if w.z > 1.90 or (w.y > 0.02 and w.z > 1.80):
        d = w - C; f = 0.84 if w.z > 1.92 else (0.90 if w.z > 1.88 else 0.95)
        v.co = inv @ (C + d * f)
bm.to_mesh(h.data); bm.free()
print('OCULOS removidos:', len(fora))
bpy.ops.wm.save_as_mainfile(filepath=OUT)
