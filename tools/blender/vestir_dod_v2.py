# V2 do Dod: GOLA ALTA, PONCHO curto e assimétrico, ALÇA diagonal com fivelas e BOLSAS utilitárias.
# Executado dentro do vestir_dod.py (V >= 2), depois das peças da V1. Referência de linguagem: poncho militar com gola alta,
# tecido sobreposto, alças diagonais e bolsa frontal — interpretado pro corpo do Dod, não copiado.
ESQ = 1                                                            # lado esquerdo do personagem = +X (frente = -Y)

def bvh_de(obs):                                                   # superfície (mundo) das peças já prontas, pra apoiar alças e bolsas
    vs, ps = [], []
    for ob in obs:
        b = len(vs); vs += [MW @ v.co for v in ob.data.vertices]; ps += [[b + i for i in p.vertices] for p in ob.data.polygons]
    return BVHTree.FromPolygons(vs, ps)
def raio(bvh, p, d, alcance=.7):                                  # acerta a superfície vindo de fora (d = direção pra fora)
    loc, nrm, _, _ = bvh.ray_cast(p + d * alcance, -d, alcance * 2)
    return loc
def restringir(ob, ossos): so_tronco(ob, ossos)

# ================================================================== anel do pescoço (base da gola e do poncho)
PESCOCO = lambda e: all(W(v.co).z > 1.64 and abs(W(v.co).x) < .16 for v in e.verts)
bm = extrair(lambda f: REG[f.index] == 'camisa'); afastar(bm, .010)
anel = list({v for e in bordas(bm, PESCOCO) for v in e.verts})
C0 = sum((W(v.co) for v in anel), Vector()) / len(anel)
base_pescoco = [W(v.co) for v in anel]; bm.free()
def pescoco_em(d):                                                  # raio e altura do pescoço na direção d (horizontal)
    melhor = max(base_pescoco, key=lambda p: Vector((p.x - C0.x, p.y - C0.y, 0)).normalized().dot(d))
    return Vector((melhor.x - C0.x, melhor.y - C0.y, 0)).length, melhor.z

# ================================================================== PONCHO (tecido caído sobre os ombros)
# Apoia nos ombros (raios de cima acham a superfície da camisa/colete) e, onde o ombro acaba, CAI acompanhando o corpo a ~3 cm
# (raios de fora pra dentro), com pregas e pontas. Assimétrico: na frente, um painel diagonal desce sobre o peito ESQUERDO;
# do lado direito o colete fica à mostra. Nos lados termina na ponta do ombro (o braço fica livre; a bandeira aparece).
APOIO = bvh_de([camisa, colete, bolsos])
NA, NS, NH = 24, 4, 4                                              # ângulos · fileiras de apoio · fileiras caindo
def barra_z(d):                                                    # onde a barra termina em cada direção (frente = -Y, esquerda = +X)
    if d.y < -.25:
        x = d.x * .25
        if d.x > -.35: return max(1.385, 1.63 - (d.x + .35) / 1.05 * .30)  # painel diagonal: mais longo à esquerda
        return 1.60                                                # lado direito da frente: curto (colete à mostra)
    if d.y > .25: return 1.355 - .045 * max(0, 1 - abs(d.x) / .3)  # costas, com ponta no meio
    return 9                                                       # lados: sem queda (sobre o ombro)
