# Metalis (base Simple PSX Character — JashiPSX)
- Folha: material/personagens/ref/metalis-textura-alvo.png
- Rosto realinhado: `ORIG=.../character_256.png python3 tools/realinhar_rosto.py tris.json folha.png saida.png "1050,577 1050,688 905,632 868,632 1150,632"`
- Manga: `tools/manga_comprida.py tris.json tex.png saida.png 96,74,50`
- Montagem: `ESPINHOS=1 CABELO_CURTO=0 blender ... montar_jashi.py -- textura.png metalis.blend` (5 espinhos + 2 orelhas presos no osso da cabeça)
- Personagem de franquia (Sega): uso fan-made, ver material/diretrizes/personagens-de-franquias.md. Arquivo 3D fora do git.

## FINAL (aprovado)
- metalis_final.blend / .glb: Sonic medium poly (solowotanks, CC BY 4.0) + tools/blender/montar_metalis.py (trapos, esqueleto PSX)
  + tools/blender/mendigar_metalis.py (sujeira, cobertor, remendos, corda, lata, garrafa, trouxa, papelão, postura)
  + tools/blender/olho_textura.py com texturas/olho_cansado_0.52.png (olho cansado).
- Crédito no vídeo: "SONIC MEDIUM POLY" by solowotanks (Sketchfab), CC BY 4.0.
