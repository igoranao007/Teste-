# 1. O projeto e o pipeline

## O filme
- **THE GREEN PATH** — curta 3D estilo **PlayStation 1 (PSX)**, 16:9, 1920×1080, 30 fps, por **Igor Anão** (o diretor).
- Versão atual **v5 (4:33)**. Personagens: **Adryan** (17, camisa do Vasco, dirige), **Nicolas** (14, Flamengo, carrega a maleta),
  **Frentista**, **Metalis** (mendigo estilo "Sonic sujo", olhos verdes que ficam amarelos), **Gusta** (terno, guarda da cabana),
  **Igor** (cabeça de caracal/"floppa" feita de foto, chefe da "Toca do Anão"), **Phantom**, **Dom** (vilão, chapéu de Hokage, aparece no fim).
- História (v5): estrada à noite → posto (frentista abastece, Metalis pede moeda) → título → maleta aberta no carro (POV) →
  placa de Casmiron City → cabana na mata (saída do carro, senha pela portinhola) → olhos na mata → elevador → sala do Igor →
  Projeto Mogg → fita VHS → chiado verde vira amarelo "LOCAL DESCOBERTO" → o Dom aparece no monitor → "EM BREVE".

## Arquitetura
```
videos/NN-nome/index.html   um PLANO por pasta; cena Three.js; tudo é função de t (S.update = t => {...}); determinístico
lib/ps1.js                  motor PS1: palco, P.mat (vértice "tremendo", cor 15 bits, pontilhado), P.luz, névoa, ?cam= de depuração
lib/v4.js                   ajudantes da v4: caminhar (trava do pé), ik2, pegar, dupla no carro, cabana, posto, mangueira, olhos...
lib/elenco4.js              carrega os atores (GLB com 10 animações) + AVALIADOR PRÓPRIO de animação (sem AnimationMixer)
lib/tgp.js                  personagens feitos em código (Igor, Dom procedural, Phantom), maleta, fita, acessórios do Dom
lib/filme.js                carro (vidro, volante, porta), estrada, placa, sala do Igor, computador, corredor
lib/terminal.js             telas de terminal verde, chiado, amarelar, aviso
render.mjs                  Playwright abre cada plano, captura quadro a quadro → ffmpeg → out/NN-nome.mp4
tools/som4.py               linha do tempo: PLANOS (ordem+duração), FALAS, cues de som, passos → cues.json/legendas
audio/synth.py              sintetiza todo o som a partir dos cues (numpy/scipy), mixa vozes, loudnorm −14 LUFS
edicao/ (Remotion)          monta os planos em sequência + legendas + fichas → out/the-green-path-v4.mp4
tools/filme4.sh             tudo: som → render dos planos → edição. PLANOS="44 57" refaz só esses
```

## Comandos que você vai usar
```bash
python3 tools/sintaxe.py                                   # SEMPRE antes de qualquer coisa
node tools/fotos.mjs 44-mendigo "4,5.5,12" "" saida.jpg    # fotos de instantes (3º arg = query: cam=x,y,z,ax,ay,az,fov · v= · etc.)
node tools/dbg_pagina.mjs 43-posto 12 "" "<expressão JS>"  # roda JS na página no instante t (medir ossos, raycast...)
node tools/qa.mjs 43-posto 1                               # QA quadro a quadro de um plano
PASSO=1 bash tools/qa_todos.sh                             # QA de todos (4 em paralelo); PLANOS="57-maleta 58-dom" pra alguns
audio/.venv/bin/python tools/som4.py                       # regenera linha do tempo/legendas
PLANOS="56 57" CONC=3 bash tools/filme4.sh                 # renderiza esses planos + som + edição
python3 tools/quadros_vazios.py out/the-green-path-v4.mp4  # acha câmera olhando pro nada
ffmpeg -i out/the-green-path-v4.mp4 -vf "fps=1,scale=240:-1,tile=8x6" folha.jpg   # folha de revisão
ffmpeg -i out/the-green-path-v4.mp4 -vf scale=1280:720 -c:v libx264 -crf 27 -preset slow -c:a aac -b:a 160k entrega/...-720p.mp4
```

## Duração de plano / acrescentar plano novo
- A ordem e a duração dos planos vivem em `PLANOS` no `tools/som4.py` (o Remotion lê de lá via `legendas4.json`).
- Plano novo: crie `videos/NN-nome/index.html` com `VIDEO={...dur:X}`, acrescente em `PLANOS` na posição certa, e em `tools/qa_todos.sh`.
  O prefixo de 2 dígitos precisa ser único (é a chave de `INI['NN']`). Ex.: 57-maleta fica entre 45 e 46 na ordem.
- Mudou a duração? Atualize `VIDEO.dur` E `PLANOS` E os cues que dependem do tempo.

## Entrega
- `entrega/the-green-path-v4-720p.mp4` (crf 27) — precisa ficar < 100 MB (limite do GitHub). Na v5 deu 93 MB: se crescer, use crf 28–29.
- Histórico: `out/historico/vX-720p.mp4` (fora do git) + tag git `vX-estavel` + `material/qa/VERSOES.md`.
