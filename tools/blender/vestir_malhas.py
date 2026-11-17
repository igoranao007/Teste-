"""Modela roupa e cabelo como peças separadas a partir do corpo em T-pose (mesma UV/textura do corpo):
cabelo (casca no topo da cabeça, com volume), paletó (tronco+braços, aberto em V, com barra), calça (pernas com volume).
Uso: blender -b --python vestir_malhas.py -- base.blend saida.blend"""
import bpy, bmesh, sys, math
from mathutils import Vector
BASE, OUT = sys.argv[sys.argv.index('--') + 1:]
bpy.ops.wm.open_mainfile(filepath=BASE)
corpo = bpy.data.objects['corpo']
# ---- ajustes no corpo: orelha sem ponta de elfo, mão mais fina e comprida (menos 'bloco')
import json, os
for v in corpo.data.vertices:
    x, y, z = v.co; ax = abs(x); s = 1 if x > 0 else -1
    if 0.07 < ax < 0.11 and 1.60 < z < 1.75 and y > -0.03:                   # orelha
        f = max(0.0, min(1.0, (z - 1.66) / 0.06))
        v.co.z -= 0.022 * f; v.co.x = s * (ax - 0.012 * f); v.co.y += 0.004 * f
    if ax > 0.60:                                                              # mão
        c = Vector((s * ax, 0.0, 1.466)); d = v.co - c
        v.co = Vector((s * (0.60 + (ax - 0.60) * 1.12), d.y * 0.72 + 0.0, 1.466 + d.z * 0.78))

def ss(a, b, v): return max(0.0, min(1.0, (v - a) / (b - a)))
def peca(nome, escolhe, desloc, solid=0.004, extra=None):
    bm = bmesh.new(); bm.from_mesh(corpo.data); bm.faces.ensure_lookup_table()
    fora = [f for f in bm.faces if not escolhe(f.calc_center_median(), f.normal)]
    bmesh.ops.delete(bm, geom=fora, context='FACES')
    bm.normal_update()
    for v in bm.verts: v.co = v.co + v.normal * desloc(v.co)
    if extra: extra(bm)
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(nome, me); bpy.context.scene.collection.objects.link(o)
    for m in corpo.data.materials: me.materials.append(m)
    for p in me.polygons: p.use_smooth = True
    if solid:
        s = o.modifiers.new('esp', 'SOLIDIFY'); s.thickness = solid; s.offset = -1; s.use_rim = True
        bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier='esp')
    print('PECA', nome, 'tris', sum(len(p.vertices) - 2 for p in me.polygons))
    return o
# ---- cabelo: topo da cabeça; frente começa na linha do cabelo; volume maior em cima
def e_cabelo(c, n):
    if c.z < 1.69 or abs(c.x) > 0.15: return False
    return c.z > 1.712 + 0.05 * ss(0.0, -0.08, c.y)     # linha do cabelo sobe suave na frente
def d_cabelo(p): return 0.002 + 0.010 * ss(1.73, 1.80, p.z)
def topete(bm):   # mechas: borda da frente puxada um pouco pra frente e pra cima, em dente
    borda = [v for v in bm.verts if v.is_boundary]
    for i, v in enumerate(sorted(borda, key=lambda v: math.atan2(v.co.x, v.co.y))):
        if v.co.y < -0.04: v.co.z += 0.006 if i % 2 else -0.002; v.co.y -= 0.004
import os
if os.environ.get('CABELO_MALHA', '0') == '1': peca('cabelo', e_cabelo, d_cabelo, 0.002)
# ---- paletó: tronco e braços até o pulso; aberto em V na frente
MAO = 0.575
def e_paleto(c, n):
    ax = abs(c.x)
    if ax > MAO: return False
    if c.z < 0.90: return False
    if c.z < 1.0 and abs(c.x) < 0.035 and c.y > -0.06 and c.y < 0.09 and c.z < 0.95: return False   # entreperna
    rn = math.hypot(c.x, (c.y - 0.035) * 1.2)
    if c.z > 1.52 and rn < 0.075: return False          # pescoço/gola de fora
    if c.z > 1.585: return False
    if n.y < -0.3 and ax < 0.26 and c.z > 1.27 and ax < 0.05 * ss(1.28, 1.50, c.z) + 0.001: return False   # decote em V
    return True
def d_paleto(p):
    ax = abs(p.x)
    if ax > 0.22 and p.z > 1.3: return 0.012                 # braço
    return 0.016 + 0.008 * ss(1.02, 0.90, p.z)                 # tronco, abrindo um pouco na barra
def barra(bm):   # barra do paletó desce até ~0,80 m (cobre o quadril)
    borda = [v for v in bm.verts if v.is_boundary and v.co.z < 0.88]
    ext = bmesh.ops.extrude_edge_only(bm, edges=[e for e in bm.edges if e.is_boundary and all(v.co.z < 0.88 for v in e.verts)])
    for v in [g for g in ext['geom'] if isinstance(g, bmesh.types.BMVert)]:
        d = Vector((v.co.x, v.co.y - 0.02, 0)); d = d.normalized() if d.length else d
        v.co.z -= 0.075; v.co += d * 0.012
