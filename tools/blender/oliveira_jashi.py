"""OLIVEIRA v2 — aliado do DOM — sobre o Simple PSX Character (JashiPSX), depois do montar_jashi.py (textura ROUPA=oliveira).
Cabeça e pescoço do GODZILLA ("PlayStation 3 - Godzilla - Heisei Godzilla" by Mathzilla5335, Sketchfab, CC BY 4.0; personagem © Toho,
uso fan-made) com ~3.500 tri, UV novo (projeção inteligente) e textura 512 transferida da original de 2048; pescoço afinado e encaixado
no centro do gorjal, cabeça em cima dos ombros.
ARMADURA do DOM feita de PLACAS CURVAS que seguem a anatomia: cada placa é medida por raios saindo do eixo do osso até a pele
(r(θ, t) + folga), com bojo, espessura, chanfro, rebites e sulcos de energia amarela (material '*brilho*' = luz própria no motor).
Placas em camadas (lâminas sobrepostas) presas 100% no osso de cada parte (como armadura de verdade: não estica nas animações).
Uso: blender -b oliveira_base.blend --python oliveira_jashi.py -- saida.blend"""
import bpy, bmesh, sys, math, os, random
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
OUT = sys.argv[sys.argv.index('--') + 1]
RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
OD = os.path.join(RAIZ, 'material/producao/personagens/oliveira')
A = bpy.data.objects['simple_character']
random.seed(7)
def interp(pts, v):
    if v <= pts[0][0]: return pts[0][1]
    for (a, fa), (b, fb) in zip(pts, pts[1:]):
        if v <= b: return fa + (fb - fa) * (v - a) / (b - a)
    return pts[-1][1]
def ss(a, b, v): t = max(0.0, min(1.0, (v - a) / (b - a))); return t * t * (3 - 2 * t)
def osso(n): return A.matrix_world @ A.data.bones[n].head_local

# ================================================================ 1) corpo mais forte (sem a cabeça humana)
bpy.data.objects.remove(bpy.data.objects['head'])
B, AR = bpy.data.objects['body'], bpy.data.objects['arms']
def forte_corpo(o):
    mw = o.matrix_world; inv = mw.inverted()
    for v in o.data.vertices:
        w = mw @ v.co; x, y, z = w
        if z > 0.95:
            r = math.hypot(x, y - 0.01); kp = 1 - ss(0.08, 0.15, r)
            sx = interp([(0.95, 1.04), (1.1, 0.98), (1.25, 1.04), (1.45, 1.22), (1.6, 1.22), (1.75, 1.0)], z) * (1 - kp) + 1.15 * kp   # V: peito largo, cintura fina
            sy = interp([(0.95, 1.02), (1.15, 0.98), (1.35, 1.10), (1.5, 1.2), (1.75, 1.0)], z) * (1 - kp) + 1.15 * kp
            nw = Vector((x * sx, 0.01 + (y - 0.01) * sy, z))
        else:
            c = 0.153 if x > 0 else -0.153; f = interp([(0.1, 1.08), (0.5, 1.12), (0.9, 1.16)], z)
            nw = Vector((c + (x - c) * f, 0.02 + (y - 0.02) * f, z))
            k = ss(0.86, 0.95, z); nw = nw * (1 - k) + Vector((x * 1.10, 0.01 + (y - 0.01) * 1.08, z)) * k; nw.z = z
        v.co = inv @ nw
EIXO_B = [(0.20, Vector((0.20, 0.039, 1.610))), (0.223, Vector((0.223, 0.039, 1.607))), (0.451, Vector((0.451, 0.039, 1.561))), (0.80, Vector((0.80, -0.01, 1.533))), (1.1, Vector((1.1, -0.03, 1.52)))]
def eixo_braco(ax):
    for (a, pa), (b, pb) in zip(EIXO_B, EIXO_B[1:]):
        if ax <= b: return pa.lerp(pb, max(0.0, (ax - a) / (b - a)))
    return EIXO_B[-1][1]
def forte_bracos(o):
    mw = o.matrix_world; inv = mw.inverted()
    for v in o.data.vertices:
        w = mw @ v.co; s = 1 if w.x > 0 else -1; e = eixo_braco(abs(w.x)); e = Vector((s * e.x, e.y, e.z))
        f = interp([(0.2, 1.12), (0.3, 1.22), (0.45, 1.18), (0.62, 1.2), (0.78, 1.12), (0.9, 1.08)], abs(w.x))
        v.co = inv @ Vector((w.x, e.y + (w.y - e.y) * f, e.z + (w.z - e.z) * f))
forte_corpo(B); forte_bracos(AR)

