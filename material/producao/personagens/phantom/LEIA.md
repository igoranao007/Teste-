# PHANTOM — Deadpool em PSX (2 versões: clássica e amarela, aliado do Dom)
Fonte: `deadpool-character.zip` (Deadpool.glb: 353 mil faces, sem esqueleto, pose A, textura PBR 2048) e `Malorian.zip`
(pistola Malorian low-poly com textura 128), enviados pelo diretor. Personagem © Marvel (uso fan-made). Licença dos arquivos não
informada → os derivados 3D (.blend/.glb e texturas assadas) ficam FORA do git (`.gitignore` desta pasta).

## Como um 3D "normal" virou PSX (`tools/blender/phantom.py`)
1. Solda os vértices soltos nas costuras de UV (senão a redução estilhaça a malha) e REDUZ de 353 mil pra ~7.000 triângulos.
2. UV novo (projeção inteligente) e textura 512 por BAKE no Cycles da malha original: cor difusa + oclusão leve; cor de 15 bits
   (32 níveis por canal), filtro "Closest" (sem suavizar), como o PS1. No motor, ainda: textura reduzida (texMax), vértices que tremem,
   textura que entorta e render em 1/4 da resolução.
3. Esqueleto do elenco (Simple PSX Character, mesmos nomes) com os ossos medidos nas articulações do modelo; pesos automáticos;
   limpeza (na pose A a mão encosta no coldre: tira peso de braço de |x| < 0,29 m abaixo de 1,05 m); braços levados da pose A pra
   pose T e aplicados como descanso; tira as faces que esticaram > 2,2× (pontes mão-coldre). Sem ossos de dedo.
4. Duas MALORIAN DENTRO dos coldres das coxas (medidos em vistas ortográficas: x 0,20–0,26, y -0,08–0,03, z 0,80–1,00): cano pra baixo, coronha saindo por cima e pra trás, 25 cm (`ARMA_COMP`, `COLDRE_X/Y/TOPO`), presas nas coxas; uma Malorian solta exportada em `malorian.glb` pra pôr na mão nas cenas.
5. `VERSAO=amarela`: o vermelho do traje vira AMARELO FORTE (luz/sombra preservadas pela luminância); preto, couro e olhos ficam.

## Refazer (zips extraídos em qualquer pasta)
```
B=material/producao/modelos-pagos/simple_character_psx; P=material/producao/personagens/phantom
for V in classica amarela; do
  VERSAO=$V blender -b --disable-autoexec $B/simple-character-psx.blend --python tools/blender/phantom.py -- <Deadpool.glb> <pasta Malorian> $P/phantom_$V.blend
  BRACO_ABRE=4 blender -b $P/phantom_$V.blend --python tools/blender/animar_jashi.py -- $P/phantom_${V}_anim.blend
  blender -b $P/phantom_${V}_anim.blend --python tools/blender/exportar_glb.py -- $P/phantom_${V}_anim.glb
done
```
- Motor: `E4.ator('phantom')` / `E4.ator('phantom_amarelo')` (10 animações) · folha no motor: `videos/91-luan/?p=phantom` · Folha: `folha_phantom.jpg`.
