# Monta um personagem a partir do PSX Character Creator Free (heyheythere, CC BY 4.0): corpo + peças no MESMO esqueleto.
# uso: blender -b --python tools/blender/montar_psx.py -- saida.blend corpo peca1:tint peca2:tint ...
import bpy, sys, os
a = sys.argv[sys.argv.index("--") + 1:]; OUT, CORPO, PECAS = a[0], a[1], a[2:]
DIR = 'material/modelos/itch/psx-creator/'
bpy.ops.wm.read_factory_settings(use_empty=True)
def importar(nome):
    antes = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=DIR + nome + '.glb'); return [o for o in bpy.data.objects if o not in antes]
def vivos(ns): return [o for o in ns if o.name in bpy.data.objects and bpy.data.objects[o.name] == o] if False else [bpy.data.objects[n] for n in [x.name for x in ns] if n in bpy.data.objects]
ATLAS = os.environ.get('ATLAS', DIR + 'atlas.png')
def mat_psx(nome, tint):                                         # textura (pixel duro) × cor de vértice (sombra assada) × tinta
    m = bpy.data.materials.new(nome); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    o = nt.nodes.new('ShaderNodeOutputMaterial'); b = nt.nodes.new('ShaderNodeBsdfPrincipled'); t = nt.nodes.new('ShaderNodeTexImage'); vc = nt.nodes.new('ShaderNodeVertexColor')
    t.image = bpy.data.images.load(os.path.abspath(ATLAS), check_existing=True); t.interpolation = 'Closest'; vc.layer_name = 'Color'
    m1 = nt.nodes.new('ShaderNodeMix'); m1.data_type = 'RGBA'; m1.blend_type = 'MULTIPLY'; m1.inputs['Factor'].default_value = 1
    m2 = nt.nodes.new('ShaderNodeMix'); m2.data_type = 'RGBA'; m2.blend_type = 'MULTIPLY'; m2.inputs['Factor'].default_value = 1
    nt.links.new(t.outputs['Color'], m1.inputs['A']); nt.links.new(vc.outputs['Color'], m1.inputs['B'])
    nt.links.new(m1.outputs['Result'], m2.inputs['A']); m2.inputs['B'].default_value = tuple(int(tint[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (1,)
    nt.links.new(m2.outputs['Result'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = 1
    for k in ('Specular IOR Level', 'Specular'):
        if k in b.inputs: b.inputs[k].default_value = 0
    nt.links.new(b.outputs['BSDF'], o.inputs['Surface']); m['tinta'] = tint; return m
def limpar(ns, nome):
    real = None
    for o in [o for o in ns if o.type == 'MESH']:
        if o.type == 'MESH' and len(o.data.polygons) == 80 and not o.vertex_groups: bpy.data.objects.remove(o, do_unlink=True)   # bolinha-marcador do pacote
        elif o.type == 'MESH': real = o; o.name = nome
    return real
novos = importar(CORPO); arm = [o for o in novos if o.type == 'ARMATURE'][0]; arm.name = 'rig'
c = limpar(novos, 'corpo'); c.data.materials.clear(); c.data.materials.append(mat_psx('mat_corpo', os.environ.get('PELE', 'ffffff')))
for p in PECAS:
    nome, _, tint = p.partition(':'); ns = importar(nome); o = limpar(ns, nome.replace('man_', '').replace('woman_', ''))
    for m in o.modifiers:
        if m.type == 'ARMATURE': m.object = arm
    mw = o.matrix_world.copy(); o.parent = arm; o.matrix_world = mw
    o.data.materials.clear(); o.data.materials.append(mat_psx('mat_' + o.name, tint or 'ffffff'))
    for x in [y for y in bpy.data.objects if y.type == 'ARMATURE' and y != arm]: bpy.data.objects.remove(x, do_unlink=True)
for ac in bpy.data.actions: ac.use_fake_user = True
arm.animation_data_create(); arm.animation_data.action = bpy.data.actions.get('idle')
for o in bpy.data.objects: print('OBJ', o.type, o.name, 'pai', o.parent.name if o.parent else None, 'tris', sum(len(p.vertices) - 2 for p in o.data.polygons) if o.type == 'MESH' else '', 'mats', [m.name for m in o.data.materials] if o.type == 'MESH' else '', 'cores', [c.name for c in o.data.color_attributes] if o.type == 'MESH' else '')
print('ACOES', [x.name for x in bpy.data.actions])
for m in bpy.data.materials:
    if m.node_tree: print('MAT', m.name, [(n.type, n.inputs['Base Color'].default_value[:3] if n.type == 'BSDF_PRINCIPLED' else '') for n in m.node_tree.nodes][:6])
bpy.ops.wm.save_as_mainfile(filepath=OUT)
