"""Roteiro de som do filme inteiro (100 s): escreve videos/00-filme/cues.json + narration.json e o volume da voz por quadro
(material/voz-igor.json, pra boca do Igor). Depois: audio/.venv/bin/python audio/synth.py 00  → audio/00-filme.wav
uso: audio/.venv/bin/python tools/som.py [audio/voz/igor-2.wav]"""
import json, os, sys, subprocess, math
import numpy as np
from scipy.io import wavfile
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R)
voz = sys.argv[1] if len(sys.argv) > 1 else 'audio/voz/igor-2.wav'
FALA = 54 + 2 + 4.4
# voz: corta o silêncio das pontas, 48 kHz mono
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', voz, '-t', '4.75', '-af', 'highpass=f=75,afade=t=out:st=4.55:d=0.2', '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s16le', 'audio/voz/igor-fala.wav'], check=True)   # tomada 2: a fala vai de 0 a ~4,4 s
sr, v = wavfile.read('audio/voz/igor-fala.wav'); v = v.astype(np.float64) / 32768; dur = len(v) / sr
q = int(sr / 30); env = [float(np.sqrt(np.mean(v[i:i + q] ** 2))) for i in range(0, len(v), q)]; mx = max(env) or 1
env = [round(min(1, (e / mx) ** .6 * 1.15) if e / mx > .08 else 0, 2) for e in env]
json.dump(env, open('material/voz-igor.json', 'w'))
C = []
def cue(tipo, t, **o): C.append({'type': tipo, 't': round(t, 3), **o})
# camadas longas
cue('drone', 0, d=44.2, root=31); cue('drone', 46, d=28, root=31, gain=-2)
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
# P7 Igor 54–73,5 (a lâmpada acende em 55,2; o resto é o tempo antigo + 2 s)
P7 = 56
cue('lamp_click', 55.2, gain=6); cue('lampada', 55.2, d=18.3, rede=60, pisca=0, gain=-9)
for k in range(4): cue('passo', P7 + 4.1 + k * .56, gain=-8)
cue('cut', P7 + 7.2, gain=-10)                  # a maleta pousa na mesa
cue('click', P7 + 9.7, gain=5); cue('click', P7 + 10.05, gain=5); cue('whoosh_slow', P7 + 10.3, gain=-10); cue('chiado', P7 + 11.5, d=6, gain=-2)
cue('paper', P7 + 15.25, gain=4)                # a mão pega a fita
# P8 computador 73,5–88 (videocassete nos primeiros 4,5 s; depois o tempo antigo)
P8 = 73.5
cue('cut', P8 + 2.65, gain=-7); cue('turbina', P8 + 2.7, d=1.3, gain=-9); cue('ui_blip', P8 + 3.2); cue('lamp_click', P8 + 3.7, gain=2); cue('rede', P8 + 3.7, d=10.5, gain=-6)
t = .2
while t < 6.9: cue('type', P8 + 4.5 + t, gain=3); t += .13 + (math.sin(t * 37) + 1) * .05
for t in (7.1, 7.9, 8.7, 9.5): cue('ui_blip', P8 + 4.5 + t)
cue('chiado', P8 + 11.5, d=3, gain=-3)
# P9 Projeto Mogg 88–94
P9 = 88
cue('ui_blip', P9 + .3); cue('ui_blip', P9 + 1.2); cue('click', P9 + 3.0, gain=6); cue('ui_blip', P9 + 3.45); cue('chiado', P9, d=6, gain=-4)
for k in range(11): cue('tick', P9 + 3.5 + k * .22)
# P10 final 94–100
P10 = 94
cue('chiado_sobe', P10, d=5.0); cue('estrondo', P10 + 5.0, d=.9); cue('boom', P10 + 5.0, gain=2); cue('chiado', P10 + 5.05, d=.83, gain=14)
os.makedirs('videos/00-filme', exist_ok=True)
json.dump({'dur': 100, 'bpm': 120, 'fps': 30, 'music': {'style': 'nenhum'}, 'cues': C}, open('videos/00-filme/cues.json', 'w'), indent=1)
json.dump({'segments': [{'file': 'audio/voz/igor-fala.wav', 'start': FALA, 'dur': round(dur, 2)}]}, open('videos/00-filme/narration.json', 'w'))
print(f'{len(C)} cues · voz {dur:.2f} s em {FALA:.1f} s · {len(env)} quadros de boca')
