# Gato Soldado (PSX) — modelo 100% em código (bmesh)

- Script: `tools/blender/gato_soldado.py` → `blender -b -P tools/blender/gato_soldado.py -- $PWD/material/producao/personagens/gato_soldado`
- Referência: meme do gato preto com o cérebro exposto (o cérebro fica no lugar do cabelo).
- Corpo: soldado de farda **vermelha** (botões, bolsos, cinto preto com fivela, bandoleira de couro), **luvas verdes**, **botas pretas**,
  patch com a **bandeira de Israel no braço ESQUERDO** (perto do ombro).
- Regras seguidas: só `bmesh` (sem `bpy.ops.mesh`), 16 peças rígidas presas a ossos (estilo PS1, sem deformar), **474 triângulos**,
  `smooth = False` em tudo + normais recalculadas, textura 128×128 desenhada pixel a pixel com **26 cores** (paleta máx. 32) e pontilhado Bayer 4×4,
  `interpolation = 'Closest'`, Principled com Roughness 1 e Specular IOR Level 0, camada de cor por vértice `AO` (escurece embaixo e nas juntas) multiplicando a textura.
- Altura ≈ 1,83 m até o topo do cérebro. Ossos: Hips, Spine, Neck, Head, Left/Right UpperArm, LowerArm, Hand, UpperLeg, LowerLeg, Foot.
- Arquivos: `gato_soldado.blend`, `gato_soldado.glb` (Three.js: frente = +Z), `gato_soldado_128.png`, `inspecao/` (3/4 em 320×240, frente, perfil, costas, rosto, bandeira).
