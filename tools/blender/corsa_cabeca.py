# CABEÇA DO CORSA v2 — cabeça de pardal LIMPA a partir da digitalização "22_23 House Sparrow.glb" (o arquivo original não é alterado).
# Uso: PARDAL_GLB=<glb original> blender -b -P tools/blender/corsa_cabeca.py -- <pasta de saída>
# 1) a digitalização é de um pardal MERGULHANDO em voo (cabeça pra baixo): gira a ave inteira até a cabeça ficar de pé
#    (bico pra frente/-Y, coroa pra cima) — conferido nos renders de inspeção;
# 2) malha nova low-poly: anéis ao longo do eixo nuca→bico, cada vértice colocado por RAIO na superfície da digitalização
#    (o crânio, as bochechas e a silhueta são os do pardal); o bico é um cone com ponta firme medido na digitalização;
# 3) UV novo com UMA ilha (cilíndrico em volta do eixo do bico, emenda embaixo da garganta) e as CORES da textura original de
#    1024 px transferidas ponto a ponto (ponto mais próximo na digitalização → UV original → cor). Nada de 308 ilhas misturadas;
# 4) olhos: domos pretos brilhantes no lugar dos olhos do pardal.
# Saída: cabeca_corsa.json (malha em coordenadas da CABEÇA, em metros da ave) + pardal_cabeca.png (256 px).
import bpy, bmesh, sys, math, json, os
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
SCAN = os.environ['PARDAL_GLB']; OUT = sys.argv[sys.argv.index('--') + 1]
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=SCAN)
o = [o for o in bpy.data.objects if o.type == 'MESH'][0]; PM = o.matrix_world.copy()
img = [n.image for n in o.data.materials[0].node_tree.nodes if n.type == 'TEX_IMAGE' and n.image.name == 'Image_0'][0]
IW, IH = img.size; TEX = np.array(img.pixels[:], dtype=np.float32).reshape(IH, IW, 4)[..., :3]
# ---- orientação: centro da cabeça (média do recorte antigo) e giro em X que põe a cabeça de pé (medido nos renders)
B0 = Vector((-.0171, -.0284, -.0223)); N0 = Vector((-.013, -.045, -.002)); EX = (N0 - B0).normalized()
def no_cilindro(p): t = (p - B0).dot(EX); r = ((p - B0) - EX * t).length; return -.004 <= t <= .036 and r <= .016 * (.55 + .45 * min(1, t / .012))
pts = [PM @ v.co for v in o.data.vertices]; dentro = [p for p in pts if no_cilindro(p)]
CEN = sum(dentro, Vector()) / len(dentro)
R = Matrix.Rotation(math.radians(-19.3), 3, 'X')
bm = bmesh.new(); bm.from_mesh(o.data)
for v in bm.verts: v.co = R @ (PM @ v.co - CEN)
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
uvl = bm.loops.layers.uv.active
bmesh.ops.triangulate(bm, faces=bm.faces[:]); bm.faces.ensure_lookup_table()
BVH = BVHTree.FromBMesh(bm)
def cor_em(p):                                                     # cor da digitalização no ponto mais próximo da superfície
    loc, nor, i, d = BVH.find_nearest(Vector(p))
    if i is None: return None
    f = bm.faces[i]; a, b, c = [l.vert.co for l in f.loops]
    v0, v1, v2 = b - a, c - a, loc - a; d00, d01, d11, d20, d21 = v0.dot(v0), v0.dot(v1), v1.dot(v1), v2.dot(v0), v2.dot(v1)
    den = d00 * d11 - d01 * d01 or 1e-12; w1 = (d11 * d20 - d01 * d21) / den; w2 = (d00 * d21 - d01 * d20) / den; w0 = 1 - w1 - w2
    uv = f.loops[0][uvl].uv * w0 + f.loops[1][uvl].uv * w1 + f.loops[2][uvl].uv * w2
    x, y = uv.x * (IW - 1), uv.y * (IH - 1); x0, y0 = int(x), int(y); x1, y1 = min(x0 + 1, IW - 1), min(y0 + 1, IH - 1); fx, fy = x - x0, y - y0
    return TEX[y0, x0] * (1 - fx) * (1 - fy) + TEX[y0, x1] * fx * (1 - fy) + TEX[y1, x0] * (1 - fx) * fy + TEX[y1, x1] * fx * fy
