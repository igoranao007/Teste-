# Dom (base Simple PSX Character — JashiPSX, o mesmo do Adryan, Gusta, Nicolas e frentista) — fora do filme
- Rosto: foto `material/dom/dom.jpg` alinhada na geometria do pintor (`material/dom/rosto_alinhado.png`, olhos nivelados) e com os
  olhos reforçados pra não sumirem na textura de 256 px (`rosto_alinhado_olhos.png`).
- Textura: `ROUPA=dom CAB=40,34,30 CONTRASTE=1.3 QUENTE=1.0,0.95,0.9 python3 tools/pintar_jashi_vasco.py tris.json character_256.png material/dom/rosto_alinhado_olhos.png texturas/dom_512.png`
  (tris.json: todos os triângulos do modelo base com objeto e material, exportados pelo Blender).
  Casaco branco de manga comprida aberto em V, blusa preta de zíper, fivela laranja, gola alta, calça escura, sapato preto.
- Montagem e animação: `CALCA=1 blender ... montar_jashi.py -- texturas/dom_512.png dom.blend` → `animar_jashi.py` → `exportar_glb.py`
  (10 animações: idle walk run talk wave sit cower attack hit death). Arquivo 3D fora do git (licença do JashiPSX).
- "Frankenstein" (escolha do diretor): corpo, roupa e animações do modelo do elenco; na cabeça, a FRENTE (cabelo da testa + rosto da foto)
  vem do primeiro modelo (`T.cabecaDom({ meiaFrente: true })`, corte na linha das orelhas) e da orelha pra trás (nuca, cabelo de trás,
  orelhas) é a cabeça do elenco. Encaixe: largura 0,94 da cabeça, 3 cm à frente (o nariz do elenco não atravessa).
  Folha: `?semveu=1` (sem chapéu/véu/capa, pra ver a emenda) · `?cabeca=inteira` · `?cabeca=mascara` · `?cabeca=elenco` · ajuste fino `&esc=&dz=&corte=`.
- Detalhes amarelos na roupa: debrum da abertura do casaco, punhos e barra.
- Capa de Hokage (`acessoriosDom`): branca, chamas amarelas na barra, "小人の隠れ家" (kobito no kakurega, "o esconderijo/toca do anão") na vertical
  nas costas (fonte IPAGothic), gola alta; presa ao tronco (spine.003).
- Chapéu cônico laranja/branco com 火 e véu: `await T.acessoriosDom(A)` (lib/tgp.js), presos ao osso da cabeça; `D.atualizar(t, { boca, pisca })`.
- Uso: `const A = await E4.ator('dom'); cena.add(A.obj); const D = await T.acessoriosDom(A);` e a cada quadro `D.atualizar(t, { boca, pisca })` · folha: `videos/98-dom` (?v=frente|tres|lado|costas|rosto &clip=walk).
- Versão antiga (corpo simples + cabeça procedural): `videos/98-dom?base=procedural`.
