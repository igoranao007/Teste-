"""Converte um modelo "normal" (glTF/GLB/FBX/OBJ/BLEND, ex.: Poly Haven) num objeto PSX: junta as malhas, reduz pra ~TRIS
triângulos, encolhe as texturas de cor pra TEX px (só a cor; normal/rugosidade saem), centraliza na base e exporta GLB.
uso: TRIS=1200 TEX=128 ALTURA=0.9 (ou COMPRIMENTO=1.0) [TEXTURA=cor.png] blender -b --python tools/blender/psx_prop.py -- entrada.gltf saida.glb
     (ALTURA opcional = escala pra essa altura em metros; o original não é alterado)"""
import bpy, sys, os
a = sys.argv[sys.argv.index('--') + 1:]; ENT, OUT = a[0], a[1]
TRIS = int(os.environ.get('TRIS', 1200)); TEX = int(os.environ.get('TEX', 128)); ALT = float(os.environ.get('ALTURA', 0) or 0)
bpy.ops.wm.read_factory_settings(use_empty=True)
ext = ENT.lower().rsplit('.', 1)[-1]
if ext in ('gltf', 'glb'): bpy.ops.import_scene.gltf(filepath=ENT)
elif ext == 'fbx': bpy.ops.import_scene.fbx(filepath=ENT)
elif ext == 'obj': bpy.ops.wm.obj_import(filepath=ENT)
elif ext == 'blend':
    with bpy.data.libraries.load(ENT) as (src, dst): dst.objects = src.objects
    for o in dst.objects:
        if o and o.type == 'MESH': bpy.context.scene.collection.objects.link(o)
ms = [o for o in bpy.context.scene.objects if o.type == 'MESH']
# só a maior variante de detalhe (LOD0) quando o arquivo traz várias
lods = [o for o in ms if 'lod' in o.name.lower()]
if lods: ms = [o for o in ms if 'lod' not in o.name.lower() or 'lod0' in o.name.lower()] or ms
for o in bpy.context.scene.objects: o.select_set(o in ms)
bpy.context.view_layer.objects.active = ms[0]
for o in ms:
    for md in list(o.modifiers):
        bpy.context.view_layer.objects.active = o
        try: bpy.ops.object.modifier_apply(modifier=md.name)
        except RuntimeError: o.modifiers.remove(md)                                  # modificador desligado no arquivo original: sai
bpy.context.view_layer.objects.active = ms[0]
if len(ms) > 1: bpy.ops.object.join()
o = bpy.context.view_layer.objects.active
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM'); bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
n0 = sum(len(p.vertices) - 2 for p in o.data.polygons)
if n0 > TRIS:
    md = o.modifiers.new('d', 'DECIMATE'); md.ratio = TRIS / n0; md.use_collapse_triangulate = True; bpy.ops.object.modifier_apply(modifier='d')
n1 = sum(len(p.vertices) - 2 for p in o.data.polygons)
# base no chão, centro em x/y; escala opcional
from mathutils import Vector
bb = [o.matrix_world @ Vector(c) for c in o.bound_box]; mn = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb))); mx = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
COMP = float(os.environ.get('COMPRIMENTO', 0) or 0)                                  # COMPRIMENTO=m: a maior medida vira essa (armas)
k = ALT / max(1e-6, mx.z - mn.z) if ALT else (COMP / max(1e-6, *(mx - mn)) if COMP else 1.0)
o.location -= Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z)); o.location *= k; o.scale *= k
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
# TEXTURA=arquivo: força essa imagem como cor em todos os materiais (FBX que perdeu o caminho da textura)
if os.environ.get('TEXTURA'):
    im = bpy.data.images.load(os.environ['TEXTURA'])
    for slot in o.material_slots:
        m = slot.material
        if not m: continue
        m.use_nodes = True; nt = m.node_tree; b = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None) or nt.nodes.new('ShaderNodeBsdfPrincipled')
        tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = im; nt.links.new(tn.outputs['Color'], b.inputs['Base Color'])
# materiais: só a textura de cor (base color), encolhida; o resto dos nós sai
for slot in o.material_slots:
    m = slot.material
    if not m or not m.use_nodes: continue
    nt = m.node_tree; bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    img = None
    if bsdf and bsdf.inputs['Base Color'].is_linked:
        n = bsdf.inputs['Base Color'].links[0].from_node
        while n and n.type != 'TEX_IMAGE' and n.inputs and any(i.is_linked for i in n.inputs): n = next(i.links[0].from_node for i in n.inputs if i.is_linked)
        if n and n.type == 'TEX_IMAGE': img = n.image; img_node = n
    for inp in ('Normal', 'Roughness', 'Metallic', 'Specular IOR Level', 'Alpha'):
        if bsdf and inp in bsdf.inputs:
            for l in list(bsdf.inputs[inp].links): nt.links.remove(l)
    if bsdf: bsdf.inputs['Metallic'].default_value = 0; bsdf.inputs['Roughness'].default_value = 1
    if img:
        if bsdf.inputs['Base Color'].links[0].from_node != img_node: nt.links.new(img_node.outputs['Color'], bsdf.inputs['Base Color'])
        w, h = img.size; s = TEX / max(w, h, 1)
        if w and h and s < 1: img.scale(max(8, int(w * s)), max(8, int(h * s)))
        try: img.pack()
        except RuntimeError: pass
        img_node.interpolation = 'Closest'
os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=False, export_image_format='AUTO', export_materials='EXPORT')
dim = o.dimensions; print(f'PSX_PROP {os.path.basename(OUT)} tri {n0}->{n1} tam {dim.x:.2f}x{dim.y:.2f}x{dim.z:.2f} m tex<={TEX}')
