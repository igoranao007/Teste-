# Dom (base Simple PSX Character — JashiPSX, o mesmo do Adryan, Gusta, Nicolas e frentista) — fora do filme
- Rosto: foto `material/dom/dom.jpg` alinhada na geometria do pintor (`material/dom/rosto_alinhado.png`, olhos nivelados) e com os
  olhos reforçados pra não sumirem na textura de 256 px (`rosto_alinhado_olhos.png`).
- Textura: `ROUPA=dom CAB=40,34,30 CONTRASTE=1.3 QUENTE=1.0,0.95,0.9 python3 tools/pintar_jashi_vasco.py tris.json character_256.png material/dom/rosto_alinhado_olhos.png texturas/dom_512.png`
  (tris.json: todos os triângulos do modelo base com objeto e material, exportados pelo Blender).
  Casaco branco de manga comprida aberto em V, blusa preta de zíper, fivela laranja, gola alta, calça escura, sapato preto.
- Montagem e animação: `ROSTO_PLANO=-0.10 CALCA=1 blender ... montar_jashi.py -- texturas/dom_512.png dom.blend` → `rosto_foto.py` → `animar_jashi.py` → `exportar_glb.py`
  (10 animações: idle walk run talk wave sit cower attack hit death). Arquivo 3D fora do git (licença do JashiPSX).
- Rosto (escolha do diretor): a CARA da cabeça do elenco foi trocada pela foto NA PRÓPRIA MALHA — sem placa por cima, sem vão:
  `RZ1=1.965 RKX=0.8 RFYMIN=334 blender -b dom.blend --python tools/blender/rosto_foto.py -- material/dom/rosto_alinhado.png dom.blend`
  (separa as faces da frente da cabeça, do queixo à testa e entre as orelhas, num objeto "rosto" com o mesmo esqueleto; UV planar de frente
  na foto alinhada; a testa trava abaixo da aba do chapéu da foto). Rodar depois do montar_jashi.py (com `ROSTO_PLANO=-0.10`: frente sem nariz)
  e antes do animar_jashi.py. Cabelo, orelhas e nuca são do modelo do elenco. Piscada e boca: `acessoriosDom` redesenha a foto num canvas.
  Versões anteriores na folha: `?cabeca=plano|meia|inteira|mascara|elenco` (· `?semveu=1` pra ver a cabeça sem chapéu/véu/capa).
- Detalhes amarelos na roupa: debrum da abertura do casaco, punhos e barra.
- Capa de Hokage (`acessoriosDom`): branca, chamas amarelas na barra, "小人の隠れ家" (kobito no kakurega, "o esconderijo/toca do anão") na vertical
  nas costas (fonte IPAGothic), gola alta; presa ao tronco (spine.003).
- Chapéu cônico laranja/branco com 火 e véu: `await T.acessoriosDom(A)` (lib/tgp.js), presos ao osso da cabeça; `D.atualizar(t, { boca, pisca })`.
- Uso: `const A = await E4.ator('dom'); cena.add(A.obj); const D = await T.acessoriosDom(A);` e a cada quadro `D.atualizar(t, { boca, pisca })` · folha: `videos/98-dom` (?v=frente|tres|lado|costas|rosto &clip=walk).
- Versão antiga (corpo simples + cabeça procedural): `videos/98-dom?base=procedural`.
- **v2 da capa/chapéu/véu** (`acessoriosDom` em lib/tgp.js; rosto continua a FOTO, escolha do diretor):
  capa de PANO (malha 12×34 recalculada a cada quadro: `pano()`), aberta na frente com a abertura alargando pra baixo (pernas aparecem ao
  andar), ombros marcados, 9 dobras verticais, barra irregular, balanço atrasado (barra balança mais que o ombro), até a canela;
  DEBRUM ACESO amarelo + aura aditiva nas bordas da frente e na barra (a tecnologia do Dom, como a dos aliados); véu de pano com dobras e
  barra irregular que balança; chapéu com aba grossa, ARO ACESO amarelo por baixo e pino no topo.
  GOLA ALTA PRETA de zíper (a blusa da foto) fechada do ombro até logo abaixo do queixo; abaixo do queixo a foto do rosto vira pele com sombra
  (antes a malha do rosto mostrava o pescoço e a gola da FOTO esticados por ~11 cm).

## DOM LÍDER (v3) — desenho próprio por cima da referência de fã
A referência de fã ao Hokage (chapéu cônico com 火, capa branca com chamas, 小人の隠れ家) fica como estava; tudo o que é novo é desenho do projeto:
- Preso no corpo (`tools/blender/dom_lider.py`, roda no dom.blend DEPOIS do rosto_foto.py e ANTES do animar_jashi.py):
  medalhão-reator dourado no peito (aro com 8 raios, núcleo aceso), linhas de energia finas até ombros e punhos, braçadeiras douradas
  com borda acesa, placa do EMBLEMA na fivela. `blender -b dom.blend --python tools/blender/dom_lider.py -- dom_lider.blend` →
  `animar_jashi.py -- dom_anim.blend` → `exportar_glb.py -- dom_anim.glb`.
- Emblema da Toca do Anão (`tools/dom_emblema.py`): porta em arco de toca acesa, 3 pedras, hexágono dourado → `texturas/emblema*.png`.
- No motor (`acessoriosDom`): capote curto nos ombros (bordado grego dourado, emblema nas costas, barra acesa), bordado dourado nas bordas
  da capa, chapéu com faixa dourada acesa, reator no topo, contas e talismãs balançando; BASTÃO DE COMANDO na mão direita (anéis
  dourados, gaiola, núcleo aceso pulsando; `{ bastao: false }` tira); CÍRCULO DE COMANDO no chão (`D.comando(0..1)`; folha: `?comando=1`).
  O medalhão do GLB pulsa (materiais `d_nucleo_brilho`/`d_aura`).
- Folha: `folha_dom_lider.jpg` (videos/98-dom: `?v=frente|tres|lado|costas|mao|rosto&comando=1&clip=...`).
