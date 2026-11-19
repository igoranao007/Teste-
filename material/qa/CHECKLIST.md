# THE GREEN PATH — checklist permanente de qualidade

Nenhum plano é aprovado sem passar por **tudo** abaixo. Vale pra toda produção nova e pra toda correção (regressão).

## 0. Antes de mexer
- `python3 tools/sintaxe.py` (libs + script de cada plano). Já roda dentro do `qa_todos.sh`.
- Ler `material/qa/NAO_REGREDIR.md` e `VERSOES.md`.
- Rodar `bash tools/qa_todos.sh` e guardar o resultado ("antes").
- Ler `material/qa/REGISTRO.md`: não repetir bug já resolvido.

## 1. Teste automático (`node tools/qa.mjs <plano> [passo]`)
Roda o plano quadro a quadro e reprova:

| Categoria | O que mede | Limite |
|---|---|---|
| Anatomia | pulso dobrado (antebraço × mão) | > 80° |
| Anatomia | mão torcida (giro da mão vs. pose neutra do rig) | > 60° |
| Anatomia | pescoço torcido (cabeça + pescoço vs. pose neutra) | > 75° |
| Anatomia | salto de mão (giro da mão em 1 quadro, mesmo plano de câmera) | > 28°/quadro |
| Anatomia | pé abaixo do chão | < −4 cm |
| Continuidade | teletransporte (quadril pula, mesmo plano de câmera, relativo a quem carrega) | > 25 cm/quadro |
| Colisão | corpo (cápsula r 16 cm) dentro de peça sólida | qualquer |
| Colisão | dois personagens a menos de 30 cm | qualquer |
| Colisão | lataria do carro (caixa orientada) dentro de peça sólida | qualquer |
| Anatomia | braço (mão/cotovelo/antebraço) dentro do tronco | > 25% do raio |
| Anatomia | braço congelado (mão parada < 4 mm no espaço do corpo) | ≥ 3 s |
| Anatomia | pé deslizando (nenhum dos dois pés parado, corpo andando) | > 0,3 m/s por ≥ 0,17 s |
| Colisão | objeto flexível (mangueira) dentro do tronco | > 20% do raio |

Exceções explícitas (marcadas no código, nunca "no olho"): personagem dentro do próprio veículo (`userData.veiculo` /
`userData.noVeiculo` ao entrar/sair), assento (`userData.assento = '<ator>'`), mesa com vão pras pernas (`userData.vaoPernas`),
peça flexível (`userData.flexivel`: mangueira), em pé em cima de plataforma, subindo degrau ≤ 25 cm, peça carregável < 55 cm.

## 1b. Tremor e acúmulo
- `node tools/tremor.mjs <plano> <ator>` (com `Q=ref=pai` pra quem está em veículo): vai-e-volta de mão/antebraço/cabeça,
  medindo posição E torção (eixo lateral do osso). Inversões periódicas no ritmo do passo são balanço normal; contínuas = bug.
- Determinismo: o mesmo instante tem que dar a mesma pose (testar `__seek(t)` duas vezes e comparar). Nada pode acumular entre quadros.

## 1c. Depois do render (obrigatório)
- `python3 tools/quadros_vazios.py out/the-green-path-v4.mp4`: acha câmera apontando pro nada (quadro sem bordas: só névoa/preto).
- Folha a 1 qps do filme **inteiro** (não só dos trechos mexidos).

## 2. Teste visual
- **Inspeção por personagem × clipe** (`videos/_pose`): cada ator em idle, walk, talk, de frente e de lado. Mãos: palma pro corpo no braço solto, sem "bandeja" no balanço. (`node tools/fotos.mjs <plano> "t1,t2,…" "cam=x,y,z,ax,ay,az,fov" saida.jpg`)
- Toda interação vista de perto, de **dois ângulos**, nos quadros de início, meio e fim.
- Mãos: o objeto está NA palma? Os dedos fecham em volta? A mão segue a orientação do objeto?
- O objeto atravessa algo (lataria, bomba, mesa)? Some ou teletransporta?
- Folha a 1 qps do filme inteiro depois do render (`ffmpeg … fps=1,tile=8x6`).

## 3. Interações (regras de construção)
- Mão em objeto = `V.pegar(ator, lado, ponto, dedos, indicador, cotovelo, k, fecha)`: posição E rotação do pulso
  (o "target rotation" do Two Bone IK). A torção vai 75% no antebraço, o resto no pulso.
- A pegada é definida **no momento de pegar** e depois a mão gira **junto** com o objeto (rígida).
- Objeto preso (porta, portinhola, bico no gancho): a mão vai até a peça que se mexe, não a um ponto fixo.
- Sequência completa: aproximação → alcance → pegada → ação → soltura (com rampas de entrada/saída, nada liga/desliga).
- Rig sem dedos (Metalis): `V.ik2` a partir da pose neutra + mistura por slerp; um alvo por mão (média ponderada).

## 4. Movimento
- Andar = `V.caminhar` (cadência pela distância; **trava do pé**; mistura parado↔andando; `de:` vira proporcional ao ângulo; `re:` de ré; `rot:` direção fixa).
- Velocidade natural: 1,1–1,4 m/s andando (pico ≈ 1,22× a média com o ease padrão). Distância ÷ tempo sempre conferida.
- Virada grande (> 90°) no arranque: começar a virar parado antes de andar.
- Rota: nunca reta por cima de obstáculo — waypoint de desvio (`DESVIO`) e conferir no QA.
- Degrau/plataforma: `V.chao(x, z, plataformas)` levanta o pé.
- Fala: animação `talk` com `fala.peso()` (peso pela fala inteira), nunca pelo volume quadro a quadro.

## 5. Áudio
- Passos: `passos()` em `tools/som4.py` — um som por **contato do pé** (fases medidas no clipe em `videos/_pes` →
  `material/qa/pes.json`), superfície por cena (concreto, mato, madeira, corredor, carpete, arrasto), peso por personagem,
  variação por pisada, volume igualado entre superfícies. Parado = sem passo.
- Depois do `synth`: nenhum "guard" (estouro); stingers no máximo ~8 dB acima da mediana.

## 6. Regressão
Depois de QUALQUER correção: `bash tools/qa_todos.sh` de novo + folha 1 qps do filme. Comparar com o "antes".
Corrigiu mão → conferir cabeça. Corrigiu cabeça → conferir braços. Mexeu em rota → conferir colisão e passos.
