# Personagens novos do jogo (corpo base do projeto + uniforme próprio MODELADO + cabeça própria), estilo PS1.
# Uso: PERSONAGEM=entrada|corsa blender -b -P tools/blender/vestir_personagem.py -- <saida.glb> <saida.blend>
# Reaproveita as FERRAMENTAS de modelagem do vestir_dod.py (cortes, afastar, espessura, extrudar, bolsos, alças, texturas PSX),
# mas cada personagem tem o seu desenho de uniforme (corte, colete, bolsos, cores, calçado) e a sua cabeça.
import os, sys, math
AQUI = os.path.dirname(os.path.abspath(__file__))
PERSONAGEM = os.environ.get('PERSONAGEM', 'entrada')
os.environ['VERSAO'] = '1'
_dod = open(os.path.join(AQUI, 'vestir_dod.py')).read()
exec(_dod[:_dod.index('# ================================================================== PEÇAS')])          # corpo, cortes, ferramentas, texturas base
exec(_dod[_dod.index('def so_tronco'):_dod.index("so_tronco(colete")])                                   # pesos só no tronco
_v2 = open(os.path.join(AQUI, 'vestir_dod_v2.py')).read()
exec(_v2[_v2.index('def bvh_de'):_v2.index('def restringir')])                                          # bvh_de, raio
exec(_v2[_v2.index('def faixa('):_v2.index('bma, fa, linhas_alca')])                                    # faixa (alça apoiada na superfície)
exec(_v2[_v2.index('def bolsa_em('):_v2.index('# bolsa utilitária presa')])                             # bolsa_em (bolsa com volume e aba)
_v3 = open(os.path.join(AQUI, 'vestir_dod_v3.py')).read()
exec(_v3[_v3.index('def faixa_costura'):_v3.index('# ------------------------------------------------------------------ CAMISA')])
_mt = open(os.path.join(AQUI, 'vestir_dod_mat.py')).read()
exec(_mt[:_mt.index('# ---- V2: peças novas')])                                                        # desgaste, lona, fita_f, bolsa_f...
SAIDA_BLEND = ARGS[1] if len(ARGS) > 1 else SAIDA.replace('.glb', '.blend')
F_, T_, C_, E_ = Vector((0, -1, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)), Vector((1, 0, 0))

import json
def pele_mat(nome, rgb, s):                                        # pele lisa com leve variação (tom medido na foto)
    B = tuple(int(c) for c in rgb); E = tuple(int(c * .82) for c in rgb)
    return material(nome, textura(nome, 16, 16, lambda x, y, w, h: mix(E, B, .7 + .3 * ruido(x // 2, y // 2, s))))
def corpo_visivel(pred, mat):                                      # o corpo base fica só com o que a roupa NÃO cobre, com a pele certa
    bmc = extrair(pred); bmc.to_mesh(corpo.data); bmc.free()
    corpo.data.materials.clear(); corpo.data.materials.append(MATS[mat])
    for p in corpo.data.polygons: p.material_index = 0; p.use_smooth = False
    uv_ = corpo.data.uv_layers.active
def tudo_no_osso(ob, osso_):                                       # peça rígida presa a um osso (cabeça, cabelo)
    for g in list(ob.vertex_groups): ob.vertex_groups.remove(g)
    for g in corpo.vertex_groups: ob.vertex_groups.new(name=g.name)
    ob.vertex_groups[osso_].add(list(range(len(ob.data.vertices))), 1.0, 'REPLACE')
def manga_curta(bm, xmax):                                         # corta a manga em |x| = xmax (manga arregaçada)
    for s in (1, -1): cortar(bm, (s * xmax, 0, 0), (1, 0, 0), [f for f in bm.faces if dono(f).startswith(('upper_arm', 'forearm'))])
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if dono(f).startswith(('upper_arm', 'forearm')) and abs(centro(f).x) > xmax], context='FACES')
def anel_torso(z0, z1, afasta, esp, pred=lambda f: True):          # faixa em volta do tronco (cós, cinta do colete)
    bm = extrair(lambda f: REG[f.index] in ('camisa', 'calca') and tronco(f)); afastar(bm, .012)
    for z in (z0, z1): cortar(bm, (0, 0, z), (0, 0, 1))
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if not (z0 < centro(f).z < z1 and pred(f))], context='FACES')
    afastar(bm, afasta); espessura(bm, bm.faces[:], esp); return bm

