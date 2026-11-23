# Paleta e texturas da V2/V3 do Dod (executado dentro do vestir_dod.py, depois dos materiais da V1).
# Paleta: verde-oliva (base) · verde-musgo (painéis) · verde-escuro (divisões) · amarelo-oliva envelhecido (costuras) ·
# bege-caqui (fitas) · verde acinzentado (poncho) · cinza metálico (fivelas) · preto (luvas, coturnos) · marrom gasto (desgaste)
P_OLIVA, P_OLIVA_E, P_OLIVA_C = '#4b5631', '#313a20', '#67733f'
P_MUSGO, P_MUSGO_E, P_MUSGO_C = '#5a633b', '#3b4327', '#727c4b'
P_ESCURO = '#232a19'
P_AMARELO, P_AMARELO_E = '#a39542', '#7c7233'
P_CAQUI, P_CAQUI_E = '#9b8c63', '#6c6245'
P_CINZA_VERDE, P_CINZA_VERDE_E, P_CINZA_VERDE_C = '#5b6450', '#373e31', '#78806a'
P_MARROM = '#5b4632'
TEX_DOD = os.path.join(RAIZ, 'material/producao/personagens/dod/texturas')

def desgaste(f, s, forca=1.0):                                    # manchas de uso: marrom gasto e caqui desbotado
    def g(x, y, w, h):
        c = f(x, y, w, h); k = ruido(x, y, s + 50)
        if k > 1 - .035 * forca: c = mix(c, hx(P_MARROM), .55)
        elif k < .03 * forca: c = mix(c, hx(P_CAQUI), .35)
        return c
    return g
