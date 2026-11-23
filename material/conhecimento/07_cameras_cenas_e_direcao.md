# 7. Câmeras, cenas e direção

## Regras de câmera que aprendi
- **Rosto feito de foto** (Igor, Dom) só fica bom **de frente**: ponha a câmera no eixo do olhar do personagem. De lado parece placa/bolha.
- **Teste o que está entre a câmera e o rosto:** monitor (Igor 53/58), moldura dianteira da porta e retrovisor (Metalis 44), vidro do carro.
  Use `dbg_pagina` com raycast do centro da câmera pra saber qual malha está tapando.
- **POV** resolve muita coisa: Adryan dirigindo (cabeça dele escondida, câmera = osso da cabeça); Gusta pela fresta (esconde o Gusta enquanto a câmera está "na cabeça" dele);
  Metalis visto de dentro do carro.
- Não deixe o último quadro de um plano ficar preto sem querer (portinhola fechando na cara da câmera) — corte antes.
- Plano de diálogo: plano/contraplano **por cima do ombro**, sem colar o ombro na lente.
- Câmera com micro-tremido rápido faz os vértices do PS1 "piscarem" → use balanço lento.
- `tools/quadros_vazios.py` depois de TODO render; pretos propositais vão em `PROPOSITAL`.

## Como cada cena difícil foi resolvida (resumo)
- **41/42 estrada e Nicolas:** câmera interior lenta; mãos no volante a 10h/2h com o volante de verdade girando.
- **43 posto:** sequência real do frentista (ver 04), câmeras de 2 ângulos em cada interação, grana com câmera lateral.
- **44 Metalis:** chegada sem patinar, mão na janela, gestos com alvos relativos ao ombro, POV do Adryan pros closes, olhos amarelos no fim.
- **47 cabana:** saída do carro realista (lado do motorista, luz da varanda), Nicolas no carro olhando em volta.
- **48 senha:** portinhola + POV do Gusta.
- **50 elevador:** andam quando a porta abre, passo natural, param e conversam.
- **57 maleta (v5):** POV do Adryan, maleta aberta brilhando, Nicolas vira o rosto pra responder (só legenda), placa surgindo na neblina.
- **56/58/59 final (v5):** chiado verde → amarelo + "LOCAL DESCOBERTO"; Igor iluminado de amarelo; câmera entra no monitor; o Dom quase invisível atrás do chiado
  (terminal por cima com opacidade 0,5–0,8 e o ator renderizado no escuro atrás); "Dom?! É você?"; preto seco; "EM BREVE" verde.
