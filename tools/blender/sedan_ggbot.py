"""Sedã do filme com a APARÊNCIA do carro 2 da GGBot (PSX Style Cars, CC0), mantendo a geometria do sedã que o filme usa
(interior, portas separadas, vidro que desce, volante). O original hey-sedan-blue.glb não é alterado.
Como: UV nova ('bake', 1ª) em todas as peças do sedã juntas → bake DIFFUSE (cor) do carro GGBot ajustado no mesmo tamanho →
textura 512 em 15 bits. A UV original fica como 2ª (o motor usa pra achar os vidros: lib/filme.js).
uso: blender -b --python tools/blender/sedan_ggbot.py -- hey-sedan-blue.glb "Car 02/Car2.blend" "Car 02/car2_black.png" saida.glb [GIRAR=0|1]"""
import bpy, sys, os
from mathutils import Vector
a = sys.argv[sys.argv.index('--') + 1:]; SED, GG, TEXG, OUT = a[:4]; RES = int(os.environ.get('RES', 512))
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SED)
sed = [o for o in bpy.context.scene.objects if o.type == 'MESH']
with bpy.data.libraries.load(GG) as (src, dst): dst.objects = [n for n in src.objects]
gg = [o for o in dst.objects if o and o.type == 'MESH']
for o in gg: bpy.context.scene.collection.objects.link(o)
img_g = bpy.data.images.load(TEXG)
for o in gg:
    for s in o.material_slots:
        m = s.material; m.use_nodes = True; nt = m.node_tree; b = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        tn = next((n for n in nt.nodes if n.type == 'TEX_IMAGE'), None) or nt.nodes.new('ShaderNodeTexImage'); tn.image = img_g; tn.interpolation = 'Closest'
        nt.links.new(tn.outputs['Color'], b.inputs['Base Color'])
def caixa(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    return Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))), Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT')
for o in gg: o.select_set(True)
bpy.context.view_layer.objects.active = gg[0]
bpy.ops.object.make_single_user(object=True, obdata=True); bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)   # eixos locais = do mundo
# GGBot: mesma orientação (comprimento no maior eixo horizontal) e MESMO tamanho do sedã em cada eixo
smn, smx = caixa(sed); gmn, gmx = caixa(gg)
if (gmx - gmn).x > (gmx - gmn).y and (smx - smn).y > (smx - smn).x:
    for o in gg: o.rotation_euler.z += 1.5708
if os.environ.get('GIRAR') == '1':
    for o in gg: o.rotation_euler.z += 3.14159
bpy.context.view_layer.update(); bpy.ops.object.transform_apply(location=False, rotation=True, scale=True); gmn, gmx = caixa(gg)
k = Vector(((smx - smn)[i] / max(1e-6, (gmx - gmn)[i]) for i in range(3)))
for o in gg:
    o.scale = Vector((o.scale.x * k.x, o.scale.y * k.y, o.scale.z * k.z))
bpy.context.view_layer.update(); gmn, gmx = caixa(gg)
d = (smn + smx) / 2 - (gmn + gmx) / 2; d.z = smn.z - gmn.z
for o in gg: o.location += d
bpy.context.view_layer.update()
print('GG alinhado', [round(x, 2) for x in caixa(gg)[0]], [round(x, 2) for x in caixa(gg)[1]], 'sedã', [round(x, 2) for x in smn], [round(x, 2) for x in smx])
# UV nova em todas as peças do sedã JUNTAS (uma textura só), como 1ª UV; a original vira a 2ª
for o in sed:
    me = o.data; orig = me.uv_layers[0]; orig.name = 'orig'
    nova = me.uv_layers.new(name='bake'); me.uv_layers.active = nova
bpy.ops.object.select_all(action='DESELECT')
for o in sed: o.select_set(True)
bpy.context.view_layer.objects.active = sed[0]
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.01); bpy.ops.object.mode_set(mode='OBJECT')
img = bpy.data.images.new('sedan_ggbot', RES, RES, alpha=False)
for o in sed:
    m = bpy.data.materials.new('carro_' + o.name); m.use_nodes = True; nt = m.node_tree
    tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = img; tn.interpolation = 'Closest'; nt.nodes.active = tn
    uvn = nt.nodes.new('ShaderNodeUVMap'); uvn.uv_map = 'bake'; nt.links.new(uvn.outputs['UV'], tn.inputs['Vector'])
    b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'); nt.links.new(tn.outputs['Color'], b.inputs['Base Color'])
    o.data.materials.clear(); o.data.materials.append(m)
# reordena: 'bake' vira a 1ª camada de UV (o glTF exporta na ordem: TEXCOORD_0 = bake, TEXCOORD_1 = orig)
for o in sed:
    me = o.data
    tmp = me.uv_layers.new(name='orig2');
    for i, l in enumerate(me.uv_layers['orig'].data): tmp.data[i].uv = l.uv
    me.uv_layers.remove(me.uv_layers['orig']); tmp.name = 'orig'
    me.uv_layers['bake'].active = True; me.uv_layers['bake'].active_render = True
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 4; sc.cycles.device = 'CPU'
for i, o in enumerate(sed):
    bpy.ops.object.select_all(action='DESELECT')
    for g in gg: g.select_set(True)
    o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, use_selected_to_active=True, cage_extrusion=0.12, max_ray_distance=0.6, margin=3, use_clear=(i == 0))
# 15 bits
px = list(img.pixels); px = [round(v * 31) / 31 for v in px]; img.pixels = px
img.filepath_raw = OUT.replace('.glb', '.png'); img.file_format = 'PNG'; img.save(); img.pack()
for g in gg: bpy.data.objects.remove(g, do_unlink=True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_image_format='AUTO')
print('SEDAN_GGBOT ok', OUT)
