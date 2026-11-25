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
    c = Cena('60-ep1-posto', 39)
    c.cue('motor', 0, d=4.5, gain=-4); c.cue('pneus', 0, d=4.2, gain=-4); c.cue('lampada', 0, d=39, rede=60, pisca=0, gain=-12); c.cue('grilos', 0, d=39, gain=-8)
    for t, g in ((5.0, -2), (13.15, -4), (15.3, -3), (18.32, -5), (20.55, -4)): c.cue('click', t, gain=g)
    c.cue('turbina', 5.1, d=.9, gain=-16); c.cue('tick', 14.65, gain=-4); c.cue('turbina', 15.4, d=2.9, gain=-10); c.cue('tick', 18.95, gain=-4)
    for a, b, L in ((5, 7, 1.91), (9.6, 11.9, 2.9), (13.9, 14.5, .76), (19.25, 20.05, .76), (20.85, 23.0, 2.9)): c.passos(a, b, L, 'frentista', 'concreto', gain=-2)
    c.cue('paper', 23.4, gain=-6)
    c.fala(C4 + 'adryan_p3a-1.wav', 5.6, 'adryan', 'Boa noite. Completa pra mim.')
    c.fala(C4 + 'adryan_p3b-2.wav', 14.2, 'adryan', 'Movimento fraco hoje, hein?')
    c.fala(C4 + 'adryan_p3c-1.wav', 18.6, 'adryan', 'Beleza... também não precisa conversar.')
    # frentista: janela → porta do alojamento (24,4–27,4) → entra (28,0–28,9) → a porta BATE (29,0) → lá dentro até a mesa (29,3–31,3)
    c.passos(24.4, 27.4, 4.82, 'frentista', 'concreto', gain=-9)
    c.som(OGA + 'door_open.ogg', 27.6, ganho=-16)
    c.passos(28.0, 28.9, 2.37, 'frentista', 'concreto', gain=-12)
    c.som(OGA + 'door_close_03.ogg', 29.0, ganho=-7)                                     # a porta bate (fora de quadro)
    c.passos(29.3, 31.3, 3.6, 'frentista', 'madeira', gain=-20)                           # lá dentro, abafado
    # a pedra: assobio curto no ar (27,9–28,5), PANCADA no teto (metal oco, 28,5) e quica no chão (29,05)
    c.cue('swoosh', 28.15, gain=-20)
    c.som(OGA + 'metal_05.ogg', 28.5, ganho=0)
    c.som(OGA + 'hit_02.ogg', 29.05, ganho=-15)
    c.cue('drone', 28.5, d=10.5, root=29, gain=-6)                                        # tensão a partir da pancada
    c.cue('sobe', 36.6, d=2.4, root=29, sem=3, gain=-10)
    # o Adryan abre a porta do carro (30,3), sai olhando o teto até a traseira (30,95–32,8), agacha e pega a pedra (34,0)
    c.cue('carro_abre', 30.3, gain=-4)
    c.passos(30.95, 32.8, 1.65, 'adryan', 'concreto', gain=-5)
    c.som(OGA + 'hit_01.ogg', 33.95, ganho=-22)                                           # a pedra raspa no chão quando ele pega
    c.gravar(); return c

# ═══ 61 · O METALIS ═══ (a conversa da moedinha do v4, agora os dois de pé; o Adryan volta pro carro e vai)
def cena61():
    c = Cena('61-ep1-metalis', 42)
    c.cue('lampada', 0, d=42, rede=60, pisca=0, gain=-12); c.cue('grilos', 0, d=42, gain=-8)
    c.cue('drone', 0, d=3, root=29, gain=-8)
    c.passos(1.8, 9.8, 6.4, 'metalis', 'arrasto', gain=-3, e=.12)
    c.som(OGA + 'hit_02.ogg', 8.95, ganho=-16)                                            # a pedra cai no chão
    c.cue('tick', 24.6, gain=-6)                                                           # a moeda sai do bolso
    c.som(OGA + 'bell_01.ogg', 25.85, ganho=-30)                                           # tilintar da moeda na mão dele
    c.passos(31.0, 32.7, 1.66, 'adryan', 'concreto', gain=-5)
    c.cue('carro_fecha', 33.5, gain=-3)
    c.cue('motor', 34.0, d=8, rpm=1.0, gain=-6); c.cue('motor', 34.6, d=5, rpm=1.4, gain=-2); c.cue('pneus', 34.8, d=4.8, gain=-3)
    c.cue('sobe', 37.0, d=5, root=29, sem=3, gain=-8)
    for arq, t, quem, txt in (('metalis_p4a-1', 2.4, 'metalis', 'Ô, Adryan! Meu parceiro! Tem uma moedinha aí?'),
                              ('adryan_p4a-2', 7.6, 'adryan', 'Ah, não... Metalis. Você de novo?'),
                              ('metalis_p4b-1', 10.4, 'metalis', 'Ué, vai me deixar na mão? Tô numa situação complicada, meu jovem.'),
                              ('adryan_p4b-1', 14.9, 'adryan', 'Você sempre tá numa situação complicada.'),
                              ('metalis_p4c-1', 20.6, 'metalis', 'É a vida, meu amigo. A vida não tá fácil pra ninguém.'),
                              ('adryan_p4c-1', 24.4, 'adryan', 'Toma. Agora deixa a gente ir.'),
                              ('metalis_p4d-1', 27.8, 'metalis', 'Sabia que podia contar contigo!'),
                              ('adryan_p4d-1', 30.2, 'adryan', 'Vai cuidar da tua vida, Metalis.'),
                              ('metalis_p4e-1', 35.0, 'metalis', 'Boa viagem!')):
        c.fala(C4 + arq + '.wav', t, quem, txt)
    c.gravar(); return c

# ═══ 62 · NICOLAS SOZINHO ═══ (plano 49 do v4 + a mão na arma nas costas)
def cena62():
    c = Cena('62-ep1-nicolas', 9)
    c.cue('grilos', 0, d=9, gain=-6); c.cue('chiado', 1.5, d=1.2, gain=-14); c.cue('sobe', 2, d=7, root=27, sem=2, gain=-6)
    c.cue('click', 3.35, gain=-10)                                                         # a mão fecha na coronha
    for t in (3.0, 3.8, 4.6, 5.4, 6.2, 7.0, 7.8): c.cue('heart', t, gain=-2)
    c.cue('boom', 8.8, gain=-8)
    c.gravar(); return c

CENAS = {'60': cena60, '61': cena61, '62': cena62}
if __name__ == '__main__':
    pre = sys.argv[1:]; voz = json.load(open('material/voz-ep1.json')) if os.path.exists('material/voz-ep1.json') else {}
    for k, fn in CENAS.items():
        if pre and not any(k.startswith(p[:2]) for p in pre): continue
        c = fn(); voz[k] = c.voz
    json.dump(voz, open('material/voz-ep1.json', 'w'))
