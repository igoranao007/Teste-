"""THE GREEN PATH v4 — linha do tempo, falas e sons do filme (3:40).
Escreve videos/00-filme4/cues.json + narration.json, material/voz-v4.json (volume da voz por quadro, pra boca/cabeça)
e edicao/src/legendas4.json. Depois: audio/.venv/bin/python audio/synth.py 00-filme4 → audio/00-filme4.wav
uso: audio/.venv/bin/python tools/som4.py"""
import json, os, subprocess, math
import numpy as np
from scipy.io import wavfile
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R)
PLANOS = [('41-estrada', 17), ('42-nicolas', 9), ('43-posto', 22), ('44-mendigo', 37), ('45-titulo', 7), ('46-casmiron', 12),
          ('47-cabana', 12), ('48-senha', 10), ('49-olhos', 8), ('50-elevador', 24), ('51-sala-igor', 14), ('52-arquivos', 13),
          ('53-projeto-mogg', 12), ('54-computador', 16), ('55-tela-mogg', 9), ('56-final', 8)]
INI = {}; acc = 0
for n, d in PLANOS: INI[n[:2]] = acc; acc += d
FIM = acc
C = 'audio/voz/v4/cortadas/'
# (arquivo ou None = só legenda, plano, instante no plano, quem, texto)
FALAS = [
 (C + 'adryan_p1-1.wav', '41', 10.2, 'adryan', 'Essa maleta precisa chegar ao destino. Não é uma entrega qualquer.|Tem coisa aí dentro que não pode simplesmente cair nas mãos de qualquer pessoa.'),
 (C + 'adryan_p2-1.wav', '42', 1.4, 'adryan', 'E você, Nicolas, não solta essa maleta por nada. Entendeu?'),
 (C + 'adryan_p3a-1.wav', '43', 5.6, 'adryan', 'Boa noite. Completa pra mim.'),
 (C + 'adryan_p3b-2.wav', '43', 14.2, 'adryan', 'Movimento fraco hoje, hein?'),
 (C + 'adryan_p3c-1.wav', '43', 18.6, 'adryan', 'Beleza... também não precisa conversar.'),
 (C + 'metalis_p4a-1.wav', '44', 2.8, 'metalis', 'Ô, Adryan! Meu parceiro! Tem uma moedinha aí?'),
 (C + 'adryan_p4a-2.wav', '44', 7.4, 'adryan', 'Ah, não... Metalis. Você de novo?'),
 (C + 'metalis_p4b-1.wav', '44', 10.2, 'metalis', 'Ué, vai me deixar na mão? Tô numa situação complicada, meu jovem.'),
 (C + 'adryan_p4b-1.wav', '44', 14.7, 'adryan', 'Você sempre tá numa situação complicada.'),
 (C + 'metalis_p4c-1.wav', '44', 20.4, 'metalis', 'É a vida, meu amigo. A vida não tá fácil pra ninguém.'),
 (C + 'adryan_p4c-1.wav', '44', 24.4, 'adryan', 'Toma. Agora deixa a gente ir.'),
 (C + 'metalis_p4d-1.wav', '44', 27.6, 'metalis', 'Sabia que podia contar contigo!'),
 (C + 'adryan_p4d-1.wav', '44', 30.0, 'adryan', 'Vai cuidar da tua vida, Metalis.'),
 (C + 'metalis_p4e-1.wav', '44', 32.6, 'metalis', 'Boa viagem!'),
 (C + 'adryan_p7-1.wav', '47', 5.6, 'adryan', 'Me entrega a maleta. Espera aqui fora e fica de olho em qualquer movimento.'),
 (C + 'gusta_p8a-1.wav', '48', 3.4, 'gusta', 'Qual a senha?'),
 (C + 'adryan_p8-1.wav', '48', 4.8, 'adryan', '15/03 007 BIFF.'),
 (C + 'gusta_p8b-1.wav', '48', 7.5, 'gusta', 'Pode entrar.'),
 (C + 'adryan_p10a-1.wav', '50', 3.0, 'adryan', 'Então... o Igor já sabe que a gente tá chegando?'),
 (C + 'gusta_p10s-1.wav', '50', 6.2, 'gusta', 'Sabe.'),
 (C + 'gusta_p10a-1.wav', '50', 7.0, 'gusta', 'Mas não é qualquer pessoa que pode ficar sabendo dessa missão.'),
 (C + 'adryan_p10b-1.wav', '50', 12.3, 'adryan', 'Por quê?'),
 (C + 'gusta_p10b-1.wav', '50', 13.2, 'gusta', 'Porque o Projeto Mogg é importante demais.|Isso não pode ser comentado em qualquer lugar. Nem mesmo fora daqui.'),
 (C + 'gusta_p10c-1.wav', '50', 19.9, 'gusta', 'Você vai entender quando encontrar o Igor.'),
 (C + 'igor_p11-1.wav', '51', 7.6, 'igor', 'Nem mesmo no meu aniversário eles conseguem se segurar...'),
 (C + 'igor_p12a-X.wav', '52', 2.2, 'igor', 'Trouxeram?'),
 (C + 'igor_p12b-1.wav', '52', 6.8, 'igor', 'Todos eles têm potencial. Um potencial que não pode ser desperdiçado.'),
 (C + 'igor_p12c-1.wav', '52', 11.0, 'igor', 'Então... o Projeto Mogg.'),
 ('audio/voz/falas/f2-1.wav', '53', 6.2, 'igor', 'Então é isso. O Projeto Mogg.'),
 (C + 'igor_p14-1.wav', '54', 9.0, 'igor', 'Vamos ver o que a Toca do Anão escondeu.'),
]
p12 = sorted(f for f in os.listdir(C) if f.startswith('igor_p12a-') and f != 'igor_p12a-1.wav')
FALAS = [(C + (p12[0] if p12 else 'igor_p12a-1.wav'), *x[1:]) if x[0] and 'p12a-X' in x[0] else x for x in FALAS]
VOZ, SEG, LEG = {}, [], []
os.makedirs('audio/voz/v4/mix', exist_ok=True)
for i, (arq, pl, t0, quem, texto) in enumerate(FALAS):
    T = INI[pl] + t0
    partes = texto.split('|')
    if arq:
        out = f'audio/voz/v4/mix/f{i:02d}.wav'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', arq, '-af', 'highpass=f=75,afade=t=in:d=0.02', '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s16le', out], check=True)
        sr, v = wavfile.read(out); v = v.astype(np.float64) / 32768; dur = len(v) / sr
        q = int(sr / 30); env = [float(np.sqrt(np.mean(v[k:k + q] ** 2))) for k in range(0, len(v), q)]; mx = max(env) or 1
        env = [round(min(1, (e / mx) ** .6 * 1.15) if e / mx > .08 else 0, 2) for e in env]
        VOZ.setdefault(pl, []).append({'t': t0, 'env': env, 'quem': quem})
        SEG.append({'file': out, 'start': round(T, 3), 'dur': round(dur, 2)})
    else: dur = max(1.4, len(texto) / 15)
    for k, p in enumerate(partes):
        a = T + dur * k / len(partes); b = T + dur * (k + 1) / len(partes) + .25
        LEG.append({'text': p, 'quem': quem, 'startMs': int(a * 1000), 'endMs': int(b * 1000), 'semVoz': arq is None})
