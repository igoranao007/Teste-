# Dom (base Simple PSX Character — JashiPSX, o mesmo do Adryan, Gusta, Nicolas e frentista) — fora do filme
- Rosto: foto `material/dom/dom.jpg` alinhada na geometria do pintor (`material/dom/rosto_alinhado.png`, olhos nivelados) e com os
  olhos reforçados pra não sumirem na textura de 256 px (`rosto_alinhado_olhos.png`).
- Textura: `ROUPA=dom CAB=40,34,30 CONTRASTE=1.3 QUENTE=1.0,0.95,0.9 python3 tools/pintar_jashi_vasco.py tris.json character_256.png material/dom/rosto_alinhado_olhos.png texturas/dom_512.png`
  (tris.json: todos os triângulos do modelo base com objeto e material, exportados pelo Blender).
  Casaco branco de manga comprida aberto em V, blusa preta de zíper, fivela laranja, gola alta, calça escura, sapato preto.
- Montagem e animação: `CALCA=1 blender ... montar_jashi.py -- texturas/dom_512.png dom.blend` → `animar_jashi.py` → `exportar_glb.py`
  (10 animações: idle walk run talk wave sit cower attack hit death). Arquivo 3D fora do git (licença do JashiPSX).
- Chapéu cônico laranja/branco com 火 e véu: `T.acessoriosDom(A)` (lib/tgp.js), presos ao osso da cabeça.
- Uso: `const A = await E4.ator('dom'); cena.add(A.obj); const D = T.acessoriosDom(A);` · folha: `videos/98-dom` (?v=frente|tres|lado|costas|rosto &clip=walk).
- Versão antiga (corpo simples + cabeça procedural): `videos/98-dom?base=procedural`.