# ================================================================ materiais
def lin(c): return tuple((v / 255) ** 2.2 for v in c) + (1,)
def mat_tex(nome, arq):
    m = bpy.data.materials.new(nome); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    ti = nt.nodes.new('ShaderNodeTexImage'); ti.image = bpy.data.images.load(arq); ti.image.pack(); ti.interpolation = 'Closest'
    nt.links.new(ti.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = 0.7; nt.nodes.active = ti
    m.diffuse_color = (0.05, 0.05, 0.055, 1); return m
def mat_cor(nome, rgb, brilho=False):
    m = bpy.data.materials.new(nome); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    c = tuple((v / 255) ** (1.0 if brilho else 2.2) for v in rgb) + (1,)
    b.inputs['Base Color'].default_value = c; m.diffuse_color = c
    if brilho: b.inputs['Emission Color'].default_value = c; b.inputs['Emission Strength'].default_value = 2.0
    return m
TX = os.path.join(OD, 'texturas/')
M_PL = mat_tex('o_placa', TX + 'placa.png')          # 0 placa
M_BR = mat_cor('o_linha_brilho', (255, 206, 30), True)  # 1 energia
M_MT = mat_tex('o_metal', TX + 'metal.png')          # 2 metal (rebites, engrenagens, canos)
M_PL2 = mat_tex('o_placa2', TX + 'placa2.png')       # 3 placa com painéis (peças grandes)
M_TC = mat_tex('o_tecido', TX + 'tecido.png')        # 4 tecido do tabardo
M_NU = mat_cor('o_nucleo_brilho', (255, 238, 150), True)  # 5 núcleo do reator / olhos
MATS = [M_PL, M_BR, M_MT, M_PL2, M_TC, M_NU]

# ================================================================ BVH da pele (corpo + braços já engordados, pose de descanso)
def bvh_de(objs):
    bm = bmesh.new()
    for o in objs:
        t = bmesh.new(); t.from_mesh(o.data); t.transform(o.matrix_world); me = bpy.data.meshes.new('t'); t.to_mesh(me); t.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
    return BVHTree.FromBMesh(bm), bm
PELE, _bm_pele = bvh_de([B, AR])

# ================================================================ acumuladores por osso
GRUPOS = {}   # nome_osso -> bmesh
def acum(osso_):
    if osso_ not in GRUPOS:
        bm = bmesh.new(); bm.loops.layers.uv.new('UVMap'); GRUPOS[osso_] = bm
    return GRUPOS[osso_]
def juntar(dst, src):
    me = bpy.data.meshes.new('t'); src.to_mesh(me); dst.from_mesh(me); bpy.data.meshes.remove(me); src.free()

def frame(P0, P1, ref):
    d = (P1 - P0).normalized(); u = (ref - d * ref.dot(d)).normalized(); w = d.cross(u); return d, u, w

def placa(osso_, P0, P1, ref, th0, th1, t0, t1, folga=0.03, esp=0.016, bojo=0.012, nth=10, nt=6, chanfro=0.005,
          brilho=(), rebites=True, mat=0, rmin=0.04, rmax=0.40, dente=0.0, lado=1):
    """Placa curva em volta do eixo P0->P1. θ medido a partir de 'ref' (rodando pra w = d x ref; 'lado' inverte o sentido).
    t em fração do comprimento (pode passar de 0..1). brilho: ('baixo', 'cima', 'meio_t', 'meio_th', ('t', f), ('th', f))."""
    d, u, w = frame(P0, P1, ref); w = w * lado; L = (P1 - P0).length
    R = [[0.0] * (nt + 1) for _ in range(nth + 1)]
    for i in range(nth + 1):
        th = math.radians(th0 + (th1 - th0) * i / nth); dirc = (u * math.cos(th) + w * math.sin(th)).normalized()
        for j in range(nt + 1):
            t = t0 + (t1 - t0) * j / nt; o_ = P0 + d * (L * t)
            h = PELE.ray_cast(o_, dirc, rmax)
            R[i][j] = h[3] if h[0] is not None and h[3] > rmin else None
    vals = [r for row in R for r in row if r]; med = sorted(vals)[len(vals) // 2] if vals else 0.1
    for i in range(nth + 1):
        for j in range(nt + 1):
            if R[i][j] is None: R[i][j] = med
    for _ in range(2):                                     # suaviza (a pele é low-poly: tira os degraus das facetas)
        R2 = [row[:] for row in R]
        for i in range(nth + 1):
            for j in range(nt + 1):
                vz = [R[a][b] for a, b in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)) if 0 <= a <= nth and 0 <= b <= nt]
                R2[i][j] = max(R[i][j], (R[i][j] * 2 + sum(vz)) / (2 + len(vz)))
        R = R2
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new('UVMap')
    fora, dentro = [], []
    for i in range(nth + 1):
        th = math.radians(th0 + (th1 - th0) * i / nth); dirc = (u * math.cos(th) + w * math.sin(th)).normalized()
        lf, ld = [], []
        for j in range(nt + 1):
            t = t0 + (t1 - t0) * j / nt; o_ = P0 + d * (L * t)
            b_ = bojo * math.sin(math.pi * i / nth) ** 0.7 * math.sin(math.pi * j / nt) ** 0.7
            dz = dente * (1 if (i % 2 == 0 and j == 0) else 0)
            r = R[i][j] + folga + b_
            lf.append(bm.verts.new(o_ + dirc * r - d * (L * dz))); ld.append(bm.verts.new(o_ + dirc * (r - esp) - d * (L * dz)))
        fora.append(lf); dentro.append(ld)
    rm = sum(sum(r) for r in R) / ((nth + 1) * (nt + 1)) + folga
    def uvf(i, j): return ((math.radians(th1 - th0) * rm * i / nth) * 4, (L * (t1 - t0) * j / nt) * 4)
    fs_fora = []
    for i in range(nth):
        for j in range(nt):
            f = bm.faces.new((fora[i][j], fora[i + 1][j], fora[i + 1][j + 1], fora[i][j + 1])); f.material_index = mat; fs_fora.append(f)
            for l, (a, b) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))): l[uvl].uv = uvf(a, b)
            g = bm.faces.new((dentro[i][j + 1], dentro[i + 1][j + 1], dentro[i + 1][j], dentro[i][j])); g.material_index = 0
            for l in g.loops: l[uvl].uv = (0.1, 0.1)
    borda = [(fora[i][0], fora[i + 1][0], dentro[i + 1][0], dentro[i][0]) for i in range(nth)] + \
            [(fora[i + 1][nt], fora[i][nt], dentro[i][nt], dentro[i + 1][nt]) for i in range(nth)] + \
            [(fora[0][j + 1], fora[0][j], dentro[0][j], dentro[0][j + 1]) for j in range(nt)] + \
            [(fora[nth][j], fora[nth][j + 1], dentro[nth][j + 1], dentro[nth][j]) for j in range(nt)]
    for q in borda:
        f = bm.faces.new(q); f.material_index = 0
        for l in f.loops: l[uvl].uv = (0.5, 0.5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if chanfro:
        ed = [e for e in bm.edges if all(v in set(sum(fora, [])) for v in e.verts) and len([f for f in e.link_faces if f in set(fs_fora)]) == 1]
        try: bmesh.ops.bevel(bm, geom=ed, offset=chanfro, segments=1, affect='EDGES', profile=0.5)
        except Exception as e_: print('chanfro falhou', e_)
    # sulcos de energia (faixa em relevo na superfície da placa)
    def ponto(th_, t_, extra):
        i_ = (th_ - th0) / (th1 - th0) * nth; j_ = (t_ - t0) / (t1 - t0) * nt
        i0, j0 = min(nth - 1, max(0, int(i_))), min(nt - 1, max(0, int(j_))); fi, fj = i_ - i0, j_ - j0
        r_ = (R[i0][j0] * (1 - fi) * (1 - fj) + R[i0 + 1][j0] * fi * (1 - fj) + R[i0][j0 + 1] * (1 - fi) * fj + R[i0 + 1][j0 + 1] * fi * fj)
        b_ = bojo * math.sin(math.pi * min(1, max(0, i_ / nth))) ** 0.7 * math.sin(math.pi * min(1, max(0, j_ / nt))) ** 0.7
        th_r = math.radians(th_); dirc = (u * math.cos(th_r) + w * math.sin(th_r)).normalized()
        return P0 + d * (L * t_) + dirc * (r_ + folga + b_ + extra), dirc
    def faixa(pts, larg=0.012, alto=0.004):
        aneis = []
        for k, (p, n_) in enumerate(pts):
            tg = (pts[min(k + 1, len(pts) - 1)][0] - pts[max(k - 1, 0)][0]).normalized(); s_ = tg.cross(n_).normalized()
            q = [p - s_ * larg / 2, p - s_ * larg / 2 + n_ * alto, p + s_ * larg / 2 + n_ * alto, p + s_ * larg / 2]
            aneis.append([bm.verts.new(c) for c in q])
        for a_, b_ in zip(aneis, aneis[1:]):
            for k in range(3):
                f = bm.faces.new((a_[k], b_[k], b_[k + 1], a_[k + 1])); f.material_index = 1
                for l in f.loops: l[uvl].uv = (0.5, 0.5)
    mth = (th1 - th0) * 0.06; mt_ = (t1 - t0) * 0.12
    for b in brilho:
        if b == 'baixo': faixa([ponto(th0 + mth + (th1 - th0 - 2 * mth) * k / 16, t0 + mt_, 0.0) for k in range(17)])
        elif b == 'cima': faixa([ponto(th0 + mth + (th1 - th0 - 2 * mth) * k / 16, t1 - mt_, 0.0) for k in range(17)])
        elif isinstance(b, tuple) and b[0] == 't': faixa([ponto(th0 + mth + (th1 - th0 - 2 * mth) * k / 16, t0 + (t1 - t0) * b[1], 0.0) for k in range(17)])
        elif isinstance(b, tuple) and b[0] == 'th': faixa([ponto(th0 + (th1 - th0) * b[1], t0 + mt_ + (t1 - t0 - 2 * mt_) * k / 10, 0.0) for k in range(11)])
        elif isinstance(b, tuple) and b[0] == 'L':   # linha em L / degrau: lista de (fθ, ft)
            pts = []
            for (a1, b1), (a2, b2) in zip(b[1], b[1][1:]):
                for k in range(6): pts.append(ponto(th0 + (th1 - th0) * (a1 + (a2 - a1) * k / 6), t0 + (t1 - t0) * (b1 + (b2 - b1) * k / 6), 0.0))
            a2, b2 = b[1][-1]; pts.append(ponto(th0 + (th1 - th0) * a2, t0 + (t1 - t0) * b2, 0.0)); faixa(pts)
    if rebites:
        for fi, fj in ((0.1, 0.18), (0.9, 0.18), (0.1, 0.82), (0.9, 0.82)):
            p, n_ = ponto(th0 + (th1 - th0) * fi, t0 + (t1 - t0) * fj, 0.0)
            cil(bm, uvl, p, n_, 0.0065, 0.0045, 6, 2)
    juntar(acum(osso_), bm)

def cil(bm, uvl, base, eixo, r, h, n, mat, r2=None, tampa=True):
    eixo = eixo.normalized(); R = eixo.to_track_quat('Z', 'Y').to_matrix(); r2 = r if r2 is None else r2
    a0 = [bm.verts.new(base + R @ Vector((r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n), 0))) for k in range(n)]
    a1 = [bm.verts.new(base + R @ Vector((r2 * math.cos(2 * math.pi * k / n), r2 * math.sin(2 * math.pi * k / n), h))) for k in range(n)]
    for k in range(n):
        f = bm.faces.new((a0[k], a0[(k + 1) % n], a1[(k + 1) % n], a1[k])); f.material_index = mat
        for l, uv in zip(f.loops, ((k / n, 0), ((k + 1) / n, 0), ((k + 1) / n, 1), (k / n, 1))): l[uvl].uv = uv
    if tampa:
        f = bm.faces.new(a1); f.material_index = mat
        for l in f.loops: l[uvl].uv = (0.5, 0.5)
    return a1

