# THE GREEN PATH — o que já funciona e NÃO pode regredir

Atualizada a cada versão. Depois de qualquer mudança, cada item abaixo é conferido do jeito indicado.
Se um item quebrar, a versão não é entregue (volta pra última estável — ver `VERSOES.md`).

| # | Funciona hoje | Plano(s) | Como conferir |
|---|---|---|---|
| 1 | Cabeças paradas no lugar (sem girar sozinhas) | todos | QA "pescoço torcido" = 0 |
| 2 | Mãos com palma pro corpo; sem "bandeja" ao andar | todos | QA "mão torcida" = 0 + `videos/_pose` de frente e de lado |
| 3 | Nada acumula entre quadros (mesmo t = mesma pose) | todos | `tools/tremor.mjs`; `__seek(t)` 2× igual |
| 4 | Volante: mãos em 10h e 2h, dedos fechados no aro, volante gira | 41, 42, 43, 47 | close no carro (41 e 42) |
| 5 | Vidro do carro fumê preto; para-brisa mais claro | 41–47 | visual |
| 6 | Adryan abaixa o vidro pelo botão da porta antes de falar | 43 (5,1–6,0) | foto 5,0 / 5,6 / 6,1 |
| 7 | Frentista: anda até a bomba, tira o bico com pegada no cabo, abre a portinhola, encaixa o bico na horizontal, abastece, tira, fecha, pendura | 43 (9,6–20,6) | fotos 12,8 · 13,3 · 14,7 · 15,3 · 18,5 · 20,2 (2 ângulos) |
| 8 | Mangueira contorna o corpo do frentista (não atravessa) | 43 | QA "mangueira atravessa o corpo" ≤ 3 cm |
| 9 | Dinheiro sai do bolso do Adryan, passa de mão em mão na janela, vai pro bolso DIREITO do frentista | 43 (19,8–24) | fotos 23,1 / 23,35 / 23,9 |
| 10 | Metalis chega andando sem patinar; gestos ao lado do corpo (sem braço cruzando o rosto) | 44 | QA 44; fotos de frente 10–27 s |
| 11 | Olhos do Metalis: íris amarela; no mato só a íris aparece | 44, 45, 49 | fotos 35 s (44), 49 |
| 12 | Entrega da maleta Nicolas → Adryan pela alça | 47 | fotos 2–5 s |
| 13 | Adryan sai do carro de verdade: maçaneta, porta abre, uma perna de cada vez, mão na coluna, cabeça baixa, sai do raio da porta, empurra, porta bate (com som) | 47 (11–15,5 s) | QA 47; fotos 11,1 · 12,2 · 12,9 · 13,3 · 13,95 · 14,95 · 15,3 |
| 14 | Porta secreta: 3 batidas (som no contato), portinhola corre, senha pela fresta (POV), portinhola fecha, Gusta sai do arco da porta, destranca e abre (rangido) | 48 | QA 48; fotos 1,05 · 2,5 · 4,8 · 7,0 · 8,4 · 9,6 |
| 15 | Elevador: andam assim que a porta abre, passo natural, param e conversam em plano/contraplano | 50 | fotos 1,5 · 6 · 11,5 · 12,4 · 14 |
| 16 | Escritório do Igor verde e escuro; mãos do Igor de palma pra baixo no teclado/fita/Enter | 51–55 | QA 51/54; closes |
| 17 | Passos: um som por contato real do pé, superfície da cena, volume igualado | todos | `tools/som4.py` (contagem) + escuta |
| 18 | Pé de apoio PARADO no chão ao andar (trava do pé) | todos com caminhada | QA "pé deslizando" = 0 |
| 19 | Nenhum trecho de câmera olhando pro nada | filme | `python3 tools/quadros_vazios.py` = 0 |
| 20 | Entrega 720p < 100 MB (GitHub) | entrega | `ls -l entrega/` |
| 21 | Metalis: mão não passa na frente do rosto ao apoiar na janela | 44 (4–5 s) | fotos 4,0–5,0 |
| 22 | Igor: cabeça presa ao pescoço, monitor fora do rosto ao pegar a fita | 53 (8,6–12 s) | fotos |
| 23 | Carro na mesma escala do Adryan nos planos com os dois do lado de fora | 47, 48 | visual |
| 24 | Fita VHS sempre na palma do Igor (pega na maleta, leva ao videocassete) | 53, 54 | fotos 53 · 10,5 / 11,9; 54 · 0,8 / 1,9 |
| 25 | Metalis agarra a borda da janela com a mão direita (pulso dobrado, sem torcer) e solta pra gesticular | 44 | QA 44; POV 5,5 / 29,6 |
