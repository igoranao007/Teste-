# uso: blender -b --python tools/blender/inspecionar.py -- arquivo.glb
import bpy, sys, bmesh
from mathutils import Vector
f = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=f)
for o in bpy.data.objects:
    print(o.type, o.name, 'pai=', o.parent.name if o.parent else None, 'loc', tuple(round(v, 3) for v in o.location), 'rot', tuple(round(v, 3) for v in o.rotation_euler), 'esc', tuple(round(v, 3) for v in o.scale))
    if o.type == 'MESH':
        me = o.data; print('  verts', len(me.vertices), 'faces', len(me.polygons), 'uvs', [u.name for u in me.uv_layers], 'mats', [m.name for m in me.materials], 'grupos', len(o.vertex_groups), 'shapekeys', bool(me.shape_keys))
        hg = o.vertex_groups.get('DEF-head'); 
        if hg:
            hv = [v for v in me.vertices if any(g.group == hg.index and g.weight > .5 for g in v.groups)]
            ws = [o.matrix_world @ v.co for v in hv]; print('  cabeça: verts', len(hv), 'min', [round(min(w[i] for w in ws), 3) for i in range(3)], 'max', [round(max(w[i] for w in ws), 3) for i in range(3)])
    if o.type == 'ARMATURE': print('  ossos', len(o.data.bones), [b.name for b in o.data.bones][:12], '...')