# ================================================================ 2) ARMADURA
FR, UP = Vector((0, -1, 0)), Vector((0, 0, 1))
C0, C1 = Vector((0, 0.02, 0.90)), Vector((0, 0.02, 1.80))           # eixo do tronco
# --- tronco: peitoral em 2 camadas, costas, abdômen em lâminas, flancos
placa('spine.003', C0, C1, FR, -78, 78, 0.44, 0.83, folga=0.03, esp=0.02, bojo=0.03, nth=14, nt=8, brilho=(('t', 0.22), ('L', [(0.18, 0.95), (0.18, 0.55), (0.30, 0.35)]), ('L', [(0.82, 0.95), (0.82, 0.55), (0.70, 0.35)])), mat=3)
placa('spine.003', C0, C1, FR, -56, 56, 0.70, 0.86, folga=0.058, esp=0.016, bojo=0.012, nth=10, nt=4, brilho=('baixo',), mat=0)    # placa alta do peito
placa('spine.003', C0, C1, -FR, -82, 82, 0.40, 0.86, folga=0.03, esp=0.02, bojo=0.02, nth=14, nt=8, brilho=(('th', 0.25), ('th', 0.75), ('t', 0.3)), mat=3)
for k, (a, b) in enumerate(((0.32, 0.44), (0.22, 0.34), (0.12, 0.24))):                        # abdômen: 3 lâminas (a de baixo por fora)
    placa('spine.001' if k else 'spine.002', C0, C1, FR, -100, 100, a, b, folga=0.034 + 0.006 * k, esp=0.014, bojo=0.006, nth=16, nt=3, brilho=('baixo',) if k == 2 else (), mat=0, rebites=False)
    placa('spine.001' if k else 'spine.002', C0, C1, -FR, -70, 70, a, b, folga=0.034 + 0.006 * k, esp=0.014, bojo=0.006, nth=12, nt=3, mat=0, rebites=False)