# som do vídeo que o Igor está vendo no monitor (plano 51 → começo do 52): caixinha de som de PC, por baixo das falas
VT = 'audio/voz/v4/mix/video_tela.wav'
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'material/cenarios/sala-igor/ref/video-tela-igor.mp4', '-vn', '-af', 'highpass=f=280,lowpass=f=3800,afade=t=out:st=15.2:d=0.7', '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s16le', VT], check=True)
SEG.append({'file': VT, 'start': round(INI['51'], 3), 'dur': 15.9, 'ganho': -7})
json.dump(VOZ, open('material/voz-v4.json', 'w'))
json.dump({'planos': PLANOS, 'legendas': LEG}, open('edicao/src/legendas4.json', 'w'), ensure_ascii=False, indent=1)
Cs = []
def cue(tipo, t, **o): Cs.append({'type': tipo, 't': round(t, 3), **o})
def P(n): return INI[n]
# PASSOS: sincronizados com cada caminhada do motor (mesma aceleração/frenagem de lib/v4.js caminhar: ease .18 nas pontas)
# um passo a cada meio ciclo de caminhada (passo_m/2 de distância). sup = superfície, peso = personagem (1 adulto, .6 Metalis)
ALT = {'adryan': 1.76, 'gusta': 1.80, 'nicolas': 1.62, 'frentista': 1.74, 'metalis': 1.10}
PESO = {'adryan': .9, 'gusta': 1.0, 'nicolas': .8, 'frentista': 1.0, 'metalis': .6}
_seed = [0]
OFF = {'concreto': 4.8, 'mato': 1.3, 'madeira': -3.2, 'corredor': -.4, 'carpete': -.5, 'arrasto': -2.3}   # iguala o volume percebido entre superfícies (medido: RMS 300 ms)
PES = json.load(open('material/qa/pes.json'))          # fração do ciclo 'walk' em que cada pé toca o chão (videos/_pes)
def passos(pl, t0, t1, L, quem, sup, gain=0, passo=1.45, pan=0, e=.18, fase=0.0):
    """um som por CONTATO do pé (como notify de animação): o motor anda u·L/passo ciclos (+fase em ciclos)."""
    pc = passo * ALT[quem] / 1.75; v = 1 / (1 - e)
    def u_de(u0): return v * u0 * u0 / (2 * e) if u0 < e else (1 - v * (1 - u0) ** 2 / (2 * e) if u0 > 1 - e else v * (u0 - e / 2))
    cont = sorted((n + PES[quem][pe] - fase, pe) for n in range(-1, int(L / pc) + 3) for pe in ('L', 'R'))
    for c, pe in cont:
        d = c * pc
        if d <= .02 or d > L: continue
        alvo, a, b = d / L, 0.0, 1.0
        for _ in range(30): m = (a + b) / 2; a, b = (m, b) if u_de(m) < alvo else (a, m)
        _seed[0] += 1; cue('pisada', P(pl) + t0 + a * (t1 - t0), sup=sup, peso=PESO[quem], seed=_seed[0], gain=gain + OFF[sup] + (-1.5 if pe == 'L' else 0), pan=pan + (.06 if pe == 'R' else -.06))
