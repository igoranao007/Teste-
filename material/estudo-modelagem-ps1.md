# Estudo: como se faz um personagem low-poly de PS1 de verdade

Fontes lidas (tutoriais, artigos, fóruns, specs de pacotes profissionais) + 3 modelos de referência abertos e medidos no Blender.

## 1. Números de verdade (o que cabia no PS1)
- **Personagem inteiro: ~300 a 1.100 triângulos.** Snake (MGS1) ≈ 600 tris; base humana CC0 da Comp-3 = 402 tris; NPCs PS1/N64 profissionais = 1.114 tris; o "character creator" PSX da heyheythere = ~970 tris o corpo + roupas de 120–330 tris cada.
- **Textura: 256×256 no máximo, quase sempre 128×128.** Cabeça separada em **64×64** (corpo 128×128) nos NPCs profissionais. FF8 (Rinoa) usou 128×128.
- **Luz pintada na textura** (o PS1 só tinha luz por vértice, sem sombra): sombra embaixo do queixo, nas dobras, no pescoço — pintadas.
- **Paleta curta** (16 a 256 cores, 4/8 bits) e pontilhado.
- Pesos de osso **simples** (cada vértice preso a 1 osso, "skinning fixo") e **peças que se sobrepõem nas juntas** pra esconder a costura quando dobra.

## 2. Como se modela (o método que os tutoriais ensinam)
1. **Imagens de referência de frente e de lado** no fundo da vista, semitransparentes; modela "por cima" delas.
2. **Começa de um cubo, corta no meio e usa Mirror** (espelho com "clipping"): modela só metade, o lado de lá se copia sozinho → simetria perfeita.
3. **Bloco primeiro, detalhe depois**: cabeça, tronco, quadril, braço, antebraço, mão, coxa, canela, pé como blocos; acerta a **proporção e a silhueta** de frente, lado e costas antes de qualquer detalhe.
4. Vai refinando com **loop cut (Ctrl+R)**, **extrude (E)**, **inset (I)** e **edge slide (GG)** pra arredondar.
5. **Membros com 6 a 8 lados**; **2 a 3 laços de aresta em cada junta** (ombro, cotovelo, pulso, quadril, joelho), sem aresta atravessando a dobra.
6. **Mão**: bloco fino com um corte no meio e o polegar extrudado do lado (muitos jogos PS1 usavam mão "luva", com os dedos juntos).
7. **Cabeça**: cubo com loop cuts pra arredondar, inset pra órbita, extrude pequeno pro nariz e pras orelhas. **No PS1 os olhos NÃO são modelados — são pintados.**

## 3. Como se pinta (o mais importante pro "parecer bom")
- A cabeça é aberta como **uma faixa só** (projeção cilíndrica / frente + lado): cabelo em cima, rosto no meio, orelhas nas pontas, nuca nas bordas.
- **O rosto é minúsculo e simples**: olhos de 2–4 pixels (pupila escura + sobrancelha), nariz sugerido com 1–2 tons, boca de 3–5 pixels. Ver o atlas da heyheythere: o rosto inteiro ocupa ~40×25 px.
- **Pinta grande e reduz**: pinta em 256 e reduz pra 64 sem filtro (o detalhe vira pixel legível).
- **Cada parte tem seu espaço no UV** (sem sobreposição, senão pintar a nuca mancha o rosto).
- Cabelo, barba, boné e roupas são **malhas separadas e simples** por cima do corpo, cada uma com sua textura pequena.
- **Semelhança com uma pessoa real vem de 3–4 traços fortes**, não de foto: corte e cor do cabelo, sobrancelha, barba, formato do rosto, tom de pele.

## 4. O que eu fazia errado
| Errado | Certo |
|---|---|
| Colar/projetar foto no rosto | Pintar 3–4 traços fortes em poucos pixels |
| Olho como geometria separada (afundava/sumia) | Olho pintado na textura |
| Detalhe "realista" grande (barba de pontinhos, lábios desenhados) | Poucos pixels, poucas cores, luz pintada |
| Remendar a mão/cabeça de um modelo pronto | Modelar a peça com o método do bloco + espelho, ou usar uma base feita pra PS1 |
| Textura 512×256 na cabeça | 64×64 (ou 128×128 se for close) |

## 5. Bases boas encontradas (licença ok)
- **PSX Character Creator Free** (heyheythere, CC BY 4.0 — precisa creditar): corpo masculino e feminino com esqueleto, cabelo curto, rabo de cavalo, bob, barba/bigode, jaqueta, camiseta, moletom, jeans, saia, botas, óculos — **tudo peça separada, feito pra PS1**, rosto pintado no estilo certo. É a melhor base pro nosso elenco.
- **Low Poly Human Mesh** (Comp-3, CC0): 402 tris, limpa, boa pra estudo de proporção.

## Fontes
- [Grant Abbitt — PS1 low poly character (resumo)](https://hq-raydata-co.pages.dev/vault/06-reference/2026-04-29-grant-abbitt-ps1-low-poly-character/)
- [David Colson — Building a PS1 style retro 3D renderer](https://www.david-colson.com/2021/11/30/ps1-style-renderer.html)
- [Bitsoft — Rigged Low-Poly Male NPCs (PS1/N64)](https://bitsoft.itch.io/low-poly-male-npc)
- [Comp-3 — Low Poly Human Mesh (CC0)](https://comp3interactive.itch.io/low-poly-human-mesh)
- [Polycount — MGS1 case study](https://polycount.com/discussion/139243/mgs1-case-study-calling-all-you-lowpoly-fiends)
- [Blender Artists — Low poly head tutorial](https://blenderartists.org/t/low-poly-head-tutorial/440186)
- [Polycount — texturas PSX (discussão)](https://polycount.com/discussion/226167/)
- [Elisabet Heikkilä — A Guide to Building a 3D Game Character (PDF)](https://www.theseus.fi/bitstream/handle/10024/133905/Heikkila_Elisabet.pdf?sequence=1) (bloqueado pra download aqui)