# --- cinto largo com fivela de energia + bolsas
placa('spine', C0, C1, FR, -180, 180, 0.04, 0.12, folga=0.05, esp=0.016, bojo=0.0, nth=24, nt=2, brilho=('meio',), mat=2, rebites=False)
bmc = bmesh.new(); uvc = bmc.loops.layers.uv.new('UVMap')
def caixa(bm, uvl, centro, dx, dy, dz, mat, rot=0.0, chanf=0.004):
    t = bmesh.ops.create_cube(bm, size=1.0)['verts']
    M = Matrix.Translation(centro) @ Matrix.Rotation(rot, 4, 'Z') @ Matrix.Diagonal((dx, dy, dz, 1))
    for v in t: v.co = M @ v.co
    fs = list({f for v in t for f in v.link_faces})
    for f in fs:
        f.material_index = mat
        for l in f.loops: l[uvl].uv = (0.5 + (l.vert.co.x - centro.x) * 4, 0.5 + (l.vert.co.z - centro.z) * 4)
    if chanf:
        ed = list({e for f in fs for e in f.edges})
        try: bmesh.ops.bevel(bm, geom=ed, offset=chanf, segments=1, affect='EDGES', profile=0.5)
        except Exception: pass
def na_pele(o_, dirc, extra=0.0):
    h = PELE.ray_cast(o_, dirc, 0.6); return (h[0] + dirc * extra) if h[0] is not None else None
cz = 0.90 + 0.9 * 0.08
p = na_pele(Vector((0, 0.02, cz)), FR, 0.07)
if p: caixa(bmc, uvc, p, 0.09, 0.03, 0.07, 3); caixa(bmc, uvc, p + Vector((0, -0.017, 0)), 0.05, 0.008, 0.035, 1, chanf=0)   # fivela + núcleo aceso
for ang in (-62, 62, -118, 118, 180):                                    # bolsas em volta do cinto
    a = math.radians(ang); dirc = Vector((math.sin(a), -math.cos(a), 0)); p = na_pele(Vector((0, 0.02, cz - 0.01)), dirc, 0.085)
    if p: caixa(bmc, uvc, p, 0.075, 0.045, 0.085, 0, rot=a); caixa(bmc, uvc, p + dirc * 0.024 + Vector((0, 0, 0.03)), 0.078, 0.012, 0.03, 2, rot=a)
juntar(acum('spine'), bmc)
# --- gorjal (gola alta em 3 anéis, esconde a base do pescoço do Godzilla)
def anel_gola(osso_, z0, z1, r0, r1, y0, nseg=24, frente_baixa=0.0, brilho_topo=True):
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new('UVMap'); an = []
    for z, r, e in ((z0, r0, 0), (z1, r1, 0), (z1, r1 - 0.016, 1), (z0, r0 - 0.016, 1)):
        anel = []
        for k in range(nseg):
            a = 2 * math.pi * k / nseg; fr = (1 + math.cos(a)) / 2
            zz = z - (frente_baixa * fr if z == z1 else 0)
            anel.append(bm.verts.new(Vector((r * 1.12 * math.sin(a), y0 - r * math.cos(a), zz))))
        an.append(anel)
    for A_, B_, mi in ((an[0], an[1], 0), (an[1], an[2], 1 if brilho_topo else 0), (an[2], an[3], 0), (an[3], an[0], 0)):
        for k in range(nseg):
            f = bm.faces.new((A_[k], A_[(k + 1) % nseg], B_[(k + 1) % nseg], B_[k])); f.material_index = mi
            for l, uv in zip(f.loops, ((k / 6, 0), ((k + 1) / 6, 0), ((k + 1) / 6, 1), (k / 6, 1))): l[uvl].uv = uv
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for k in range(0, nseg, 3):                                         # rebites
        a = 2 * math.pi * k / nseg; n_ = Vector((math.sin(a), -math.cos(a), 0)); r = (r0 + r1) / 2
        cil(bm, uvl, Vector((r * 1.12 * math.sin(a), y0 - r * math.cos(a), (z0 + z1) / 2 - (frente_baixa * (1 + math.cos(a)) / 4))) + n_ * 0.002, n_, 0.006, 0.004, 6, 2)
    juntar(acum(osso_), bm)
anel_gola('spine.003', 1.60, 1.68, 0.180, 0.160, 0.015, frente_baixa=0.02, brilho_topo=False)
N0, N1 = Vector((0, 0.015, 1.60)), Vector((0, 0.015, 1.90))             # gorjal: lâminas curvas em volta do pescoço (2 fileiras, com vão)
for k in range(6):
    a = -180 + 60 * k
    placa('spine.004', N0, N1, FR, a + 4, a + 56, 0.22, 0.52, folga=0.030, esp=0.014, bojo=0.012, nth=5, nt=3, brilho=('cima',), mat=3, rebites=False, rmax=0.01)
    placa('spine.003', N0, N1, FR, a + 34, a + 86, 0.05, 0.32, folga=0.055, esp=0.014, bojo=0.01, nth=5, nt=3, mat=0, rebites=True, rmax=0.01)

