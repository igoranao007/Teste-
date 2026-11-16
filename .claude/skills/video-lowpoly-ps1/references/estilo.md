# Estilo low-poly PS1 — o que define o visual

## As 8 marcas técnicas (todas implementadas em `lib/ps1.js`)

| Marca | No PS1 | No motor |
|---|---|---|
| Resolução baixa | 320×240 | cena em 270×480 (1/4 de 1080×1920) ampliada 4× com `image-rendering: pixelated` |
| Vértice tremido | sem precisão abaixo do pixel | `gl_Position.xy` arredondado pra grade da resolução baixa (`tremor`: 1 = 1 pixel; 2 = mais grosso) |
| Textura entortada | sem correção de perspectiva | varyings `uv·w` e `w`, divididos no fragment (mapeamento afim) |
| Textura pequena sem filtro | ≤ 256×256, comum 128 ou menos, CLUT 4/8 bits | `P.textura` 16–32 px, nearest, sem mipmap, posterizada em 31 níveis |
| Cor de 15 bits + pontilhado | 5 bits por canal, dithering ordenado | passe final: Bayer 4×4 + 31 níveis por canal |
| Gouraud | luz por vértice | ambiente + key + fill calculados no vertex shader |
| Neblina | depth cueing pra esconder a distância de desenho | `smoothstep(perto, longe, profundidade)` por vértice |
| Transparência de 1 bit | cor-chave | alfa da textura < .5 é descartado; `opac` < 1 mistura como os 50% do console |

Fora: desfoque de profundidade, bloom, sombra projetada, antisserrilhado, reflexo especular — nada disso existia.

## Cenários do canal (`P.CENARIOS`)

- **Sala de teste (padrão).** Céu `#6f8496 → #aab5bd → #c6cbce` em 16 faixas pontilhadas; chão xadrez `#a3abb2 / #7f888f` (casa de 0,6, padrão a cada 1,2) que some na névoa `#c4c9cc` entre 3,5 e 14 unidades. Lembra as fases de teste dos jogos 3D da época. É neutra (baixo contraste, cinza-azulado), não briga com textura nenhuma e dá chão e escala pra qualquer objeto. Use `chaoY` pra encostar a cena no chão.
- **Degradê pontilhado.** Sem chão: `#47535f → #8b959d → #b7bcbe` em 10 faixas. Pra cenas sem onde pisar (dentro do corpo, espaço, fluxo de dados, diagrama), como as telas de seleção de personagem.
- Outros fundos continuam possíveis por cena (`fundoTex: P.ceu({...})`, `P.blueprint()`, `nevoa: {...}`), mas o canal usa os 2 acima pra manter a identidade.

## Paleta neutra (o padrão)

- Superfícies: branco-gelo `#e6e3dc`, cinza-claro `#c8cbc9`, bege `#bab2a3`, cinza-azulado `#a9b6be`.
- Materiais de obra: tijolo `#b4613b` com argamassa `#968f84`, aglomerado `#b89b72`, concreto `#b9b4aa`.
- Luz: key `#ece6dc` de cima-esquerda-frente, fill frio `#5b626e` da direita, ambiente `#585a60`.
- **Um acento por vídeo** — a coisa que o roteiro explica: incandescente `#ff7426`, veneno `#e6c344`, água `#9fd1ec`.
- Mais soturno quando o roteiro pedir: baixe `amb` e `keyCor`, puxe a névoa pra perto (`perto` 1,5 / `longe` 6) e escureça o céu. Mais alegre: céu mais azul, key mais quente. O motor é o mesmo.

## Composição 9:16

- Cena em profundidade (um atrás do outro); o assunto ocupa ⅓ ou mais da largura.
- Objetos e cômodos **em corte**: corta-se a metade virada pra câmera e marca-se a borda do corte.
- Câmera: plano fixo no estilo Resident Evil (alto, num canto) ou movimento lento — o tremido dos vértices aparece mais em movimento lento.
- Personagem orgânico só quando inevitável; cobra, minhoca, cabo e mangueira funcionam como corpo varrido.

## Legenda

Formato curiosidade: 1 a 3 palavras por vez, branca, Arial Black, contorno preto grosso e sombra, entrando com um "pop" curto. Fica **nítida** por cima da cena (é DOM, não passa pelo PS1) pra ler no celular. Posição padrão `y: 1240–1500` de 1920, sem cobrir o assunto.