LIM = lambda d: (OMBRO.x + (.05 if d.x > 0 else .025)) * abs(d.x) + .17 * abs(d.y)    # até onde o tecido apoia
grade = []
for k in range(NA):
    a_ = -math.pi + 2 * math.pi * (k + .5) / NA; d = Vector((math.cos(a_), math.sin(a_), 0))
    r0, z0 = pescoco_em(d); r0 += .012
    # procura a borda do apoio caminhando pra fora
    ultimo, rr = None, r0
    while rr < 1.0:
        p = Vector((C0.x, C0.y, 0)) + d * rr; hit = APOIO.ray_cast(Vector((p.x, p.y, 2.4)), Vector((0, 0, -1)), 2.0)[0]
        if hit is None or (ultimo and hit.z < ultimo.z - .05) or abs(p.x) > OMBRO.x + .06 or rr > LIM(d) + r0: break
        ultimo, rr = hit, rr + .01
    if ultimo is None: ultimo = Vector((C0.x, C0.y, z0)) + d * r0
    r1 = Vector((ultimo.x - C0.x, ultimo.y - C0.y, 0)).length
    col = []; zant = z0 + .045
    for j in range(NS):                                             # fileiras apoiadas (seguem o ombro; o pano só desce a partir do pescoço)
        t = j / (NS - 1); p = Vector((C0.x, C0.y, 0)) + d * (r0 + (r1 - r0) * t)
        hit = APOIO.ray_cast(Vector((p.x, p.y, 2.4)), Vector((0, 0, -1)), 2.0)[0]
        z = min((hit.z if hit is not None else z0) + .058, zant) if j else zant
        zant = z; col.append(Vector((p.x, p.y, z)))
    zb = barra_z(d); topo = col[-1]
    for j in range(1, NH + 1):                                      # fileiras caindo até a barra
        if zb > topo.z - .03: z = topo.z - .022 * j / NH            # sem queda: só uma borda virada pra baixo
        else: z = topo.z + (zb - topo.z) * (j / NH)
        eixo = Vector((C0.x, C0.y, z)); hit = APOIO.ray_cast(eixo + d * .9, -d, .9)[0]
        rc = Vector((hit.x - C0.x, hit.y - C0.y, 0)).length + .042 if hit is not None else r1
        rq = max(rc, r1 + .006 * j) + (.010 if (k % 2) and j >= 2 else 0) * (1 if zb < topo.z - .03 else 0)   # pregas (a queda sempre abre pra fora: sem dobrar pra dentro)
        col.append(Vector((C0.x, C0.y, z)) + d * rq)
    # PONTAS: frente-esquerda e meio das costas descem mais
    if zb < 9:
        ponta = .05 * max(0, 1 - abs(math.atan2(d.y, d.x) - math.atan2(-.75, .66)) / .35) + .04 * max(0, 1 - abs(math.atan2(d.y, d.x) - math.pi / 2) / .3)
        col[-1] = col[-1] - Vector((0, 0, ponta))
    grade.append(col)
for _ in range(2):                                                  # suaviza alturas e raios entre ângulos vizinhos (sem picos)
    nova = []
    for k in range(NA):
        a0, a1, a2 = grade[k - 1], grade[k], grade[(k + 1) % NA]; col = []
        for j in range(len(a1)):
            p = a1[j]; zs = .25 * a0[j].z + .5 * p.z + .25 * a2[j].z
            rr = lambda q: Vector((q.x - C0.x, q.y - C0.y, 0)).length
            r_ = .25 * rr(a0[j]) + .5 * rr(p) + .25 * rr(a2[j]) if j < NS else rr(p)
            d_ = Vector((p.x - C0.x, p.y - C0.y, 0)).normalized()
            col.append(Vector((C0.x, C0.y, zs)) + d_ * r_)
        nova.append(col)
    grade = nova
bmp_ = bmesh.new(); VG = [[bmp_.verts.new(MWi @ p) for p in col] for col in grade]
nl = NS + NH
for k in range(NA):
    k2 = (k + 1) % NA
    for j in range(nl - 1):
        f = bmp_.faces.new((VG[k][j], VG[k2][j], VG[k2][j + 1], VG[k][j + 1])); f.material_index = 1 if j == nl - 2 else 0
bmp_.normal_update()
if sum(Wn(f.normal).dot(Vector((W(f.calc_center_median()).x - C0.x, W(f.calc_center_median()).y - C0.y, .3)).normalized()) for f in bmp_.faces) < 0:
    bmesh.ops.reverse_faces(bmp_, faces=bmp_.faces[:])
INT_P, PAR_P = espessura(bmp_, [f for f in bmp_.faces], .006)
for f in PAR_P: f.material_index = 1
pesar(bmp_)
poncho = objeto(bmp_, 'poncho', ['poncho', 'poncho_barra'], mat_de=lambda f: f.material_index, dens=4)
restringir(poncho, ['spine.001', 'spine.002', 'spine.003', 'shoulder.L', 'shoulder.R'])
print('poncho ok')

# ================================================================== GOLA ALTA
# tubo de tecido que sobe do pescoço por cima da borda do poncho e dobra pra fora no alto (gola enrolada).
# Na frente é mais baixa: não cobre o queixo nem a boca do Dod; atrás e dos lados abraça a base da cabeça.
N = 14
ANEIS = [(-.012, .040), (.012, .056), (.040, .060), (.066, .060), (.078, .070), (.064, .080)]   # (altura, afastamento do pescoço)
bmg = bmesh.new(); grade = []
for j, (dz, dr) in enumerate(ANEIS):
    linha = []
    for k in range(N):
        a_ = -math.pi + 2 * math.pi * (k + .5) / N; d = Vector((math.cos(a_), math.sin(a_), 0)); rr, z0 = pescoco_em(d)
        frente = max(0, -d.y) ** 1.5
        alt = dz * (1 - .5 * frente)
        dobra = .005 * math.sin(k * 2.7 + j) if 1 <= j <= 3 else 0
        linha.append(bmg.verts.new(MWi @ (Vector((C0.x, C0.y, z0)) + d * (rr + dr + dobra) + Vector((0, 0, alt)))))
    grade.append(linha)
