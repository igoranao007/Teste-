# THE GREEN PATH — auditoria da v4.3 → correções da v4.4

Tempos: **plano + segundo dentro do plano** e, entre parênteses, o tempo no vídeo v4.3 que o diretor assistiu.
(Na v4.4 o plano 43 ficou 2 s mais longo, então do 44 em diante tudo anda +2 s.)

## Os 4 bugs do protocolo

| # | Problema | Cena / momento exato | Causa técnica | Correção | Como verificar |
|---|---|---|---|---|---|
| BUG 01 | Metalis com o braço cruzando o corpo | 44 · 10,4–14,0 s, 20,4–23,6 s, 25,5–27,0 s (0:58,4–1:02 · 1:08,4–1:11,6 · 1:13,5–1:15) | alvos dos gestos em coordenada do mundo; com o corpo girado, o alvo do braço direito caía do lado esquerdo | alvos relativos ao ombro (`RightArm`), cotovelo pra fora, mistura por slerp | QA 44 "braço atravessa o corpo" = 0; fotos de frente 10–27 s |
| BUG 01 | Braço do Metalis congelado no peitoril | 44 · 4,0–30,5 s (0:52–1:18,5) | mão presa num ponto fixo por 26 s | mão respira, ergue nas falas (8,4 · 16,4 · 23,7 · 29,6 s) | QA "braço congelado" = 0 |
| BUG 01 | Metalis com o pé patinando (chegada e passo de ré) | 44 · 0,3–3,6 s e 31,4–32,3 s (0:48,3–0:51,6 · 1:19,4–1:20,3) | passada chutada (67% maior que a real); passo de ré com pose sobrescrita | passada medida (0,451 m); `caminhar` de ré com trava do pé | QA "pé deslizando" = 0 |
| BUG 02 | Demora no elevador | 50 · 0–2,4 s parados com a porta aberta; 2,4–17,8 s pra 10,3 m (2:14–2:31,8) | caminhada a 0,67 m/s começando 1,2 s depois da porta abrir | saem com a porta abrindo (1,7 s), ~1,1 m/s, chegam em 11 s, viram um pro outro, plano/contraplano | fotos 1,5–23 s; QA 50 aprovado |
| BUG 03 | Mangueira atravessando o frentista | 43 · 13,4–20,0 s (0:39,4–0:46) | tubo reto da bomba ao bico, sem saber do corpo | rota que desce e contorna as cápsulas do corpo; arco do bico pra fora ao encaixar/tirar | menor distância ao eixo do tronco 18 cm (limite 12,9) em 15,0 · 15,03 · 18,57 · 18,6 s |
| BUG 04 | Revisão geral | todos | — | lista abaixo | `bash tools/qa_todos.sh` (PASSO=1) |

## BUG 04 — revisão geral (achados novos desta auditoria)

| Problema | Cena / momento | Causa | Correção | Verificação |
|---|---|---|---|---|
| Frentista "correndo" com animação de andar | 43 · 11,2–12,3 s e 20,6–21,45 s (0:37,2 · 0:46,6) | 2,9 m em 1,1 s / 0,85 s (2,6–3,4 m/s) | 2,3 s e 2,15 s; plano 43 → 24 s | medição quadro a quadro |
| Pé de apoio patinando em todas as caminhadas | 43, 44, 47, 48, 50, 52 | ciclo do passo ≠ deslocamento do corpo (arranque, freada, virada) | trava do pé (foot locking) no motor | pé de apoio a 0 m/s |
| Corpo girando 130° em 0,35 s no arranque | 43 · 19,0 s e 20,6 s (0:45 · 0:46,6) | virada com tempo fixo | virada proporcional ao ângulo + começa a virar parado | QA 43 |
| Frentista guardando a grana no bolso esquerdo com a mão direita | 43 · fim (não aparecia na v4.3, apareceu ao alongar o plano) | lado trocado no vetor do quadril | bolso direito | QA + fotos 23,1–23,9 |
| Saltos da mão do Adryan indo ao bolso / à janela | 43 · 19,97–20,67 s (0:45,97) · 44 · 23,97–24,57 s (1:11,97) | direção da mão e dedos trocando em degrau | misturas contínuas | QA "salto de mão" = 0 |
| Gesto de fala do Metalis entrando de uma vez | 44 · 3,7 s (0:51,7) | peso da fala sem rampa ao parar de andar | rampa 3,65–4,1 s | QA 44 |
| Adryan deslizando 1,2 m pra fora do carro em 0,55 s | 47 · 11,25–11,8 s (1:55,25) | movimento rápido (atrás do carro, pé invisível) | levanta em 1,15 s; porta fecha depois do corte | QA 47 |
| Gusta andando de costas na diagonal com o clipe pra frente | 48 · 8,1–9,35 s (2:04,1) | caminhada pra frente usada pra recuar | passo de ré alinhado ao corpo (vira 40° abrindo passagem) | QA 48 |
| Mãos do Igor imóveis | 51 · 6,5–14 s (2:44,5–2:52) | IK em alvo fixo depois de digitar | respiração + rajada curta de digitação | QA 51 |
| Igor folheando com a mão errada (cotovelo dentro do tronco) | 52 · 6,5–9,3 s (2:58,5–3:01,3) | pastas do lado esquerdo, mão direita | mão esquerda | QA 52 |
| Mão do Igor saltando depois do Enter | 55 · 3,8 s (3:36,8) | IK desligado de uma vez | a mão fica no teclado respirando | QA 55 |
| Detector de deslize com alarme falso | ferramenta | janela de cada pé caía na fase de balanço | mede os dois pés | validado quadro a quadro |
| Plano quebrado por comentário `//` no meio da linha (2× durante a auditoria, pego antes do render) | processo | edição automática | `tools/sintaxe.py` obrigatório no QA | sintaxe ok |

## O que NÃO dá pra verificar automaticamente (documentado)
- **Dedos atravessando objetos** (bico, maleta, volante): o QA mede tronco/braço, não cada dedo. Conferido nas fotos de perto.
- **Expressão facial**: os rigs não têm ossos de rosto além da boca/pálpebra; julgamento visual.
- **Saltos de mão em corte de câmera**: o QA ignora de propósito (corte não é movimento).
- **Saída do carro (47)**: não existe animação de "sair do carro"; o movimento é feito por código atrás do carro (pés não aparecem).
- Cotovelo do frentista ao tirar o bico inclinado (43 · 18,43 s): passa no limite (12,3 cm do eixo, limite 12,1).