# --- ombreiras: 4 lâminas grandes + calota, por lado
for s, sfx in ((1, 'L'), (-1, 'R')):
    S0, S1 = Vector((s * 0.06, 0.02, 1.64)), Vector((s * 0.62, 0.03, 1.56))
    placa(f'shoulder.{sfx}', S0, S1, UP, -105, 105, 0.12, 0.40, folga=0.05, esp=0.022, bojo=0.03, nth=14, nt=6, brilho=(('th', 0.5),), mat=3, lado=s)
    for k, (a, b) in enumerate(((0.33, 0.47), (0.42, 0.55), (0.50, 0.62))):
        placa(f'upper_arm.{sfx}', S0, S1, UP, -100 + 6 * k, 100 - 6 * k, a, b, folga=0.05 - 0.008 * k, esp=0.014, bojo=0.008, nth=12, nt=3, brilho=('cima',) if k == 0 else (), mat=0, rebites=k == 2, lado=s)
    # braço: braçal em 2 anéis + cotoveleira
    E0, E1 = osso(f'upper_arm.{sfx}'), osso(f'forearm.{sfx}')
    placa(f'upper_arm.{sfx}', E0, E1, UP, -180, 180, 0.62, 0.95, folga=0.018, esp=0.012, bojo=0.004, nth=16, nt=3, mat=0, rebites=False, lado=s)
    F0, F1 = osso(f'forearm.{sfx}'), osso(f'hand.{sfx}')
    placa(f'forearm.{sfx}', F0, F1, -FR, -80, 80, -0.10, 0.14, folga=0.03, esp=0.014, bojo=0.025, nth=10, nt=4, mat=3, lado=s)        # cotoveleira (atrás)
    # manopla: 2 lâminas + placa de cima com sulco aceso
    placa(f'forearm.{sfx}', F0, F1, UP, -180, 180, 0.18, 0.60, folga=0.022, esp=0.014, bojo=0.008, nth=16, nt=5, brilho=('baixo', ('th', 0.5)), mat=3, lado=s)
    placa(f'forearm.{sfx}', F0, F1, UP, -180, 180, 0.56, 0.98, folga=0.03, esp=0.014, bojo=0.006, nth=16, nt=4, brilho=('cima',), mat=0, lado=s)
    H0 = osso(f'hand.{sfx}'); H1 = osso(f'f_middle.01.{sfx}')
    placa(f'hand.{sfx}', H0, H1, UP, -70, 70, 0.05, 1.05, folga=0.012, esp=0.008, bojo=0.006, nth=8, nt=3, mat=0, rebites=False, lado=s)
    for dedo in ('f_index.01', 'f_middle.01', 'f_ring.01', 'f_pinky.01'):                            # nós dos dedos
        D0, D1 = osso(f'{dedo}.{sfx}'), osso(f'{dedo.replace(".01", ".02")}.{sfx}')
        placa(f'{dedo}.{sfx}', D0, D1, UP, -60, 60, 0.0, 0.9, folga=0.006, esp=0.006, bojo=0.003, nth=4, nt=2, mat=2, rebites=False, chanfro=0, lado=s, rmin=0.002)
    # --- pernas
    T0, T1 = osso(f'thigh.{sfx}'), osso(f'shin.{sfx}'); K1 = osso(f'foot.{sfx}')
    placa(f'thigh.{sfx}', T0, T1, FR, -85, 95, 0.10, 0.50, folga=0.03, esp=0.016, bojo=0.015, nth=12, nt=5, brilho=(('L', [(0.2, 0.15), (0.2, 0.75), (0.35, 0.9)]),), mat=3, lado=s)
    placa(f'thigh.{sfx}', T0, T1, FR, -75, 85, 0.46, 0.86, folga=0.04, esp=0.016, bojo=0.012, nth=12, nt=5, brilho=('baixo',), mat=0, lado=s)
    placa(f'shin.{sfx}', T1, K1, FR, -75, 75, -0.12, 0.13, folga=0.045, esp=0.02, bojo=0.035, nth=10, nt=5, brilho=(('t', 0.5),), mat=3, lado=s)   # joelheira
    placa(f'shin.{sfx}', T1, K1, FR, -115, 115, 0.12, 0.86, folga=0.032, esp=0.016, bojo=0.015, nth=14, nt=7, brilho=(('th', 0.5), 'baixo'), mat=3, lado=s)   # caneleira
    placa(f'shin.{sfx}', T1, K1, -FR, -60, 60, 0.18, 0.62, folga=0.028, esp=0.014, bojo=0.01, nth=8, nt=5, mat=0, rebites=False, lado=s)            # panturrilha
    # bota: cano + peito do pé em lâminas + sola grossa
    P_ = osso(f'foot.{sfx}'); Q_ = osso(f'toe.{sfx}')
    placa(f'foot.{sfx}', P_ + Vector((0, 0, 0.16)), P_ + Vector((0, 0, -0.02)), FR, -180, 180, 0.0, 0.62, folga=0.025, esp=0.014, bojo=0.004, nth=16, nt=3, brilho=('baixo',), mat=0, rebites=False)
    placa(f'foot.{sfx}', P_ + Vector((0, 0.05, 0.02)), Q_ + Vector((0, -0.05, 0.0)), UP, -95, 95, 0.0, 1.0, folga=0.02, esp=0.014, bojo=0.012, nth=10, nt=6, mat=3, lado=1, rmin=0.005)
    bmf = bmesh.new(); uvf_ = bmf.loops.layers.uv.new('UVMap')
    caixa(bmf, uvf_, Vector((P_.x, (P_.y + Q_.y) / 2 - 0.035, 0.012)), 0.15, 0.36, 0.026, 2, chanf=0.006)
    juntar(acum(f'foot.{sfx}'), bmf)
# --- saiote lateral (tassets) presos no quadril
for s, sfx in ((1, 'L'), (-1, 'R')):
    T0, T1 = osso(f'thigh.{sfx}'), osso(f'shin.{sfx}')
    placa(f'thigh.{sfx}', T0 + Vector((0, 0, 0.06)), T1, FR, 40, 130, -0.02, 0.24, folga=0.05, esp=0.014, bojo=0.01, nth=8, nt=4, brilho=('baixo',), mat=0, lado=s)

