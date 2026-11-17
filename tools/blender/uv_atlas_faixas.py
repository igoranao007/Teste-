"""Refaz a UV do corpo (T-pose) pra usar uma folha de textura em faixas (estilo PS1, 1536x1024):
 y 0-320: cabeça (faixa cilíndrica, rosto no meio x=384) | x 768-1536: cabelo (nuca/topo de trás)
 y 320-695: paletó: x 0-768 tronco (frente no meio, costas nas bordas) | x 768-1152 manga esq. | 1152-1536 manga dir.
 y 695-915: calça: x 0-768 perna esq. | 768-1536 perna dir.   y 915-1024: sapatos (esq. | dir.)
Uso: blender -b base.blend --python uv_atlas_faixas.py -- saida.blend"""
import bpy, bmesh, sys, math
OUT = sys.argv[sys.argv.index('--') + 1]
W, H = 1536.0, 1024.0
o = bpy.data.objects['corpo']; me = o.data
bm = bmesh.new(); bm.from_mesh(me); uvl = bm.loops.layers.uv.active or bm.loops.layers.uv.new()
def interp(pts, v):
    for (a, ya), (b, yb) in zip(pts, pts[1:]):
        if (a - v) * (b - v) <= 0 and a != b: return ya + (v - a) * (yb - ya) / (b - a)
    return pts[0][1] if abs(v - pts[0][0]) < abs(v - pts[-1][0]) else pts[-1][1]
CAB_Z = [(1.80, 2), (1.735, 82), (1.695, 112), (1.625, 212), (1.585, 300), (1.55, 318), (1.40, 319)]
def ang(x, y, cx, cy): return math.atan2(x - cx, -(y - cy))      # 0 = frente, + = lado esquerdo do corpo (x+)
def contínuo(angs):
    if max(angs) - min(angs) > math.pi: return [a + 2 * math.pi if a < 0 else a for a in angs]
    return angs
def regiao(c):
    ax = abs(c.x)
    if ax > 0.585: return 'mao'
    rn = math.hypot(c.x, (c.y - 0.035) * 1.2)
    if ax < 0.15 and (c.z > 1.60 or (c.z > 1.555 and rn < 0.085) or (c.z > 1.54 and c.y < -0.04 and ax < 0.075)): return 'cabeca'
    if c.z > 1.50 and math.hypot(c.x, (c.y - 0.035) * 1.2) < 0.075: return 'pescoco'
    if c.z < 0.095: return 'sapato'
    if c.z < 0.90 and ax < 0.25: return 'calca'
    if ax > 0.20 and c.z > 1.30: return 'manga'
    return 'tronco'
cont = {}
for f in bm.faces:
    c = f.calc_center_median(); r = regiao(c)
    P = [l.vert.co for l in f.loops]
    if r in ('cabeca', 'pescoco') and any(abs(p.x) > 0.085 and p.z < 1.585 for p in P): r = 'tronco'   # ombro é paletó
    if r in ('cabeca', 'pescoco') and c.z < 1.578 and c.y > -0.045: r = 'gola'   # base do pescoço = gola da camisa preta
    cont[r] = cont.get(r, 0) + 1
    if r == 'cabeca':
        a = contínuo([ang(p.x, p.y, 0, 0.025) for p in P])
        ac = sum(a) / len(a)
        if abs(ac) < 2.55 or (ac > 0 and ac - 2 * math.pi > -2.55):
            uv = [(384 + (ai if ai <= math.pi else ai - 2 * math.pi) * 146, interp(CAB_Z, p.z)) for ai, p in zip(a, P)]
        elif c.z > 1.635:   # parte de trás da cabeça: textura de cabelo
            uv = [(768 + 384 + ((ai % (2 * math.pi)) - math.pi) * 200, 20 + (1.80 - p.z) * 1500) for ai, p in zip(a, P)]
        else:               # nuca baixa: pele (bochecha da faixa do rosto)
            uv = [(110 + p.x * 300, 250 + (1.635 - p.z) * 300) for p in P]
    elif r == 'gola':
        uv = [(384 + p.x * 500, 330 + (1.578 - p.z) * 150) for p in P]
    elif r == 'pescoco':
        uv = [(384 + p.x * 900, 300 + (1.585 - p.z) * 200) for p in P]
    elif r == 'mao':   # pele da bochecha
        uv = [(120 + (p.y + 0.05) * 300, 240 + (1.50 - p.z) * 300) for p in P]
    elif r == 'tronco':
        a = contínuo([ang(p.x, p.y, 0, 0.03) for p in P])
        uv = [(384 + (ai if ai <= math.pi else ai - 2 * math.pi) / math.pi * 384, 328 + max(0.0, 1.555 - p.z) / (1.555 - 0.90) * 365) for ai, p in zip(a, P)]
    elif r == 'manga':
        lado = 1 if c.x > 0 else -1; x0 = 768 if lado > 0 else 1152
        a = contínuo([math.atan2(p.y - 0.03, (p.z - 1.46) * lado) for p in P])
        uv = [(x0 + 192 + (ai if ai <= math.pi else ai - 2 * math.pi) / math.pi * 192, 330 + (abs(p.x) - 0.20) / (0.585 - 0.20) * 355) for ai, p in zip(a, P)]
    elif r == 'calca':
        lado = 1 if c.x > 0 else -1; x0 = 0 if lado > 0 else 768; cx = 0.087 * lado
        a = contínuo([ang(p.x, p.y, cx, 0.01) for p in P])
        uv = [(x0 + 384 + (ai if ai <= math.pi else ai - 2 * math.pi) / math.pi * 384, 695 + (0.90 - p.z) / (0.90 - 0.095) * 220) for ai, p in zip(a, P)]
    else:   # sapato
        lado = 1 if c.x > 0 else -1; x0 = 0 if lado > 0 else 768; cx = 0.09 * lado
        a = contínuo([ang(p.x, p.y, cx, -0.03) for p in P])
        uv = [(x0 + 384 + (ai if ai <= math.pi else ai - 2 * math.pi) / math.pi * 384, 917 + (0.095 - p.z) / 0.095 * 105) for ai, p in zip(a, P)]
    for l, (u, v) in zip(f.loops, uv):
        l[uvl].uv = (min(max(u, 1), W - 1) / W, 1 - min(max(v, 1), H - 1) / H)
bm.to_mesh(me); bm.free()
print('REGIOES', cont)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
