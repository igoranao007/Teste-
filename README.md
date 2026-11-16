# Animação PS1 → MP4

Ferramentas instaladas (ainda sem cena; as cenas vêm do roteiro).

| Ferramenta | Pra quê |
|---|---|
| **Three.js** + `@react-three/fiber` | cena 3D com visual PS1 (`src/ps1/`) |
| **Remotion** (+ transitions, captions, three) | edição final, textos, legendas, transições → MP4 |
| **Blender 5.3** (`blender`) | converter e limpar modelos (FBX/OBJ → GLB), low-poly |
| **ffmpeg** | juntar vídeo e áudio, tratar a voz |
| **faster-whisper** | legendas automáticas a partir da sua voz |

## Pastas
- `public/models/` – modelos PSX baixados (.glb de preferência)
- `public/textures/` – texturas
- `audio/voz/` – sua voz gravada
- `audio/musica/`, `audio/sfx/` – música e efeitos (ElevenLabs etc.)

## Utilitários PS1 (`src/ps1/`)
- `ps1Material.ts` – vertex snapping, texturas sem filtro, cor 15-bit com dither
- `PS1Canvas.tsx` – renderiza em 320px e amplia pixelado
- `Model.tsx` – carrega .glb de `public/models/` já com visual PS1
- `CameraRig.tsx` – câmera por keyframes

## Comandos
```bash
npm run studio                                   # prévia no navegador
npm run render                                   # out/video.mp4
bash scripts/voice-clean.sh bruto.m4a audio/voz/voz.wav
python3 scripts/transcribe.py audio/voz/voz.wav src/captions.json
bash scripts/mix-audio.sh out/video.mp4 audio/voz/voz.wav audio/musica/musica.mp3
blender -b -P script.py                          # Blender sem interface
```
