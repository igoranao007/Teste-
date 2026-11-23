# Gato Soldado (PSX) — modelado 100% em bmesh, peças segmentadas presas a ossos (rígido, estilo PS1).
# Uso: blender -b -P tools/blender/gato_soldado.py -- <pasta_saida>
# Saída: gato_soldado.blend, gato_soldado.glb, gato_soldado_128.png, render_34.png (320x240) + folha.
import bpy, bmesh, sys, os, math
from mathutils import Vector, Matrix

OUT = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "/tmp/gato"
os.makedirs(OUT, exist_ok=True)
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)

# ---------------------------------------------------------------- textura 128x128, paleta <= 32, Bayer 4x4
T = 128
PAL = {  # nome: (r,g,b) 0-255
 'preto': (10, 10, 12), 'pelo1': (26, 24, 30), 'pelo2': (44, 40, 50), 'pelo3': (66, 60, 72),
 'branco1': (178, 172, 168), 'branco2': (222, 218, 212), 'olho': (150, 108, 40), 'olho2': (86, 56, 22),
 'nariz': (120, 60, 70), 'lingua': (196, 70, 78), 'cer1': (150, 84, 62), 'cer2': (204, 132, 98),
 'cer3': (236, 178, 140), 'cer4': (96, 48, 40), 'verm1': (92, 14, 18), 'verm2': (150, 24, 28),
 'verm3': (196, 44, 42), 'verde1': (24, 64, 28), 'verde2': (46, 104, 44), 'verde3': (82, 140, 66),
 'bota1': (14, 14, 16), 'bota2': (40, 38, 40), 'couro': (58, 40, 26), 'metal': (150, 140, 110),
 'azul': (16, 56, 168), 'bandb': (236, 236, 236), 'cinza': (96, 92, 90),
}
assert len(PAL) <= 32
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
px = [[PAL['preto']] * T for _ in range(T)]

def mistura(x, y, a, b, f):  # pontilhado ordenado entre duas cores da paleta
    return PAL[b] if f * 16 > BAYER[y % 4][x % 4] + .5 else PAL[a]

def ruido(x, y, s=0):
    n = (x * 374761393 + y * 668265263 + s * 982451653) & 0xffffffff
    n = (n ^ (n >> 13)) * 1274126177 & 0xffffffff
    return (n & 0xffff) / 65535.0

# tiles (x0,y0,w,h) em pixels, origem embaixo-esquerda (como UV)
TILE = {'cabeca': (0, 64, 64, 64), 'cerebro': (64, 96, 32, 32), 'tronco': (0, 0, 64, 64),
        'manga': (64, 64, 32, 32), 'calca': (96, 64, 32, 32), 'luva': (64, 32, 16, 16),
        'bota': (80, 32, 16, 16), 'bandeira': (96, 32, 32, 24), 'orelha': (96, 96, 16, 16),
        'peito_gato': (112, 96, 16, 16), 'focinho': (96, 112, 16, 16), 'pelo': (112, 112, 16, 16), 'pescoco': (64, 48, 16, 16), 'cinto': (80, 48, 16, 16)}

def tile_pinta(nome, fn):
    x0, y0, w, h = TILE[nome]
    for j in range(h):
        for i in range(w):
            px[y0 + j][x0 + i] = fn(i, j, w, h, x0 + i, y0 + j)

