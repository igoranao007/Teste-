# LUAN GORDO — aliado do DOM (camisa do Atlético-MG · máscara de gás)

15 anos, gordo, pele "branco queimado", cabelo escuro meio cacheado, óculos, máscara de gás (metade de baixo do rosto) e a camisa
do Atlético-MG enviada pelo diretor (`referencia/camisa_atletico.jpg`; escudo CAM redesenhado em pixel art — uso fan-made).
Conceito em `referencia/conceito.png`.

- `luan.blend` / `exports/luan.glb` · `texturas/` (rosto_v2.png, cabelo_v2.png, cabeca.json, escudo_cam.png) · `folha_luan.jpg`
- Refazer: `python3 tools/desenhar_escudo_cam.py && python3 tools/luan_cabeca.py && PERSONAGEM=luan blender -b -P tools/blender/vestir_personagem.py -- $PWD/material/producao/personagens/luan/exports/luan.glb $PWD/material/producao/personagens/luan/luan.blend`

## Como foi feito
- **Cabeça** (`tools/luan_cabeca.py`, mesmo método da Entrada, sem foto): rosto redondo com papada, olhos e sobrancelhas pintados,
  cabelo = casca + cachos em tufos; ÓCULOS de armação preta (aros com espessura, lentes, ponte, hastes); MÁSCARA DE GÁS apoiada no
  rosto (bojo na boca, borda fechada até a pele), 2 filtros com tampa de aro amarelo aceso, válvula e tiras. 1.626 tri.
- **Corpo** gordo (tronco ×1,34 de largura e ×1,5 de fundo, barriga redonda na frente, braços e coxas grossos).
- **Camisa**: preta com padrão em V grafite, 3 listras douradas nos ombros, debrum dourado nas laterais, gola em V e punhos dourados,
  escudo CAM em relevo no peito esquerdo; manga curta com o antebraço à mostra.
- **Calça e coturnos** pretos BLINDADOS com frisos de energia amarela (luz própria), placas nas coxas, joelheiras, caneleiras,
  cinto, braçadeiras e luvas táticas.