# ================================================================ 3) "トカ" em relevo aceso no peito + reator nas costas + canos
bmt = bmesh.new(); uvt = bmt.loops.layers.uv.new('UVMap')
ZT, YT = 1.43, None
p0 = na_pele(Vector((0, 0.02, ZT)), FR, 0.0)
YT = (p0.y if p0 else -0.17) - 0.03 - 0.03 - 0.004                       # na frente do peitoral (folga + bojo)
caixa(bmt, uvt, Vector((0, YT + 0.006, ZT)), 0.21, 0.012, 0.13, 3, chanf=0.004)   # moldura da placa
def traco(x0, z0, x1, z1, larg=0.014):
    c = Vector(((x0 + x1) / 2, YT - 0.004, (z0 + z1) / 2)); L = math.hypot(x1 - x0, z1 - z0); a = math.atan2(z1 - z0, x1 - x0)
    t = bmesh.ops.create_cube(bmt, size=1.0)['verts']
    M = Matrix.Translation(c) @ Matrix.Rotation(-a, 4, 'Y') @ Matrix.Diagonal((L + larg, 0.008, larg, 1))
    for v in t: v.co = M @ v.co
    for f in {f for v in t for f in v.link_faces}:
        f.material_index = 1
        for l in f.loops: l[uvt].uv = (0.5, 0.5)
S_ = 0.0021   # 1 px do desenho = 2,1 mm
def px(x, z): return ((x - 32) * S_, ZT + (24 - z) * S_)
for (a, b, c_, d_) in ((14, 6, 14, 42), (14, 20, 27, 27),                     # ト
                       (34, 15, 57, 15), (57, 15, 53, 41), (53, 41, 47, 37), (43, 6, 35, 42)):   # カ
    x0, z0 = px(a, b); x1, z1 = px(c_, d_); traco(x0, z0, x1, z1)
juntar(acum('spine.003'), bmt)
# reator (costas): moldura octogonal acesa, núcleo, 2 engrenagens, carcaça e canos
bmr = bmesh.new(); uvr = bmr.loops.layers.uv.new('UVMap')
pr = na_pele(Vector((0, 0.02, 1.40)), -FR, 0.0); YR = (pr.y if pr else 0.2) + 0.075
caixa(bmr, uvr, Vector((0, YR - 0.02, 1.40)), 0.30, 0.05, 0.36, 3, chanf=0.008)                    # carcaça
def octogono(raio, esp, y, z, mat, larg):
    pts_o = [Vector((raio * math.cos(math.pi / 8 + k * math.pi / 4), y, z + raio * math.sin(math.pi / 8 + k * math.pi / 4))) for k in range(8)]
    pts_i = [Vector((p.x * (raio - larg) / raio, y, z + (p.z - z) * (raio - larg) / raio)) for p in pts_o]
    vo = [bmr.verts.new(p) for p in pts_o]; vi = [bmr.verts.new(p) for p in pts_i]
    vo2 = [bmr.verts.new(p + Vector((0, esp, 0))) for p in pts_o]; vi2 = [bmr.verts.new(p + Vector((0, esp, 0))) for p in pts_i]
    for k in range(8):
        k2 = (k + 1) % 8
        for q in ((vo[k], vo[k2], vi[k2], vi[k]), (vo2[k], vo[k], vi[k], vi2[k])[::-1], (vo[k], vo2[k], vo2[k2], vo[k2]), (vi[k2], vi2[k2], vi2[k], vi[k])):
            f = bmr.faces.new(q); f.material_index = mat
            for l in f.loops: l[uvr].uv = (0.5, 0.5)
octogono(0.15, 0.03, YR + 0.005, 1.42, 2, 0.035)                    # moldura de metal
octogono(0.118, 0.012, YR + 0.03, 1.42, 1, 0.012)                  # filete aceso
cil(bmr, uvr, Vector((0, YR + 0.02, 1.42)), Vector((0, 1, 0)), 0.075, 0.03, 16, 2, r2=0.068)   # base do núcleo
cil(bmr, uvr, Vector((0, YR + 0.05, 1.42)), Vector((0, 1, 0)), 0.05, 0.022, 16, 5, r2=0.04)    # núcleo aceso
def engrenagem(c, raio, dentes, esp, mat):
    n = dentes * 4; vs_f, vs_t = [], []
    for k in range(n):
        a = 2 * math.pi * k / n; r = raio * (1.0 if (k % 4) in (1, 2) else 0.82)
        vs_f.append(bmr.verts.new(c + Vector((r * math.cos(a), 0, r * math.sin(a))))); vs_t.append(bmr.verts.new(c + Vector((r * math.cos(a), esp, r * math.sin(a)))))
    cf = bmr.verts.new(c); ct = bmr.verts.new(c + Vector((0, esp, 0)))
    for k in range(n):
        k2 = (k + 1) % n
        for q in ((cf, vs_f[k2], vs_f[k]), (ct, vs_t[k], vs_t[k2]), (vs_f[k], vs_f[k2], vs_t[k2], vs_t[k])):
            f = bmr.faces.new(q); f.material_index = mat
            for l in f.loops: l[uvr].uv = (0.5 + l.vert.co.x * 3, 0.5 + l.vert.co.z * 3)
engrenagem(Vector((-0.11, YR + 0.035, 1.56)), 0.07, 10, 0.016, 2)
engrenagem(Vector((0.115, YR + 0.035, 1.27)), 0.06, 9, 0.016, 2)
for s in (-1, 1):                                                        # canos do reator até os ombros e pra baixo
    pts = [Vector((s * 0.10, YR + 0.0, 1.52)), Vector((s * 0.16, YR - 0.01, 1.62)), Vector((s * 0.20, YR - 0.05, 1.66))]
    for a_, b_ in zip(pts, pts[1:]): cil(bmr, uvr, a_, b_ - a_, 0.016, (b_ - a_).length, 8, 2, tampa=False)
    cil(bmr, uvr, Vector((s * 0.12, YR, 1.24)), Vector((s * 0.3, -0.2, -1)), 0.016, 0.12, 8, 2)
    for z in (1.30, 1.50): caixa(bmr, uvr, Vector((s * 0.16, YR - 0.01, z)), 0.03, 0.03, 0.08, 1, chanf=0)   # luzes laterais
