# 2. Apps e ferramentas usados

| App / biblioteca | Versão | Pra que serviu | Armadilhas |
|---|---|---|---|
| **Three.js** | r186 (`three@0.186`) | todo o 3D (cenas, personagens, IK) | `AnimationMixer`/`PropertyMixer` **só reescreve um osso quando o valor muda** → em pose parada, qualquer rotação aplicada por cima ACUMULA a cada quadro (cabeças girando, braço do Nicolas "tremendo"). Solução: avaliador próprio (ver 04). |
| **Playwright + Chromium** | 1.63 | abre cada plano e captura quadro a quadro; fotos de inspeção | já vem instalado no ambiente; **não rode `playwright install`**. Página com erro trava as ferramentas — sempre `python3 tools/sintaxe.py` antes. |
| **ffmpeg** | 6.1 | junta quadros, áudio, cortes, folhas de revisão, 720p, tratamento de voz | `afade=d=.7` inválido (use `0.7`). Pra trocar o tom sem mudar a velocidade: `asetrate=SR*k,aresample=SR,atempo=1/k`. |
| **Remotion** | 4.0.544 | edição final (sequência, legendas, fichas) | lê `edicao/src/legendas4.json` (gerado pelo som4.py). |
| **Blender** (headless) | 5.3 | montar/pintar/riggar personagens do pacote pago, retarget de animações, recortar o rosto do Dom, exportar GLB | sempre `blender -b --disable-autoexec arquivo.blend --python script.py -- args`. No mundo do Blender a frente do personagem é **−Y** e o alto é **+Z**; no GLB/Three a frente vira **+Z** e o alto **+Y**. |
| **Python 3.13 + numpy/scipy/Pillow** | — | síntese de som (`audio/synth.py`), pintura de texturas, ferramentas | o venv do som é `audio/.venv`. |
| **Chatterbox multilíngue** (Resemble AI, open source) | — | **clonagem de voz LOCAL** (sem mandar áudio pra fora) pras falas do Adryan, Igor, Gusta, Metalis e Dom | fica num venv separado (na sessão: `scratchpad/tts`). Às vezes "alucina" (tomada de 15 s pra uma frase de 3 s) → gere 3 tomadas e escolha. Lê nomes curtos errado: "Dom" virou "Então" — a grafia **"D'om"** resolveu. |
| **faster-whisper** (small) | — | conferir se a fala gerada diz o texto certo | o PyAV do sistema dá erro `metadata_errors` → passe o áudio como numpy (ffmpeg → s16le 16 kHz) em vez do caminho. |
| **IPAGothic / WenQuanYi** | fontes do sistema | texto japonês na capa do Dom (小人の隠れ家) | no canvas do navegador: `font = 'bold 30px IPAGothic'`. |
| Pacote pago **Simple PSX Character (JashiPSX)** | — | base do Adryan, Gusta, Nicolas, Frentista, Dom | **licença: NÃO pode ir pro git nem ser redistribuído** (`.gitignore` cobre `material/producao/modelos-pagos/**`). Só scripts e texturas próprias vão pro git. |
| Pacotes grátis do **itch.io** (PSX Office Pack CC0, Retro World, árvores...) | — | cenário (escritório do Igor, posto, árvores) | baixe com `tools/baixar-itch.sh` / `tools/itch_baixar.mjs`; créditos em `material/CREDITOS.md`. Esconda os LODs 1–3 dos pacotes de árvore (a LOD3 "flutuava" como arbusto preto). |
| **git** | — | versão; branch `claude/mp4-animation-threejs-remotion-xyh5wp` | commit em PT-BR terminando com as linhas de autoria; nunca commitar o pacote pago. |

## Ferramentas próprias criadas (em `tools/`)
- `qa.mjs` / `qa_todos.sh` — QA automático quadro a quadro (anatomia, colisão, continuidade, braço×corpo, pé deslizando, braço congelado, objeto flexível × corpo).
- `sintaxe.py` — checa a sintaxe de todas as libs e do script de cada plano (obrigatório).
- `quadros_vazios.py` — acha trechos com a câmera olhando pro nada (energia de bordas). `PROPOSITAL` lista os pretos de propósito.
- `fotos.mjs` — folha de fotos de instantes de um plano, com câmera de depuração (`cam=`).
- `dbg_pagina.mjs` — executa JS dentro da página num instante (medir ossos, posição, raycast). Ossos têm nomes sem ponto em `traverse` (`footL`), mas `A.osso('foot.L')` aceita o nome com ponto.
- `tremor.mjs`, `maos.mjs` — medem tremor/torção de ossos ao longo do tempo.
- `pintar_jashi_vasco.py` — pinta a textura do modelo JashiPSX (roupa por região 3D + rosto de foto). `ROUPA=frentista|terno|dom|vasco`.
- `blender/montar_jashi.py`, `animar_jashi.py`, `exportar_glb.py`, `rosto_foto.py` — montar, animar (10 clipes), exportar, trocar a cara pela foto.
- `som4.py` (linha do tempo), `falas_v4.py` / `falas_v5.py` (vozes), `vilao.sh` (voz de vilão).
