# DOD — o gato preto do meme (cérebro exposto), de farda militar MODELADA · VERSÃO DEFINITIVA: V4 (`modelo/dod_farda_v4.glb`)

## Arquivos
- `T.dod()` em `lib/tgp.js` (cabeça: `T.cabecaDod()`) · folha: `videos/95-dod`
  (`?v=frente|tres|lado|costas|rosto|topo|bandeira|colete|botas|ombro|quadril`, `&pose=andar|bracos|sentar|girar`, `&boca=0..1`, `&corpo=gato`).
- **Modelo:** `modelo/dod_farda.glb` — gerado por `blender -b -P tools/blender/vestir_dod.py -- $PWD/material/producao/personagens/dod/modelo/dod_farda.glb [pasta_renders]`
  (`COR=MATERIAL|TEXTURE` pros renders de inspeção do `vestir_dod_render.py`).
- `inspecao/folha_dod.jpg` (frente, 3/4, lateral, costas, colete, bandeira, coturnos, expressões, poses) · `backup/` = versão anterior (equipamento feito de primitivas no código).

## Como a farda foi feita (pedido do diretor: "o CORPO ORIGINAL do Dod vestindo peças 3D modeladas e adaptadas à anatomia dele")
- **Corpo = o primeiro modelo** (`material/modelos/personagem-simples.glb`, o mesmo do Igor/Floppa), com o mesmo esqueleto.
- **Pesquisa (itch.io e outros):** CSAF *Fort Vale Rifleman* (licença livre) é um corpo MakeHuman PELADO com a roupa só PINTADA na textura — não tem
  colete/bolso/coturno modelado pra extrair. O soldado CC0 do OpenGameArt tem equipamento modelado, mas são caixas retas. joncrow e SkyesCloud são pagos;
  Psionic exige conta. Conclusão: as peças foram **modeladas no Blender sobre a superfície do próprio Dod** (fluxo de roupa de jogo), com os soldados só como referência.
- Cada peça nasce das faces do corpo (cortes retos na cintura, no cano da bota e no pulso), é afastada pela normal e ganha forma com operações de modelagem:
  - **camisa** de manga comprida + **gola** extrudada da borda do pescoço;
  - **calça** com **barra** descendo por cima do cano + **bolsos cargo** extrudados da lateral da coxa (com aba) + **joelheiras** com espessura;
  - **coturno** com solado (faixa de borracha) rente ao chão e **cano** com borda;
  - **luvas** com **punho** que sobe por cima da manga;
  - **colete porta-placas**: placa da frente e de trás, faixa lateral, alças nos ombros, espessura de 1,6 cm (casca interna + parede — o `bmesh.ops.solidify`
    explodia nas quinas); **3 porta-carregadores + bolso de peito** como peças próprias tiradas da placa, frente rígida, aba e presilha na textura de cada bolso;
  - **cinto** com espessura e **fivela** extrudada;
  - **bandeira de Israel**: recorte das faces da própria manga esquerda (lado de fora quando o braço desce), afastado 3 mm, UV pela posição no braço → acompanha a curva.
- Pesos de osso herdados do corpo (as peças seguem o esqueleto); colete, bolsos e cinto só nos ossos do tronco. As faces do corpo cobertas pela roupa saem (fica só o pescoço).
- Texturas PSX geradas no script: 16–64 px, cor de 15 bits com pontilhado Bayer, filtro Closest (farda, calça, colete com fitas MOLLE, bolso, cinto, metal, bota, sola, luva, joelheira, bandeira).
- **3.144 triângulos** na roupa.

## V2 e V3 (pedido do diretor: identidade militar própria, sem destruir a V1)
- Gerar: `VERSAO=2` / `VERSAO=3 blender -b -P tools/blender/vestir_dod.py -- $PWD/material/producao/personagens/dod/modelo/dod_farda_v3.glb`
  (módulos: `vestir_dod_mat.py` = paleta/texturas, `vestir_dod_v2.py` = peças novas, `vestir_dod_v3.py` = detalhes). V1 sai igual (`VERSAO=1`, padrão).
- No motor: `T.dod({ versao: 'v1'|'v2'|'v3' })` (padrão v3) · folha `videos/95-dod?versao=v2` · comparação: `inspecao/comparacao_v1_v2_v3.jpg`,
  folhas `inspecao/folha_dod_v2.jpg` e `inspecao/folha_dod_v3.jpg` (vistas, closes e testes andar/correr/braços/sentar/girar: `&pose=`).
