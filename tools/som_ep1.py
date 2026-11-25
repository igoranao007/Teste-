"""THE GREEN PATH — A SILENT WAR · EPISÓDIO 1 (reformulado): som de CADA CENA, no mesmo formato do v4 (tools/som4.py).
Pra cada cena escreve videos/<cena>/cues.json (efeitos sintetizados por audio/synth.py) e videos/<cena>/narration.json
(falas + sons gravados dos pacotes, com 'ganho' = som de cena sem cadeia de voz), e material/voz-ep1.json (volume da voz por
quadro, pra boca/cabeça). Depois: audio/.venv/bin/python audio/synth.py <cena> → audio/<cena>.wav
uso: audio/.venv/bin/python tools/som_ep1.py [prefixos...]      (sem prefixo = todas as cenas)"""
import json, os, subprocess, sys
import numpy as np
from scipy.io import wavfile
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R)
C4 = 'audio/voz/v4/cortadas/'
OGA = 'material/modelos/oga/100-CC0-SFX_0/'          # 100 CC0 SFX (OpenGameArt, CC0)
os.makedirs('audio/voz/ep1/mix', exist_ok=True)

# ── passos sincronizados com o motor (mesma conta do tools/som4.py: um som por contato do pé) ──
ALT = {'adryan': 1.76, 'gusta': 1.80, 'nicolas': 1.62, 'frentista': 1.74, 'metalis': 1.38}
PESO = {'adryan': .9, 'gusta': 1.0, 'nicolas': .8, 'frentista': 1.0, 'metalis': .6}
OFF = {'concreto': 4.8, 'mato': 1.3, 'madeira': -3.2, 'corredor': -.4, 'carpete': -.5, 'arrasto': -2.3}
PES = json.load(open('material/qa/pes.json'))

class Cena:
    def __init__(self, nome, dur): self.nome, self.dur, self.cues, self.segs, self.voz, self._seed = nome, dur, [], [], [], 0
    def cue(self, tipo, t, **o): self.cues.append({'type': tipo, 't': round(t, 3), **o})
    def passos(self, t0, t1, L, quem, sup, gain=0, passo=1.45, pan=0, e=.18, fase=0.0, ate=None):
        pc = PES[quem].get('passada', passo * ALT[quem] / 1.75); v = 1 / (1 - e)
        def u_de(u0): return v * u0 * u0 / (2 * e) if u0 < e else (1 - v * (1 - u0) ** 2 / (2 * e) if u0 > 1 - e else v * (u0 - e / 2))
        cont = sorted((n + PES[quem][pe] - fase, pe) for n in range(-1, int(L / pc) + 3) for pe in ('L', 'R'))
        for c, pe in cont:
            d = c * pc
            if d <= .02 or d > L: continue
            alvo, a, b = d / L, 0.0, 1.0
            for _ in range(30): m = (a + b) / 2; a, b = (m, b) if u_de(m) < alvo else (a, m)
            if ate is not None and t0 + a * (t1 - t0) > ate: continue
            self._seed += 1
            self.cue('pisada', t0 + a * (t1 - t0), sup=sup, peso=PESO[quem], seed=self._seed, gain=gain + OFF[sup] + (-1.5 if pe == 'L' else 0), pan=pan + (.06 if pe == 'R' else -.06))
    def som(self, arq, t, ganho=0, filtro=None):
        """som gravado (pacote CC0) tocado como 'som de cena' (sem cadeia de voz, sem abaixar o resto)."""
        out = f'audio/voz/ep1/mix/{self.nome[:2]}_{len(self.segs):02d}.wav'
        af = 'afade=t=in:d=0.005' + (',' + filtro if filtro else '')
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', arq, '-af', af, '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s16le', out], check=True)
        sr, v = wavfile.read(out); self.segs.append({'file': out, 'start': round(t, 3), 'dur': round(len(v) / sr, 2), 'ganho': ganho})
    def fala(self, arq, t, quem, texto):
        out = f'audio/voz/ep1/mix/{self.nome[:2]}_{len(self.segs):02d}.wav'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', arq, '-af', 'highpass=f=75,afade=t=in:d=0.02', '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s16le', out], check=True)
        sr, v = wavfile.read(out); v = v.astype(np.float64) / 32768; q = int(sr / 30)
        env = [float(np.sqrt(np.mean(v[k:k + q] ** 2))) for k in range(0, len(v), q)]; mx = max(env) or 1
        env = [round(min(1, (e / mx) ** .6 * 1.15) if e / mx > .08 else 0, 2) for e in env]
        self.voz.append({'t': t, 'env': env, 'quem': quem, 'texto': texto})
        self.segs.append({'file': out, 'start': round(t, 3), 'dur': round(len(v) / sr, 2)})
    def gravar(self):
        d = f'videos/{self.nome}'
        json.dump({'dur': self.dur, 'bpm': 120, 'fps': 30, 'music': {'style': 'nenhum'}, 'cues': self.cues}, open(f'{d}/cues.json', 'w'), indent=1)
        json.dump({'segments': self.segs}, open(f'{d}/narration.json', 'w'), indent=1)
        print(f'{self.nome}: {len(self.cues)} cues, {len(self.segs)} sons/falas')

