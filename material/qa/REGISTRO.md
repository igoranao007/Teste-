# THE GREEN PATH — registro de bugs (causa → correção → teste)

Motor: Three.js (render quadro a quadro com Playwright) + Remotion (edição) + síntese de áudio própria (`audio/synth.py`).
Não é Unity/Unreal/Blender em tempo real: as ideias de lá (Two Bone IK com rotação do alvo, notify de passo, NavMesh)
foram adaptadas pra este motor.

| # | Bug | Causa raiz | Correção | Teste |
|---|---|---|---|---|
| 1 | Cabeças girando sem parar | retarget aplicou a rotação da cabeça 2× (pescoço + cabeça) → loop idle/sit/talk rodava a cabeça | amortecimento do pescoço no ator (`lib/elenco4.js`) | QA "pescoço torcido": 0 ocorrências |
| 2 | Mão tremendo (Metalis) | animação `talk` ligada/desligada a cada sílaba (seguia o volume quadro a quadro) | `fala.peso()`: peso suave pela fala inteira | QA "salto de mão": 89 → 0 |
| 3 | Corpo virando 100–170° num quadro | início/fim de caminhada trocava pose e direção sem transição | `caminhar`: mistura parado↔andando + `de:` (virada gradual) | QA "salto": 0 |
| 4 | Mãos/pulsos torcidos | IK posicionava a mão mas deixava o giro do pulso livre | `V.pegar`: alvo com rotação (dedos + lado do indicador), torção 75% no antebraço | QA "mão torcida"/"pulso dobrado" no 41–50: 0 |
| 5 | Bico de combustível artificial | bico seguia a mão sem pegada; orientação inventada | pegada definida no gancho e rígida; bico horizontal (fotos de referência); portinhola do tanque que abre/fecha; tirar/pendurar no gancho | QA 43 aprovado; close de 2 ângulos |
| 6 | Volante: mãos "por cima" do aro | IK sem rotação | pegada orientada no aro (dedos envolvem pela frente, indicador pras 12h) | QA 41/42 aprovado |
| 7 | Maleta "flutuando" com a mão aberta | maleta presa a um ponto, sem girar, mão aberta | pende da mão fechada, alinhada ao corpo | visual 47/48/50 |
| 8 | Adryan sai do carro atravessando a lataria | nascia no capô e andava reto | porta do motorista abre, ele se levanta pela abertura, **fecha a porta** fora do raio dela e contorna | QA 47: 6 colisões → 0 |
| 9 | Porta da cabana passando pelo Gusta | Gusta dentro do arco da porta | fora do raio (1,04 m) + passo pra trás quando abre | QA 48 |
| 10 | Adryan atravessando o degrau da varanda | sem altura de chão | `V.chao()` com plataformas (degrau 20 cm, piso 8 cm) | QA 48 |
| 11 | Frentista e Metalis atravessando a ilha das bombas (degrau 21 cm) | rotas retas | rota com desvio; pegar o bico de fora da ilha | QA 43/44 |
| 12 | Carro atravessando pilar da cobertura (chegada e saída) | pilar dentro da faixa do carro + curva de saída | fileira da frente dos pilares fora da faixa; curvas novas | QA de lataria (caixa orientada) 43/44 |
| 13 | "Arbusto preto" flutuando na estrada e na frente da loja | pacote de árvores com as 4 versões de detalhe visíveis; a LOD3 deslocada | só a LOD0 visível | QA 43 + visual |
| 14 | Passos iguais em todo lugar, eco de corredor ao ar livre, alto | 1 som só, com eco de 2,2 s; em temporizador | superfície × personagem × variação, no contato real do pé (fases medidas no clipe), volume igualado | contagem: 79 pisadas, 6 superfícies |
| 15 | Sons muito altos em alguns momentos | stingers 12 dB acima da mediana, estouro no mix | stingers −5…−9 dB; sem "guard" | medição de janelas de 400 ms |
| 18 | **Mãos de TODOS os personagens "girando"** (Adryan, Gusta, Nicolas, frentista): palma pra frente; andando, a mão virava "bandeja" a cada passo | o retarget deixou o antebraço sem pronação (palmas pra frente, como na pose T); o osso da mão é constante nos clipes, então a medição de *variação* (0°) não pegava — só olhando de perto | pronação de 82° no antebraço + pulso neutro do rig em toda pose (`lib/elenco4.js`), pros 4 personagens do mesmo esqueleto; Metalis conferido (outro rig, ok) | inspeção visual por personagem × clipe (`videos/_pose`), QA de todos os planos aprovado |
| 17 | **Mãos do Igor de lado/torcidas** (teclado, fita, Enter, pastas) — o que o diretor via como "mãos girando" | o IK do Igor só apontava os dedos; o giro da mão ficava livre (mesma causa do #4, num rig à parte) | `c.orientar()` no rig do Igor (`m.pegada`): palma pra baixo nas teclas, na fita e no Enter; 75% da torção no antebraço | QA 51/54: 65–70° → aprovado; closes 2 s, 8 s (54) e 3,5 s (55) |
| 16 | Vidro do carro | sem vidro → depois claro demais | fumê preto (laterais/traseiro), para-brisa mais leve | visual |

## Lição (processo)
Medição não substitui olhar. Toda correção de anatomia passa também pela inspeção por personagem × clipe em `videos/_pose`
(`node tools/fotos.mjs _pose "0.2,0.5" "ator=<nome>&clip=<clipe>&cam=0,.95,1.9,0,.9,0,34" saida.jpg`), de frente e de lado.

## Pendências conhecidas (não corrigidas nesta rodada)
- **Gusta (48)**: transição curta de passo pra trás com salto de 32–36° na mão por 1–2 quadros (limite 28°).
- **Corrida, pulo, aterrissagem**: não existem no filme; o sistema de passos ainda não tem corrida/aterrissagem.
- **Colisão de mão × objeto** (dedos atravessando peças): o QA mede o corpo, não os dedos; verificado no visual.