def f_cabeca(i, j, w, h, X, Y):
    u, v = (i + .5) / w, (j + .5) / h            # u: 0..1 em volta (0,5 = frente), v: 0 embaixo
    du = (u - .5) * 2                             # -1..1 na frente
    base = mistura(X, Y, 'pelo1', 'pelo2', .25 + .3 * ruido(i // 2, j // 2, 1))
    # focinho e queixo brancos (o gato do meme tem a parte de baixo branca)
    if abs(du) < .34 - (v - .05) * .5 and v < .42:
        base = mistura(X, Y, 'branco1', 'branco2', .55)
    # mancha branca descendo do nariz
    if abs(du) < .06 and .34 < v < .48: base = mistura(X, Y, 'pelo2', 'branco1', .5)
    # nariz
    if abs(du) < .07 and .42 <= v < .5: base = PAL['nariz']
    # boca + língua
    if abs(du) < .09 and .26 < v < .32: base = PAL['preto']
    if abs(du) < .06 and .22 < v < .28: base = PAL['lingua']
    # olhos meio fechados, cor âmbar escura com pálpebra
    for c in (-.3, .3):
        dx, dy = (du - c) / .17, (v - .6) / .12
        if dx * dx + dy * dy < 1:
            base = PAL['olho2'] if dy < -.1 else PAL['olho']
            if abs(dx) < .18: base = PAL['preto']           # pupila em fenda
            if dy > .5: base = PAL['pelo1']                 # pálpebra pesada (olhar de "lavado")
            if -.6 < dx < -.3 and -.2 < dy < .2: base = PAL['branco2']  # brilho
    # topo da cabeça (perto do cérebro) mais escuro
    if v > .9: base = PAL['pelo1']
    return base

def f_cerebro(i, j, w, h, X, Y):
    u, v = i / w, j / h
    # dobras do cérebro: linhas onduladas
    d = math.sin(u * 22 + math.sin(v * 9) * 2.2) * math.sin(v * 18 + math.cos(u * 7) * 2)
    if abs(d) < .16: return PAL['cer4']
    f = .5 + .5 * math.sin(u * 13 + v * 5)
    c = mistura(X, Y, 'cer1', 'cer2', f)
    if ruido(i, j, 3) > .9: c = PAL['cer3']
    if abs(u - .5) < .03: c = PAL['cer4']           # fissura entre hemisférios
    return c

def f_tecido(base1, base2, base3):
    def f(i, j, w, h, X, Y):
        r = ruido(i // 2, j // 2, 7)
        c = mistura(X, Y, base1, base2, .55 + .35 * r)
        if r > .93: c = PAL[base3]
        if j < 2: c = PAL[base1]                     # bainha
        return c
    return f

def f_tronco(i, j, w, h, X, Y):
    u, v = (i + .5) / w, (j + .5) / h
    du = (u - .5) * 2
    c = f_tecido('verm1', 'verm2', 'verm3')(i, j, w, h, X, Y)
    if abs(du) < .03: c = PAL['verm1']                           # abertura da farda
    if abs(du) < .06 and int(v * 10) % 2 == 0 and v > .3 and abs(du) > .02: c = PAL['metal']  # botões
    for cx in (-.45, .45):                                        # bolsos do peito
        if abs(du - cx) < .18 and .62 < v < .78: c = mistura(X, Y, 'verm2', 'verm3', .4)
        if abs(du - cx) < .18 and .76 < v < .8: c = PAL['verm1']
    if .12 < v < .22: c = mistura(X, Y, 'bota1', 'bota2', .3)    # cinto preto
    if .12 < v < .22 and abs(du) < .1: c = PAL['metal']          # fivela
    if v > .94: c = PAL['verm1']                                   # gola
    # alça diagonal (bandoleira) só na frente
    if abs((du + .9) - (v - .2) * 1.6) < .1 and v > .22 and abs(du) < .95: c = PAL['couro']
    return c

def f_luva(i, j, w, h, X, Y):
    c = mistura(X, Y, 'verde1', 'verde2', .5 + .4 * ruido(i, j, 9))
    if j > h - 3: c = PAL['verde1']                                # punho
    if ruido(i, j, 4) > .94: c = PAL['verde3']
    return c

def f_bota(i, j, w, h, X, Y):
    c = mistura(X, Y, 'bota1', 'bota2', .25)
    if j < 2: c = PAL['cinza']                                     # sola
    if j > h - 3: c = PAL['bota2']
    return c

def f_bandeira(i, j, w, h, X, Y):   # Israel: fundo branco, 2 faixas azuis, estrela de Davi
    u, v = (i + .5) / w, (j + .5) / h
    if i == 0 or j == 0 or i == w - 1 or j == h - 1: return PAL['verm1']    # costura do patch
    c = PAL['bandb']
    if .1 < v < .24 or .76 < v < .9: c = PAL['azul']
    x, y = (u - .5) * w / h, v - .5
    def dentro_tri(x, y, r, inv):
        s = -1 if inv else 1
        y = y * s
        return y > -r / 2 and abs(x) < (r - y) / math.sqrt(3) and y < r
    r = .2
    a, b = dentro_tri(x, y, r, False), dentro_tri(x, y, r, True)
    a2, b2 = dentro_tri(x, y, r * .62, False), dentro_tri(x, y, r * .62, True)
    if (a or b) and not (a2 or b2): c = PAL['azul']
    return c

tile_pinta('cabeca', f_cabeca); tile_pinta('cerebro', f_cerebro); tile_pinta('tronco', f_tronco)
tile_pinta('manga', f_tecido('verm1', 'verm2', 'verm3')); tile_pinta('calca', f_tecido('verm1', 'verm2', 'verm1'))
tile_pinta('luva', f_luva); tile_pinta('bota', f_bota); tile_pinta('bandeira', f_bandeira)
tile_pinta('orelha', lambda i, j, w, h, X, Y: PAL['nariz'] if abs(i - w / 2) < (h - j) * .25 and j < h - 4 else mistura(X, Y, 'pelo1', 'pelo2', .3))
tile_pinta('peito_gato', lambda i, j, w, h, X, Y: mistura(X, Y, 'branco1', 'branco2', .5))
tile_pinta('pescoco', lambda i, j, w, h, X, Y: mistura(X, Y, 'pelo1', 'branco1', .5) if j > h * .5 else PAL['verm1'])
def f_focinho(i, j, w, h, X, Y):
    u, v = (i + .5) / w, (j + .5) / h
    c = mistura(X, Y, 'branco1', 'branco2', .55)
    if abs(u - .5) < .16 and v > .72: c = PAL['nariz']
    if abs(u - .5) < .05 and .45 < v <= .72: c = PAL['cinza']
    if abs(u - .5) < .3 and .38 < v < .46: c = PAL['cinza']
    if abs(u - .5) < .12 and .18 < v < .38: c = PAL['lingua']
    return c
tile_pinta('focinho', f_focinho)
tile_pinta('pelo', lambda i, j, w, h, X, Y: mistura(X, Y, 'pelo1', 'pelo2', .3))
tile_pinta('cinto', lambda i, j, w, h, X, Y: mistura(X, Y, 'bota1', 'bota2', .3))

img = bpy.data.images.new('gato_soldado_128', T, T, alpha=False)
flat = []
for y in range(T):
    for x in range(T):
        r, g, b = px[y][x]; flat += [r / 255, g / 255, b / 255, 1]
img.pixels = flat
img.filepath_raw = os.path.join(OUT, 'gato_soldado_128.png'); img.file_format = 'PNG'; img.save()
cores_usadas = {px[y][x] for y in range(T) for x in range(T)}
print('CORES NA TEXTURA:', len(cores_usadas))

# ---------------------------------------------------------------- material
mat = bpy.data.materials.new('gato_soldado'); mat.use_nodes = True
nt = mat.node_tree; P = nt.nodes['Principled BSDF']
P.inputs['Roughness'].default_value = 1.0
P.inputs['Specular IOR Level'].default_value = 0.0
tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = img; tx.interpolation = 'Closest'
vc = nt.nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'AO'
mu = nt.nodes.new('ShaderNodeMix'); mu.data_type = 'RGBA'; mu.blend_type = 'MULTIPLY'; mu.inputs['Factor'].default_value = 1.0
nt.links.new(tx.outputs['Color'], mu.inputs['A']); nt.links.new(vc.outputs['Color'], mu.inputs['B'])
nt.links.new(mu.outputs['Result'], P.inputs['Base Color'])

# ---------------------------------------------------------------- geometria (bmesh)
def uv_tile(nome, u, v):
    x0, y0, w, h = TILE[nome]
    e = .5  # meio pixel de margem pra não vazar entre tiles
    return Vector(((x0 + e + u * (w - 2 * e)) / T, (y0 + e + v * (h - 2 * e)) / T))

def prisma(bm, lados, aneis, tile, tampa_cima=True, tampa_baixo=True, tile_tampa=None, giro=0.0):
    """aneis: lista de (z, rx, ry, dx, dy). Prisma de 'lados' lados; UV cilíndrico com u=0,5 na frente (-Y)."""
    uv = bm.loops.layers.uv.verify()
    anel_v = []
    for (z, rx, ry, dx, dy) in aneis:
        vs = []
        for k in range(lados):
            a = -math.pi / 2 + 2 * math.pi * k / lados + giro   # k=0 -> frente (-Y)
            vs.append(bm.verts.new((dx + rx * math.cos(a), dy + ry * math.sin(a), z)))
        anel_v.append(vs)
    z0, z1 = aneis[0][0], aneis[-1][0]
    faces = []
    for r in range(len(aneis) - 1):
        for k in range(lados):
            k2 = (k + 1) % lados
            f = bm.faces.new((anel_v[r][k], anel_v[r][k2], anel_v[r + 1][k2], anel_v[r + 1][k]))
            # u em volta: frente (k=0) no meio do tile
            ua = ((k / lados) + .5) % 1.0; ub = ua + 1 / lados
            for l, (uu, rr) in zip(f.loops, ((ua, r), (ub, r), (ub, r + 1), (ua, r + 1))):
                vv = (aneis[rr][0] - z0) / (z1 - z0) if z1 != z0 else 0
                l[uv].uv = uv_tile(tile, uu, vv)
            faces.append(f)
    tt = tile_tampa or tile
    for vs, cima in ((anel_v[0], False), (anel_v[-1], True)):
        if (cima and not tampa_cima) or (not cima and not tampa_baixo): continue
        f = bm.faces.new(vs if cima else list(reversed(vs)))
        for l in f.loops:
            a = math.atan2(l.vert.co.y, l.vert.co.x)
            l[uv].uv = uv_tile(tt, .5 + .45 * math.cos(a), .5 + .45 * math.sin(a))
        faces.append(f)
    return faces

def caixa(bm, cx, cy, cz, sx, sy, sz, tile, cima_menor=1.0, tile_frente=None):
    uv = bm.loops.layers.uv.verify()
    m = cima_menor
    vs = [bm.verts.new((cx + x * sx / 2 * (m if z > 0 else 1), cy + y * sy / 2 * (m if z > 0 else 1), cz + z * sz / 2))
          for z in (-1, 1) for y in (-1, 1) for x in (-1, 1)]
    quads = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    for qi, q in enumerate(quads):
        f = bm.faces.new([vs[i] for i in q])
        tl = tile_frente if (qi == 2 and tile_frente) else tile
        uvs = ((0, 0), (0, 1), (1, 1), (1, 0)) if qi == 2 else ((0, 0), (1, 0), (1, 1), (0, 1))
        for l, (uu, vv) in zip(f.loops, uvs): l[uv].uv = uv_tile(tl, uu, vv)

def finaliza(bm, nome, origem, osso, escuro_baixo=.55, escuro_juntas=()):
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces: f.smooth = False
    # AO falso por vértice: escurece embaixo da peça e perto das juntas
    col = bm.loops.layers.color.new('AO')
    zs = [v.co.z for v in bm.verts]; zmin, zmax = min(zs), max(zs)
    for f in bm.faces:
        for l in f.loops:
            co = l.vert.co
            t = (co.z - zmin) / max(zmax - zmin, 1e-6)
            k = escuro_baixo + (1 - escuro_baixo) * min(1, t * 1.6)
            for (jz, raio, forca) in escuro_juntas:
                d = abs(co.z - jz)
                if d < raio: k *= 1 - forca * (1 - d / raio)
            l[col] = (k, k, k, 1)
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    me.materials.append(mat)
    ob = bpy.data.objects.new(nome, me); bpy.context.scene.collection.objects.link(ob)
    ob.location = origem
    ob['osso'] = osso
    return ob

pecas = []
# Medidas (m), personagem ~1,78 m até o topo do cérebro. Frente = -Y (Blender), sobe = +Z.
# --- CABEÇA (gato: larga e achatada, como no meme) + cérebro exposto no topo
bm = bmesh.new()
H = [(-.13, .06, .05, 0, -.01), (-.10, .13, .11, 0, -.01), (-.03, .165, .13, 0, -.02),
     (.05, .17, .135, 0, -.01), (.11, .145, .12, 0, 0)]
prisma(bm, 8, H, 'cabeca', tampa_cima=True, tile_tampa='pelo')
# cérebro: cúpula em cima, um pouco mais estreita que o crânio (o crânio "aberto")
C = [(.105, .13, .11, 0, .0), (.16, .118, .1, 0, .005), (.2, .075, .065, 0, .01), (.215, .0, .0, 0, .01)]
prisma(bm, 8, C, 'cerebro', tampa_cima=False, tampa_baixo=False)
# focinho
caixa(bm, 0, -.122, -.06, .12, .045, .07, 'peito_gato', .85, tile_frente='focinho')
# orelhas (pirâmides achatadas, saindo dos lados do topo, inclinadas pra fora)
uvl = bm.loops.layers.uv.verify()
for s in (-1, 1):
    b0 = Vector((s * .08, -.04, .1)); b1 = Vector((s * .17, -.02, .06)); b2 = Vector((s * .13, .06, .09)); tp = Vector((s * .23, .0, .25))
    vb = [bm.verts.new(p) for p in (b0, b1, b2, tp)]
    for tri, uvs in (((0, 1, 3), ((0, 0), (1, 0), (.5, 1))), ((1, 2, 3), ((0, 0), (1, 0), (.5, 1))),
                     ((2, 0, 3), ((0, 0), (1, 0), (.5, 1))), ((0, 2, 1), ((0, 0), (1, 0), (.5, .5)))):
        f = bm.faces.new([vb[i] for i in tri])
        for l, (uu, vv) in zip(f.loops, uvs): l[uvl].uv = uv_tile('orelha', uu, vv)
bmesh.ops.scale(bm, vec=(1.15, 1.15, 1.15), verts=bm.verts)   # cabeça de gato grande, como no meme
pecas.append(finaliza(bm, 'cabeca', (0, 0, 1.58), 'Head', .6, ((.11, .03, .35),)))

# --- PESCOÇO
bm = bmesh.new(); prisma(bm, 6, [(-.06, .055, .05, 0, 0), (.05, .06, .055, 0, 0)], 'pescoco', False, False)
pecas.append(finaliza(bm, 'pescoco', (0, 0, 1.46), 'Neck', .5))

# --- TRONCO (farda vermelha) e QUADRIL
bm = bmesh.new()
prisma(bm, 6, [(-.27, .165, .11, 0, 0), (-.05, .175, .115, 0, 0), (.13, .215, .125, 0, -.005), (.21, .17, .11, 0, 0), (.25, .1, .08, 0, 0)],
       'tronco', tile_tampa='verm1' if False else 'manga')
pecas.append(finaliza(bm, 'tronco', (0, 0, 1.2), 'Spine', .55, ((-.27, .05, .3),)))
bm = bmesh.new(); caixa(bm, 0, 0, 0, .3, .2, .14, 'calca', .95)
pecas.append(finaliza(bm, 'quadril', (0, 0, .9), 'Hips', .5))

# --- BRAÇOS (lado do personagem: Left = +X no Blender com frente -Y)
for lado, s in (('Left', 1), ('Right', -1)):
    bm = bmesh.new(); prisma(bm, 6, [(-.29, .055, .055, 0, 0), (0, .07, .068, 0, 0)], 'manga')
    if lado == 'Left':   # bandeira de Israel: patch no braço esquerdo, de fora, perto do ombro
        uvb = bm.loops.layers.uv.verify()
        z0, z1, y0, y1, x = -.14, -.06, -.05, .05, .0715
        vs = [bm.verts.new((x, y, z)) for (y, z) in ((y1, z0), (y0, z0), (y0, z1), (y1, z1))]
        f = bm.faces.new(vs)
        for l, (uu, vv) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): l[uvb].uv = uv_tile('bandeira', uu, vv)
    pecas.append(finaliza(bm, f'braco_{lado}', (s * .245, 0, 1.39), f'{lado}UpperArm', .6, ((0, .04, .3),)))
    bm = bmesh.new(); prisma(bm, 6, [(-.26, .048, .046, 0, 0), (0, .058, .056, 0, 0)], 'manga')
    pecas.append(finaliza(bm, f'antebraco_{lado}', (s * .245, 0, 1.1), f'{lado}LowerArm', .6, ((0, .04, .35),)))
    bm = bmesh.new()
    caixa(bm, 0, -.005, -.07, .075, .12, .15, 'luva', 1.0)                       # palma + dedos (luva)
    caixa(bm, s * -.01, -.07, -.04, .035, .04, .07, 'luva', .9)                     # polegar pra frente
    pecas.append(finaliza(bm, f'mao_{lado}', (s * .245, 0, .84), f'{lado}Hand', .7))

# --- PERNAS
for lado, s in (('Left', 1), ('Right', -1)):
    bm = bmesh.new(); prisma(bm, 6, [(-.42, .07, .072, 0, 0), (0, .1, .105, 0, 0)], 'calca')
    pecas.append(finaliza(bm, f'coxa_{lado}', (s * .095, 0, .9), f'{lado}UpperLeg', .6, ((0, .05, .3),)))
    bm = bmesh.new(); prisma(bm, 6, [(-.36, .058, .058, 0, 0), (0, .072, .074, 0, 0)], 'calca')
    pecas.append(finaliza(bm, f'canela_{lado}', (s * .095, 0, .48), f'{lado}LowerLeg', .6, ((0, .05, .3),)))
    bm = bmesh.new()
    caixa(bm, 0, .0, .065, .12, .14, .13, 'bota', .92)              # cano da bota
    caixa(bm, 0, -.1, .035, .115, .14, .07, 'bota', .9)            # bico
    pecas.append(finaliza(bm, f'bota_{lado}', (s * .095, 0, .0), f'{lado}Foot', .5))

tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in pecas)
print('TRIANGULOS TOTAL:', tris)
for o in pecas: print(f'  {o.name:16s} {sum(len(p.vertices) - 2 for p in o.data.polygons)}')

# ---------------------------------------------------------------- esqueleto + peças presas a ossos (rígido)
arm_d = bpy.data.armatures.new('rig'); arm = bpy.data.objects.new('rig', arm_d); bpy.context.scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode='EDIT')
OS = {'Hips': ((0, 0, .9), (0, 0, 1.0), None), 'Spine': ((0, 0, 1.0), (0, 0, 1.4), 'Hips'),
      'Neck': ((0, 0, 1.4), (0, 0, 1.5), 'Spine'), 'Head': ((0, 0, 1.5), (0, 0, 1.75), 'Neck')}