# ═══ 60 · POSTO ═══ (0–24 s = o plano 43 do v4, com o mesmo som; depois alojamento, pedra e o Adryan saindo)
def cena60():
    c = Cena('60-ep1-posto', 40)
    c.cue('motor', 0, d=4.5, gain=-4); c.cue('pneus', 0, d=4.2, gain=-4); c.cue('lampada', 0, d=40, rede=60, pisca=0, gain=-12); c.cue('grilos', 0, d=40, gain=-8)
    for t, g in ((5.0, -2), (13.15, -4), (15.3, -3), (18.32, -5), (20.55, -4)): c.cue('click', t, gain=g)
    c.cue('turbina', 5.1, d=.9, gain=-16); c.cue('tick', 14.65, gain=-4); c.cue('turbina', 15.4, d=2.9, gain=-10); c.cue('tick', 18.95, gain=-4)
    for a, b, L in ((5, 7, 1.91), (9.6, 11.9, 2.9), (13.9, 14.5, .76), (19.25, 20.05, .76), (20.85, 23.0, 2.9)): c.passos(a, b, L, 'frentista', 'concreto', gain=-2)
    c.cue('paper', 23.4, gain=-6)
    c.fala(C4 + 'adryan_p3a-1.wav', 5.6, 'adryan', 'Boa noite. Completa pra mim.')
    c.fala(C4 + 'adryan_p3b-2.wav', 14.2, 'adryan', 'Movimento fraco hoje, hein?')
    c.fala(C4 + 'adryan_p3c-1.wav', 18.6, 'adryan', 'Beleza... também não precisa conversar.')
    # frentista: janela → porta do alojamento → entra → mesa (distâncias medidas no motor)
    c.passos(24.4, 28.0, 4.82, 'frentista', 'concreto', gain=-9)
    c.som(OGA + 'door_open.ogg', 28.5, ganho=-14)
    c.passos(29.1, 30.2, 2.37, 'frentista', 'concreto', gain=-10)
    c.som(OGA + 'door_close_03.ogg', 30.45, ganho=-4)                                    # a porta bate
    c.passos(31.0, 33.0, 3.6, 'frentista', 'madeira', gain=-16)                           # lá dentro, abafado
    # a pedra: assobio curto no ar, PANCADA no teto (metal oco) e quica no chão
    c.cue('swoosh', 31.25, gain=-20)
    c.som(OGA + 'metal_05.ogg', 31.6, ganho=0)
    c.som(OGA + 'hit_02.ogg', 32.1, ganho=-14)
    c.cue('drone', 31.6, d=8.4, root=29, gain=-6)                                         # tensão a partir da pancada
    c.cue('sobe', 37.6, d=2.4, root=29, sem=3, gain=-10)
    # o Adryan abre a porta do carro e sai
    c.cue('carro_abre', 33.3, gain=-4)
    c.passos(35.4, 37.0, 1.69, 'adryan', 'concreto', gain=-4)
    c.gravar(); return c

CENAS = {'60': cena60}
if __name__ == '__main__':
    pre = sys.argv[1:]; voz = json.load(open('material/voz-ep1.json')) if os.path.exists('material/voz-ep1.json') else {}
    for k, fn in CENAS.items():
        if pre and not any(k.startswith(p[:2]) for p in pre): continue
        c = fn(); voz[k] = c.voz
    json.dump(voz, open('material/voz-ep1.json', 'w'))
