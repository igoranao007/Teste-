# renders de inspeção do vestir_dod.py (executado dentro dele com exec): frente, 3/4, lado, costas — em T e com os braços abaixados
import bpy, math, os
os.makedirs(RENDERS, exist_ok=True)
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'; sh = sc.display.shading
sh.light = 'STUDIO'; sh.color_type = os.environ.get('COR', 'TEXTURE'); sh.show_cavity = True; sh.cavity_type = 'WORLD'
sh.background_type = 'VIEWPORT'; sh.background_color = (.16, .17, .18)
sc.render.resolution_x, sc.render.resolution_y = 520, 860
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name == 'head': o.hide_render = True
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = 'ORTHO'
def foto(n, pos, alvo, esc):
    cam.location = pos; cam.rotation_euler = (Vector(alvo) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler(); cam.data.ortho_scale = esc
    sc.render.filepath = os.path.join(RENDERS, n + '.png'); bpy.ops.render.render(write_still=True)
def vistas(pre, esc=2.4):
    foto(pre + 'frente', (0, -6, 1.0), (0, 0, 1.0), esc); foto(pre + 'tres', (4.2, -4.2, 2.2), (0, 0, 1.0), esc)
    foto(pre + 'lado', (6, 0, 1.0), (0, 0, 1.0), esc); foto(pre + 'costas', (0, 6, 1.0), (0, 0, 1.0), esc)
vistas('T_', 2.6)
# braços abaixados (pose de inspeção): gira o upper_arm em torno do eixo da frente
bpy.context.view_layer.objects.active = rig; bpy.ops.object.mode_set(mode='POSE')
for s, nome in ((1, 'upper_arm.L'), (-1, 'upper_arm.R')):
    pb = rig.pose.bones[nome]; pb.rotation_mode = 'XYZ'
    # roda em volta do OMBRO, no eixo frente-trás do mundo (Y), ~72° pra baixo
    eixo = (rig.matrix_world.inverted().to_3x3() @ Vector((0, 1, 0))).normalized(); h = pb.head.copy()
    pb.matrix = Matrix.Translation(h) @ Matrix.Rotation(s * math.radians(72), 4, eixo) @ Matrix.Translation(-h) @ pb.matrix
    bpy.context.view_layer.update()
bpy.ops.object.mode_set(mode='OBJECT'); bpy.context.view_layer.update()
vistas('A_', 2.4)
# closes (com os braços abaixados): colete, bandeira (braço esquerdo), coturnos
cam.data.type = 'PERSP'; cam.data.lens = 50
def perto(n, pos, alvo):
    cam.location = pos; cam.rotation_euler = (Vector(alvo) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    sc.render.resolution_x = sc.render.resolution_y = 700; sc.render.filepath = os.path.join(RENDERS, n + '.png'); bpy.ops.render.render(write_still=True)
perto('Z_colete', (.55, -1.35, 1.55), (0, 0, 1.35))
pb = rig.pose.bones['upper_arm.L']; ombro = rig.matrix_world @ pb.head; cot = rig.matrix_world @ rig.pose.bones['forearm.L'].head
pm = ombro.lerp(cot, .3)
perto('Z_bandeira', (pm.x + .8, pm.y, pm.z + .05), (pm.x, pm.y, pm.z))
perto('Z_botas', (.55, -1.1, .35), (0, 0, .12))

cam.data.type = 'ORTHO'; cam.data.ortho_scale = .6
cam.location = (0, -.12, 2.0); cam.rotation_euler = (0, 0, 0); sc.render.resolution_x = sc.render.resolution_y = 600
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name not in ('bota',): o.hide_render = True
sc.render.filepath = os.path.join(RENDERS, 'Z_botas_cima.png'); bpy.ops.render.render(write_still=True)