- Referências: imagem B do guia (poncho com gola alta) + guia em PDF. Os assets indicados não servem (Fort Vale e Gunner pagos; Rebel Soldier fora do ar;
  Sketchfab/Poly Pizza exigem login/bloqueiam) → tudo modelado sobre o corpo do Dod.
- **V2:** gola alta (tubo de tecido com dobra e cordões, mais baixa na frente: boca e queixo livres) · poncho curto assimétrico CAÍDO sobre os ombros
  (raios de cima acham o apoio, a queda acompanha o colete a ~4 cm; painel diagonal no peito esquerdo, pregas e ponta nas costas; termina na ponta do
  ombro, então o braço fica livre e a bandeira aparece) · alça diagonal (bandoleira) apoiada na superfície com 2 fivelas em relevo · bolsa na alça e bolsa no cinto.
- **V3:** paleta oliva / musgo / verde-escuro / amarelo-oliva envelhecido (costuras) / caqui (fitas) / cinza-metal / preto / marrom gasto (desgaste).
  Colete em componentes (placas com debrum, pesponto e cantos reforçados; laterais em musgo; alças; 4 fileiras MOLLE em relevo na frente e atrás;
  fita "DOD"; fivelas nas alças e laterais) · camisa com pala e painéis em musgo, costuras do ombro e do punho, reforço no cotovelo, bolso na manga direita
  com zíper e patch da Toca do Anão · calça com bolsos cargo grandes, costuras laterais e do joelho, reforço no joelho, faixas caqui no tornozelo com fivela ·
  coturno com cadarço, biqueira e sola em 2 camadas · luva com reforço na palma · bolsa extra atrás do cinto · patch da bandeira com pesponto.
- Lições: `bmesh.ops.solidify` explode em quinas (usar `espessura()` própria); material exportado como dupla face faz a casca interna aparecer
  (V2/V3 = face única); o tecido apoiado precisa descer sempre a partir do pescoço e ser suavizado entre ângulos (sem picos); a queda nunca pode
  ficar mais estreita que a borda de apoio (dobra pra dentro = triângulos virados). `dissolve_limit` (mesmo material/UV) tira as lascas dos cortes:
  V3 com 6.079 triângulos de roupa (V2: 4.848; V1: 3.144).

## V4 (personalidade e assimetria; V1–V3 intactas)
- `VERSAO=4` → `modelo/dod_farda_v4.glb` · motor `T.dod({ versao: 'v4' })` · `inspecao/folha_dod_v4.jpg`, `inspecao/comparacao_v3_v4.jpg`.
- Colete: porta-carregadores de 3 tamanhos (duplo largo · simples · pequeno) com lingueta de couro envelhecido em relevo; compartimento lateral só à esquerda.
- Poncho: 32 colunas e 6 fileiras de queda; caimento em curva, 5 dobras macias que abrem pra baixo, boca de sino, barra ondulada, 3 pontas
  (frente-esquerda, meio das costas, uma menor atrás à direita) que puxam o pano de cima; comprimento CONTÍNUO em volta (sem "asa" no ombro);
  ombro esquerdo curto pra bandeira ficar livre.
- Mangas: cotoveleiras com espessura; bolso de caneta na manga esquerda (abaixo da bandeira); divisa no velcro da aba do bolso da manga direita
  (acima do patch da Toca). A bandeira ficou fora da fusão de faces (senão achatava e a manga atravessava).
- Calças: bolsos cargo ASSIMÉTRICOS (esquerdo maior e estufado — fole —, direito menor e mais alto); assento reforçado; bolso traseiro com aba só à
  esquerda e costura de bolso embutido à direita; costura diagonal na coxa direita.
- Costas/equipamento: bolsa de rádio na lateral-trás direita (tira de couro, fivela) com antena (tubo fino em 3 faces + ponteira); suspensórios do cinto
  com fivela; alça diagonal; bolsa utilitária no cinto; identificação "DOD" no peito. 7.230 triângulos de roupa.

## Cabeça (não mudou)
- Foto do meme projetada (método do Floppa), cara chapada, cérebro em cúpula, orelhas, boca redesenhada em pixel com repouso/falando (`animar(t, {boca, pisca})`).
