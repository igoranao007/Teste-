# ENTRADA — militar (v2)

Personagem com o rosto das fotos enviadas pelo diretor (uso autorizado pela pessoa retratada).

- `entrada_militar.blend` — cena com esqueleto (64 ossos) e todas as peças · `exports/entrada_militar.glb` — o que o motor carrega
  (`videos/93-elenco-novo/?p=entrada`, texMax 256).
- `referencia/` — fotos originais (frente, 3/4, frente com óculos/orelhas), só o recorte do rosto. Não são alteradas.
- `texturas/` — `rosto_v2.png` (textura ÚNICA da cabeça, 256 px), `cabelo_v2.png`, `cabeca.json` (malha da cabeça), `rosto.json` (medidas da foto).
- `inspecao/` — `cabeca_v2_aprovacao.jpg` (cabeça em 6 ângulos, malha, textura, teste de virar).
- `folha_entrada_militar.jpg` — vistas, closes e testes de animação.
- `backup/v1/` — primeira versão (foto projetada + chest rig), preservada.

## Refazer
1. `python3 tools/preparar_entrada.py` (medidas da foto) · 2. `python3 tools/entrada_cabeca.py` (cabeça + textura) ·
3. `PERSONAGEM=entrada blender -b -P tools/blender/vestir_personagem.py -- $PWD/material/producao/personagens/entrada/exports/entrada_militar.glb $PWD/material/producao/personagens/entrada/entrada_militar.blend`
(`UNIFORME=v1` / `CABECA=v1` refazem a versão antiga) · QA: `blender -b <arquivo>.blend -P tools/blender/qa_personagem.py`

## v2
- **Cabeça**: loft de anéis com colunas densas no rosto (nariz, lábios, queixo, maçãs, mandíbula modelados), orelhas de abano,
  cabelo = casca com volume + 13 mechas (franja em pontas, tufos). Textura única em volta da cabeça: pele pintada + sombra assada;
  da foto entram só o tom e o DETALHE (olhos, sobrancelhas, boca) — sem emenda. Laterais/nuca em degradê pintado. 890 tri.
- **Corpo**: corpo base afinado (tronco ×0,86, braços ×0,84, coxas ×0,91) — rapaz magro.
- **Uniforme** (próprio, `tools/blender/uniforme_entrada_v2.py`): camisa verde-acinzentada de manga longa (gola virada, zíper,
  costuras amarelo-oliva, cotoveleiras, bolso com aba na manga esquerda) · colete cáqui (painéis, faixa lateral, alças com fivelas,
  MOLLE, 4 porta-carregadores individuais, 2 bolsos de peito, bolso nas costas, alça de resgate) · calça cargo marrom (bolsos baixos
  com fole e aba, costuras, reforços nos joelhos, bolso traseiro direito) · joelheira esquerda · cinto bege com passadores ·
  coldre de perna direita · bolsa de descarga · luvas oliva com palma de couro · coturno cáqui (sola + entressola, biqueira,
  contraforte, cadarço com ilhoses, colarinho). Tecido com sombreamento suave; equipamento facetado. 5.324 tri no total.
