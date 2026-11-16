# THE GREEN PATH — feito por Igor Anão

Vídeo 16:9, 1920×1080, 30 fps, 90 s, estilo PS1 (skill `video-lowpoly-ps1` em `.claude/skills/`).

## Montar o filme
```bash
npm install
bash tools/baixar-itch.sh        # modelos gratuitos do itch.io (ficam fora do git) — precisa do Blender
python3 -m venv audio/.venv && audio/.venv/bin/pip install numpy scipy pillow
bash tools/filme.sh              # som + render dos 10 planos + junta → out/the-green-path.mp4
PLANOS="07" bash tools/filme.sh  # refaz só um plano e junta de novo
node render.mjs 03 --at=1,4,7    # preview de um plano → previews/
```

## Onde está cada coisa
- `videos/01-estrada … 10-final/` — um plano por pasta (tudo é função de `t`).
- `lib/ps1.js`, `lib/arh.js` — motor da skill (com esqueleto, pontilhado de 1 bit e casca de contorno acrescentados).
- `lib/modelo.js` — carrega GLB/FBX e troca os materiais por `P.mat`.
- `lib/tgp.js` — Igor, Phantom, maleta, fita VHS, mesa. `lib/filme.js` — carro, estrada, placa, casa, corredor, computador. `lib/terminal.js` — telas verdes e perda de sinal.
- `tools/som.py` — roteiro de som (cues + voz) → `audio/synth.py` sintetiza. `tools/clonar_voz.py` — clona a voz localmente (Chatterbox).
- `material/` — floppa.jpg, logo, modelos convertidos pra GLB, créditos. `audio/voz/` — voz original e a fala gerada.
- `edicao/` — projeto Remotion (vazio) caso queira edição extra por cima do MP4.
