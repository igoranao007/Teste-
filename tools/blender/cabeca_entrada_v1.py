# CABEÇA da ENTRADA (executado dentro do vestir_personagem.py): rosto da FOTO projetado de frente numa cabeça low-poly
# (alinhado pelos dois olhos: escala e o leve giro da selfie), CABELO modelado (volume em cima, laterais curtas, franja caindo
# pro lado direito da pessoa) e ORELHAS. Tudo preso ao osso da cabeça (spine.005).
TEXD = os.path.join(RAIZ, 'material/producao/personagens/entrada/texturas')
def img_png(n): i = bpy.data.images.load(os.path.join(TEXD, n)); i.pack(); return i
material('e_rosto', img_png('rosto.png'), repete=False)
material('e_cabelo', img_png('cabelo.png'))
material('e_orelha', textura('e_orelha', 16, 16, lambda x, y, w, h: mix(tuple(int(c * .78) for c in PELE), tuple(int(c) for c in PELE), min(1, (abs(x - 8) + abs(y - 8)) / 9))))
HC = Vector((0, -.005, 1.86)); HX, HY, HZ = .1, .118, .145          # centro e meias-medidas da cabeça (mundo)
Z_OLHO = 1.875
(ex1, ey1), (ex2, ey2) = R_['olhos']; mx_, my_ = (ex1 + ex2) / 2, (ey1 + ey2) / 2
S_ = math.hypot(ex2 - ex1, ey2 - ey1) / .108; TH_ = math.atan2(ey2 - ey1, ex2 - ex1)
rx0, ry0, rx1, ry1 = R_['rec']
BOCHECHA = (665, 1568)                                             # bordas reais das bochechas na altura dos olhos (o rosto está um pouco virado)
def foto_uv(p):                                                    # ponto do mundo (x, z) → pixel da foto → UV do recorte
    sx = (mx_ - BOCHECHA[0]) / HX if p.x < 0 else (BOCHECHA[1] - mx_) / HX            # cada lado do rosto vai até a sua bochecha
    u, v = p.x * sx / S_, -(p.z - Z_OLHO)
    px = mx_ + S_ * (u * math.cos(TH_) - v * math.sin(TH_)); py = my_ + S_ * (u * math.sin(TH_) + v * math.cos(TH_))
    return ((px - rx0) / (rx1 - rx0), 1 - (py - ry0) / (ry1 - ry0))

def cabeca_bm():
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=11, radius=1.0)
    for v in bm.verts:
        x, y, z = v.co.x, v.co.y, v.co.z
        if y < 0:
            y *= .86                                                                  # frente chapada (PS1)
            y -= .21 * math.exp(-(x / .13) ** 2) * math.exp(-((z + .16) / .17) ** 2)   # nariz
            y -= .07 * math.exp(-(x / .3) ** 2) * math.exp(-((z + .86) / .14) ** 2)    # queixo
            y += .05 * math.exp(-((abs(x) - .5) / .16) ** 2) * math.exp(-((z - .1) / .1) ** 2)   # órbitas
        else: y *= 1.04                                                               # nuca redonda
        if z < -.22: t = min(1, (-.22 - z) / .78); x *= 1 - .17 * t; y *= 1 - .08 * t     # mandíbula (larga, como na foto)
        v.co = MWi @ (HC + Vector((x * HX, y * HY, z * HZ)))
    bm.normal_update(); return bm

# ---- cabeça (rosto projetado na frente e nos lados; atrás, coberto pelo cabelo, cor de cabelo)
bm = cabeca_bm(); uvl = bm.loops.layers.uv.verify()
for f in bm.faces:
    if normal(f).y < -.28:                                          # só a FRENTE recebe a foto (nos lados ela esticaria e pegaria a parede)
        f.material_index = 0
        for l in f.loops: l[uvl].uv = foto_uv(W(l.vert.co))
    else:                                                          # lados e trás: pele no tom da bochecha (o cabelo cobre o alto)
        f.material_index = 1
        for l in f.loops: q = W(l.vert.co); l[uvl].uv = (q.y * 12, q.z * 12)
cabeca = objeto(bm, 'cabeca', ['e_rosto', 'e_pele'], mat_de=lambda f: f.material_index, uv=False)
tudo_no_osso(cabeca, 'spine.005')

# ---- cabelo: casca acima da linha do cabelo (testa na frente, acima da orelha nos lados, nuca atrás), com volume em cima e franja
def linha(c):                                                      # altura da linha do cabelo em volta da cabeça
    tb = min(1, max(0, (c.y + .02) / .08)); ws = min(1, max(0, (abs(c.x) - .05) / .05))
    frente = 1.972 - .045 * (c.x / .1) ** 2                         # linha do cabelo medida na foto (testa à mostra)
    return (frente * (1 - ws) + 1.888 * ws) * (1 - tb) + 1.765 * tb
bm = cabeca_bm()
bmesh.ops.delete(bm, geom=[f for f in bm.faces if centro(f).z < linha(centro(f))], context='FACES')
bm.normal_update()
for v in bm.verts:                                                 # volume: grosso em cima, rente nos lados (degradê)
    p = W(v.co); topo = min(1, max(0, (p.z - 1.9) / .1))
    off = .006 + .032 * topo + .006 * math.sin(p.x * 140 + p.y * 90) * topo        # tufos irregulares no alto
    v.co += v.normal * L(off)
franja = bordas(bm, lambda e: all(W(v.co).y < -.05 and W(v.co).z > 1.9 for v in e.verts))
if franja:
    vs = extrudar_borda(bm, franja, (0, 0, 0))
    for i, v in enumerate(sorted(vs, key=lambda v: W(v.co).x)):   # mechas da franja: caem sobre a testa, puxadas pro lado direito da pessoa (-X)
        p = W(v.co); comp = .016 + (.012 if i % 2 else 0) - .006 * abs(p.x) / .1   # franja curta, em mechas
        v.co = MWi @ (p + Vector((-.014, -.012, -comp)))
espessura(bm, bm.faces[:], .006)
uvl = bm.loops.layers.uv.verify()
for f in bm.faces:
    for l in f.loops: q = W(l.vert.co); l[uvl].uv = (q.x * 10 + q.y * 4, q.z * 10)
cabelo = objeto(bm, 'cabelo', ['e_cabelo'], uv=False)
tudo_no_osso(cabelo, 'spine.005')

# ---- orelhas: concha achatada dos dois lados, na altura entre o olho e a ponta do nariz
bm = bmesh.new(); uvl = bm.loops.layers.uv.verify()
for s in (1, -1):
    c = Vector((s * (HX * .93), .012, 1.842)); n = 7
    centro_v = bm.verts.new(MWi @ (c + Vector((s * .004, 0, 0))))
    borda_ = [bm.verts.new(MWi @ (c + Vector((s * (.012 + .006 * math.sin(a)), .03 * math.cos(a) * .9, .042 * math.sin(a))))) for a in [math.pi * (k / (n - 1)) - math.pi / 2 for k in range(n)]]
    for k in range(n - 1):
        f = bm.faces.new((centro_v, borda_[k], borda_[k + 1]) if s > 0 else (centro_v, borda_[k + 1], borda_[k]))
        for l in f.loops: q = W(l.vert.co); l[uvl].uv = ((q.y - c.y) / .06 + .5, (q.z - c.z) / .084 + .5)
bm.normal_update()
orelhas = objeto(bm, 'orelhas', ['e_orelha'], uv=False)
tudo_no_osso(orelhas, 'spine.005')
for m in MATS.values(): m.use_backface_culling = True
