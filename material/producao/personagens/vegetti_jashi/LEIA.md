# Vegetti (base Simple PSX Character — JashiPSX)
Licença da base: pode usar e modificar no projeto; NÃO pode redistribuir os arquivos (nem modificados).
Por isso a textura repintada e o .blend ficam fora do git. Pra refazer:
1. `python3 tools/pintar_jashi_vasco.py tris.json material/producao/modelos-pagos/simple_character_psx/texture/character_256.png material/personagens/ref/v_nv1.jpg saida.png`
2. `blender -b --disable-autoexec material/producao/modelos-pagos/simple_character_psx/simple-character-psx.blend --python tools/blender/montar_jashi.py -- saida.png vegetti_jashi.blend`
(tris.json vem de um dump dos objetos head/body/arms.)
