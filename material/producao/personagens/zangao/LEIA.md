# ZANGÃO — duas versões separadas

Modelo base: **"PlayStation 1 - South Park - Eric Cartman" by DamianToons Cartoon Comedy Animation Studios (Sketchfab), CC BY 4.0**
— crédito obrigatório. Personagem © South Park Studios / Comedy Central; uso fan-made (rever se houver monetização/publicação comercial).
O arquivo original está intacto em `referencia/cartman_original.glb`.

| arquivo | versão |
|---|---|
| `zangao_original.blend` / `exports/zangao_original.glb` | **A · original**: aparência, proporções, textura e roupa preservadas + bigode estilo Chaplin + águia no peito |
| `zangao_militar.blend` / `exports/zangao_militar.glb` | **B · militar**: mesmo rosto, bigode e silhueta + uniforme modelado + águia na manga |

- `texturas/aguia.png` — distintivo da águia: desenho PRÓPRIO inspirado na águia da Lazio (águia branca de asas abertas, bico adunco
  dourado, sobre disco azul-celeste com aro branco). Gerado por `tools/desenhar_aguia.py`. Não é o escudo do clube.
- `folha_zangao_original.jpg`, `folha_zangao_militar.jpg`, `zangao_A_B_comparacao.jpg` — vistas, closes e testes de animação.

## Refazer
`ZANGAO=original|militar blender -b -P tools/blender/zangao.py -- $PWD/material/producao/personagens/zangao/exports/zangao_<v>.glb $PWD/material/producao/personagens/zangao/zangao_<v>.blend`
QA: `blender -b <arquivo>.blend -P tools/blender/qa_personagem.py` · ver: `videos/93-elenco-novo/?p=zangao` e `?p=zangao_militar`

## Detalhes
- Escala: 1,30 m no motor. Esqueleto próprio (22 ossos, nomes do motor) nas proporções dele (cabeça enorme, braços curtos);
  pesos por região com transição suave (a cabeça gira inteira; o toco do braço não puxa o corpo).
- **Bigode** (as duas versões): estreito como o do Chaplin (largura do nariz), peça fechada colada no rosto — cada vértice por raio na pele, cresce pela normal (acompanha a
  curvatura), logo acima da boca (boca medida em 2,15–2,31 e olhos a partir de 2,64, unidades do modelo).
- **Militar**: camisa verde-musgo (casca própria, sombreamento de tecido) com gola; colete cáqui-marrom com espessura; 2 fileiras MOLLE
  na frente e 3 atrás; 3 porta-carregadores com aba; 2 bolsos de peito; cinto de couro com fivela de metal; calça verde-escura;
  joelheiras; cotoveleiras; coturnos pretos com sola grossa; luvas oliva; gorro na mesma forma em verde-oliva; águia na manga esquerda.
  A jaqueta vermelha, as luvas amarelas e a base marrom do original saem dessa versão (o original continua no outro arquivo).
