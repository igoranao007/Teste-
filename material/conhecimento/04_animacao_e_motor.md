# 4. Animação e motor — o que funciona (e por quê)

## Avaliador de animação próprio (`lib/elenco4.js`)
- **Problema:** cabeças girando sem parar, antebraço do Nicolas "girando ~90° por quadro", mãos tremendo.
- **Causa raiz:** o `AnimationMixer` do Three.js só escreve num osso quando o valor muda. Em pose congelada (sentado) nada era reescrito,
  e tudo que se aplicava por cima (pronação, dedos, olhares) **somava a cada quadro**.
- **Solução:** a cada quadro todos os ossos voltam à pose base (`BASE`); cada trilha do clipe é avaliada (`track.createInterpolant()`) e escrita;
  mistura entre clipes por `slerp`. `A.pose(clipe, t, clipeB, pesoB, tB)` e `A.quadro(clipe, t)` (pose congelada).
- **Determinismo:** o mesmo `t` tem que dar a mesma pose (teste: `__seek(t)` duas vezes). Nunca guarde estado entre quadros.

## Retarget e mãos
- Rotação da cabeça vinha dobrada (pescoço + cabeça) → amortecer o pescoço.
- Mãos "bandeja"/palma pra frente em TODOS os personagens: o antebraço do retarget não tinha pronação → **82° de pronação** + pulso neutro do rig.
  (O diretor reclamou 2× — eu tinha corrigido só o Igor. Lição: bug visual num personagem → **verifique todos**.)

## IK com rotação do alvo — `V.pegar(A, lado, ponto, dedos, indicador, polo, k, fecha)`
- Como o "Two Bone IK" da Unity com *target rotation*: posição E orientação da mão; 75% da torção no antebraço, o resto no pulso.
- A pegada é definida **no momento de pegar** e depois a mão gira **junto** com o objeto (rígida) — bico de combustível, maleta, volante 10h/2h.
- **Polo (cotovelo) relativo ao corpo** quando o corpo gira (senão a solução "vira" e dá salto de mão).
- Dedos devem seguir a direção **ombro → alvo** (pulso reto); direção fixa no mundo dobra o pulso 100°+.
- `V.ik2` (rig sem dedos, Metalis): resolve a partir da pose neutra e mistura por slerp. Misturar quatérnios do braço inteiro faz a mão
  passar por caminhos estranhos (cruzou o rosto do Metalis) → **interpole o ALVO** (posição) por um caminho por fora do corpo, com peso em rampa.
- Média ponderada de vários alvos de gesto: os envelopes precisam **se sobrepor**; se a soma dos pesos cai a ~0 entre dois gestos, o alvo salta.

## Caminhar — `V.caminhar(A, a, b, t, t0, t1, o)`
- Ease nas pontas; **cadência pela distância** (fase = distância ÷ passada × duração do clipe). **Passada medida no próprio clipe**
  (`videos/_pes` → `material/qa/pes.json`), nunca chutada (a do Metalis estava 67% errada).
- **Trava do pé (foot locking):** no apoio, o pé fica onde tocou o chão. O ponto de contato é recalculado a cada quadro posando o ator
  no instante do toque (função pura do tempo). IK de perna com joelho pra frente, mantendo a orientação do pé. Rampa de entrada/saída.
  Bugs que tive: em `t0` exato a caminhada não posava (use `t0+1e-4`); travar na pose IDLE em vez da de caminhada; de ré a rampa de saída tem que ser curta.
- `o.de`: direção anterior; a virada dura **proporcional ao ângulo** (~3,3 rad/s máx). Virada > 90° no arranque: comece a virar parado.
- `o.re` (de ré, clipe ao contrário) e `o.rot` (direção fixa): passo pra trás. Recuo na diagonal: gire o corpo pra alinhar o recuo com o passo.
- **Velocidade:** 1,1–1,4 m/s. Pico ≈ 1/(1−ease) × média. Frentista andando 2,9 m em 0,85 s (3,4 m/s) = pé patinando.

## Interações resolvidas (receitas)
- **Frentista no posto:** anda até a bomba → pega o cabo no gancho (pegada rígida) → tira pra cima/fora → leva à traseira → abre a portinhola
  com a outra mão → encaixa o bico **na horizontal** → segura → tira → fecha → pendura → janela → recebe a grana → **bolso DIREITO**.
- **Mangueira:** curva CatmullRom com ponto que "desce primeiro", empurrada pra fora das cápsulas do corpo (`V.capsulasCorpo`), última passada só afasta (a suavização puxava pra dentro).
- **Sair do carro** (pesquisa: cartilhas de "como sair do carro"): maçaneta → porta abre → gira no banco e chega pra beirada → perna esquerda, depois a direita
  (pés no chão) → mão na coluna (do lado certo!) → levanta **abaixando a cabeça** → sai do **raio da porta** → empurra a porta (ela bate no embalo) → anda.
- **Porta secreta:** bate 3× (som no contato dos nós dos dedos) → portinhola na altura dos olhos corre → senha pela fresta (POV) → fecha → o de dentro **sai do arco da porta** (abre pra dentro) → destranca → abre (rangido).
- **Fita VHS / objetos na mão:** prenda o objeto na **PALMA real** (osso da mão + dedo médio), não no alvo do IK — senão flutua quando o braço não alcança.
- **Metalis na janela:** agarra a borda com a mão (pulso dobrado por cima da borda, sem torcer), solta pra gesticular e volta.
- **Vidro do carro:** a janela tem que descer INTEIRA (48 cm); com 39 cm sobrava uma faixa preta na frente dos rostos.

## Bones e convenções úteis
- No Three: frente do ator = +Z com `rotation.y = 0`; `direita(r) = (−cos r, 0, sin r)`; esquerda é o oposto.
- `osso.attach(obj)` mantém a posição de mundo ao prender acessório.
- Medidas do sedã (local): banco do motorista x=+0,35, passageiro x=−0,35, teto ≈1,33, volante (0,35; 0,84; 0,49); dobradiça da porta do motorista (0,87; 0,43; 0,95).
