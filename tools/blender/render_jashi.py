# Render de inspeção em resolução cheia (Workbench com textura, sem filtro): frente, 3/4, lado, costas, rosto, rosto 3/4.
# Uso: blender -b arq.blend --python render_jashi.py -- pasta_saida [acao] [quadro]
import bpy, sys, math
from mathutils import Vector
a = sys.argv[sys.argv.index('--') + 1:]; OUT = a[0]; ACAO = a[1] if len(a) > 1 else ''; FR = int(a[2]) if len(a) > 2 else 1
sc = bpy.context.scene; sc.render.engine = 'BLENDER_WORKBENCH'; sh = sc.display.shading
sh.light = 'STUDIO'; sh.color_type = 'TEXTURE'; sh.background_type = 'VIEWPORT'; sh.background_color = (.11, .12, .12)
sh.show_cavity = False; sh.show_shadows = True; sh.show_specular_highlight = False; sc.display.shadow_shift = .1; sc.view_settings.view_transform = 'Standard'
sc.display.render_aa = 'OFF'
arm = next((o for o in bpy.data.objects if o.type == 'ARMATURE'), None)
if arm and ACAO and ACAO in bpy.data.actions: arm.animation_data_create(); arm.animation_data.action = bpy.data.actions[ACAO]; sc.frame_set(FR)
for o in bpy.data.objects:
    if o.type == 'MESH':
        for m in o.data.materials:
            if m and m.use_nodes:
                for n in m.node_tree.nodes:
                    if n.type == 'TEX_IMAGE': n.interpolation = 'Closest'
import os
if os.environ.get('BELO') == '1':                                      # render "bonito": Cycles, luz de recorte, brilho nas linhas acesas
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = int(os.environ.get('AMOSTRAS', '24')); sc.cycles.use_denoising = True
    w = sc.world or bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (.012, .012, .014, 1); w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0
    for nome, en, rot, cor in (('key', 3.2, (0.95, 0.15, -0.6), (1, .96, .9)), ('rim', 4.0, (1.2, 0, 2.7), (.75, .8, 1)), ('fill', 1.0, (1.1, 0, 0.9), (.8, .8, .85))):
        l = bpy.data.objects.new(nome, bpy.data.lights.new(nome, 'SUN')); l.data.energy = en; l.data.color = cor; l.rotation_euler = rot; sc.collection.objects.link(l)
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'
    # (brilho/bloom das linhas: feito depois no PIL — tools/brilho_png.py)
    for m in bpy.data.materials:
        if 'brilho' in m.name and m.use_nodes:
            b = m.node_tree.nodes.get('Principled BSDF')
            if b: b.inputs['Emission Strength'].default_value = 1.6
cam = bpy.data.objects.new('camR', bpy.data.cameras.new('camR')); sc.collection.objects.link(cam); sc.camera = cam
def mirar(p, alvo, lente=50): cam.location = Vector(p); cam.rotation_euler = (Vector(alvo) - Vector(p)).to_track_quat('-Z', 'Y').to_euler(); cam.data.lens = lente
VISTAS = os.environ.get('VISTAS', '').split(',') if os.environ.get('VISTAS') else None
def foto(n, w=900, h=1300):
    if VISTAS and n not in VISTAS: return
    sc.render.resolution_x, sc.render.resolution_y = w, h; sc.render.filepath = f'{OUT}/{n}.png'; bpy.ops.render.render(write_still=True)
H = 1.0
for n, ang in (('frente', 0), ('tres', 35), ('lado', 90), ('costas', 180)):
    r = 4.2; t = math.radians(ang); mirar((r * math.sin(t), -r * math.cos(t), H), (0, 0, H - .02), 50); foto(n)
C = Vector([float(v) for v in __import__('os').environ.get('CAB_C', '0,0,1.88').split(',')])
mirar(C + Vector((0, -1.0, .02)), C, 85); foto('rosto', 1000, 1000)
mirar(C + Vector((.62, -.8, .05)), C, 85); foto('rosto_34', 1000, 1000)
mirar(Vector((0, -1.5, 1.42)), Vector((0, 0, 1.40)), 60); foto('peito', 1000, 1000)
mirar(Vector((0, 1.5, 1.50)), Vector((0, 0, 1.45)), 60); foto('costas_perto', 1000, 1000)
mirar(Vector((.9, -.9, 2.3)), Vector((0, 0, 1.6)), 55); foto('ombros', 1000, 1000)
print('RENDER OK')
