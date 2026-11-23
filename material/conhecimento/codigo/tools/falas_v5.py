"""Falas novas da v5 (cena da maleta aberta e cena do Dom), com voz clonada LOCALMENTE (Chatterbox multilíngue).
Adryan: referência = as falas dele já usadas no filme (mesma voz). Igor: audio/voz/igor-ref.wav.
Dom: voz PÚBLICA (a voz padrão do modelo aberto, de ninguém identificável), depois engrossada e tratada como vilão (tools/vilao.sh).
uso: <venv>/bin/python tools/falas_v5.py [--tomadas N]"""
import sys, os, subprocess, glob, torch, torchaudio
N = int(sys.argv[sys.argv.index('--tomadas') + 1]) if '--tomadas' in sys.argv else 3
FALAS = {
 'adryan': [('p5a', "O que eu disse, caralho? Que não era pra abrir a maleta!"), ('p5b', "Não sei por que o Igor deu a confiança em você.")],
 'igor': [('p15a', "Como, caralho, isso aconteceu? Como?!"), ('p15b', "Dom?! É você?")],
 'dom': [('p15', "Finalmente... depois de tanto tempo, nos encontramos. Dessa vez você não vai escapar, Igor.")],
}
os.makedirs('audio/voz/v5/ref', exist_ok=True)
ref_ad = 'audio/voz/v5/ref/adryan_ref.wav'
if not os.path.exists(ref_ad):
    clips = sorted(glob.glob('audio/voz/v4/cortadas/adryan_p*.wav'))[:6]
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *sum([['-i', c] for c in clips], []), '-filter_complex', ''.join(f'[{i}:a]' for i in range(len(clips))) + f'concat=n={len(clips)}:v=0:a=1,loudnorm=I=-18', '-ar', '24000', '-ac', '1', ref_ad], check=True)
import perth
if perth.PerthImplicitWatermarker is None: perth.PerthImplicitWatermarker = perth.DummyWatermarker
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
for p, linhas in FALAS.items():
    ref = {'adryan': ref_ad, 'igor': 'audio/voz/igor-ref.wav', 'dom': None}[p]
    os.makedirs(f'audio/voz/v5/{p}', exist_ok=True)
    for nome, txt in linhas:
        for i in range(N):
            torch.manual_seed(21 + i)
            kw = dict(language_id='pt', exaggeration=.75 if p == 'dom' else .55, cfg_weight=.4 if p == 'dom' else .5, temperature=.7)
            w = m.generate(txt, audio_prompt_path=ref, **kw) if ref else m.generate(txt, **kw)
            out = f'audio/voz/v5/{p}/{nome}-{i+1}.wav'; torchaudio.save(out, w, m.sr); print('ok', out, round(w.shape[-1] / m.sr, 2), 's', flush=True)
