"""Troca a CARA da cabeça do Simple PSX Character (JashiPSX) pela foto de uma pessoa, sem placa por cima:
a região do rosto (frente da cabeça, do queixo à testa, entre as orelhas) vira um objeto à parte ("rosto"), com o mesmo
esqueleto, e recebe a foto projetada de frente (UV planar) num material próprio. As bordas são as mesmas da cabeça: nada de vão.
Uso: blender -b X.blend --python rosto_foto.py -- foto_alinhada.png saida.blend
(foto alinhada como as do pintor: olhos em y=378.5, meio do rosto em x=478 — ver tools/pintar_jashi_vasco.py PX/PY)"""
import bpy, bmesh, sys, os
FOTO, OUT = sys.argv[sys.argv.index('--') + 1:]
h = bpy.data.objects['head']; mw = h.matrix_world; inv = mw.inverted()
Z0, Z1, XM = float(os.environ.get('RZ0', '1.69')), float(os.environ.get('RZ1', '1.965')), float(os.environ.get('RXM', '0.084'))
# 1) seleciona as faces do rosto: de frente (normal pra -y), na faixa do queixo à testa, entre as orelhas
bpy.context.view_layer.objects.active = h
for o in bpy.context.selected_objects: o.select_set(False)
h.select_set(True)
bpy.ops.object.mode_set(mode='EDIT'); bm = bmesh.from_edit_mesh(h.data); bm.faces.ensure_lookup_table()
nm = mw.to_3x3(); n_sel = 0
for f in bm.faces:
    c = mw @ f.calc_center_median(); n = (nm @ f.normal).normalized()
    f.select = (Z0 < c.z < Z1 and abs(c.x) < XM and n.y < -0.25 and c.y < -0.03)
    n_sel += f.select
bmesh.update_edit_mesh(h.data); print('ROSTO faces:', n_sel)
bpy.ops.mesh.separate(type='SELECTED'); bpy.ops.object.mode_set(mode='OBJECT')
r = [o for o in bpy.data.objects if o.name.startswith('head') and o != h][0]; r.name = 'rosto'
# 2) UV planar de frente, mapeando a posição 3D na foto alinhada (mesma conta do pintor: CZ 1,86, ESC 0,4 → 512 px)
PY = [(242, 10), (290, 140), (360, 180), (378.5, 215), (422.5, 280), (465, 330), (530, 385), (600, 440)]
def interp(pts, v):
    pts = sorted(pts, key=lambda p: p[1])
    for a, b in zip(pts, pts[1:]):
        if a[1] <= v <= b[1]: return a[0] + (v - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
    a, b = (pts[0], pts[1]) if v < pts[0][1] else (pts[-2], pts[-1])
    return a[0] + (v - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
img = bpy.data.images.load(os.path.abspath(FOTO)); img.pack(); FW, FH = img.size
KX = float(os.environ.get('RKX', '0.92'))
me = r.data; mwr = r.matrix_world; uvl = me.uv_layers.active
for poly in me.polygons:
    for li in poly.loop_indices:
        w = mwr @ me.vertices[me.loops[li].vertex_index].co
        mx = w.x / 0.4 * 512 + 256; my = (1.86 - w.z) / 0.4 * 512 + 256
        fx = 478 - (mx - 256) * KX * 1.0      # x do modelo (+ = lado esquerdo do personagem) → foto (espelhado: a foto está de frente)
        fy = max(float(os.environ.get('RFYMIN', '0')), interp(PY, my))   # trava acima: a testa repete a pele (não pega a aba do chapéu da foto)
        uvl.data[li].uv = (fx / FW, 1 - fy / FH)
# 3) material próprio com a foto (pixel duro, estilo PS1)
mat = bpy.data.materials.new('rosto_foto'); mat.use_nodes = True
nt = mat.node_tree; bsdf = nt.nodes.get('Principled BSDF'); tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = img; tx.interpolation = 'Closest'
nt.links.new(tx.outputs['Color'], bsdf.inputs['Base Color']); nt.nodes.active = tx
me.materials.clear(); me.materials.append(mat)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(OUT)); print('ROSTO OK', OUT)
