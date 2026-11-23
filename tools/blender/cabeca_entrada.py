# CABEÇA da ENTRADA v2 (executado dentro do vestir_personagem.py). A malha e a textura vêm do tools/entrada_cabeca.py
# (cabeça com nariz, olhos, boca, maçãs, mandíbula e orelhas modelados; textura única pintada; cabelo com volume).
# Aqui só se monta no Blender: cabeça+pescoço+orelhas num objeto, cabelo noutro, pesos no pescoço/cabeça.
TEXD = os.path.join(RAIZ, 'material/producao/personagens/entrada/texturas')
def img_png(n): i = bpy.data.images.load(os.path.join(TEXD, n)); i.pack(); return i
material('e_rosto', img_png('rosto_v2.png'), repete=False)
material('e_cabelo', img_png('cabelo_v2.png'))
CJ = json.load(open(os.path.join(TEXD, 'cabeca.json')))
def peca_json(nome, i0, i1, mats, mat_de):
    bm = bmesh.new(); uvl = bm.loops.layers.uv.verify(); mapa = {}
    for i in range(i0, i1):
        f = CJ['f'][i]
        for v in f:
            if v not in mapa: mapa[v] = bm.verts.new(MWi @ Vector(CJ['v'][v]))
        try: face = bm.faces.new([mapa[v] for v in f])
        except ValueError: continue
        face.material_index = mat_de(CJ['mat'][i])
        for l, uv in zip(face.loops, CJ['uv'][i]): l[uvl].uv = uv
    bm.normal_update(); bm.verts.index_update(); inv = {b.index: k for k, b in mapa.items()}
    ob = objeto(bm, nome, mats, mat_de=lambda f: f.material_index, uv=False)
    for v in ob.data.vertices:                                   # pesos vindos do json (pescoço dividido entre pescoço e cabeça)
        for osso_, w in CJ['peso'][inv[v.index]].items(): ob.vertex_groups[osso_].add([v.index], w, 'REPLACE')
    return ob
a, b = CJ['pecas']['cabeca']; cabeca = peca_json('cabeca', a, b, ['e_rosto'], lambda m: 0)
a, b = CJ['pecas']['cabelo']; cabelo = peca_json('cabelo', a, b, ['e_cabelo'], lambda m: 0)
for m in MATS.values(): m.use_backface_culling = True