def raio(orig, d, maxd):
    loc, nor, i, dist = BVH.ray_cast(Vector(orig), Vector(d).normalized(), maxd)
    return dist if loc is not None else None
# ---- marcos: ponta do bico (o ponto mais à frente perto do eixo), fundo e topo da cabeça
melhor = None
for z in np.linspace(-.004, .006, 21):
    for x in np.linspace(-.0015, .0015, 7):
        d = raio((x, -.05, z), (0, 1, 0), .1)
        if d is not None and (melhor is None or -.05 + d < melhor[1]): melhor = (x, -.05 + d, z)
TIPX, TIPY, TIPZ = melhor; print('ponta do bico', [round(c, 4) for c in melhor])
dtr = raio((0, 0, 0), (0, 1, 0), .03); YBACK = min(dtr, .0105) if dtr else .0095
print('nuca em y', round(YBACK, 4))
# ---- estações (anéis) ao longo de y: bico (cone) → rosto → crânio → nuca
NA = 16                                                            # vértices por anel (φ = 0 em cima, gira pro lado +X)
FI = [2 * math.pi * k / NA for k in range(NA)]
BICO_L = .0105                                                     # comprimento do bico (pardal-doméstico ≈ 1 cm)
EST = [('bico1', TIPY + .0028), ('bico2', TIPY + .0062), ('base', TIPY + BICO_L), ('rosto', TIPY + BICO_L + .0025),
       ('olho', .001), ('cranio', .0045), ('tras', .0075), ('nuca', .0088)]
def eixo_z(y):                                                     # o eixo sobe do bico (TIPZ) pro centro do crânio (z = 0)
    t = min(1, max(0, (y - TIPY) / (BICO_L + .004))); return TIPZ * (1 - t) + 0.0 * t
def limite(nome, fi):                                              # raio máximo (onde a digitalização "continua" pro pescoço/corpo)
    cima = math.cos(fi); return {'bico1': .0022, 'bico2': .0038, 'base': .0062, 'nuca': .0055}.get(nome, .0115 if cima > -.3 else .0105)
V, F, UV, MAT = [], [], [], []
aneis = []
for nome, y in EST:
    zc = eixo_z(y); anel = []
    for fi in FI:
        d = (math.sin(fi), 0, math.cos(fi)); r = raio((TIPX * 0, y, zc), d, .03); lim = limite(nome, fi)
        if r is None or r > lim: r = lim * (.92 if nome not in ('bico1', 'bico2', 'base') else 1)
        V.append((math.sin(fi) * r, y, zc + math.cos(fi) * r)); anel.append(len(V) - 1)
    aneis.append(anel)
V.append((TIPX * 0, TIPY, TIPZ)); iponta = len(V) - 1
V.append((0, YBACK, .001)); inuca = len(V) - 1
# u: ângulo em volta do eixo (emenda embaixo: φ = π) · v: distância ao longo do eixo (ponta = 0, nuca = 1)
ys = [TIPY] + [y for _, y in EST] + [YBACK]
def v_de(y): return .03 + .94 * (y - TIPY) / (YBACK - TIPY)
def u_de(k, mais=False): fi = (FI[k] if not mais else 2 * math.pi); return ((fi + math.pi) % (2 * math.pi)) / (2 * math.pi) if not mais else .5
def uk(k): return (k / NA + .5) % 1.0                              # φ=0 (cima) no meio da textura; emenda embaixo
for j in range(len(EST) - 1):
    for k in range(NA):
        k2 = (k + 1) % NA; a, b, c, d = aneis[j][k], aneis[j][k2], aneis[j + 1][k2], aneis[j + 1][k]
        u0, u1 = uk(k), uk(k) + 1 / NA
        F.append([a, d, c, b]); MAT.append(0)
        UV.append([(u0, v_de(EST[j][1])), (u0, v_de(EST[j + 1][1])), (u1, v_de(EST[j + 1][1])), (u1, v_de(EST[j][1]))])
for k in range(NA):
    k2 = (k + 1) % NA; u0, u1 = uk(k), uk(k) + 1 / NA
    F.append([iponta, aneis[0][k], aneis[0][k2]][::-1]); MAT.append(0); UV.append([((u0 + u1) / 2, .01), (u0, v_de(EST[0][1])), (u1, v_de(EST[0][1]))][::-1])
    F.append([aneis[-1][k], inuca, aneis[-1][k2]][::-1]); MAT.append(0); UV.append([(u0, v_de(EST[-1][1])), ((u0 + u1) / 2, .99), (u1, v_de(EST[-1][1]))][::-1])
