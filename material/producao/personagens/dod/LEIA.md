# DOD — o gato preto do meme (cérebro exposto), de farda militar MODELADA

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

## Cabeça (não mudou)
- Foto do meme projetada (método do Floppa), cara chapada, cérebro em cúpula, orelhas, boca redesenhada em pixel com repouso/falando (`animar(t, {boca, pisca})`).
