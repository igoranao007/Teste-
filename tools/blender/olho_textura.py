"""Troca os olhos (faces olho/iris/preto acima de z 0,80) por uma textura plana projetada de frente, cada olho no seu retângulo.
Uso: blender -b metalis.blend --python olho_textura.py -- olho.png saida.blend"""
import bpy, bmesh, sys
TEX, OUT = sys.argv[sys.argv.index('--') + 1:]
o = bpy.data.objects['corpo']; me = o.data
nomes = [m.name for m in me.materials]
m = bpy.data.materials.new('olho_cansado'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
ti = nt.nodes.new('ShaderNodeTexImage'); ti.image = bpy.data.images.load(bpy.path.abspath(TEX)); ti.image.pack(); ti.interpolation = 'Linear'
nt.links.new(ti.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = 0.9; nt.nodes.active = ti
me.materials.append(m); mi = len(me.materials) - 1
bm = bmesh.new(); bm.from_mesh(me)
uvl = bm.loops.layers.uv.active or bm.loops.layers.uv.new('UVMap')
olhos = [f for f in bm.faces if nomes[f.material_index] in ('olho', 'iris', 'preto') and f.calc_center_median().z > 0.80 and abs(f.calc_center_median().x) > 0.022]
lim = {}
for f in olhos:
    s = 1 if f.calc_center_median().x > 0 else -1
    for v in f.verts:
        x0, x1, z0, z1 = lim.get(s, (9, -9, 9, -9)); lim[s] = (min(x0, abs(v.co.x)), max(x1, abs(v.co.x)), min(z0, v.co.z), max(z1, v.co.z))
# nivela a pupila antiga (afundada) com o branco em volta: some o contorno cinza
brancos = {v for f in olhos if nomes[f.material_index] == 'olho' for v in f.verts}
pupila = {v for f in olhos if nomes[f.material_index] in ('iris', 'preto') for v in f.verts} - brancos
for v in pupila:
    viz = sorted(brancos, key=lambda w: (w.co.x - v.co.x) ** 2 + (w.co.z - v.co.z) ** 2)[:4]
    ps = [1 / max(1e-6, ((w.co.x - v.co.x) ** 2 + (w.co.z - v.co.z) ** 2) ** 0.5) for w in viz]
    v.co.y = sum(w.co.y * p for w, p in zip(viz, ps)) / sum(ps)
print('PUPILA niveladas', len(pupila))
print('LIM', {k: [round(a, 3) for a in v] for k, v in lim.items()})
for f in olhos:
    s = 1 if f.calc_center_median().x > 0 else -1; x0, x1, z0, z1 = lim[s]
    f.material_index = mi
    for l in f.loops:
        u = (x1 - abs(l.vert.co.x)) / (x1 - x0)     # 0 fora, 1 nariz
        v = (l.vert.co.z - z0) / (z1 - z0)
        l[uvl].uv = (u, v)
bm.to_mesh(me); bm.free(); print('OLHO faces', len(olhos))
bpy.ops.wm.save_as_mainfile(filepath=OUT)
