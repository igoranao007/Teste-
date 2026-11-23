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
