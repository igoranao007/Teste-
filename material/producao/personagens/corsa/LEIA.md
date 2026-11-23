# CORSA — militar (v2)

Corpo humanoide; **só a cabeça** é de pardal, feita a partir da digitalização "22_23 House Sparrow.glb" (pacote
pardal-domestico-house-sparrow.zip enviado pelo diretor). Sem asas, cauda, pernas de ave ou penas no corpo; pescoço humanoide.

## Licença
O pacote não traz licença. Por isso o que é DERIVADO da digitalização (`corsa_militar.blend`, `exports/corsa_militar.glb`,
`texturas/cabeca_corsa.json`, `texturas/pardal_cabeca.png`, `backup/`) **não vai pro git** (ver `.gitignore`); ficam os scripts e a folha.

## Refazer (aponte PARDAL_GLB pro arquivo original, que não é alterado)
1. `PARDAL_GLB="/caminho/22_23 House Sparrow.glb" blender -b -P tools/blender/corsa_cabeca.py -- $PWD/material/producao/personagens/corsa/texturas`
2. `PARDAL_GLB=... PERSONAGEM=corsa blender -b -P tools/blender/vestir_personagem.py -- $PWD/material/producao/personagens/corsa/exports/corsa_militar.glb $PWD/material/producao/personagens/corsa/corsa_militar.blend`
(`CORSA=v1` refaz a versão antiga) · QA: `blender -b <arquivo>.blend -P tools/blender/qa_personagem.py` · ver: `videos/93-elenco-novo/?p=corsa`

## v2 (o que mudou e por quê)
- **Causa do problema da v1**: a digitalização é de um pardal MERGULHANDO em voo (cabeça pra baixo); a v1 tratou a cabeça como se
  estivesse de pé e reduziu a textura de 1024 px com 308 ilhas de UV pra 128 px (as ilhas se misturaram = manchas).
- **Cabeça v2**: a ave é girada até a cabeça ficar de pé (conferido em renders); malha NOVA (272 tri) com anéis ao longo do eixo
  nuca→bico, cada vértice posto por raio na superfície da digitalização; bico medido (cone com ponta firme); olhos no lugar do olho
  real (o globo escuro e azulado, medido do lado bom e espelhado); UV com UMA ilha e as cores da textura original transferidas ponto
  a ponto (256 px); nuca (que a digitalização não tem) continua a plumagem do alto da cabeça.
- **Pescoço** humanoide com plumagem marrom; sem lenço; gola virada baixa (não encosta na cabeça).
- **Uniforme** (`tools/blender/vestir_corsa_v2.py`): jaqueta de campanha marrom-oliva até o meio da coxa (gola virada, carcela de
  botões, costuras amarelo-oliva discretas, cotoveleiras, platinas, bolsos de peito/baixo/laterais com aba) · calça verde-oliva
  (bolso de coxa à esquerda, costuras, reforço nos joelhos) · cinto de lona · suspensório em Y · 3 porta-munições, 2 cantis, bolsa de
  equipamento · luvas bege com palma de couro · coturno de couro marrom (sola clara + entressola, biqueira, contraforte, cadarço,
  colarinho). Corpo base levemente afinado (porte médio). 3.386 tri.