for j in range(len(ANEIS) - 1):
    for k in range(N):
        f = bmg.faces.new((grade[j][k], grade[j][(k + 1) % N], grade[j + 1][(k + 1) % N], grade[j + 1][k])); f.material_index = 0
bmg.normal_update()
if sum(Wn(f.normal).dot(Vector((W(f.calc_center_median()).x - C0.x, W(f.calc_center_median()).y - C0.y, 0)).normalized()) for f in bmg.faces[:N]) < 0:
    bmesh.ops.reverse_faces(bmg, faces=bmg.faces[:])
espessura(bmg, [f for f in bmg.faces], .005)
for s in (-1, 1):                                                  # cordões de ajuste pendurados na frente
    k = min(range(N), key=lambda k: abs(-math.pi + 2 * math.pi * (k + .5) / N - (-math.pi / 2 + s * .38)))
    topo = W(grade[2][k].co) + Vector((0, -.004, 0)); fundo = topo + Vector((s * .01, -.014, -.085)); lado = Vector((.0035, 0, 0))
    f = bmg.faces.new([bmg.verts.new(MWi @ p) for p in (topo - lado, topo + lado, fundo + lado, fundo - lado)]); f.material_index = 1
    f = bmg.faces.new([bmg.verts.new(MWi @ (fundo + Vector((dx, -.003, dz)))) for dx, dz in ((-.006, 0), (.006, 0), (.006, -.014), (-.006, -.014))]); f.material_index = 2
pesar(bmg)
gola = objeto(bmg, 'gola', ['gola', 'alca', 'metal'], mat_de=lambda f: f.material_index, dens=5)
restringir(gola, ['spine.003'])
print('gola ok')

# ================================================================== ALÇA DIAGONAL (bandoleira) com fivelas
# do quadril direito, por trás, sobe pelo ombro DIREITO e desce cruzando o peito até o quadril ESQUERDO — por cima do poncho e do colete.
SUP = bvh_de([o for o in (poncho, colete, bolsos, camisa, cinto, calca) if o])
F, T, C, E_ = Vector((0, -1, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)), Vector((1, 0, 0))
GUIA = [(Vector((-.13, .1, 1.24)), (T * .8 - E_ * .6).normalized()), (Vector((-.12, .1, 1.50)), T), (Vector((-.13, .02, 1.78)), C),
        (Vector((-.13, -.1, 1.63)), F), (Vector((-.01, -.1, 1.575)), F), (Vector((.10, -.1, 1.495)), F), (Vector((.19, -.1, 1.38)), F),
        (Vector((.23, -.05, 1.27)), (F * .5 + E_).normalized())]
def faixa(guia, largura, folga, passos=5):
    amostras = []
    for i in range(len(guia) - 1):
        (p0, d0), (p1, d1) = guia[i], guia[i + 1]
        for k in range(passos): t = k / passos; amostras.append((p0.lerp(p1, t), d0.lerp(d1, t).normalized()))
    amostras.append(guia[-1])
    pts = []
    for p, d in amostras:
        hit = raio(SUP, p, d)
        if hit is not None: pts.append((hit + d * folga, d))
    bmf = bmesh.new(); linhas = []
    for i, (q, d) in enumerate(pts):
        a, b = pts[max(i - 1, 0)][0], pts[min(i + 1, len(pts) - 1)][0]; tg = (b - a).normalized(); sd = d.cross(tg).normalized()
        linhas.append((bmf.verts.new(MWi @ (q + sd * largura / 2)), bmf.verts.new(MWi @ (q - sd * largura / 2)), q, d))
    faces = []
    for i in range(len(linhas) - 1):
        a0, b0, _, _ = linhas[i]; a1, b1, _, _ = linhas[i + 1]
        faces.append(bmf.faces.new((a0, b0, b1, a1)))
    bmf.normal_update()
    if sum(Wn(f.normal).dot(linhas[i][3]) for i, f in enumerate(faces)) < 0: bmesh.ops.reverse_faces(bmf, faces=faces)
    return bmf, faces, linhas
bma, fa, linhas_alca = faixa(GUIA, .042, .009)
espessura(bma, fa, .004)
fivelas = []
for t in (.52, .74):                                               # duas fivelas de ajuste na parte da frente (peças em relevo)
    i = int(len(fa) * t); ff = fa[i]
    for f in extrudar(bma, [ff], .006): f.material_index = 1
for f in fa:
    if f.is_valid and f.material_index != 1: f.material_index = 0
pesar(bma)
alca = objeto(bma, 'alca', ['alca', 'metal'], mat_de=lambda f: f.material_index, dens=10)
restringir(alca, ['spine', 'spine.001', 'spine.002', 'spine.003'])
print('alca ok')

