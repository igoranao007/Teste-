# ENTRADA — militar

Personagem com o rosto da foto enviada pelo diretor (uso autorizado pela pessoa retratada).

- `entrada_militar.blend` — cena com esqueleto (64 ossos do personagem-simples) e todas as peças.
- `exports/entrada_militar.glb` — o que o motor carrega (`videos/93-elenco-novo/?p=entrada`).
- `texturas/` — `rosto.png` (recorte da foto, 128 px, 15 bits), `cabelo.png`, `rosto.json` (medidas: olhos, nariz, boca, linha do cabelo).
- `referencia_foto.jpg` — a foto original (não é alterada).
- `folha_entrada_militar.jpg` — vistas, closes e testes de animação.

Refazer: `python3 tools/preparar_entrada.py` e depois
`PERSONAGEM=entrada blender -b -P tools/blender/vestir_personagem.py -- $PWD/material/producao/personagens/entrada/exports/entrada_militar.glb $PWD/material/producao/personagens/entrada/entrada_militar.blend`
QA: `blender -b <arquivo>.blend -P tools/blender/qa_personagem.py`

Uniforme (próprio, diferente do Dod e do Corsa): camisa verde-acinzentada de manga arregaçada, colete de peito coyote
(4 porta-carregadores + bolso largo), suspensório em X, calça cargo coyote, joelheira só à esquerda, cinto bege,
coldre de perna direita, bolsa de descarga, coturno coyote, luvas oliva. 3.054 triângulos.
