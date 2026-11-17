import bpy, sys
out = sys.argv[sys.argv.index('--') + 1]
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS', export_vertex_color='ACTIVE', export_image_format='AUTO')