# camadas longas de clima
cue('drone', 0, d=26, root=31, gain=-4); cue('drone', P('44') + 20, d=17, root=29, gain=-3); cue('drone', P('46'), d=37, root=31, gain=-2); cue('drone', P('51'), d=55, root=31, gain=-3)
# 41 estrada
cue('chiado', 0, d=2, gain=-6); cue('motor', 2, d=8); cue('pneus', 2, d=8); cue('grilos', 2, d=8); cue('motor', 10, d=7, abafado=1, gain=-3)
# 42 nicolas
cue('motor', P('42'), d=9, abafado=1, gain=-3); cue('radio', P('42'), d=9, gain=-6)
# 43 posto
cue('motor', P('43'), d=4.5, gain=-4); cue('pneus', P('43'), d=4.2, gain=-4); cue('lampada', P('43'), d=22, rede=60, pisca=0, gain=-12); cue('grilos', P('43'), d=22, gain=-8)
cue('click', P('43') + 5.0, gain=-2); cue('turbina', P('43') + 5.1, d=.9, gain=-16); cue('click', P('43') + 13.15, gain=-4); cue('tick', P('43') + 14.65, gain=-4); cue('click', P('43') + 15.3, gain=-3); cue('turbina', P('43') + 15.4, d=2.9, gain=-10); cue('click', P('43') + 18.32, gain=-5); cue('tick', P('43') + 18.95, gain=-4); cue('click', P('43') + 20.3, gain=-4)
import math as _m
for a, b, L in ((5, 7, 1.91), (11.2, 12.3, 2.9), (13.9, 14.5, .76), (19.0, 19.7, .76), (20.6, 21.45, 2.9)): passos('43', a, b, L, 'frentista', 'concreto', gain=-2)
cue('paper', P('43') + 21.8, gain=-6)
passos('43', 22.4, 26.8, 6.3, 'frentista', 'concreto', gain=-6)          # vai embora: some ao longe
# 44 mendigo
cue('lampada', P('44'), d=37, rede=60, pisca=0, gain=-12); cue('grilos', P('44'), d=37, gain=-8); cue('motor', P('44') + .6, d=31, abafado=1, gain=-8)
passos('44', .2, 1.63, 1.51, 'metalis', 'arrasto', gain=-3, passo=1.2, e=.12); passos('44', 1.63, 3.6, 2.07, 'metalis', 'arrasto', gain=-3, passo=1.2, e=.12, fase=1.51 / (1.2 * 1.1 / 1.75)); passos('44', 31.4, 32.3, .67, 'metalis', 'arrasto', gain=-5, passo=.9)
cue('tick', P('44') + 25.35, gain=-1); cue('turbina', P('44') + 31.2, d=.8, gain=-16)
cue('sobe', P('44') + 20, d=14, root=29, sem=3, gain=-8); cue('motor', P('44') + 32.2, d=4.8, rpm=1.4, gain=-2); cue('pneus', P('44') + 32.4, d=4.6, gain=-3)
# 45 título
cue('sobe', P('45'), d=4, root=31, sem=7, gain=-7); cue('boom', P('45') + 2.6, gain=-9); cue('motor', P('45'), d=7, gain=-14)
# 46 casmiron
cue('motor', P('46'), d=12, gain=-5); cue('pneus', P('46'), d=12, gain=-5); cue('grilos', P('46'), d=12, gain=-6); cue('sobe', P('46') + 4, d=8, root=34, sem=8, gain=-4)
for t in (4, 6, 8, 10): cue('heart', P('46') + t)
cue('boom', P('46') + 11.85, gain=-5)
# 47 cabana
cue('motor', P('47'), d=4.5, gain=-5); cue('pneus', P('47'), d=4.5, gain=-4); cue('motor', P('47') + 4.5, d=.8, rpm=.6, gain=-6); cue('click', P('47') + 5.2, gain=-2)
cue('grilos', P('47'), d=12, gain=-8); cue('cut', P('47') + 10.6, gain=-4)
passos('47', 11.05, 13, 6.13, 'adryan', 'mato', gain=-1)
# 48 senha
cue('grilos', P('48'), d=10, gain=-10); passos('48', 9.2, 10.6, 2.4, 'adryan', 'madeira', gain=-3)
for k in range(3): cue('cut', P('48') + 1.0 + k * .32, gain=2)
cue('click', P('48') + 2.8, gain=-2); cue('whoosh_slow', P('48') + 8.6, gain=-6)
# 49 olhos
cue('grilos', P('49'), d=8, gain=-6); cue('chiado', P('49') + 1.5, d=1.2, gain=-14); cue('sobe', P('49') + 2, d=6, root=27, sem=2, gain=-6)
for t in (3, 3.8, 4.6, 5.4, 6.2, 7.0): cue('heart', P('49') + t, gain=-2)
cue('boom', P('49') + 7.8, gain=-8)
# 50 elevador
cue('lampada', P('50'), d=24, rede=60, pisca=[.4, .55, 4.9, 5.05, 9.6, 9.72, 16.2, 16.3], gain=2); cue('ding', P('50') + .8); cue('whoosh_slow', P('50') + 1.0, gain=-4)
passos('50', 2.4, 17.8, 10.3, 'gusta', 'corredor', gain=-5, passo=1.3, pan=.15); passos('50', 2.4, 17.8, 10.3, 'adryan', 'corredor', gain=-6, passo=1.3, pan=-.15, fase=.4 / 1.083)
# 51 sala do Igor
cue('rede', P('51'), d=14, gain=-8)
t = .5
while t < 6.5: cue('type', P('51') + t, gain=-2); t += .14 + (math.sin(t * 37) + 1) * .06
# 52 arquivos
cue('whoosh_slow', P('52') + .3, gain=-6); passos('52', .3, 3.6, 2.47, 'adryan', 'carpete', gain=0, pan=.1); passos('52', .3, 3.6, 2.38, 'gusta', 'carpete', gain=-1, pan=-.1); cue('cut', P('52') + 4.6, gain=-8)
for t in (5.6, 6.9, 8.2, 9.5): cue('paper', P('52') + t, gain=2)
# 53 projeto mogg
cue('click', P('53') + 1.2, gain=5); cue('click', P('53') + 1.55, gain=5); cue('whoosh_slow', P('53') + 1.8, gain=-10); cue('chiado', P('53') + 3, d=6, gain=-6); cue('paper', P('53') + 9.6, gain=4)
# 54 computador
cue('cut', P('54') + 2.65, gain=-7); cue('turbina', P('54') + 2.7, d=1.3, gain=-9); cue('ui_blip', P('54') + 3.2); cue('lamp_click', P('54') + 3.7, gain=2); cue('rede', P('54') + 3.7, d=12, gain=-6)
t = .2
while t < 4: cue('type', P('54') + 4.5 + t, gain=3); t += .13 + (math.sin(t * 37) + 1) * .05
for t in (12.0, 12.8, 13.6, 14.4): cue('ui_blip', P('54') + t)
cue('chiado', P('54') + 13, d=3, gain=-3)
# 55 tela
cue('ui_blip', P('55') + .3); cue('ui_blip', P('55') + 1.2); cue('click', P('55') + 3.4, gain=6); cue('ui_blip', P('55') + 3.85); cue('chiado', P('55'), d=9, gain=-4)
for k in range(20): cue('tick', P('55') + 4 + k * .24)
# 56 final
cue('chiado_sobe', P('56'), d=7.0); cue('estrondo', P('56') + 7.0, d=.9, gain=-3); cue('boom', P('56') + 7.0, gain=-2); cue('chiado', P('56') + 7.05, d=.83, gain=14)
os.makedirs('videos/00-filme4', exist_ok=True)
json.dump({'dur': FIM, 'bpm': 120, 'fps': 30, 'music': {'style': 'nenhum'}, 'cues': Cs}, open('videos/00-filme4/cues.json', 'w'), indent=1)
json.dump({'segments': SEG}, open('videos/00-filme4/narration.json', 'w'))
print(f'{len(Cs)} cues · {len(SEG)} falas · {len(LEG)} legendas · {FIM} s')
