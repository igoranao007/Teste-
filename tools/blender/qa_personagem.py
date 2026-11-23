# QA de um personagem salvo (.blend): peças, escala, orientação, esqueleto, pesos, vértices soltos, normais, texturas.
import bpy, bmesh
from mathutils import Vector
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE']; mes = [o for o in bpy.data.objects if o.type == 'MESH']
print('ARMATURE', [a.name for a in arm], 'ossos', len(arm[0].data.bones) if arm else 0)
zs, ys = [], []; problemas = []
for o in mes:
    me = o.data; md = [m for m in o.modifiers if m.type == 'ARMATURE']
    sem_peso = sum(1 for v in me.vertices if not v.groups or sum(g.weight for g in v.groups) < .5)
    bm = bmesh.new(); bm.from_mesh(me); soltos = sum(1 for v in bm.verts if not v.link_faces); bm.free()
    imgs = [n.image.name for m in me.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image]
    w = [o.matrix_world @ v.co for v in me.vertices]; zs += [p.z for p in w]; ys += [p.y for p in w]
    if not md or md[0].object is None: problemas.append(o.name + ': sem modificador de esqueleto')
    if sem_peso: problemas.append(f'{o.name}: {sem_peso} vértices sem peso')
    if soltos: problemas.append(f'{o.name}: {soltos} vértices soltos')
    if not imgs: problemas.append(o.name + ': sem textura')
    print(f'  {o.name:20s} tris {sum(len(p.vertices) - 2 for p in me.polygons):5d}  textura {imgs[:2]}')
print('ALTURA (Blender) %.3f .. %.3f  · no motor ×0,85 = %.2f m' % (min(zs), max(zs), (max(zs) - min(zs)) * .85))
print('FRENTE: y mín %.3f / y máx %.3f (frente = -Y)' % (min(ys), max(ys)))
print('PROBLEMAS:', problemas or 'nenhum')