if PERSONAGEM == 'entrada':
    R_ = json.load(open(os.path.join(RAIZ, 'material/producao/personagens/entrada/texturas/rosto.json')))
    PELE = R_['pele']
    # ---------------- paleta PRÓPRIA (diferente do Dod): camisa verde-acinzentado, calça e colete coyote, coturno coyote, luva oliva escura
    material('e_camisa', textura('e_camisa', 64, 64, desgaste(tecido('#5a614d', '#3d4335', '#737b63', 81), 82, .7)))
    material('e_dobra', textura('e_dobra', 16, 16, lambda x, y, w, h: mix(hx('#6c735c'), hx('#4a5040'), .4 * ruido(x, y // 2, 85)) if y % 5 else hx('#3a3f31')))
    material('e_calca', textura('e_calca', 64, 64, desgaste(tecido('#77674a', '#554933', '#8f7f5f', 83), 84, .8)))
    material('e_rig', textura('e_rig', 64, 64, lambda x, y, w, h: (mix(hx('#5a4d36'), hx('#7a6a4c'), .5) if y % 9 in (0, 1) else lona('#7a6a4c', '#5a4d36', '#93825f', 86)(x, y, w, h)) if x % 21 else hx('#4d4230')))
    material('e_bolso', textura('e_bolso', 32, 32, bolsa_f('#7d6c4d', '#584b35', '#978661', 87, aba=.6)), repete=False)
    material('e_fita', textura('e_fita', 32, 8, fita_f('#6d5f44', '#4a3f2d', 88, ponto=False)))
    material('e_cinto', textura('e_cinto', 32, 8, fita_f('#9a8a62', '#6e6245', 89, ponto=False)))
    material('e_bota', textura('e_bota', 32, 32, lambda x, y, w, h: mix(hx('#6e5a3e'), hx('#94805c'), .55 * ruido(x // 2, y // 2, 90)) if y % 11 else hx('#55452f')))
    material('e_sola', textura('e_sola', 16, 16, lambda x, y, w, h: hx('#2a2219') if (x + y) % 5 < 2 else hx('#3f3326')))
    material('e_luva', textura('e_luva', 32, 32, lambda x, y, w, h: mix(hx('#30352a'), hx('#4b5340'), .5 * ruido(x // 2, y // 2, 91) ** 2) if y % 8 else hx('#262a21')))
    material('e_coldre', textura('e_coldre', 32, 32, bolsa_f('#2b2b28', '#1a1a18', '#3d3d39', 92, aba=.75, tira=False)), repete=False)
    material('e_joelheira', textura('e_joelheira', 16, 16, preto_f('#3a3328', '#5e533f', 93)))
    pele_mat('e_pele', PELE, 94)
    material('e_metal', textura('e_metal', 8, 8, preto_f('#77766c', '#b3b1a4', 95)))
    MANGA = COTOVELO.x - .035
    # ---------------- CAMISA de manga arregaçada (antebraço à mostra), gola em pé, bolso de manga
    bm = extrair(lambda f: REG[f.index] == 'camisa'); manga_curta(bm, MANGA); afastar(bm, .010)
    gola_ = bordas(bm, lambda e: all(W(v.co).z > 1.62 and abs(W(v.co).x) < .14 for v in e.verts))
    if gola_:
        vs = extrudar_borda(bm, gola_, (0, 0, .028)); c0 = sum((W(v.co) for v in vs), Vector()) / len(vs)
        for v in vs: p = W(v.co); d = Vector((p.x - c0.x, p.y - c0.y, 0)); v.co = MWi @ (p + (d.normalized() * .01 if d.length > 1e-6 else Vector()))
    for s in (1, -1):                                              # manga dobrada: rolo grosso na ponta
        pu = bordas(bm, lambda e, s=s: all(abs(W(v.co).x - s * MANGA) < .012 for v in e.verts))
        if not pu: continue
        vs = extrudar_borda(bm, pu, (0, 0, 0)); fs1 = extrudar_borda.faces
        c0 = sum((W(v.co) for v in vs), Vector()) / len(vs)
        for v in vs: p = W(v.co); r = Vector((0, p.y - c0.y, p.z - c0.z)); v.co = MWi @ (p + (r.normalized() * .014 if r.length > 1e-6 else Vector()))
        vs2 = extrudar_borda(bm, [e for e in bm.edges if e.is_boundary and all(v in vs for v in e.verts)], (-s * .045, 0, 0))
        for f in fs1 + extrudar_borda.faces: f.material_index = 1
    na = lambda f: dono(f).startswith('upper_arm') and centro(f).x > OMBRO.x and normal(f).z > .3
    for x in (OMBRO.x + .06, OMBRO.x + .13): cortar(bm, (x, 0, 0), (1, 0, 0), [f for f in bm.faces if na(f)])
    for y in (-.03, .03): cortar(bm, (0, y, 0), (0, 1, 0), [f for f in bm.faces if na(f)])
    for f in extrudar(bm, [f for f in bm.faces if na(f) and OMBRO.x + .06 < centro(f).x < OMBRO.x + .13 and abs(centro(f).y) < .03], .01): f.material_index = 2
    camisa = objeto(bm, 'camisa', ['e_camisa', 'e_dobra', 'e_bolso'], mat_de=lambda f: f.material_index)
    # ---------------- CALÇA cargo coyote: bolsos baixos (abaixo do meio da coxa), joelheira só na esquerda, barra por cima do coturno
    bm = extrair(lambda f: REG[f.index] == 'calca'); afastar(bm, .014)
    barra = bordas(bm, lambda e: all(abs(W(v.co).z - BOTA) < .01 for v in e.verts))
    if barra: extrudar_borda(bm, barra, (0, 0, -.03))
    for s in (1, -1):
        lado = lambda f, s=s: dono(f).startswith('thigh') and normal(f).x * s > .55 and centro(f).x * s > 0
        for z in (JOELHO + .07, JOELHO + .25): cortar(bm, (0, 0, z), (0, 0, 1), [f for f in bm.faces if lado(f)])
        for f in extrudar(bm, [f for f in bm.faces if lado(f) and JOELHO + .07 < centro(f).z < JOELHO + .25], .024): f.material_index = 1
    calca = objeto(bm, 'calca', ['e_calca', 'e_bolso'], mat_de=lambda f: f.material_index)
    bm = extrair(lambda f: REG[f.index] == 'calca'); afastar(bm, .014)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if not (abs(centro(f).z - JOELHO) < .06 and normal(f).y < -.35 and centro(f).x > 0)], context='FACES')
    afastar(bm, .008); extrudar(bm, bm.faces[:], .016, normal_unica=False)
    objeto(bm, 'joelheira', ['e_joelheira'])
    # ---------------- COTURNO coyote com solado escuro
    bm = extrair(lambda f: REG[f.index] == 'bota'); afastar(bm, .017)
    for v in bm.verts:
        p = W(v.co)
        if p.z < 0: v.co = MWi @ Vector((p.x, p.y, 0.0))
    cortar(bm, (0, 0, .024), (0, 0, 1))
    cano = bordas(bm, lambda e: all(abs(W(v.co).z - BOTA) < .01 for v in e.verts))
    if cano: extrudar_borda(bm, cano, (0, 0, .01))
    objeto(bm, 'bota', ['e_bota', 'e_sola'], mat_de=lambda f: 1 if centro(f).z < .024 else 0)
    # ---------------- LUVAS oliva escuras com punho curto
    bm = extrair(lambda f: REG[f.index] == 'luva'); afastar(bm, .006)
    for s in (1, -1):
        pu = bordas(bm, lambda e, s=s: all(abs(W(v.co).x - s * PULSO) < .01 for v in e.verts))
        if pu:
            vs = extrudar_borda(bm, pu, (-s * .02, 0, 0)); c0 = sum((W(v.co) for v in vs), Vector()) / len(vs)
            for v in vs: p = W(v.co); d = Vector((0, p.y - c0.y, p.z - c0.z)); v.co = MWi @ (p + d.normalized() * .007)
    objeto(bm, 'luva', ['e_luva'], dens=8)
    # ---------------- COLETE DE PEITO (chest rig): só a frente, com cinta em volta e suspensório em X nas costas
    bm = extrair(lambda f: REG[f.index] == 'camisa' and tronco(f)); afastar(bm, .010)
    for z in (1.235, 1.515): cortar(bm, (0, 0, z), (0, 0, 1))
    for x in (-.165, .165): cortar(bm, (x, 0, 0), (1, 0, 0))
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if not (1.235 < centro(f).z < 1.515 and abs(centro(f).x) < .165 and normal(f).y < -.3)], context='FACES')
    afastar(bm, .02); espessura(bm, bm.faces[:], .014)
    colete_e = objeto(bm, 'colete', ['e_rig'], dens=6)
    cinta = objeto(anel_torso(1.238, 1.268, .02, .006), 'cinta', ['e_fita'], dens=10)
    SUP = bvh_de([colete_e, camisa, calca])
    BOLSOS_E = []
    for x in (-.1, -.033, .033, .1):                               # 4 porta-carregadores enfileirados
        hit = raio(SUP, Vector((x, -.1, 1.315)), F_)
        b_ = bolsa_em(hit or Vector((x, -.2, 1.315)), F_, C_, .058, .11, .03); pesar(b_); BOLSOS_E.append(objeto(b_, 'carregador', ['e_bolso'], uv=False))
    hit = raio(SUP, Vector((0, -.1, 1.45)), F_)                    # bolso administrativo largo e raso em cima
    b_ = bolsa_em(hit or Vector((0, -.2, 1.45)), F_, C_, .2, .07, .016, nx=3, nz=2); pesar(b_); BOLSOS_E.append(objeto(b_, 'bolso_peito', ['e_bolso'], uv=False))
    SUP = bvh_de([colete_e, camisa, calca] + BOLSOS_E)
    for s in (1, -1):                                              # suspensório: canto de cima do colete → ombro → cruza nas costas
        g_ = [(Vector((s * .13, -.1, 1.50)), F_), (Vector((s * .12, -.05, 1.66)), (F_ + C_).normalized()), (Vector((s * .11, .02, 1.76)), C_),
              (Vector((s * .09, .1, 1.62)), T_), (Vector((0, .1, 1.45)), T_), (Vector((-s * .1, .1, 1.27)), T_)]
        bms, fs_, _ = faixa(g_, .034, .007, passos=4); espessura(bms, fs_, .003); pesar(bms)
        sus = objeto(bms, 'suspensorio', ['e_fita'], dens=10); so_tronco(sus, ['spine', 'spine.001', 'spine.002', 'spine.003'])
    for o in [colete_e, cinta] + BOLSOS_E: so_tronco(o, ['spine', 'spine.001', 'spine.002', 'spine.003'])
    # ---------------- CINTO bege com fivela tipo cobra + COLDRE de perna (direita) com 2 tiras + bolsa de descarga atrás
    bm = extrair(lambda f: REG[f.index] == 'calca'); afastar(bm, .014)
    cortar(bm, (0, 0, CINTURA - .042), (0, 0, 1))
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if not (CINTURA - .042 < centro(f).z < CINTURA + .001)], context='FACES')
    afastar(bm, .008); espessura(bm, bm.faces[:], .009)
    for x in (-.025, .025): cortar(bm, (x, 0, 0), (1, 0, 0))
    for f in extrudar(bm, [f for f in bm.faces if normal(f).y < -.7 and abs(centro(f).x) < .025 and centro(f).y < 0], .01): f.material_index = 1
    cinto = objeto(bm, 'cinto', ['e_cinto', 'e_metal'], mat_de=lambda f: f.material_index, dens=8); so_tronco(cinto, ['spine', 'spine.001'])
    SUP = bvh_de([calca, cinto])
    hit = raio(SUP, Vector((-.16, 0, QUADRIL - .17)), -E_)
    b_ = bolsa_em(hit or Vector((-.2, 0, QUADRIL - .17)), -E_, C_, .075, .15, .045); pesar(b_)
    coldre = objeto(b_, 'coldre', ['e_coldre'], uv=False)
    bm = extrair(lambda f: REG[f.index] == 'calca'); afastar(bm, .014)
    perna_d = lambda f: dono(f).startswith('thigh') and centro(f).x < 0
    for z in (QUADRIL - .13, QUADRIL - .108, QUADRIL - .235, QUADRIL - .213): cortar(bm, (0, 0, z), (0, 0, 1), [f for f in bm.faces if perna_d(f)])
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if not (perna_d(f) and (QUADRIL - .13 < centro(f).z < QUADRIL - .108 or QUADRIL - .235 < centro(f).z < QUADRIL - .213))], context='FACES')
    afastar(bm, .006); objeto(bm, 'tiras_coldre', ['e_fita'], dens=10)
    hit = raio(SUP, Vector((.1, .12, CINTURA - .07)), Vector((.5, .86, 0)).normalized())
    b_ = bolsa_em(hit or Vector((.1, .15, CINTURA - .07)), Vector((.5, .86, 0)).normalized(), C_, .1, .09, .04); pesar(b_)
    so_tronco(objeto(b_, 'bolsa_descarga', ['e_bolso'], uv=False), ['spine', 'spine.001'])
    # o corpo fica com pescoço e ANTEBRAÇOS (manga arregaçada), na cor da pele da foto
    corpo_visivel(lambda f: REG[f.index] == 'pescoco' or (dono(f).startswith('forearm') and abs(centro(f).x) > MANGA + .02 and REG[f.index] != 'luva'), 'e_pele')
    exec(open(os.path.join(AQUI, 'cabeca_entrada.py')).read())

if PERSONAGEM == 'corsa':
    exec(open(os.path.join(AQUI, 'vestir_corsa.py')).read())

for o in list(bpy.data.objects):
    if o.name == 'head': bpy.data.objects.remove(o)
tris = {o.name: sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.type == 'MESH'}
print('TRIANGULOS', tris, 'total', sum(tris.values()))
for o in bpy.data.objects: o.select_set(o.type in ('MESH', 'ARMATURE'))
bpy.ops.export_scene.gltf(filepath=SAIDA, export_format='GLB', use_selection=True, export_skins=True, export_animations=False, export_apply=False)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=SAIDA_BLEND, compress=True)
print('PERSONAGEM OK', PERSONAGEM, SAIDA, SAIDA_BLEND)
