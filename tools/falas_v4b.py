"""Falas novas do v4 (Gusta + Adryan no elevador), voz clonada localmente (Chatterbox). uso: <venv>/bin/python tools/falas_v4b.py"""
import os, subprocess, torch, torchaudio, perth
if perth.PerthImplicitWatermarker is None: perth.PerthImplicitWatermarker = perth.DummyWatermarker
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
FALAS = {
 'gusta': [('p8a', "Senha?"), ('p8b', "Pode entrar."),
  ('p10a', "Sabe. Mas não é qualquer pessoa que pode ficar sabendo dessa missão."),
  ('p10b', "Porque o Projeto Mogg é importante demais. Isso não pode ser comentado em qualquer lugar. Nem mesmo fora daqui."),
  ('p10c', "Você vai entender quando encontrar o Igor.")],
 'adryan': [('p10a', "Então... o Igor já sabe que a gente tá chegando?"), ('p10b', "Por quê?")],
}
import sys
if 'curtas' in sys.argv:  # falas curtas: mais tomadas, o Whisper escolhe
    FALAS = {'gusta': [('p8a', "Senha?"), ('p8a', "Qual a senha?"), ('p8b', "Pode entrar."), ('p10s', "Sabe.")]}
N = 6 if 'curtas' in sys.argv else 2
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
for p, L in FALAS.items():
    ref = f"audio/voz/v4/ref/{p}_ref.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"audio/voz/v4/ref/{p}_amostra.mp3", "-af", "highpass=f=70,afftdn=nf=-28,loudnorm=I=-18", "-ar", "24000", "-ac", "1", ref], check=True)
    os.makedirs(f"audio/voz/v4/{p}", exist_ok=True)
    for k, (nome, txt) in enumerate(L):
        for i in range(N):
            torch.manual_seed(41 + i + 100 * k)
            w = m.generate(txt, language_id="pt", audio_prompt_path=ref, exaggeration=.45, cfg_weight=.5, temperature=.7)
            out = f"audio/voz/v4/{p}/{nome}-{i+1+(10*k if N>2 else 0)}.wav"; torchaudio.save(out, w, m.sr); print("ok", out, round(w.shape[-1] / m.sr, 2), flush=True)