juntar(acum('spine.003'), bmr)

# ================================================================ 4) tabardo de tecido rasgado (frente e trás)
def tabardo(y_sinal, z0, z1, larg, nome):
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new('UVMap'); NX, NZ = 8, 10; grade = []
    for j in range(NZ + 1):
        z = z0 - (z0 - z1) * j / NZ; linha = []
        for i in range(NX + 1):
            x = -larg / 2 + larg * i / NX
            h = PELE.ray_cast(Vector((x, y_sinal * 0.6, z)), Vector((0, -y_sinal, 0)), 1.0)
            y = (h[0].y if h[0] is not None else y_sinal * 0.15) + y_sinal * (0.06 + 0.02 * j / NZ)
            if j == NZ: z += (0.03 if i % 2 else -0.02) * (1 + (i * 37 % 5) / 5)       # barra rasgada
            linha.append(bm.verts.new(Vector((x, y, z))))
        grade.append(linha)
    for j in range(NZ):
        for i in range(NX):
            f = bm.faces.new((grade[j][i], grade[j][i + 1], grade[j + 1][i + 1], grade[j + 1][i])); f.material_index = 4
            for l, (a, b) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))): l[uvl].uv = (a / NX, 1 - b / NZ)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(nome, me); bpy.context.scene.collection.objects.link(o)
    for m in MATS: me.materials.append(m)
    g0 = o.vertex_groups.new(name='spine'); gl = o.vertex_groups.new(name='thigh.L'); gr = o.vertex_groups.new(name='thigh.R')
    for v in me.vertices:
        t = max(0.0, min(1.0, (z0 - v.co.z) / (z0 - z1))) * 0.6; ks = max(0.0, min(1.0, 0.5 + v.co.x / larg))
        g0.add([v.index], 1 - t, 'REPLACE'); gl.add([v.index], t * ks, 'REPLACE'); gr.add([v.index], t * (1 - ks), 'REPLACE')
    m = o.modifiers.new('Armature', 'ARMATURE'); m.object = A; o.parent = A; o.matrix_parent_inverse = A.matrix_world.inverted()
    return o
tabardo(-1, 0.93, 0.40, 0.24, 'tabardo_frente'); tabardo(1, 0.93, 0.50, 0.26, 'tabardo_tras')

# ================================================================ 5) cabeça e pescoço do Godzilla
antes = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=os.path.join(OD, 'referencia/godzilla_original.glb'))
novos = [o for o in bpy.data.objects if o not in antes]
corpo_g = bpy.data.objects['Object_7']; olhos_g = [bpy.data.objects.get(n) for n in ('Object_8', 'Object_9')]
CORTE_Z, ESC_G, ALVO_G = 39.5, 0.040, Vector((0, 0.012, 1.66))
img_g = next(nd.image for nd in corpo_g.data.materials[0].node_tree.nodes if nd.type == 'TEX_IMAGE')
GW, GH = img_g.size; TEXG = np.array(img_g.pixels[:], np.float32).reshape(GH, GW, 4)[..., :3]
def recortar(ob, alvo, mi):
    me_ = ob.data.copy(); me_.transform(ob.matrix_world); bm = bmesh.new(); bm.from_mesh(me_)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, CORTE_Z), plane_no=(0, 0, 1), clear_inner=True)
    bm.to_mesh(me_); bm.free(); t = bpy.data.objects.new('tmp', me_); bpy.context.scene.collection.objects.link(t)
    tri = sum(len(p.vertices) - 2 for p in me_.polygons)
    if tri > alvo:
        md = t.modifiers.new('d', 'DECIMATE'); md.ratio = alvo / tri; md.use_collapse_triangulate = True
        bpy.context.view_layer.objects.active = t; bpy.ops.object.modifier_apply(modifier='d')
    for p in t.data.polygons: p.material_index = mi
    return t
# malha original (alta) pra tirar as cores
bmA = bmesh.new(); bmA.from_mesh(corpo_g.data); bmA.transform(corpo_g.matrix_world)
bmesh.ops.bisect_plane(bmA, geom=bmA.verts[:] + bmA.edges[:] + bmA.faces[:], plane_co=(0, 0, CORTE_Z - 1.5), plane_no=(0, 0, 1), clear_inner=True)
bmesh.ops.triangulate(bmA, faces=bmA.faces[:]); bmA.faces.ensure_lookup_table(); UVA = bmA.loops.layers.uv.active; BVHA = BVHTree.FromBMesh(bmA)
cab = recortar(corpo_g, 3400, 0)
print('GODZILLA tri', len(cab.data.polygons))
# UV novo (projeção inteligente) e textura 512 com as cores da original no ponto mais próximo
for o_ in bpy.context.selected_objects: o_.select_set(False)          # só a cabeça (senão empacota as ilhas de todos juntos)
bpy.context.view_layer.objects.active = cab; cab.select_set(True)
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(float(os.environ.get('GZ_ANG', '80'))), island_margin=0.004, area_weight=1.0); bpy.ops.object.mode_set(mode='OBJECT')
TR = 512
# BAKE (Cycles) da malha ORIGINAL inteira (alta) na cabeça reduzida: cor difusa + oclusão (as escamas/rugas da geometria viram textura)
hi = recortar(corpo_g, 10 ** 9, 0)
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 24
if sc.world is None: sc.world = bpy.data.worlds.new('w')
sc.world.light_settings.distance = 1.2
mt_b = hi.data.materials[0]
alvo = {}
for nome_ in ('cor', 'ao'):
    im_ = bpy.data.images.new('bake_' + nome_, TR, TR, alpha=False); alvo[nome_] = im_
nd = mt_b.node_tree.nodes.new('ShaderNodeTexImage'); mt_b.node_tree.nodes.active = nd
for o_ in bpy.context.selected_objects: o_.select_set(False)
hi.select_set(True); cab.select_set(True); bpy.context.view_layer.objects.active = cab
for nome_, tipo in (('cor', 'DIFFUSE'), ('ao', 'AO')):
    nd.image = alvo[nome_]
    kw = dict(type=tipo, use_selected_to_active=True, cage_extrusion=0.35, max_ray_distance=1.0, margin=6)
    if tipo == 'DIFFUSE': kw['pass_filter'] = {'COLOR'}
    bpy.ops.object.bake(**kw)
