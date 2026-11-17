# Exporta triângulos (uv + posição no mundo + normal) de uma malha, pra projetar foto na textura fora do Blender
import bpy, json, sys
a = sys.argv[sys.argv.index('--') + 1:]; nome, out = a[0], a[1]
o = bpy.data.objects[nome]; me = o.data; me.calc_loop_triangles(); uv = me.uv_layers.active.data
mw = o.matrix_world; nm = mw.to_3x3()
L = []
for t in me.loop_triangles:
    n = (nm @ t.normal).normalized()
    L.append({'uv': [list(uv[l].uv) for l in t.loops], 'p': [list(mw @ me.vertices[v].co) for v in t.vertices], 'n': list(n)})
json.dump(L, open(out, 'w')); print('TRIS', len(L))
