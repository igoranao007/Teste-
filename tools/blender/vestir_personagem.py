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

def afinar_corpo(kt=(.86, .92), ka=.84, kc=.91, kn=.95):            # PROPORÇÕES PRÓPRIAS: afina tronco (x, y), braços, coxas e canelas do corpo base
    nomes = {g.index: g.name for g in corpo.vertex_groups}
    YT = osso('spine.002').y; MAO = osso('hand.L'); PE = osso('foot.L'); COXA = osso('thigh.L')
    def afina(nome, p):
        if nome.startswith(('spine.004', 'spine.005')): return p
        if nome.startswith(('upper_arm', 'forearm', 'hand')):            # braço em T: encolhe em volta do eixo do braço
            t = min(1, max(0, (abs(p.x) - OMBRO.x) / (MAO.x - OMBRO.x)))
            ey = OMBRO.y + (MAO.y - OMBRO.y) * t; ez = OMBRO.z + (MAO.z - OMBRO.z) * t; k = .95 if nome.startswith('hand') else ka
            return Vector((p.x, ey + (p.y - ey) * k, ez + (p.z - ez) * k))
        if nome.startswith(('thigh', 'shin')):                           # perna: encolhe em volta do eixo da perna
            s = 1 if p.x > 0 else -1; t = min(1, max(0, (COXA.z - p.z) / (COXA.z - PE.z)))
            ex = s * (COXA.x + (PE.x - COXA.x) * t); ey = COXA.y + (PE.y - COXA.y) * t; k = kc if nome.startswith('thigh') else kn
            return Vector((ex + (p.x - ex) * k, ey + (p.y - ey) * k, p.z))
        if nome.startswith(('foot', 'toe')): return p
        return Vector((p.x * kt[0], YT + (p.y - YT) * kt[1], p.z))     # tronco
    for v in bm0.verts:
        ws = [(nomes[g], w) for g, w in v[DL].items() if g in nomes and w > 0]
        tot = sum(w for _, w in ws)
        if tot <= 0: continue
        p = W(v.co); q = Vector()
        for n_, w in ws: q += afina(n_, p) * (w / tot)
        v.co = MWi @ q
    bm0.normal_update()
    return max(abs(W(v.co).x) for f in bm0.faces if tronco(f) and 1.3 < centro(f).z < 1.5 for v in f.verts)   # nova meia-largura do tronco (TX)

if PERSONAGEM == 'entrada':
    R_ = json.load(open(os.path.join(RAIZ, 'material/producao/personagens/entrada/texturas/rosto.json')))
    PELE = R_['pele']
    UNIFORME = os.environ.get('UNIFORME', 'v2')                      # v1 = chest rig + manga arregaçada (antigo) · v2 = uniforme refeito
    if UNIFORME == 'v2': TX = afinar_corpo()                         # rapaz magro: tronco ×0,86, braços ×0,84, coxas ×0,91
    exec(open(os.path.join(AQUI, 'uniforme_entrada_%s.py' % UNIFORME)).read())
    CABECA = os.environ.get('CABECA', 'v2')                          # v1 = foto projetada (antiga) · v2 = cabeça modelada + textura pintada
    if UNIFORME == 'v1' or CABECA == 'v1':                           # o corpo fica só com o que aparece (pescoço da v1, antebraços da manga arregaçada)
        MANGA = MANGA if 'MANGA' in dir() else 9
        corpo_visivel(lambda f: (CABECA == 'v1' and REG[f.index] == 'pescoco') or (UNIFORME == 'v1' and dono(f).startswith('forearm') and abs(centro(f).x) > MANGA + .02 and REG[f.index] != 'luva'), 'e_pele')
    exec(open(os.path.join(AQUI, 'cabeca_entrada.py' if CABECA == 'v2' else 'cabeca_entrada_v1.py')).read())
    if UNIFORME == 'v2' and CABECA == 'v2': bpy.data.objects.remove(corpo)   # nada do corpo base aparece (manga longa, luvas, pescoço da cabeça)

if PERSONAGEM == 'oliveira':
    exec(open(os.path.join(AQUI, 'vestir_oliveira.py')).read())

if PERSONAGEM == 'luan':
    exec(open(os.path.join(AQUI, 'vestir_luan.py')).read())

if PERSONAGEM == 'corsa':
    CORSA = os.environ.get('CORSA', 'v2')                            # v1 = cabeça recortada da digitalização (antiga) · v2 = cabeça limpa + uniforme refeito
    exec(open(os.path.join(AQUI, 'vestir_corsa.py' if CORSA == 'v1' else 'vestir_corsa_v2.py')).read())

for o in list(bpy.data.objects):
    if o.name == 'head': bpy.data.objects.remove(o)
tris = {o.name: sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.type == 'MESH'}
print('TRIANGULOS', tris, 'total', sum(tris.values()))
for o in bpy.data.objects: o.select_set(o.type in ('MESH', 'ARMATURE'))
bpy.ops.export_scene.gltf(filepath=SAIDA, export_format='GLB', use_selection=True, export_skins=True, export_animations=False, export_apply=False)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=SAIDA_BLEND, compress=True)
print('PERSONAGEM OK', PERSONAGEM, SAIDA, SAIDA_BLEND)
