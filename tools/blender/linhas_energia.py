"""Linhas de energia (faixas luminosas em relevo) coladas na superfície de malhas com esqueleto.
O caminho é dado em coordenadas do mundo projetadas: ('frente', [(x, z), ...]) raio vindo de -Y; ('costas', ...) de +Y;
('lado+', [(y, z)...]) de +X; ('lado-', ...) de -X. Cada ponto acha a superfície por raio (BVH das malhas em repouso),
a faixa é um perfil em relevo (topo + 2 lados) e cada vértice copia os pesos do vértice mais próximo da malha de origem
(mexe junto nas animações). Uso (dentro do Blender): exec(open('tools/blender/linhas_energia.py').read()); linhas(...)"""
import bpy, bmesh, math
from mathutils import Vector, kdtree
from mathutils.bvhtree import BVHTree

def _fontes(objs):
    dados = []
    for o in objs:
        bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); bm.verts.ensure_lookup_table()
        kd = kdtree.KDTree(len(bm.verts))
        for i, v in enumerate(bm.verts): kd.insert(v.co, i)
        kd.balance(); dados.append((o, bm, BVHTree.FromBMesh(bm), kd))
    return dados

def _raio(dados, orig, dirc):
    melhor = None
    for o, bm, bvh, kd in dados:
        h = bvh.ray_cast(orig, dirc)
        if h[0] is not None and (melhor is None or h[3] < melhor[3]): melhor = (h[0], h[1], o, h[3])
    return melhor

def linhas(nome, objs, caminhos, mat, arm, larg=0.010, alto=0.004, afasta=0.004, passo=0.012):
    dados = _fontes(objs)
    bm = bmesh.new(); pesos = []          # pesos[i] = (obj, idx_vertice_fonte)
    for lado, pts in caminhos:
        # densifica o caminho
        dens = []
        for a, b in zip(pts, pts[1:]):
            n = max(1, int(math.dist(a, b) / passo))
            for k in range(n): dens.append((a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n))
        dens.append(pts[-1])
        sup = []
        for u, z in dens:
            if lado == 'frente': o_, d_ = Vector((u, -1.0, z)), Vector((0, 1, 0))
            elif lado == 'costas': o_, d_ = Vector((u, 1.0, z)), Vector((0, -1, 0))
            elif lado == 'lado+': o_, d_ = Vector((1.5, u, z)), Vector((-1, 0, 0))
            elif lado == 'lado-': o_, d_ = Vector((-1.5, u, z)), Vector((1, 0, 0))
            else: o_, d_ = Vector((u, 0.0, 3.0)), Vector((0, 0, -1))   # 'cima': (x, y)
            if lado == 'cima': o_ = Vector((u, z, 3.0))
            h = _raio(dados, o_, d_)
            if h: sup.append(h)
        if len(sup) < 2: continue
        aneis = []
        for i, (p, nrm, o, _) in enumerate(sup):
            t = (sup[min(i + 1, len(sup) - 1)][0] - sup[max(i - 1, 0)][0]).normalized()
            nrm = nrm.normalized(); s = t.cross(nrm).normalized()
            base = p + nrm * afasta
            q = [base - s * larg / 2, base - s * larg / 2 + nrm * alto, base + s * larg / 2 + nrm * alto, base + s * larg / 2]
            anel = [bm.verts.new(c) for c in q]
            kd = next(d[3] for d in dados if d[0] is o); _, idx, _ = kd.find(p)
            for _ in anel: pesos.append((o, idx))
            aneis.append(anel)
        for a, b in zip(aneis, aneis[1:]):
            for k in range(3): bm.faces.new((a[k], b[k], b[k + 1], a[k + 1]))
        bm.faces.new(list(reversed(aneis[0][:4]))); bm.faces.new(aneis[-1][:4])
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(nome, me); bpy.context.scene.collection.objects.link(ob); me.materials.append(mat)
    for p in me.polygons: p.use_smooth = False
    grupos = {}
    for i, (o, idx) in enumerate(pesos):
        for g in o.data.vertices[idx].groups:
            nomeg = o.vertex_groups[g.group].name
            if nomeg not in grupos: grupos[nomeg] = ob.vertex_groups.new(name=nomeg)
            grupos[nomeg].add([i], g.weight, 'REPLACE')
    m = ob.modifiers.new('Armature', 'ARMATURE'); m.object = arm; ob.parent = arm; ob.matrix_parent_inverse = arm.matrix_world.inverted()
    for o, b, bvh, kd in dados: b.free()
    print('LINHAS', nome, len(me.polygons)); return ob
