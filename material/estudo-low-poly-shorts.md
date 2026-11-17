# Estudo: "You've Never Touched Anything" (canal Low Poly Shorts)

38,8 s · 1080×1920 (9:16) · 30 fps · 53 mi de views. Analisado quadro a quadro (2 por segundo), cortes detectados por mudança de cena, narração transcrita com tempo por palavra, volume medido.

## 1. Roteiro (a estrutura é o segredo)

| Tempo | Função | Fala |
|---|---|---|
| 0,0–3,2 | **Gancho absurdo, sem introdução** | "If you touch something and your atoms align in just the perfect way…" |
| 3,8–7,1 | Promessa impossível | "…you could phase right through it like a ghost." |
| 7,6–8,6 | Virada | "But this is statistically impossible." |
| 9,5–22,2 | Explicação em 1 ideia só | átomos têm uma camada de energia que repele, como ímã |
| 22,7–30,0 | Conclusão chocante | "So you've never actually touched anything in your entire life." |
| 30,6–33,5 | **2 piadas de internet** | "never touched grass" / "she technically didn't cheat on you" |
| 33,6–37,9 | Escalada final | "if you forced them to contact… they would fuse and trigger a—" |
| 37,9–38,8 | **Corte no meio da palavra** + clarão amarelo, o homem desintegra | (sem fala) |

- **134 palavras em 38,8 s = ~207 palavras por minuto.** Rápido, sem respiro, sem "olá", sem "inscreva-se".
- A frase termina cortada ("trigger a—") e o vídeo volta ao início "If you touch something": **o loop prende o espectador** (assiste de novo sem perceber).
- A retenção do vídeo cai pela metade nos 2 primeiros segundos: tudo depende da 1ª frase.

## 2. Ritmo de edição

- **19 cortes em 39 s → um plano novo a cada ~2 s** (o mais longo, 5 s, é a animação dos átomos).
- **Cada corte acompanha uma frase**: o que a voz diz é exatamente o que aparece ("press your hand" → close na mão encostando na parede).
- **A câmera nunca fica parada**: todo plano tem dolly, giro ou zoom lento. Mesmo o personagem parado está sendo orbitado.
- Ângulos exagerados: câmera de baixo (contra-plongée) no dedo, de cima no homem caindo, close extremo na mão.

## 3. Animação e textura (o que deixa fluido e bonito)

Medido quadro a quadro (30 quadros seguidos em 4 trechos):

- **Animação de verdade a 30 qps: nenhum quadro repetido.** Todo quadro muda (diferença média 2,8 a 8,6 por quadro), então nada "trava".
- **Movimento de câmera constante e macio**: no trecho da mão a diferença entre quadros varia só ±0,2. A câmera anda em velocidade quase fixa (dolly/órbita lenta, com aceleração suave no começo e no fim), sem trancos nem cortes de velocidade.
- **Corpo animado por keyframes com curva suave** (estilo animação pronta tipo Mixamo): o braço sobe e desce acelerando e freando; mãos com dedos posados (aponta, espalma, mostra as palmas). Nada é "teleportado".
- **Sem tremor de vértice e sem resolução baixa**: renderiza em 1080×1920 nativo. A geometria é low-poly (bordas retas e serrilhadas, sem antisserrilhado), mas a imagem é estável. O nosso PS1 tem vértice tremendo + render a 1/4 + pontilhado, e isso faz o movimento parecer "picado".
- **Texturas fotográficas** (papel de parede, carpete, couro, jeans, pele, xadrez do sofá), de 256 a 512 px, **com filtro suave** (bilinear): de perto ficam borradas, não quadriculadas. Só a mão em close extremo mostra pixel.
- **Luz chapada e clara**: quase sem sombra, cor de textura aparece pura. Nada de névoa.
- **Modelos com proporção certa e texturas bem mapeadas** (rosto foto no personagem, roupas com dobras pintadas): é isso que dá o ar de "jogo de PC de 2002" em vez de "boneco".

**Pra chegar nisso no nosso motor:** um "modo fluido" = `divisor` 1 ou 2 (em vez de 4), `tremor: 0`, sem pontilhado, textura com filtro linear e 256–512 px, luz mais aberta; animações de corpo prontas (o pacote *PSX Animation Library Free* que já baixamos tem 30 animações humanoides: andar, sentar, apontar, pegar) em vez da IK feita na mão; câmera sempre andando com curva suave.

## 4. Visual

- Low-poly de PC/PS2 do fim dos anos 90 (não é PS1 duro): **render em resolução cheia**, sem pontilhado e sem vértice tremendo. Bordas serrilhadas, texturas fotográficas pequenas e esticadas (papel de parede, carpete, jaqueta de couro).
- **Cores saturadas e claras**: lilás, laranja, verde-grama, azul royal. Nada escuro. Luz chapada, quase sem sombra.
- Um personagem "cara comum" (jaqueta marrom, rosto meio esquisito) que faz tudo: aponta, cai, grita, mostra as mãos.
- Sala de casa simples (sofá xadrez, relógio, janela de céu azul) = cenário reaproveitado em vários planos.
- **Mundo microscópico**: esferas azuis transparentes com núcleos coloridos sobre fundo de água/plasma animado (azul, depois roxo, rosa, amarelo).
- Efeitos baratos e claros: **cena em preto e branco** para "impossível", **número gigante em vermelho** ("1 in 1,000,000,000…"), **logo do canal flutuando** entre partículas, **clarão branco/amarelo** e o corpo "desmanchando" em pixels no final.
- **Piada visual na hora certa**: na fala "she didn't cheat on you", aparece a esposa abraçada com outro homem na porta.

## 5. Texto na tela

- Legenda **pequena**, amarela com contorno preto, fonte sem serifa simples, **no meio da tela** (não embaixo).
- **2 a 4 palavras por vez**, sincronizadas palavra a palavra com a voz.
- Sem emoji, sem animação de texto, sem destaque de palavra: é só leitura rápida.

## 6. Som

- **Narração em inglês, voz masculina calma**, sintetizada ou de locutor, num tom de "curiosidade".
- Música de fundo constante (Bert Cole, bitbybitsound.com), baixa, sem drop.
- Volume integrado **−15,7 LUFS** com **LRA 1,7 LU**: volume praticamente constante do começo ao fim (bem comprimido, para celular).
- Efeitos pontuais (choque elétrico no final).

## 7. O que levar pro THE GREEN PATH

1. **Gancho em 2 s.** Hoje abrimos com 1,5 s de chiado no preto: no Shorts isso perde metade do público. Abrir já com o carro e uma frase/título forte.
2. **Um plano a cada 2–3 s e câmera sempre andando.** Os planos de 8–17 s (elevador, sala do Igor) precisam virar 3–5 planos curtos cada, com dolly/giro.
3. **Fala e imagem casadas.** Cada frase do Igor com um close do que ele fala (o arquivo, a maleta, a fita).
4. **Legendas de 2–4 palavras, no meio da tela**, sincronizadas palavra a palavra (o whisper já dá o tempo de cada palavra).
5. **Final cortado que puxa o loop**: o estrondo do final cortar no meio e voltar no carro na estrada.
6. **Um momento de humor/absurdo** na hora certa, como a piada da traição.
7. **Volume constante** (comprimir a mix pra LRA baixo) e mais **cor**: manter o verde, mas com contraste maior, menos tela quase preta.
8. Se for pra Shorts/Reels: **versão 9:16** (a skill já renderiza 1080×1920).