mt_b.node_tree.nodes.remove(nd)
C_ = np.array(alvo['cor'].pixels[:], np.float32).reshape(TR, TR, 4)[::-1, :, :3]
AO_ = np.array(alvo['ao'].pixels[:], np.float32).reshape(TR, TR, 4)[::-1, :, 0]
bpy.data.objects.remove(hi)
tem = C_.sum(-1) > 1e-4
print('BAKE texels', int(tem.sum()), 'cor media', float(C_[tem].mean()), 'ao media', float(AO_[tem].mean()))
cor = C_
lum = cor.mean(-1, keepdims=True); cor = cor * 0.45 + lum * 0.55                 # menos roxo/verde
cor = cor * (0.22 / max(1e-4, float(cor[tem].mean())))                     # normaliza: a pele original é quase preta
ao = np.clip((AO_ - 0.35) / 0.6, 0, 1) ** 1.2
cor = cor * (0.30 + 0.95 * ao[..., None])                                 # escamas/sulcos da geometria original
cor = np.clip(cor ** 0.92 + 0.02, 0, 1) * np.array([1.0, 0.985, 0.96])
img = bpy.data.images.new('godzilla_cabeca_v2', TR, TR, alpha=False); pxl = np.ones((TR, TR, 4), np.float32)
pxl[..., :3] = np.round(cor[::-1] * 31) / 31; img.pixels.foreach_set(pxl.ravel())
img.filepath_raw = os.path.join(OD, 'texturas/godzilla_cabeca_v2.png'); img.file_format = 'PNG'; img.save(); img.pack()
M_GZ = bpy.data.materials.new('o_godzilla'); M_GZ.use_nodes = True; nt_ = M_GZ.node_tree; ti = nt_.nodes.new('ShaderNodeTexImage'); ti.image = img; ti.interpolation = 'Closest'
nt_.links.new(ti.outputs['Color'], nt_.nodes['Principled BSDF'].inputs['Base Color']); nt_.nodes.active = ti; nt_.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.85
M_OL = mat_cor('o_olho_brilho', (255, 214, 40), True)
partes = [cab] + [recortar(o, 80, 1) for o in olhos_g if o]
# alinhamento: centro da base do pescoço no centro do gorjal; pescoço afinado embaixo; focinho levantado
P_ = np.array([tuple(v.co) for v in cab.data.vertices]); base_ = P_[P_[:, 2] < CORTE_Z + 0.8]; cx, cy = base_[:, 0].mean(), base_[:, 1].mean()
ROT = Matrix.Rotation(math.radians(-10), 3, 'X')
def transf(p):
    q = Vector((p.x - cx, p.y - cy, p.z - CORTE_Z))
    afina = interp([(0.0, 0.62), (2.5, 0.78), (5.0, 1.0)], q.z)            # pescoço do original é largo como o peito: afina embaixo
    q.x *= afina; q.y = q.y * afina if q.y > 0 else q.y * (0.8 + 0.2 * afina)
    return ALVO_G + (ROT @ q) * ESC_G
bmG = bmesh.new(); uvG = bmG.loops.layers.uv.new('UVMap')
for t in partes:
    uv_ = t.data.uv_layers.active.data if t.data.uv_layers else None; mapa = {}
    for v in t.data.vertices: mapa[v.index] = bmG.verts.new(transf(v.co))
    for p in t.data.polygons:
        try: f = bmG.faces.new([mapa[i] for i in p.vertices])
        except ValueError: continue
        f.material_index = p.material_index
        for l, li in zip(f.loops, p.loop_indices): l[uvG].uv = uv_[li].uv if (uv_ and p.material_index == 0) else (0.5, 0.5)
bmesh.ops.delete(bmG, geom=[v for v in bmG.verts if not v.link_faces], context='VERTS')
meG = bpy.data.meshes.new('cabeca_godzilla'); bmG.to_mesh(meG); bmG.free(); bmA.free()
for o in novos + partes: bpy.data.objects.remove(o)
og = bpy.data.objects.new('cabeca_godzilla', meG); bpy.context.scene.collection.objects.link(og)
meG.materials.append(M_GZ); meG.materials.append(M_OL)
for p in meG.polygons: p.use_smooth = True
g4 = og.vertex_groups.new(name='spine.004'); g5 = og.vertex_groups.new(name='spine.005')
for v in meG.vertices:
    t = ss(1.72, 1.82, v.co.z); g4.add([v.index], 1 - t, 'REPLACE'); g5.add([v.index], t, 'REPLACE')
md = og.modifiers.new('Armature', 'ARMATURE'); md.object = A; og.parent = A; og.matrix_parent_inverse = A.matrix_world.inverted()
zs = [v.co.z for v in meG.vertices]; ys = [v.co.y for v in meG.vertices]
print('GODZILLA z', round(min(zs), 3), round(max(zs), 3), 'y', round(min(ys), 3), round(max(ys), 3))

# ================================================================ objetos finais da armadura (1 por osso, peso 100%)
for nome_osso, bm in GRUPOS.items():
    me = bpy.data.meshes.new('arm_' + nome_osso); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('armadura_' + nome_osso, me); bpy.context.scene.collection.objects.link(o)
    for m in MATS: me.materials.append(m)
    for p in me.polygons: p.use_smooth = False
    g = o.vertex_groups.new(name=nome_osso); g.add(list(range(len(me.vertices))), 1.0, 'REPLACE')
    m = o.modifiers.new('Armature', 'ARMATURE'); m.object = A; o.parent = A; o.matrix_parent_inverse = A.matrix_world.inverted()
tot = sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH')
print('OLIVEIRA tri(faces)', tot, 'objetos', len([o for o in bpy.data.objects if o.type == 'MESH']))
_bm_pele.free()
bpy.ops.wm.save_as_mainfile(filepath=OUT); print('OLIVEIRA OK', OUT)
