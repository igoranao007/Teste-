"""Clona a voz do dono do projeto LOCALMENTE (Chatterbox multilíngue, sem enviar o áudio pra fora) e gera a fala do Igor.
uso: <venv-com-chatterbox>/bin/python tools/clonar_voz.py audio/voz/original.mp3 "texto" audio/voz/igor [n_tomadas]
Precisa de: pip install chatterbox-tts   (baixa o modelo na primeira vez)"""
import sys, torch, torchaudio, subprocess, os
ref, texto, saida = sys.argv[1:4]; n = int(sys.argv[4]) if len(sys.argv) > 4 else 3
wav = saida + "-ref.wav"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", ref, "-af", "highpass=f=70,afftdn=nf=-28", "-ar", "24000", "-ac", "1", wav], check=True)
import perth
if perth.PerthImplicitWatermarker is None: perth.PerthImplicitWatermarker = perth.DummyWatermarker   # marca-d'água opcional indisponível neste Python
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
for i in range(n):
    torch.manual_seed(11 + i)
    w = m.generate(texto, language_id="pt", audio_prompt_path=wav, exaggeration=.45, cfg_weight=.5, temperature=.7)
    torchaudio.save(f"{saida}-{i+1}.wav", w, m.sr); print("ok", f"{saida}-{i+1}.wav", w.shape[-1] / m.sr, "s", flush=True)
