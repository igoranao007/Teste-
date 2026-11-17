# Nicolas (base Simple PSX Character — JashiPSX) — camisa 10 do Flamengo
- Folha: material/personagens/ref/nicolas-textura-alvo.png (layout do modelo).
- Rosto realinhado: `ORIG=.../character_256.png python3 tools/realinhar_rosto.py tris.json folha.png saida.png "1115,575 1115,647 1010,612 980,612 1160,612"` -> 512.
- Montagem: `CABELO_CURTO=0 blender ... montar_jashi.py -- texturas/nicolas_512.png nicolas.blend`. Arquivo 3D fora do git (licença JashiPSX).

## Teste black power (estilo jogos do Puppet Combo: volume simples + textura crespa pixelada)
`AFRO=texturas/crespo_foto.png AFRO_TUFOS=0 AFRO_C=0,0.025,2.0 AFRO_R=0.215,0.215,0.235 AFRO_AFINA=0.18 AFRO_JIT=0.05 AFRO_LINHA=1.945 CABELO_CURTO=0 blender ... montar_jashi.py -- texturas/nicolas_afro_512.png nicolas_afro.blend`
(textura: tools/pintar_crespo_foto.py; referência visual só do estilo, nenhum arquivo do jogo usado)
