"""EPISÓDIO 1 (reformulado) — falas novas com ATUAÇÃO (crítica do público: "parecem lidas"), geradas LOCALMENTE (Chatterbox multilíngue).
Cada fala tem a intensidade própria (exaggeration alto = mais emoção; cfg baixo = ritmo mais solto) e várias tomadas; depois escolhe-se
a melhor (audio/voz/ep1/ESCOLHIDAS.txt) e trata-se (tools/tratar_voz.sh: compressão, EQ e a sala).
Referências: Igor = audio/voz/igor-ref.wav (voz do dono do projeto) · Adryan/Gusta = as falas deles já usadas no v4 (mesma voz) ·
Dom = voz pública do modelo (ninguém identificável) + tools/vilao.sh · Oliveira/Luan = vozes LIVRES Piper pt_BR (CC0), material/vozes_livres.
uso: <venv-chatterbox>/bin/python tools/falas_ep1.py [quem...] [--tomadas N]"""
import sys, os, subprocess, glob, torch, torchaudio
N = int(sys.argv[sys.argv.index('--tomadas') + 1]) if '--tomadas' in sys.argv else 4
SO = [a for a in sys.argv[1:] if not a.startswith('--') and not a.isdigit()]
# (id, texto, exaggeration, cfg_weight, temperatura) — exaggeration .5 = neutro · .7–.9 = emoção forte · cfg .3 = fala mais solta/rápida
FALAS = {
 'igor': [('i66', "Preciso apagar imediatamente os experimentos que o Wallen fez.", .6, .45, .75),
          ('i67', "Então... o ARG-14.", .55, .5, .7),
          ('i64', "Então é isso. O ARG-14.", .6, .45, .7),
          ('i69', "Aaah!", .95, .3, .9),
          ('i70', "Malditos! Eles me acharam!", .9, .3, .85),
          ('i71a', "Fecha essa porta imediatamente!", .9, .3, .85),
          ('i71c', "Fécha essa porta! Imediatamente!", .85, .35, .8),        # mesma fala, grafia que ajuda a pronúncia do "Fecha" (o modelo falava "Deixa")
          ('i71b', "Ele vai ficar bem. O Nicolas conhece os procedimentos de sobrevivência.", .6, .4, .75)],   # frase aprovada pelo diretor (25/11)
 'adryan': [('a71', "Mas é o Nicolas, ele tá só!", .9, .3, .85)],
 'gusta': [('g71', "Ele vai ficar bem. Mas se ficar na rebeldia, iremos morrer.", .7, .35, .8),
           ('g10b', "Porque o ARG-14 é importante demais. Isso não pode ser comentado em qualquer lugar. Nem mesmo fora daqui.", .5, .5, .7)],
}
os.makedirs('audio/voz/ep1/ref', exist_ok=True)
def ref_de(quem, padrao):
    out = f'audio/voz/ep1/ref/{quem}_ref.wav'
    if not os.path.exists(out):
        clips = sorted(glob.glob(padrao))[:6]
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *sum([['-i', c] for c in clips], []), '-filter_complex',
                        ''.join(f'[{i}:a]' for i in range(len(clips))) + f'concat=n={len(clips)}:v=0:a=1,loudnorm=I=-18', '-ar', '24000', '-ac', '1', out], check=True)
    return out
REF = {'igor': 'audio/voz/igor-ref.wav', 'adryan': ref_de('adryan', 'audio/voz/v4/cortadas/adryan_p*.wav'), 'gusta': ref_de('gusta', 'audio/voz/v4/cortadas/gusta_p*.wav')}
import perth
if perth.PerthImplicitWatermarker is None: perth.PerthImplicitWatermarker = perth.DummyWatermarker   # (marca-d'água indisponível neste Python, como no v5)
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
for quem, linhas in FALAS.items():
    if SO and quem not in SO: continue
    os.makedirs(f'audio/voz/ep1/{quem}', exist_ok=True)
    for nome, txt, ex, cfg, temp in linhas:
        for i in range(N):
            out = f'audio/voz/ep1/{quem}/{nome}-{i+1}.wav'
            if os.path.exists(out): continue
            torch.manual_seed(31 + i)
            w = m.generate(txt, language_id='pt', audio_prompt_path=REF.get(quem), exaggeration=ex, cfg_weight=cfg, temperature=temp)
            torchaudio.save(out, w, m.sr); print('ok', out, round(w.shape[-1] / m.sr, 2), 's', flush=True)
