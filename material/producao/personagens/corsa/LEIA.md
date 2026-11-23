# CORSA — militar

Corpo humanoide; **só a cabeça** é do pardal (recortada da digitalização "22_23 House Sparrow.glb", do pacote
pardal-domestico-house-sparrow.zip enviado pelo diretor). Sem asas, cauda, pernas de ave ou penas no corpo.

O pacote não traz licença. Por isso o `.blend` e o `.glb` (que contêm a malha e a textura da digitalização) **não vão pro git**
(ver `.gitignore`); ficam só a folha e os scripts. Pra refazer, aponte `PARDAL_GLB` pro arquivo original:

`PARDAL_GLB="/caminho/22_23 House Sparrow.glb" PERSONAGEM=corsa blender -b -P tools/blender/vestir_personagem.py -- $PWD/material/producao/personagens/corsa/exports/corsa_militar.glb $PWD/material/producao/personagens/corsa/corsa_militar.blend`

Uniforme (próprio): jaqueta de campanha comprida marrom-oliva (bolsos, platinas, gola virada), calça oliva com bolso de coxa
à esquerda, suspensório em Y, cinto de lona com 2 cantis atrás e 3 porta-munição na frente, lenço quadriculado, pescoço
emplumado, coturno de couro marrom, luvas bege. 2.933 triângulos. Visualizar: `videos/93-elenco-novo/?p=corsa`.
