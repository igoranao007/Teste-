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
| 20 | Plano 41 (0:10–0:17) só névoa: a câmera olhando pro nada | ao tirar o micro-tremido, um comentário entrou no meio da linha e desativou o `lookAt` da câmera; a revisão olhou só os trechos mexidos | linha corrigida; `tools/quadros_vazios.py` (energia de bordas) obrigatório após todo render; revisão do filme inteiro | detector: 0 trechos vazios |
| 19 | **Braço e mão do Nicolas tremendo/girando** (e a origem dos giros acumulados em geral) | o `AnimationMixer` do Three.js só reescreve um osso quando o valor muda; em pose parada (sentado no carro) nada era reescrito e tudo aplicado por cima (pronação, dedos, olhares) SOMAVA a cada quadro — antebraço dando ~90° de volta por quadro | avaliador de animação próprio em `lib/elenco4.js`: cada quadro os ossos voltam à base, cada trilha é avaliada e escrita, mistura por slerp; câmera do close no carro sem micro-tremido rápido (vértices do PS1 piscavam) | 4 quadros seguidos idênticos (42); `tools/tremor.mjs` (agora mede também a torção): Nicolas 0; QA de todos os planos aprovado |
| 18 | **Mãos de TODOS os personagens "girando"** (Adryan, Gusta, Nicolas, frentista): palma pra frente; andando, a mão virava "bandeja" a cada passo | o retarget deixou o antebraço sem pronação (palmas pra frente, como na pose T); o osso da mão é constante nos clipes, então a medição de *variação* (0°) não pegava — só olhando de perto | pronação de 82° no antebraço + pulso neutro do rig em toda pose (`lib/elenco4.js`), pros 4 personagens do mesmo esqueleto; Metalis conferido (outro rig, ok) | inspeção visual por personagem × clipe (`videos/_pose`), QA de todos os planos aprovado |
| 17 | **Mãos do Igor de lado/torcidas** (teclado, fita, Enter, pastas) — o que o diretor via como "mãos girando" | o IK do Igor só apontava os dedos; o giro da mão ficava livre (mesma causa do #4, num rig à parte) | `c.orientar()` no rig do Igor (`m.pegada`): palma pra baixo nas teclas, na fita e no Enter; 75% da torção no antebraço | QA 51/54: 65–70° → aprovado; closes 2 s, 8 s (54) e 3,5 s (55) |
| 16 | Vidro do carro | sem vidro → depois claro demais | fumê preto (laterais/traseiro), para-brisa mais leve | visual |
| 21 | **Metalis com o braço cruzando o corpo e braço "congelado"** (44, 10,4–27 s) | alvos dos gestos em coordenada do MUNDO (quando o corpo virava, o alvo ficava do outro lado); mão no peitoril fixa por 26 s | alvos relativos ao ombro (`RightArm`), cotovelo pra fora, mão do peitoril respira e ergue nas falas | QA "braço atravessa o corpo"/"braço congelado" 44 = 0; fotos de frente |
| 22 | **Demora no elevador** (50) | 2,4 s parados com a porta aberta + 15,4 s pra 10,3 m (0,67 m/s, câmera lenta) | andam quando a porta abre (1,7 s), passo natural (~1,1 m/s), chegam em 11 s, viram um pro outro; plano/contraplano | fotos 1,5–23 s; QA 50 |
| 23 | **Mangueira atravessando o frentista** (43) | tubo reto da bomba ao bico, sem saber do corpo | rota que desce primeiro + empurrada pra fora das cápsulas do corpo; última passada só afasta; caminho do bico com arco pra fora ao encaixar/tirar | menor distância ao eixo do tronco 18 cm (limite 12,9) |
| 24 | **Frentista "correndo" com animação de andar** (43, 11,2–12,3 e 20,6–21,45) | 2,9 m em 1,1 s e 0,85 s (2,6–3,4 m/s): o pé patinava 1–4 m/s | caminhadas com tempo natural (2,3 s / 2,15 s); plano 43 de 22 → 24 s; pagamento reposicionado | QA "pé deslizando" |
| 25 | **Pé de apoio patinando em todas as caminhadas** | ciclo de passo com velocidade fixa contra corpo com aceleração/virada; mistura parado↔andando | **trava do pé** (foot locking) no `caminhar`: o pé fica onde tocou o chão (IK de perna, função pura do tempo); virada proporcional ao ângulo | pé de apoio a 0 m/s (medido quadro a quadro) |
| 26 | Passos de ré (Metalis 44, Gusta 48) com o pé deslizando | pose sobrescrita depois da trava; Gusta andando de costas com o clipe pra frente | `caminhar` com `re` (clipe ao contrário) e `rot` (direção fixa); som do passo de ré no contato certo | QA 44/48 |
| 27 | **Frentista guardava a grana no bolso ESQUERDO com a mão direita** (braço cruzando o corpo) | vetor do quadril com o lado trocado | bolso direito (`direita(r)`) + câmera lateral na troca da grana | QA 43; fotos 23,1–23,9 |
| 28 | **Igor folheava as pastas (do lado esquerdo) com a mão direita**, cotovelo dentro do tronco (52, 6,5–9,3 s) | mão errada | mão esquerda, palma pra baixo | QA 52 |
| 29 | **Plano inteiro quebrado por comentário `//` no meio da linha** (aconteceu de novo durante esta auditoria, pego antes do render) | edição automática anexando comentário de linha antes do resto do código | `tools/sintaxe.py` obrigatório (roda dentro do `qa_todos.sh`); comentários inseridos em linha única só com `/* */` | sintaxe ok em 17 planos + libs |
| 30 | Saltos de mão do Adryan indo ao bolso / à janela (43) | direção da mão e fechamento dos dedos trocavam em degrau (limiares 0,3/0,5) | misturas contínuas | QA "salto de mão" |
| 31 | Mãos do Igor 100% imóveis por 7 s (51) e atrás do terminal (55) | IK em alvo fixo depois que para de digitar | respiração nas mãos + rajada curta de digitação; pose viva no 55 | QA "braço congelado" |
| 32 | Detector de deslize dava alarme falso | olhava cada pé sozinho em janelas de 0,45 s (caía na fase de balanço) | mede os DOIS pés: acusa se nenhum fica parado por ≥ 0,17 s com o corpo andando | validado contra medição quadro a quadro |

## Lição (processo)
Toda edição passa por `python3 tools/sintaxe.py` antes do QA (bug #20 e #29).
Medição não substitui olhar. Toda correção de anatomia passa também pela inspeção por personagem × clipe em `videos/_pose`
(`node tools/fotos.mjs _pose "0.2,0.5" "ator=<nome>&clip=<clipe>&cam=0,.95,1.9,0,.9,0,34" saida.jpg`), de frente e de lado.

## Pendências conhecidas (não corrigidas nesta rodada)
- **Corrida, pulo, aterrissagem**: não existem no filme; o sistema de passos ainda não tem corrida/aterrissagem.
- **Colisão de mão × objeto** (dedos atravessando peças): o QA mede o corpo, não os dedos; verificado no visual.