peca('paleto', e_paleto, d_paleto, 0.006)
# ---- calça: pernas do joelho pra baixo e coxa (abaixo da barra), com boca levemente larga
def e_calca(c, n): return 0.075 < c.z < 0.95 and abs(c.x) < 0.25 and not (abs(c.x) < 0.035 and c.z > 0.78)   # sem volume no meio das pernas
def d_calca(p): return 0.010 + 0.008 * ss(0.30, 0.10, p.z)
peca('calca', e_calca, d_calca, 0.004)
# ---- gola e gravata modeladas (material próprio)
from mathutils.bvhtree import BVHTree
dg = bpy.context.evaluated_depsgraph_get(); bvh = BVHTree.FromObject(corpo, dg)
def superficie(orig, dirv):
    loc, nrm, i, d = bvh.ray_cast(Vector(orig), Vector(dirv).normalized())
    return loc
def mat(nome, cor):
    m = bpy.data.materials.new(nome); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = cor; b.inputs['Roughness'].default_value = 0.9; m['proprio'] = 1; return m
def objeto(nome, bm, m):
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(nome, me); bpy.context.scene.collection.objects.link(o); me.materials.append(m); o['proprio'] = 1
    print('PECA', nome, 'tris', sum(len(p.vertices) - 2 for p in me.polygons)); return o
# gola: anel em volta do pescoço, mais alto atrás, com as duas pontas na frente
bm = bmesh.new(); SEG = 16; C = Vector((0, 0.035, 0))
base, topo = [], []
for k in range(SEG + 1):
    a = -math.pi / 2 + (k / SEG) * 2 * math.pi            # começa na frente (y negativo), dá a volta
    d = Vector((math.cos(a + math.pi / 2) * 0, 0, 0))
    dirv = Vector((math.sin(a - (-math.pi / 2)) * 0 + math.cos(a), math.sin(a), 0))
    frente = max(0.0, -math.sin(a))                         # 1 na frente, 0 atrás
    z0 = 1.535 - 0.012 * frente; z1 = 1.585 - 0.020 * frente
    def pt(z, extra):
        hit = superficie((C.x, C.y, z), dirv)
        r = (Vector((hit.x, hit.y, 0)) - Vector((C.x, C.y, 0))).length if hit else 0.06
        return Vector((C.x + dirv.x * (r + extra), C.y + dirv.y * (r + extra), z))
    base.append(bm.verts.new(pt(z0, 0.010))); topo.append(bm.verts.new(pt(z1, 0.006)))
for k in range(SEG):
    if k in (0, SEG - 1): continue                          # abertura da gola na frente
    bm.faces.new((base[k], base[k + 1], topo[k + 1], topo[k]))
# pontas da gola caindo sobre o peito
for k, lado in ((1, 1), (SEG - 1, -1)):
    v = base[k].co; ponta = bm.verts.new(Vector((0.028 * (1 if v.x > 0 else -1), v.y - 0.012, v.z - 0.045)))
    bm.faces.new((base[k], topo[k], ponta))
s_ = bmesh.ops.solidify if hasattr(bmesh.ops, 'solidify') else None
gola = objeto('gola', bm, mat('proprio_camisa', (0.86, 0.87, 0.85, 1)))
md = gola.modifiers.new('esp', 'SOLIDIFY'); md.thickness = 0.003
bpy.context.view_layer.objects.active = gola; bpy.ops.object.modifier_apply(modifier='esp')
# gravata: nó + faixa que acompanha o peito e alarga embaixo, terminando em ponta
bm = bmesh.new(); zs = [1.545, 1.53, 1.50, 1.45, 1.40, 1.35, 1.31, 1.285]
larg = [0.016, 0.014, 0.014, 0.017, 0.020, 0.023, 0.025, 0.0]
esq, dir_ = [], []
for z, w in zip(zs, larg):
    hit = superficie((0, -0.5, z), (0, 1, 0)); y = (hit.y if hit else -0.08) - 0.006
    if w == 0: ponta = bm.verts.new((0, y, z)); continue
    esq.append(bm.verts.new((-w, y, z))); dir_.append(bm.verts.new((w, y, z)))
for i in range(len(esq) - 1): bm.faces.new((esq[i], dir_[i], dir_[i + 1], esq[i + 1]))
bm.faces.new((esq[-1], dir_[-1], ponta))
gravata = objeto('gravata', bm, mat('proprio_gravata', (0.06, 0.55, 0.18, 1)))
md = gravata.modifiers.new('esp', 'SOLIDIFY'); md.thickness = 0.006
bpy.context.view_layer.objects.active = gravata; bpy.ops.object.modifier_apply(modifier='esp')
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print('VESTIR OK')
