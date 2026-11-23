# OLIVEIRA — aliado do DOM (cabeça de Godzilla · armadura com energia)

Cabeça e pescoço: **"PlayStation 3 - Godzilla - Heisei Godzilla" by Mathzilla5335 (Sketchfab), CC BY 4.0** — crédito obrigatório.
Personagem © Toho; uso fan-made (rever se houver monetização/publicação comercial). Original intacto em `referencia/godzilla_original.glb`.
Conceito do diretor em `referencia/conceito.png`.

- `oliveira.blend` / `exports/oliveira.glb` · `texturas/godzilla_cabeca.png` · `folha_oliveira.jpg` · ver: `videos/93-elenco-novo/?p=oliveira`
- Refazer: `PERSONAGEM=oliveira blender -b -P tools/blender/vestir_personagem.py -- $PWD/material/producao/personagens/oliveira/exports/oliveira.glb $PWD/material/producao/personagens/oliveira/oliveira.blend`

## Como foi feito
- **Cabeça**: recorte do corpo do Godzilla em z = 42 (logo abaixo da mandíbula; o pescoço do original é largo como o peito),
  reduzida pra 980 tri, UV NOVO de uma ilha (projeção cilíndrica, emenda atrás) com as cores transferidas da cabeça original de
  2048 px (o UV do original, picado, misturava a boca/dentes com a pele), clareada, sem saturação, com escamas em blocos;
  focinho levantado 14° (o original olha pra baixo); OLHOS amarelos acesos.
- **Corpo** encorpado (tronco ×1,12) com traje preto e ARMADURA do DOM: peitoral/costas em placas com frisos de energia amarela
  (material `*_brilho` = luz própria no motor), "トカ" aceso no peito, gola blindada alta (esconde o corte), ombreiras grandes,
  braçadeiras, manoplas, cinto com bolsas, tabardo de tecido rasgado, coxas/joelheiras/canelas, coturnos; REATOR nas costas
  (moldura octogonal acesa, núcleo, 2 engrenagens, 2 tubos). 4.739 tri. 1,82 m no motor.


## v2 (atual) — corpo do Simple PSX Character (JashiPSX) + armadura em placas curvas + cabeça com bake
Arquivos 3D fora do git (licença do JashiPSX): `material/producao/modelos-pagos/simple_character_psx/oliveira.blend`, `oliveira_anim.blend`, `oliveira_anim.glb`.
Refazer (na raiz do projeto):
1. `python3 tools/oliveira_texturas.py` (placa, placa2, metal, tecido — 128 px)
2. `ROUPA=oliveira RES=512 python3 tools/pintar_jashi_vasco.py tris.json .../texture/character_256.png material/dom/dom.jpg oli_512.png` (traje de baixo)
3. `CABELO_CURTO=1 CALCA=1 blender -b --disable-autoexec simple-character-psx.blend --python tools/blender/montar_jashi.py -- oli_512.png oli_base.blend`
4. `blender -b oli_base.blend --python tools/blender/oliveira_jashi.py -- oliveira.blend`
5. `BRACO_ABRE=10 blender -b oliveira.blend --python tools/blender/animar_jashi.py -- oliveira_anim.blend` → `exportar_glb.py`
- Corpo em V (peito largo, cintura fina), sem a cabeça humana. ~16.400 faces, 32 objetos.
- **Armadura**: cada placa é medida por RAIOS do eixo do osso até a pele (r(θ,t) + folga), suavizada, com bojo, espessura, CHANFRO,
  REBITES e SULCOS de energia em relevo (`o_linha_brilho`, luz própria). Peitoral em 2 camadas com o トカ em relevo aceso, costas,
  abdômen em 3 lâminas, cinto com fivela acesa e 5 bolsas, gorjal em 2 fileiras de lâminas, ombreiras (calota + 3 lâminas), braçal,
  cotoveleira, manopla em 2 lâminas, placa da mão e dos nós dos dedos, coxote, joelheira, caneleira, panturrilha, saiote lateral,
  bota (cano + peito do pé + sola). Cada peça presa 100% no osso dela (não estica nas animações).
- **Reator nas costas**: carcaça, moldura octogonal de metal, filete aceso, núcleo aceso, 2 engrenagens, canos e luzes laterais.
- **Tabardo** de tecido rasgado (frente e trás), pesos divididos entre quadril e coxas.
- **Cabeça**: Godzilla recortado em z=39,5 (com o começo do pescoço), ~3.400 tri, UV novo; textura 512 por BAKE no Cycles da malha
  ORIGINAL inteira (cor difusa + oclusão: as escamas e rugas da geometria viram textura) → `texturas/godzilla_cabeca_v2.png`;
  pescoço afinado embaixo, base no centro do gorjal (encaixa no corpo), focinho levantado 10°, olhos acesos.
- Motor: `E4.ator('oliveira')` · `videos/91-luan/?p=oliveira` · Folha: `folha_oliveira_v2.jpg` (render Cycles `BELO=1` do `tools/blender/render_jashi.py` + `tools/brilho_png.py`).
- Pacotes do itch.io avaliados como base (não usados no modelo final): Corebreaker (CC0), Viking armor chad (OnlyHooks), Sci Fi Samurai (domínio público).
