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

## v2 (atual) — base Simple PSX Character (JashiPSX), mesmo caminho do Adryan/Dom
Licença da base: usar e modificar no projeto, NÃO redistribuir → textura pintada, .blend e .glb ficam fora do git
(`material/producao/modelos-pagos/simple_character_psx/luan.blend`, `luan_anim.blend`, `luan_anim.glb`). Pra refazer:
1. `python3 tools/luan_camisa_costas.py` (costas da camisa a partir da foto) · `python3 tools/luan_cachos.py` · `python3 tools/luan_texturas_acessorios.py`
2. `ROUPA=luan PELE_RGB=218,164,128 CAB=34,26,22 RES=1024 python3 tools/pintar_jashi_vasco.py tris.json .../texture/character_256.png material/dom/dom.jpg luan_1024.png`
   (camisa = a FOTO `referencia/camisa_atletico.jpg` projetada no tronco/mangas/ombros; rosto pintado do modelo com o tom de pele trocado;
   calça preta com frisos amarelos; luvas pretas)
3. `AFRO=texturas/cachos.png AFRO_TAM=0.7 AFRO_C=0,0.0,1.965 AFRO_R=0.207,0.221,0.179 AFRO_LINHA=1.945 AFRO_TUFOS=70 AFRO_JIT=0.12 OCULOS=1 CABELO_CURTO=0 CALCA=1 blender -b --disable-autoexec simple-character-psx.blend --python tools/blender/montar_jashi.py -- luan_1024.png luan_base.blend`
4. `blender -b luan_base.blend --python tools/blender/luan_jashi.py -- luan.blend` (corpo gordo com a MESMA escala no pescoço e na cabeça —
   a ligação pescoço-corpo fica fechada —, máscara de gás moldada no rosto, filtros com aro luminoso, armadura feita da própria malha)
5. `BRACO_ABRE=22 blender -b luan.blend --python tools/blender/animar_jashi.py -- luan_anim.blend` (braços afastados da barriga) → `exportar_glb.py`
- Motor: `E4.ator('luan')` (lib/elenco4.js) · folha no motor: `videos/91-luan` (?v=frente|tres|lado|costas|rosto|rosto34|peito &clip=...)
- Folha em resolução cheia: `folha_luan_v2.jpg` (render `tools/blender/render_jashi.py`).
