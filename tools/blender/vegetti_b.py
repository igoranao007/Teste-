# VEGETTI — etapa B (Blender): materiais com as texturas pintadas, casca do cabelo, shape keys (boca e piscada),
# pose neutra + ações (Parado, Gesto, Andar), exportação GLB e imagens de inspeção.
import bpy, bmesh, sys, json, math
from mathutils import Vector, Matrix, Quaternion
OUT = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.open_mainfile(filepath=OUT + '/vegetti_trabalho.blend')
info = json.load(open(OUT + '/cabeca_uv.json'))
arm = bpy.data.objects['vegetti_rig']; corpo = bpy.data.objects['vegetti_corpo']; cab = bpy.data.objects['vegetti_cabeca']
# ── materiais (sem brilho, textura com pixel duro) ──
def material(nome, img):
    m = bpy.data.materials.get(nome) or bpy.data.materials.new(nome); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    o = nt.nodes.new('ShaderNodeOutputMaterial'); b = nt.nodes.new('ShaderNodeBsdfPrincipled'); t = nt.nodes.new('ShaderNodeTexImage')
    t.image = bpy.data.images.load(bpy.path.abspath(img), check_existing=True); t.interpolation = 'Closest'
    b.inputs['Roughness'].default_value = 1; b.inputs['Metallic'].default_value = 0
    for k in ('Specular IOR Level', 'Specular'):
        if k in b.inputs: b.inputs[k].default_value = 0
    nt.links.new(t.outputs['Color'], b.inputs['Base Color']); nt.links.new(b.outputs['BSDF'], o.inputs['Surface']); return m
T = OUT + '/texturas/'
corpo.data.materials.clear(); corpo.data.materials.append(material('vegetti_corpo', T + 'corpo.png'))
cab.data.materials[0] = material('vegetti_cabeca', T + 'cabeca.png'); cab.data.materials[1] = material('vegetti_olhos', T + 'olhos.png')
# ── casca do cabelo: duplica as faces cobertas de cabelo e afasta da pele (volume em cima, rente nas laterais) ──
W, H = 512, 256; YOLHO = (1 - info['pts']['olhoE']['uv'][1]) * H
def linha(u):
    a = abs(u - .5) * 2 * math.pi
    if a < .7: return YOLHO - 46 + 6 * (a / .7) ** 2
    if a < 1.35: return YOLHO - 40 + 22 * ((a - .7) / .65)
    if a < 1.75: return YOLHO - 8
    return YOLHO + 34 * min(1, (a - 1.75) / .9)
bm = bmesh.new(); bm.from_mesh(cab.data); uvl = bm.loops.layers.uv.active; deform = bm.verts.layers.deform.active
cabelo = [f for f in bm.faces if f.material_index == 0 and all((1 - l[uvl].uv.y) * H < linha(l[uvl].uv.x % 1) - 3 for l in f.loops)]
res = bmesh.ops.duplicate(bm, geom=cabelo); novas = [g for g in res['geom'] if isinstance(g, bmesh.types.BMFace)]
nverts = {v for f in novas for v in f.verts}
borda = {v for v in nverts if any(not e.is_manifold or len([f for f in e.link_faces if f in set(novas)]) < 2 for e in v.link_edges)}
bm.normal_update(); zmin, zmax = info['zmin'], info['zmax']
for v in nverts:
    alt = (v.co.z - zmin) / (zmax - zmin); off = .001 if v in borda else (.003 + .008 * max(0, alt - .72) / .28)
    v.co += v.normal * off
bm.to_mesh(cab.data); bm.free(); cab.data.update()
# ── shape keys: boca aberta (mandíbula e lábio de baixo descem) e olhos fechados (o globo recua pra dentro da órbita) ──
me = cab.data; Wm = cab.matrix_world
cab.shape_key_add(name='Basis'); kb = cab.shape_key_add(name='boca_aberta'); ko = cab.shape_key_add(name='olhos_fechados')
zq = info['pts']['queixo']['mundo'][2]; zb = zq + (info['pts']['olhoE']['mundo'][2] - zq) * (1 - .70); CY = info['CY']
olhos = set(); 
for p in me.polygons:
    if p.material_index == 1: olhos.update(p.vertices)
for v in me.vertices:
    w = Wm @ v.co
    if v.index in olhos: ko.data[v.index].co = v.co + Vector((0, .016, 0)); continue
    if w.y < CY - .05 and w.z < zb - .002 and w.z > zq - .03 and abs(w.x) < .06:
        f = max(0, 1 - abs(w.x) / .06) ** .7; t = min(1, (zb - w.z) / .012)
        kb.data[v.index].co = v.co + Vector((0, .004 * f, -.02 * f * t))