# ================================================================== BOLSAS (peças próprias com volume, aba e tira com fivela)
SUP = bvh_de([o for o in (poncho, colete, bolsos, camisa, cinto, calca, alca) if o])
def bolsa_em(c, dfora, cima, w, h, prof, nx=2, nz=3):
    dfora = dfora.normalized(); dir_ = cima.cross(dfora).normalized(); cima = dfora.cross(dir_).normalized()
    tras = [[None] * (nz + 1) for _ in range(nx + 1)]
    for i in range(nx + 1):
        for j in range(nz + 1):
            p = c + dir_ * ((i / nx - .5) * w) + cima * ((j / nz - .5) * h)
            hit = raio(SUP, p, dfora); tras[i][j] = (hit if hit is not None else p) + dfora * .003
    d0 = max(q.dot(dfora) for col in tras for q in col)
    frente = [[q + dfora * (d0 + prof - q.dot(dfora)) for q in col] for col in tras]
    bmb = bmesh.new(); uvq = {}
    VT = [[bmb.verts.new(MWi @ q) for q in col] for col in tras]; VF = [[bmb.verts.new(MWi @ q) for q in col] for col in frente]
    for i in range(nx):
        for j in range(nz):
            bmb.faces.new((VF[i][j], VF[i + 1][j], VF[i + 1][j + 1], VF[i][j + 1]))
            bmb.faces.new((VT[i][j + 1], VT[i + 1][j + 1], VT[i + 1][j], VT[i][j]))
    borda = [(i, 0) for i in range(nx)] + [(nx, j) for j in range(nz)] + [(i, nz) for i in range(nx, 0, -1)] + [(0, j) for j in range(nz, 0, -1)]
    prox = borda[1:] + borda[:1]
    for (i0, j0), (i1, j1) in zip(borda, prox):
        try: bmb.faces.new((VT[i0][j0], VT[i1][j1], VF[i1][j1], VF[i0][j0]))
        except ValueError: pass
    bmb.normal_update()
    if sum(Wn(f.normal).dot(dfora) for f in bmb.faces if f.verts[0] in [v for col in VF for v in col]) < 0: bmesh.ops.reverse_faces(bmb, faces=bmb.faces[:])
    # ABA: tampa que sai um pouco da frente e cobre o terço de cima
    topo = [frente[i][nz] + dfora * .006 for i in range(nx + 1)]; base_aba = [frente[i][nz] - cima * (h * .36) + dfora * .006 for i in range(nx + 1)]
    trasa = [tras[i][nz] + cima * .004 for i in range(nx + 1)]
    VA = [bmb.verts.new(MWi @ p) for p in topo]; VB_ = [bmb.verts.new(MWi @ p) for p in base_aba]; VC = [bmb.verts.new(MWi @ p) for p in trasa]
    for i in range(nx):
        bmb.faces.new((VB_[i], VB_[i + 1], VA[i + 1], VA[i])); bmb.faces.new((VA[i], VA[i + 1], VC[i + 1], VC[i]))
    bmb.normal_update()
    uvl = bmb.loops.layers.uv.verify()
    for f in bmb.faces:
        for l in f.loops:
            p = W(l.vert.co); u = (p - c).dot(dir_) / w + .5; v = (p - c).dot(cima) / h + .5
            l[uvl].uv = (min(1, max(0, u)), min(1, max(0, v)))
    return bmb
# bolsa utilitária presa na alça, no peito esquerdo (por cima do poncho)
pa = linhas_alca[int(len(linhas_alca) * .80)][2]
bmb = bolsa_em(pa + Vector((-.01, 0, -.035)), F, C, .08, .09, .036)
pesar(bmb); bolsa_peito = objeto(bmb, 'bolsa_peito', ['bolsa'], uv=False); restringir(bolsa_peito, ['spine.001', 'spine.002', 'spine.003'])
# bolsa no cinto, quadril direito
hit = raio(SUP, Vector((-.2, 0, CINTURA - .06)), -E_)
bmb = bolsa_em((hit or Vector((-.2, 0, CINTURA - .06))) + Vector((0, 0, 0)), -E_, C, .07, .085, .034)
pesar(bmb); bolsa_cinto = objeto(bmb, 'bolsa_cinto', ['bolsa'], uv=False); restringir(bolsa_cinto, ['spine', 'spine.001'])
if V >= 3:                                                         # porta-equipamento atrás, no lado esquerdo do cinto
    dtras = Vector((.55, .85, 0)).normalized()
    hit = raio(SUP, Vector((.12, .12, CINTURA - .065)), dtras)
    bmb = bolsa_em((hit or Vector((.12, .15, CINTURA - .065))), dtras, C, .075, .09, .045)
    pesar(bmb); bolsa_tras = objeto(bmb, 'bolsa_tras', ['bolsa'], uv=False); restringir(bolsa_tras, ['spine', 'spine.001'])
print('bolsas ok')
