"""Modela roupa e cabelo como peças separadas a partir do corpo em T-pose (mesma UV/textura do corpo):
cabelo (casca no topo da cabeça, com volume), paletó (tronco+braços, aberto em V, com barra), calça (pernas com volume).
Uso: blender -b --python vestir_malhas.py -- base.blend saida.blend"""
import bpy, bmesh, sys, math
from mathutils import Vector
BASE, OUT = sys.argv[sys.argv.index('--') + 1:]
bpy.ops.wm.open_mainfile(filepath=BASE)
corpo = bpy.data.objects['corpo']
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
peca('cabelo', e_cabelo, d_cabelo, 0.002)
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
    if n.y < -0.3 and ax < 0.26 and c.z > 1.27 and ax < 0.05 * ss(1.28, 1.50, c.z) + 0.008: return False   # decote em V
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
def e_calca(c, n): return 0.075 < c.z < 0.95 and abs(c.x) < 0.25
def d_calca(p): return 0.010 + 0.008 * ss(0.30, 0.10, p.z)
peca('calca', e_calca, d_calca, 0.004)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print('VESTIR OK')