def lona(base, esc, clara, s):                                    # lona mesclada (como o tecido da referência do poncho)
    B, E, C = hx(base), hx(esc), hx(clara)
    def f(x, y, w, h):
        m = ruido(x // 3, y // 3, s) * .6 + ruido(x // 6, y // 6, s + 1) * .4
        c = mix(E, B, .35 + .65 * m)
        if ruido(x, y, s + 2) > .93: c = mix(c, C, .5)
        if (x * 3 + y) % 9 == 0: c = mix(c, E, .25)
        return c
    return f
def costura_f(x, y, w, h):                                         # faixa de costura: fundo escuro com pesponto amarelo-oliva
    c = hx(P_ESCURO)
    if (y in (3, 4) and x % 4 < 2) or (x in (3, 4) and y % 4 < 2): c = hx(P_AMARELO)
    return c
def fita_f(base, borda, s, ponto=True):                            # fita (webbing): bordas, pesponto e travetes
    B, E = hx(base), hx(borda)
    def f(x, y, w, h):
        c = mix(B, E, .25 * ruido(x, y // 2, s))
        if y in (0, h - 1): c = mix(B, E, .6)
        if ponto and y in (1, h - 2) and x % 2 == 0: c = hx(P_AMARELO)
        if x % 16 in (7, 8) and 3 < y < h - 4: c = mix(B, E, .5)
        return c
    return f
def bolsa_f(base, esc, clara, s, aba=.66, tira=True):              # bolso inteiro (UV plana 0..1): aba com pesponto, tira caqui com fivela
    B, E, C = hx(base), hx(esc), hx(clara)
    def f(x, y, w, h):
        v, u = y / (h - 1), x / (w - 1)
        c = mix(B, C, .35 * ruido(x // 2, y // 2, s))
        if v > aba: c = mix(c, E, .3)
        if abs(v - aba) < .035: c = mix(E, B, .15)
        if v > aba and (x in (2, w - 3) or y == h - 3) and (x + y) % 2 == 0: c = hx(P_AMARELO)   # pesponto da aba
        if (x in (1, w - 2) or y == 1) and (x + y) % 2 == 0: c = mix(hx(P_AMARELO), B, .3)       # costura do corpo
        if tira and abs(u - .5) < .09 and aba - .22 < v < aba + .08: c = hx(P_CAQUI) if abs(u - .5) < .07 else hx(P_CAQUI_E)
        if tira and abs(u - .5) < .1 and abs(v - (aba - .2)) < .04: c = hx('#8a8a84')            # fivela
        return desgaste(lambda *a: c, s, .6)(x, y, w, h)
    return f
def placa_f(x, y, w, h):                                           # painel do colete (UV plana): borda reforçada, pesponto, cantos
    u, v = x / (w - 1), y / (h - 1)
    c = lona(P_OLIVA, P_OLIVA_E, P_OLIVA_C, 21)(x, y, w, h)
    b = min(x, y, w - 1 - x, h - 1 - y)
    if b < 3: c = mix(hx(P_ESCURO), c, .3)                         # debrum
    elif b == 4 and (x + y) % 3 != 0: c = hx(P_AMARELO)             # pesponto amarelo-oliva
    if (x < 9 and y < 9 and x + y < 10) or (x > w - 10 and y < 9 and (w - 1 - x) + y < 10) or (x < 9 and y > h - 10 and x + (h - 1 - y) < 10) or (x > w - 10 and y > h - 10 and (w - 1 - x) + (h - 1 - y) < 10):
        if b >= 3: c = mix(hx(P_MUSGO_E), c, .3)                    # reforço dos cantos
    if abs(x - w // 2) == 0 and 6 < y < h - 6 and y % 3: c = mix(hx(P_CAQUI_E), c, .5)   # costura central discreta
    return desgaste(lambda *a: c, 22, 1.2)(x, y, w, h)
def lateral_f(x, y, w, h):                                         # faixa lateral (cummerbund): musgo com fitas horizontais
    c = lona(P_MUSGO, P_MUSGO_E, P_MUSGO_C, 23)(x, y, w, h)
    yy = y % 10
    if yy in (0, 1): c = mix(hx(P_ESCURO), c, .3)
    elif yy in (2, 3, 4, 5): c = mix(hx(P_OLIVA_C), c, .5)
    if yy in (3, 4) and x % 12 == 0: c = hx(P_AMARELO_E)
    return c
def bota3_f(x, y, w, h):                                           # couro preto com painéis e vincos
    c = mix(hx('#141415'), hx('#3a3a3c'), .5 * ruido(x // 2, y // 2, 31) ** 2)
    if y % 16 == 0 or x % 21 == 0: c = hx('#2a2a2c')               # costura dos painéis
    if (x + 2 * y) % 13 == 0: c = mix(c, hx('#4a4a4c'), .4)         # vinco
    return c
def cadarco_f(x, y, w, h):                                         # língua + cadarço cruzado + ilhoses (UV plana)
    u, v = x / (w - 1), y / (h - 1)
    c = hx('#1d1d1f') if abs(u - .5) < .28 else hx('#141415')
    yy = y % 6
    if abs(u - .5) < .3 and abs((u - .5) * 10) - abs(yy - 3) < 1.2 and abs(u - .5) * 10 > abs(yy - 3) - 1.0: c = hx('#5a5a5c')
    if abs(abs(u - .5) - .3) < .04 and yy == 3: c = hx('#8c8b84')   # ilhós
    return c
def sola_f2(x, y, w, h):
    return hx('#0f0f10') if (x + y) % 5 < 2 else hx('#262628')
def entressola_f(x, y, w, h):
    return hx('#4a4a4c') if y % 8 not in (0, 7) else hx('#333335')
def biqueira_f(x, y, w, h):
    return mix(hx('#101011'), hx('#4b4b4d'), (ruido(x // 2, y // 2, 37) ** 3))
def luva3_f(x, y, w, h):                                           # luva preta: nós dos dedos e costuras
    c = mix(hx('#19191a'), hx('#3b3c37'), .45 * ruido(x // 2, y // 2, 41) ** 2)
    if y % 8 == 0: c = hx('#2f302c')
    if x % 8 == 4 and y % 2 == 0: c = mix(hx(P_AMARELO_E), c, .55)
    return c
def palma_f(x, y, w, h):                                           # reforço da palma (couro cinza-marrom com pesponto)
    c = mix(hx('#3b342c'), hx('#544a3c'), .5 * ruido(x // 2, y // 2, 43))
    if (x in (1, w - 2) or y in (1, h - 2)) and (x + y) % 2 == 0: c = hx('#6e6450')
    return c
def poncho_barra_f(x, y, w, h):                                    # barra do poncho: faixa mais escura com pesponto duplo
    c = lona(P_CINZA_VERDE, P_CINZA_VERDE_E, P_CINZA_VERDE_C, 51)(x, y, w, h); c = mix(c, hx(P_ESCURO), .35)
    if (y % 8 in (2, 5)) and x % 3 != 0 and V >= 3: c = hx(P_AMARELO)
    return c
def png(nome):
    img = bpy.data.images.load(os.path.join(TEX_DOD, nome)); img.pack(); return img

# ---- V2: peças novas
material('poncho', textura('poncho', 64, 64, desgaste(lona(P_CINZA_VERDE, P_CINZA_VERDE_E, P_CINZA_VERDE_C, 50), 52, 1.3 if V >= 3 else .6)))
material('poncho_barra', textura('poncho_barra', 16, 16, poncho_barra_f))
material('gola', textura('gola', 64, 64, desgaste(lona('#4d5733', '#30381f', '#69744a', 53), 54, .8)))
material('alca', textura('alca', 32, 8, fita_f('#1f2b23', '#101712', 55, ponto=V >= 3)))
material('bolsa', textura('bolsa', 32, 32, bolsa_f(P_OLIVA, P_OLIVA_E, P_OLIVA_C, 56)), repete=False)
material('metal', textura('metal', 8, 8, preto_f('#77766c', '#b3b1a4', 9)))
# ---- V3: tudo ganha paleta, costuras e desgaste
if V >= 3:
    material('farda', textura('farda', 64, 64, desgaste(tecido(P_OLIVA, P_OLIVA_E, P_OLIVA_C, 1), 60)))
    material('farda2', textura('farda2', 64, 64, desgaste(tecido(P_MUSGO, P_MUSGO_E, P_MUSGO_C, 3), 61)))
    material('calca', textura('calca', 64, 64, desgaste(tecido('#46502f', '#2e361e', '#606b40', 2), 62)))
    material('costura', textura('costura', 8, 8, costura_f))
    material('reforco', textura('reforco', 32, 32, desgaste(lambda x, y, w, h: mix(hx(P_MUSGO_E), hx(P_MUSGO), .5 * ruido(x // 2, y // 2, 63)) if (x - y) % 8 else hx(P_AMARELO_E), 64)))
    material('bolso_manga', png('bolso_manga.png'), repete=False)
    material('bolso_calca', textura('bolso_calca', 32, 40, bolsa_f(P_MUSGO, P_MUSGO_E, P_MUSGO_C, 65, aba=.62)), repete=False)
    material('placa', textura('placa', 64, 64, placa_f), repete=False)
    material('lateral', textura('lateral', 64, 64, lateral_f))
    material('borda', textura('borda', 8, 8, costura_f))
    material('fita', textura('fita', 32, 8, fita_f(P_CAQUI, P_CAQUI_E, 66)))
    material('nome', png('nome_dod.png'), repete=False)
    material('bolso', textura('bolso', 32, 32, bolsa_f(P_MUSGO, P_MUSGO_E, P_MUSGO_C, 67)), repete=False)
    material('cinto', textura('cinto', 32, 32, fita_f('#1d1e1b', '#0f100e', 68)))
    material('bota', textura('bota', 64, 64, bota3_f))
    material('cadarco', textura('cadarco', 32, 32, cadarco_f), repete=False)
    material('biqueira', textura('biqueira', 16, 16, biqueira_f))
    material('sola', textura('sola', 16, 16, sola_f2))
    material('entressola', textura('entressola', 16, 16, entressola_f))
    material('luva', textura('luva', 32, 32, luva3_f))
    material('palma', textura('palma', 16, 16, palma_f))
    material('joelheira', textura('joelheira', 16, 16, lambda x, y, w, h: mix(hx('#1e231b'), hx('#4a5340'), .5 * ruido(x // 2, y // 2, 69) ** 2) if y % 8 else hx(P_CAQUI_E)))
    def bandeira3_f(x, y, w, h):                                   # patch costurado: debrum verde-escuro com pesponto amarelo-oliva
        if x in (0, w - 1) or y in (0, h - 1): return hx(P_ESCURO)
        if x in (1, w - 2) or y in (1, h - 2): return hx(P_AMARELO) if (x + y) % 2 == 0 else hx(P_OLIVA_E)
        return bandeira_f(x, y, w, h)
    material('bandeira', textura('bandeira', 48, 32, bandeira3_f), repete=False)
