"""Gera as falas do roteiro v4 com voz clonada LOCALMENTE (Chatterbox multilíngue) a partir das amostras enviadas.
uso: <venv>/bin/python tools/falas_v4.py [personagem ...] [--tomadas N]"""
import sys, os, subprocess, torch, torchaudio
FALAS = {
 'adryan': [
  ('p1', "Essa maleta precisa chegar ao destino. Não é uma entrega qualquer. Tem coisa aí dentro que não pode simplesmente cair nas mãos de qualquer pessoa."),
  ('p2', "E você, Nicolas, não solta essa maleta por nada. Entendeu?"),
  ('p3a', "Boa noite. Completa pra mim."),
  ('p3b', "Movimento fraco hoje, hein?"),
  ('p3c', "Beleza... também não precisa conversar."),
  ('p4a', "Ah, não... Metalis. Você de novo?"),
  ('p4b', "Você sempre tá numa situação complicada."),
  ('p4c', "Toma. Agora deixa a gente ir."),
  ('p4d', "Vai cuidar da tua vida, Metalis."),
  ('p7', "Me entrega a maleta. Espera aqui fora e fica de olho em qualquer movimento."),
  ('p8', "Quinze do três, zero zero sete, Biff."),
 ],
 'metalis': [
  ('p4a', "Ô, Adryan! Meu parceiro! Tem uma moedinha aí?"),
  ('p4b', "Ué, vai me deixar na mão? Tô numa situação complicada, meu jovem."),
  ('p4c', "É a vida, meu amigo. A vida não tá fácil pra ninguém."),
  ('p4d', "Sabia que podia contar contigo!"),
  ('p4e', "Boa viagem!"),
 ],
}
args = [a for a in sys.argv[1:] if not a.startswith('--')]
N = int(sys.argv[sys.argv.index('--tomadas') + 1]) if '--tomadas' in sys.argv else 2
quem = [a for a in args if a in FALAS] or list(FALAS)
import perth
if perth.PerthImplicitWatermarker is None: perth.PerthImplicitWatermarker = perth.DummyWatermarker
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
for p in quem:
    ref = f"audio/voz/v4/ref/{p}_ref.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"audio/voz/v4/ref/{p}_amostra.mp3", "-af", "highpass=f=70,afftdn=nf=-28,loudnorm=I=-18", "-ar", "24000", "-ac", "1", ref], check=True)
    os.makedirs(f"audio/voz/v4/{p}", exist_ok=True)
    for nome, txt in FALAS[p]:
        for i in range(N):
            torch.manual_seed(7 + i)
            w = m.generate(txt, language_id="pt", audio_prompt_path=ref, exaggeration=.5 if p == 'metalis' else .45, cfg_weight=.5, temperature=.7)
            out = f"audio/voz/v4/{p}/{nome}-{i+1}.wav"; torchaudio.save(out, w, m.sr)
            print("ok", out, round(w.shape[-1] / m.sr, 2), "s", flush=True)