# ── pose e ações ──
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode='POSE')
PB = arm.pose.bones
for pb in PB: pb.rotation_mode = 'QUATERNION'
def zerar():
    for pb in PB: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
    bpy.context.view_layer.update()
def apontar(nome, d):                                         # gira o osso pra que seu eixo Y aponte pra d (espaço da armadura)
    pb = PB['DEF-' + nome]; M = pb.matrix.copy(); y = (M.to_3x3() @ Vector((0, 1, 0))).normalized()
    q = y.rotation_difference(Vector(d).normalized()); pb.matrix = Matrix.Translation(M.translation) @ (q.to_matrix() @ M.to_3x3()).to_4x4(); bpy.context.view_layer.update()
def girar(nome, eixo, ang):                                   # gira o osso em torno de um eixo do mundo
    pb = PB['DEF-' + nome]; M = pb.matrix.copy(); q = Quaternion(Vector(eixo).normalized(), ang)
    pb.matrix = Matrix.Translation(M.translation) @ (q.to_matrix() @ M.to_3x3()).to_4x4(); bpy.context.view_layer.update()
def braco(s, bra, ante, mao=None):
    apontar('upper_arm.' + s, bra); apontar('forearm.' + s, ante); apontar('hand.' + s, mao or ante)
def neutro(t=0, resp=1.0):
    zerar(); a = math.sin(t * 2 * math.pi / 4) * resp
    girar('spine.002', (1, 0, 0), .012 * a); girar('spine.003', (1, 0, 0), .01 * a)
    braco('L', (.22, .04, -1), (.12, -.12, -1)); braco('R', (-.22, .04, -1), (-.12, -.12, -1))
    for s in ('L', 'R'):                                       # dedos levemente curvados (mão relaxada)
        for f in ('f_index', 'f_middle', 'f_ring', 'f_pinky'):
            for k in ('02', '03'): girar(f'{f}.{k}.{s}', (1, 0, 0), .35)
    girar('head', (1, 0, 0), .02 * a)
def chave(fr):
    for pb in PB: pb.keyframe_insert('rotation_quaternion', frame=fr)
def acao(nome, nfr, fn, passo=5):
    arm.animation_data_create(); a = bpy.data.actions.new(nome); arm.animation_data.action = a
    for fr in range(1, nfr + 2, passo): bpy.context.scene.frame_set(fr); fn((fr - 1) / 30); chave(fr)
    tr = arm.animation_data.nla_tracks.new(); tr.name = nome; tr.strips.new(nome, 1, a); arm.animation_data.action = None
FPS = 30; bpy.context.scene.render.fps = FPS
acao('Parado', 120, lambda t: neutro(t))
def gesto(t):
    neutro(t, .6); b = math.sin(t * 2 * math.pi / 1.5)
    braco('R', (-.35, -.55, -.75), (-.1, -1, .25 + .12 * b), (-.05, -1, .3 + .1 * b)); girar('head', (0, 0, 1), .08 * math.sin(t * 2.1)); girar('head', (1, 0, 0), .04 * b)
acao('Gesto', 90, gesto)
def andar(t):
    zerar(); f = t * 2 * math.pi / 1.0; a = math.sin(f)
    for s, k in (('L', 1), ('R', -1)):
        th = .42 * a * k; dob = max(0, -math.cos(f) * k) * .7 + .08
        apontar('thigh.' + s, (0, -math.sin(th), -math.cos(th))); apontar('shin.' + s, (0, -math.sin(th - dob), -math.cos(th - dob)))
        ang = -.32 * a * k; sx = .2 if s == 'L' else -.2
        braco(s, (sx, -math.sin(ang), -math.cos(ang)), (sx * .5, -math.sin(ang + .3), -math.cos(ang + .3)))
    girar('spine.003', (0, 0, 1), .06 * a); girar('head', (0, 0, 1), -.04 * a)
acao('Andar', 30, andar, 3)
# pose de exportação = neutra (rest continua T-pose, como o padrão dos rigs)
zerar(); bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.wm.save_as_mainfile(filepath=OUT + '/vegetti.blend')
# ── exporta GLB ──
bpy.ops.object.select_all(action='DESELECT')
for o in (arm, corpo, cab): o.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT + '/vegetti_teste.glb', export_format='GLB', use_selection=True, export_animations=True, export_animation_mode='ACTIONS',
                          export_morph=True, export_skins=True, export_yup=True, export_apply=False)
tri = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in (corpo, cab))
print('EXPORTADO', OUT + '/vegetti_teste.glb', 'triângulos', tri, 'ações', [a.name for a in bpy.data.actions])
