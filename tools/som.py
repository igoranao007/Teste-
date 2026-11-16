"""Roteiro de som do filme inteiro (100 s): escreve videos/00-filme/cues.json + narration.json e o volume da voz por quadro
(material/voz-igor.json, pra boca do Igor). Depois: audio/.venv/bin/python audio/synth.py 00  → audio/00-filme.wav
uso: audio/.venv/bin/python tools/som.py [audio/voz/igor-2.wav]"""
import json, os, sys, subprocess, math
import numpy as np
from scipy.io import wavfile
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R)
# falas do Igor (voz clonada localmente com tools/clonar_voz.py): arquivo, plano, instante dentro do plano, até onde vale (s), texto
P7, P8, P9, P10, FIM = 54, 71, 85.5, 91.5, 97.5
FALAS = [
    ('audio/voz/igor-2.wav', 'p7', 4.7, 4.75, 'Você trouxe o arquivo. Sabe que é de extrema importância.'),
    ('audio/voz/falas/f2-1.wav', 'p7', 12.3, 2.4, 'Então é isso. O Projeto Mogg.'),
    ('audio/voz/falas/f3-2.wav', 'p8', 8.4, 2.1, 'Vamos ver o que a Federação escondeu.'),
]
BASE = {'p7': P7, 'p8': P8}
VOZ, SEG, LEG = {}, [], []
for i, (arq, plano, t0, corte, texto) in enumerate(FALAS):
    out = f'audio/voz/fala-{i + 1}.wav'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', arq, '-t', str(corte), '-af', f'highpass=f=75,afade=t=out:st={corte - .2:.2f}:d=0.2', '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s16le', out], check=True)
    sr, v = wavfile.read(out); v = v.astype(np.float64) / 32768; dur = len(v) / sr
    q = int(sr / 30); env = [float(np.sqrt(np.mean(v[k:k + q] ** 2))) for k in range(0, len(v), q)]; mx = max(env) or 1
    env = [round(min(1, (e / mx) ** .6 * 1.15) if e / mx > .08 else 0, 2) for e in env]
    VOZ.setdefault(plano, []).append({'t': t0, 'env': env})
    SEG.append({'file': out, 'start': BASE[plano] + t0, 'dur': round(dur, 2)}); LEG.append({'text': texto, 'startMs': int((BASE[plano] + t0) * 1000), 'endMs': int((BASE[plano] + t0 + dur + .3) * 1000)})
json.dump(VOZ, open('material/voz-igor.json', 'w'))
json.dump(LEG, open('edicao/src/legendas.json', 'w'), ensure_ascii=False, indent=1)
C = []
def cue(tipo, t, **o): C.append({'type': tipo, 't': round(t, 3), **o})
# camadas longas
cue('drone', 0, d=44.2, root=31); cue('drone', 46, d=25.5, root=31, gain=-2)
cue('chiado', 0, d=1.6, gain=-4)
# P1 estrada 0–8
cue('motor', 1.5, d=6.5); cue('pneus', 1.5, d=6.5); cue('grilos', 1.5, d=6.5)
for i, ch in enumerate('THE GREEN PATH'):
    if ch != ' ': cue('key', 3 + i * .12)
for i in range(0, 78, 2): cue('type', 6.05 + i / 62)
# P2 dentro do carro 8–20
cue('motor', 8, d=12, abafado=1, gain=-3); cue('radio', 8, d=12); cue('sobe', 13, d=7, root=31, sem=3, gain=-6)
# P3 a placa 20–28
cue('sobe', 20, d=8, root=34, sem=8); cue('motor', 20, d=4.2, gain=-4); cue('pneus', 20, d=4, gain=-3)
for t in (20, 22, 24, 26): cue('heart', t)
# P4 corte por cor 28–38
cue('boom', 28); cue('motor', 30, d=8, gain=-5); cue('pneus', 31, d=7, gain=-2); cue('grilos', 30, d=8); cue('whoosh_in', 37.2, gain=4); cue('motor', 36.6, d=1.5, rpm=1.5, gain=3)
# P5 a casa 38–46 (44–46: preto e silêncio)
cue('motor', 38, d=3.9, gain=-3); cue('pneus', 38, d=3.6); cue('grilos', 38, d=4); cue('motor', 42, d=2, abafado=1, rpm=.7, gain=-6); cue('ui_blip', 43.1, gain=-4); cue('click', 44.0, gain=6)
# P6 elevador 46–54
PISCA = [.35, .5, 2.9, 3.05, 3.2, 5.6, 5.72, 7.1]
cue('lampada', 46, d=8, rede=60, pisca=PISCA, gain=4); cue('ding', 47); cue('whoosh_slow', 47.2, gain=-4)
for k in range(9): cue('passo', 48.3 + k * .59)
# P7 Igor 54–71: plano geral (porta, lâmpada, passos), depois o plano médio (tempo interno t = T − 0,3)
cue('whoosh_slow', P7, gain=-6); cue('lamp_click', P7 + .9, gain=6); cue('lampada', P7 + .9, d=16, rede=60, pisca=0, gain=-9)
for k in range(5): cue('passo', P7 + .8 + k * .56, gain=-3)
M7 = P7 + .3
for k in range(5): cue('passo', M7 + 3.5 + k * .56, gain=-8)
cue('cut', M7 + 7.2, gain=-10)                  # a maleta pousa na mesa
cue('click', M7 + 9.7, gain=5); cue('click', M7 + 10.05, gain=5); cue('whoosh_slow', M7 + 10.3, gain=-10); cue('chiado', M7 + 11.5, d=5.2, gain=-4)
cue('paper', M7 + 15.25, gain=4)                # a mão pega a fita
# P8 computador 71–85,5 (videocassete nos primeiros 4,5 s)
cue('cut', P8 + 2.65, gain=-7); cue('turbina', P8 + 2.7, d=1.3, gain=-9); cue('ui_blip', P8 + 3.2); cue('lamp_click', P8 + 3.7, gain=2); cue('rede', P8 + 3.7, d=10.5, gain=-6)
t = .2
while t < 3.9: cue('type', P8 + 4.5 + t, gain=3); t += .13 + (math.sin(t * 37) + 1) * .05
for t in (7.1, 7.9, 8.7, 9.5): cue('ui_blip', P8 + 4.5 + t)
cue('chiado', P8 + 11.5, d=3, gain=-3)
# P9 Projeto Mogg 85,5–91,5
cue('ui_blip', P9 + .3); cue('ui_blip', P9 + 1.2); cue('click', P9 + 3.0, gain=6); cue('ui_blip', P9 + 3.45); cue('chiado', P9, d=6, gain=-4)
for k in range(11): cue('tick', P9 + 3.5 + k * .22)
# P10 final 91,5–97,5
cue('chiado_sobe', P10, d=5.0); cue('estrondo', P10 + 5.0, d=.9); cue('boom', P10 + 5.0, gain=2); cue('chiado', P10 + 5.05, d=.83, gain=14)
os.makedirs('videos/00-filme', exist_ok=True)
json.dump({'dur': FIM, 'bpm': 120, 'fps': 30, 'music': {'style': 'nenhum'}, 'cues': C}, open('videos/00-filme/cues.json', 'w'), indent=1)
json.dump({'segments': SEG}, open('videos/00-filme/narration.json', 'w'))
print(f'{len(C)} cues · {len(SEG)} falas · {FIM} s')
