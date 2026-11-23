# 5. QA, erros que cometi e lições

## Os erros que EU cometi (e a regra que nasceu de cada um)
| # | Erro | Como apareceu | Regra |
|---|---|---|---|
| 1 | Comentário `//` inserido no meio de uma linha por edição automática (3 vezes!) | 1ª: a câmera do plano 41 parou de olhar pro carro (0:13 só névoa) — o diretor achou. 2ª e 3ª: planos quebraram (pego antes do render) | comentários inseridos em linha única só com `/* */`; `python3 tools/sintaxe.py` obrigatório; revisar o filme inteiro |
| 2 | Corrigir só um personagem quando o bug era de todos (mãos girando) | "Vc só focou no Igor... era todos" | bug visual → verificar o elenco inteiro |
| 3 | Confiar em métrica sem olhar (palma, deslize) | métrica de "variação" dava 0° com a mão errada; detector de deslize dava alarme falso | toda correção: medir + fotos de 2 ângulos |
| 4 | Velocidade irreal (frentista "correndo" andando) | pé patinando 1–4 m/s | distância ÷ tempo sempre |
| 5 | Mão cruzando o corpo (grana no bolso esquerdo com a mão direita; Igor folheando com a mão errada; tampa com a mão do lado errado) | QA "braço atravessa o corpo" | escolher a mão do lado do objeto |
| 6 | Objeto preso ao ALVO do IK em vez da mão (fita flutuando) | diretor: "fica flutuando" | objeto segue a palma real |
| 7 | Personagem que não alcança (Metalis 1,10 m) | mão parada no ar a 22 cm da porta | medir ombro, braço, alvo |
| 8 | Câmera atrás de algo (monitor cortando o rosto do Igor; moldura da porta = "bloco preto"; vidro que não desceu) | capturas do diretor 0:54 e 3:18 | raycast do centro da câmera; fotos do enquadramento real |
| 9 | Rotação/abertura invertida (véu fechado na frente; Nicolas virando pro lado errado) | fotos | sempre testar com foto depois de girar algo |
| 10 | Liga/desliga em 1 quadro (fechamento de dedos, direção da mão em degrau, gesto de fala entrando de uma vez) | QA "salto de mão" | tudo com rampa contínua |
| 11 | Entender o pedido pela metade ("frente da cabeça" × "cabeça inteira") | diretor: "acho que entendeu errado" | reler o pedido; quando ambíguo, mostrar opções lado a lado |
| 12 | Saída do carro antiga: pernas atravessando a porta fechada | só vi quando o diretor pediu a animação nova | revisar de perto TODA cena com interação, não só as mexidas |

## Sistema de QA (`tools/qa.mjs`) — o que mede
- Anatomia: pulso dobrado > 80°, mão torcida > 60°, pescoço > 75°, salto de mão > 28°/quadro, pé abaixo do chão, braço dentro do tronco,
  braço congelado ≥ 3 s, **pé deslizando** (nenhum dos dois pés parado por ≥ 0,17 s com o corpo andando).
- Continuidade: teletransporte > 25 cm/quadro (relativo a quem carrega). Colisão: cápsula do corpo em peça sólida, dois corpos < 30 cm,
  lataria do carro (caixa orientada), objeto flexível × tronco. Exceções marcadas no código (`userData.veiculo/noVeiculo/assento/vaoPernas/flexivel`).
- Limitações: não mede dedos atravessando objetos, expressão, nem visibilidade (um deslize atrás de uma porta fechada aparece no QA mesmo invisível).

## Processo obrigatório (protocolo do diretor)
1. Antes: `sintaxe.py`, ler `REGISTRO.md`/`NAO_REGREDIR.md`, QA "antes".
2. Corrigir pela causa raiz; registrar no `REGISTRO.md` (problema, cena, tempo exato, causa, correção, verificação).
3. QA de novo (PASSO=1 nos planos mexidos), fotos de perto, render, `quadros_vazios.py`, folha 1 qps do filme inteiro.
4. Versão: tag `vX-estavel`, cópia em `out/historico/`, `VERSOES.md`, relatório pro diretor (o que mudou, o que não deu pra verificar).
Ver cópias em `referencia/` (REGISTRO, CHECKLIST, NAO_REGREDIR, VERSOES, AUDITORIA).
