# Gusta (base Simple PSX Character — JashiPSX)
- Textura: folha enviada pelo responsável (material/personagens/ref/gusta-textura-alvo.png), já no layout do modelo,
  reduzida pra 512 + manga comprida até o pulso (tools/manga_comprida.py).
- Montagem: `blender -b --disable-autoexec material/producao/modelos-pagos/simple_character_psx/simple-character-psx.blend --python tools/blender/montar_jashi.py -- texturas/gusta_512.png gusta.blend` (tira os óculos).
- Arquivo 3D fica fora do git (licença do JashiPSX). Falta: animações.

## v2 (rosto novo)
- Folha: material/personagens/ref/gusta-textura-alvo-v2.png. O rosto veio maior que o espaço do modelo: realinhado com
  `ORIG=.../character_256.png python3 tools/realinhar_rosto.py tris.json folha.png saida.png "1116,565 1121,640 1018,602 981,602 1176,600"`
  (marcos na folha: olho D, olho E, boca, queixo, testa) -> reduz pra 512 -> tools/manga_comprida.py -> montar_jashi.py com CABELO_CURTO=0.