for lado, s in (('Left', 1), ('Right', -1)):
    OS[f'{lado}UpperArm'] = ((s * .245, 0, 1.39), (s * .245, 0, 1.1), 'Spine')
    OS[f'{lado}LowerArm'] = ((s * .245, 0, 1.1), (s * .245, 0, .84), f'{lado}UpperArm')
    OS[f'{lado}Hand'] = ((s * .245, 0, .84), (s * .245, 0, .74), f'{lado}LowerArm')
    OS[f'{lado}UpperLeg'] = ((s * .095, 0, .9), (s * .095, 0, .48), 'Hips')
    OS[f'{lado}LowerLeg'] = ((s * .095, 0, .48), (s * .095, 0, .1), f'{lado}UpperLeg')
    OS[f'{lado}Foot'] = ((s * .095, 0, .1), (s * .095, -.15, .02), f'{lado}LowerLeg')
for n, (h, t, p) in OS.items():
    b = arm_d.edit_bones.new(n); b.head, b.tail = h, t
    if p: b.parent = arm_d.edit_bones[p]; b.use_connect = False
bpy.ops.object.mode_set(mode='OBJECT')
for o in pecas:
    mw = o.matrix_world.copy(); o.parent = arm; o.parent_type = 'BONE'; o.parent_bone = o['osso']
    bpy.context.view_layer.update(); o.matrix_world = mw

