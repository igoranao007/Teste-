# Inspeção de personagem montado (.blend): frente/perfil/costas/perspectiva, rosto (frente e 3/4), mão, sem textura, animações.
import bpy, sys
from mathutils import Vector
arq, OUT = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.open_mainfile(filepath=arq)
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 24; sc.cycles.device = 'CPU'; sc.cycles.use_denoising = False
w = sc.world or bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (.16, .18, .17, 1); w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0
lz = bpy.data.objects.new('sol', bpy.data.lights.new('sol', 'SUN')); lz.data.energy = 2.2; lz.rotation_euler = (.9, 0, -.5); sc.collection.objects.link(lz)
sh = sc.display.shading
sc.view_settings.view_transform = 'Standard'
arm = bpy.data.objects['rig']; cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
def mirar(p, a, l=50): cam.location = p; cam.rotation_euler = (Vector(a) - Vector(p)).to_track_quat('-Z', 'Y').to_euler(); cam.data.lens = l
def foto(n, w=800, h=1100): sc.render.resolution_x, sc.render.resolution_y = w, h; sc.render.filepath = f'{OUT}/{n}.png'; bpy.ops.render.render(write_still=True)
def acao(n, fr): arm.animation_data.action = bpy.data.actions[n]; sc.frame_set(fr)
def osso(n): return arm.matrix_world @ arm.pose.bones[n].head
acao('idle', 1); cab = osso('Head') + Vector((0, 0, .1))
for n, p in (('frente', (0, -3.3, .95)), ('perfil', (3.3, 0, .95)), ('costas', (0, 3.3, .95)), ('perspectiva', (2.1, -2.6, 1.4))): mirar(p, (0, 0, .88)); foto(n)
mirar(cab + Vector((0, -.62, 0)), cab, 60); foto('rosto', 900, 900); mirar(cab + Vector((.4, -.45, .04)), cab, 60); foto('rosto_34', 900, 900); mirar(cab + Vector((0, .62, 0)), cab, 60); foto('rosto_costas', 900, 900)
m = osso('RightHand'); mirar(m + Vector((-.1, -.4, .1)), m, 55); foto('mao', 900, 900)
for n, fr in (('talk', 12), ('walk', 8), ('sit', 10), ('wave', 14)): acao(n, fr); mirar((1.9, -2.8, 1.25), (0, 0, .8)); foto('anim_' + n)
acao('idle', 1); sc.render.engine = 'BLENDER_WORKBENCH'; sh.color_type = 'SINGLE'; sh.single_color = (.75, .75, .75); sh.light = 'STUDIO'; sh.background_type = 'VIEWPORT'; sh.background_color = (.16, .18, .17)
mirar((0, -3.3, .95), (0, 0, .88)); foto('frente_sem_textura'); mirar(cab + Vector((0, -.62, 0)), cab, 60); foto('rosto_sem_textura', 900, 900)
print('INSPECAO OK')