VA = np.array(V)
def nface(f):
    p = VA[f]; n = np.zeros(3)
    for k in range(len(p)): n += np.cross(p[k], p[(k + 1) % len(p)])
    return n
cen_eixo = lambda c: np.array([0, c[1], eixo_z(c[1])])
for i, f in enumerate(F):                                           # cada face com a frente pra fora (em relação ao eixo do bico)
    if np.dot(nface(f), VA[f].mean(0) - cen_eixo(VA[f].mean(0))) < 0: F[i] = f[::-1]; UV[i] = UV[i][::-1]
print('faces viradas pra dentro (depois de acertar):', sum(1 for f in F if np.dot(nface(f), VA[f].mean(0) - cen_eixo(VA[f].mean(0))) < 0), 'de', len(F))
# ---- olhos: o olho do pardal na digitalização é escuro e AZULADO (brilho do globo); a mancha preta entre o olho e o bico (loro)
# é escura mas marrom. Mede do lado +X (o olho do lado -X está danificado na digitalização) e espelha.
cand = []
for y in np.linspace(TIPY + BICO_L - .001, .006, 22):
    for z in np.linspace(-.003, .005, 18):
        d = raio((0, y, z), (1, 0, 0), .03)
        if d is None or d > .012: continue
        p = (d, y, z); c = cor_em(p)
        if c is not None and c.mean() < .06 and c[2] > c[0] * 1.15: cand.append(p)
OC = np.mean(np.array(cand), 0) if cand else np.array([.0071, .0036, 0.0])
print('olho (azulado):', len(cand), 'pontos, centro', OC.round(4))
OLHOS = [tuple(OC), (-OC[0], OC[1], OC[2])]
for s, oc in zip((1, -1), OLHOS):                                  # domo do olho: 8 lados, saindo da superfície
    c = np.array(oc); n = np.array([s, 0, 0.0]); r = .0017; base = len(V)
    V.append(tuple(c + n * .0011)); topo = base
    for k in range(8):
        a = 2 * math.pi * k / 8; q = c + n * .0002 + np.array([0, math.cos(a), math.sin(a)]) * r; V.append(tuple(q))
    for k in range(8):
        f = [topo, base + 1 + k, base + 1 + (k + 1) % 8]
        p_ = np.array([V[i] for i in f]); nn = np.cross(p_[1] - p_[0], p_[2] - p_[0])
        if np.dot(nn, n) < 0: f = f[::-1]
        F.append(f); MAT.append(1); UV.append([(.5, .5), (.1, .1), (.2, .1)] if f[0] == topo else [(.1, .1), (.5, .5), (.2, .1)])
VA = np.array(V)
# ---- textura: rasteriza o UV em 512, cada texel → ponto da malha nova → cor da digitalização; reduz pra 256
TR = 512; pos = np.zeros((TR, TR, 3)); tem = np.zeros((TR, TR), bool)
for i, f in enumerate(F):
    if MAT[i] != 0: continue
    uvs = UV[i]
    for k in range(1, len(f) - 1):
        tri = [0, k, k + 1]; P = np.array([uvs[t] for t in tri]) * TR; P[:, 1] = TR - P[:, 1]
        x0, y0 = np.floor(P.min(0)).astype(int); x1, y1 = np.ceil(P.max(0)).astype(int)
        xs, ys_ = np.meshgrid(np.arange(max(x0, 0), min(x1, TR - 1) + 1) + .5, np.arange(max(y0, 0), min(y1, TR - 1) + 1) + .5)
        dd = (P[1, 1] - P[2, 1]) * (P[0, 0] - P[2, 0]) + (P[2, 0] - P[1, 0]) * (P[0, 1] - P[2, 1])
        if abs(dd) < 1e-9: continue
        l1 = ((P[1, 1] - P[2, 1]) * (xs - P[2, 0]) + (P[2, 0] - P[1, 0]) * (ys_ - P[2, 1])) / dd
        l2 = ((P[2, 1] - P[0, 1]) * (xs - P[2, 0]) + (P[0, 0] - P[2, 0]) * (ys_ - P[2, 1])) / dd
        l3 = 1 - l1 - l2; m = (l1 >= -.02) & (l2 >= -.02) & (l3 >= -.02)
        if not m.any(): continue
        L3 = np.stack([l1, l2, l3], -1)[m]; X = (xs[m] - .5).astype(int); Y = (ys_[m] - .5).astype(int)
        pos[Y, X] = L3 @ VA[[f[t] for t in tri]]; tem[Y, X] = True
