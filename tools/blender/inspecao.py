# Imagens de inspeção de um personagem (.blend): frente, perfil, costas, perspectiva, rosto, mãos — com e sem textura —
# e quadros de animação. uso: blender -b --python tools/blender/inspecao.py -- arquivo.blend pasta_saida
import bpy, sys, math
from mathutils import Vector
arq, OUT = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.open_mainfile(filepath=arq)
sc = bpy.context.scene; sc.render.engine = 'BLENDER_WORKBENCH'; sc.render.resolution_x = 900; sc.render.resolution_y = 1200
sh = sc.display.shading; sh.light = 'STUDIO'; sh.color_type = 'TEXTURE'; sh.show_specular_highlight = False; sh.show_object_outline = False
sc.display.shading.background_type = 'VIEWPORT'; sc.world = sc.world or bpy.data.worlds.new('w')
sh.background_type = 'VIEWPORT'; sh.background_color = (.16, .18, .17)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
def mirar(pos, alvo, lente=50):
    cam.location = pos; d = Vector(alvo) - Vector(pos); cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); cam.data.lens = lente
def foto(nome, w=900, h=1200):
    sc.render.resolution_x, sc.render.resolution_y = w, h; sc.render.filepath = f'{OUT}/{nome}.png'; bpy.ops.render.render(write_still=True)
def acao(nome, fr):
    arm.animation_data_create(); arm.animation_data.action = bpy.data.actions.get(nome); sc.frame_set(fr)
for o in bpy.data.objects:
    if o.type == 'MESH':
        for k in (o.data.shape_keys.key_blocks if o.data.shape_keys else []): k.value = 0
acao('Idle_Loop', 1)
VIS = {'frente': ((0, -3.4, 1.0), (0, 0, .95), 50), 'perfil': ((3.4, 0, 1.0), (0, 0, .95), 50), 'costas': ((0, 3.4, 1.0), (0, 0, .95), 50),
       'perspectiva': ((2.2, -2.6, 1.5), (0, 0, .95), 50), 'rosto': ((.0, -.75, 1.7), (0, -.08, 1.68), 70), 'rosto_34': ((.42, -.62, 1.72), (0, -.06, 1.68), 70)}
for nome, (p, a, l) in VIS.items(): mirar(p, a, l); foto(nome, 1200, 1200) if nome.startswith('rosto') else foto(nome)
# mãos
corpo_o = [o for o in bpy.data.objects if o.type == 'MESH' and not o.data.shape_keys][0]
dg = bpy.context.evaluated_depsgraph_get(); ev = corpo_o.evaluated_get(dg).to_mesh(); gi = {g.index: g.name for g in corpo_o.vertex_groups}
hv = [corpo_o.matrix_world @ ev.vertices[v.index].co for v in corpo_o.data.vertices if v.groups and gi[max(v.groups, key=lambda g: g.weight).group] == 'DEF-hand.R']
hp = sum(hv, Vector()) / len(hv)
mirar(hp + Vector((-.05, -.42, .12)), hp, 55); foto('mao', 1200, 1200); mirar(hp + Vector((-.3, .05, .3)), hp, 55); foto('mao_cima', 1200, 1200)
# sem textura
sh.color_type = 'SINGLE'; sh.single_color = (.72, .72, .72)
for nome in ('frente', 'perfil', 'rosto'): p, a, l = VIS[nome]; mirar(p, a, l); foto(nome + '_sem_textura', 1200 if nome == 'rosto' else 900, 1200)
sh.color_type = 'TEXTURE'
# animação + boca + piscada
for nome, fr in (('Idle_Talking_Loop', 20), ('Walk_Formal_Loop', 12), ('Sitting_Talking_Loop', 30), ('PickUp_Table', 40), ('Gesto', 30)):
    if bpy.data.actions.get(nome): acao(nome, fr); mirar((1.9, -2.9, 1.3), (0, 0, .85), 50); foto('anim_' + nome)
acao('Idle_Loop', 1)
cabs = [o for o in bpy.data.objects if o.type == 'MESH' and o.data.shape_keys]
for o in cabs: o.data.shape_keys.key_blocks['boca_aberta'].value = 1
mirar(*VIS['rosto'][:2], 70); foto('rosto_boca_aberta', 1200, 1200)
for o in cabs: o.data.shape_keys.key_blocks['boca_aberta'].value = 0; o.data.shape_keys.key_blocks['olhos_fechados'].value = 1
foto('rosto_piscando', 1200, 1200)
print('INSPECAO OK')