# pose de inspeção levemente relaxada (braços um pouco abertos)
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode='POSE')
pb = arm.pose.bones
for lado, s in (('Left', 1), ('Right', -1)):
    pb[f'{lado}UpperArm'].rotation_mode = 'XYZ'; pb[f'{lado}UpperArm'].rotation_euler = (0, 0, 0)
bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'gato_soldado.blend'))
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, 'gato_soldado.glb'), export_format='GLB')

# ---------------------------------------------------------------- verificação: 3/4 em 320x240 + folha
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 16; sc.cycles.device = 'CPU'; sc.cycles.use_denoising = False
sc.view_settings.view_transform = 'Standard'
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Color'].default_value = (.12, .1, .2, 1); w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.2
sol = bpy.data.objects.new('sol', bpy.data.lights.new('sol', 'SUN')); sol.data.energy = 2.5; sol.rotation_euler = (.8, 0, -.6); sc.collection.objects.link(sol)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
def foto(n, p, a, l=50, w=320, h=240):
    cam.location = p; cam.rotation_euler = (Vector(a) - Vector(p)).to_track_quat('-Z', 'Y').to_euler(); cam.data.lens = l
    sc.render.resolution_x, sc.render.resolution_y = w, h; sc.render.filepath = os.path.join(OUT, n + '.png'); bpy.ops.render.render(write_still=True)
foto('render_34', (2.6, -3.4, 1.6), (0, 0, .92), 40)
foto('frente', (0, -3.6, 1.0), (0, 0, .92), 40, 480, 640)
foto('costas', (0, 3.6, 1.0), (0, 0, .92), 40, 480, 640)
foto('perfil_esq', (3.6, 0, 1.0), (0, 0, .92), 40, 480, 640)
foto('rosto', (.35, -.9, 1.66), (0, 0, 1.6), 50, 480, 480)
foto('bandeira', (.95, -.35, 1.3), (.245, 0, 1.3), 50, 480, 480)
print('GATO OK')