cor = np.zeros((TR, TR, 3), np.float32)
for Y, X in zip(*np.nonzero(tem)):
    c = cor_em(pos[Y, X]); cor[Y, X] = c if c is not None else (.3, .25, .2)
# nuca: a digitalização não tem nuca própria (continua pras costas da ave) → a plumagem do alto/trás do crânio segue pra trás
r0 = int(TR - v_de(.0045) * TR); rng = np.random.default_rng(5)
topo_c = cor[r0, int(TR * .3):int(TR * .7)][tem[r0, int(TR * .3):int(TR * .7)]].mean(0)       # cor do alto da cabeça (marrom)
for r in range(0, r0):
    t = (r / r0) ** 1.5                                               # t = 1 logo atrás do crânio, 0 no fundo da nuca
    alvo = cor[r0] * t + topo_c * (1 - t)
    ruido = .9 + .2 * rng.random((TR, 1)) * (1 + .5 * (np.arange(TR)[:, None] % 3 == 0))
    alvo = (alvo + np.roll(alvo, 6, 0) + np.roll(alvo, -6, 0) + np.roll(alvo, 12, 0) + np.roll(alvo, -12, 0)) / 5 * (1 - t) + alvo * t   # suaviza em volta (sem riscos)
    cor[r] = np.where(tem[r][:, None], alvo * ruido, cor[r])
viva = cor[tem]; lum = viva.mean()
GANHO = min(1.6, .42 / max(lum, 1e-3)); print('luminância média da digitalização', round(float(lum), 3), 'ganho', round(GANHO, 2))
cor = np.clip(cor * GANHO, 0, 1) ** .95                           # a digitalização é escura (luz do estúdio): só um ganho global, sem mexer no tom
c8 = (cor * 255).astype(np.float32)
# reduz pra 256 com média e preenche fora da ilha (sem puxar preto)
pre = c8.reshape(256, 2, 256, 2, 3).mean((1, 3)); m2 = tem.reshape(256, 2, 256, 2).mean((1, 3))
pre = np.where(m2[..., None] > 0, pre / np.maximum(m2[..., None], 1e-6) * 1, 0); ok = m2 > 0
for _ in range(24):
    viz = np.zeros_like(pre); cnt = np.zeros(ok.shape)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        viz += np.roll(np.roll(pre * ok[..., None], dy, 0), dx, 1); cnt += np.roll(np.roll(ok, dy, 0), dx, 1)
    novo = (~ok) & (cnt > 0); pre[novo] = viz[novo] / cnt[novo][:, None]; ok = ok | novo
BAY = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 - .47
q = np.clip(np.floor(pre / 8 + .5 + np.tile(BAY, (64, 64))[..., None]) * 8, 0, 255).astype(np.uint8)
im = bpy.data.images.new('pardal_cabeca', 256, 256, alpha=False)
px = np.ones((256, 256, 4), np.float32); px[..., :3] = q[::-1] / 255; im.pixels.foreach_set(px.ravel())
im.filepath_raw = os.path.join(OUT, 'pardal_cabeca.png'); im.file_format = 'PNG'; im.save()
# cor média da garganta (frente, embaixo) e da nuca (atrás, embaixo) pro pescoço
def media(p_list): cs = [cor_em(p) for p in p_list]; cs = [c for c in cs if c is not None]; return (np.clip(np.mean(cs, 0) * GANHO, 0, 1) ** .95 * 255).round().tolist()
garganta = media([(x, y, -.0085) for x in (-.002, 0, .002) for y in (-.006, -.004, -.002)])
nuca = media([(x, .006, -.005) for x in (-.002, 0, .002)])
print('garganta', garganta, 'nuca', nuca)
json.dump({'v': VA.round(6).tolist(), 'f': F, 'uv': UV, 'mat': MAT, 'garganta': garganta, 'nuca': nuca,
           'ponta': [TIPX, TIPY, TIPZ], 'nuca_y': YBACK}, open(os.path.join(OUT, 'cabeca_corsa.json'), 'w'))
print('CABEÇA CORSA: faces', len(F), 'tri', sum(len(f) - 2 for f in F))
