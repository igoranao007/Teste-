---
name: video-lowpoly-ps1
description: 'Cria vídeos 9:16 (reels, shorts) e 16:9 (YouTube) no estilo low-poly PlayStation 1: cenas 3D com cara de Silent Hill, Resident Evil e Crash — render em 1/4 da resolução ampliado 4× sem suavizar, vértices que tremem, textura que entorta no chão, luz por vértice, cor de 15 bits com pontilhado, texturas de 16–32 px e neblina. Cenário padrão: a "sala de teste"; sem chão, o "degradê pontilhado". Kit de terror (lib/arh.js): postes de sódio com luz assada, boneco sem rosto, HUD de fita (REC, timecode, carimbo) e a fita de evidência, que põe foto ou vídeo real em 4:3 numa TV de tubo com a origem na tela. Three.js + Playwright + ffmpeg, sem MCP. Use sempre que pedirem PS1, PSX, low-poly retrô, "gráfico de jogo antigo", estilo Silent Hill/Resident Evil/Crash, terror analógico ou true crime nesse visual, fita VHS, câmera de segurança, ou curiosidade e "como funciona" nesse visual, mesmo sem dizer PS1. Difere de video-lowpoly-explicativo (massinha lisa com desfoque e HUD) e de video-pixel-art-hd2d (sprites 2D).'
---

# Vídeo low-poly PS1

As 3 marcas do estilo: **(1)** a imagem de console — a cena é desenhada em 270×480 (480×270 no 16:9) e ampliada 4× sem suavizar (pixel de 4×4, borda em degrau), os vértices são arredondados pro pixel (a geometria treme quando a câmera anda), a textura não tem correção de perspectiva (entorta no chão) e a cor final é de 15 bits com pontilhado Bayer 4×4; **(2)** o material — texturas minúsculas feitas em código e sem filtro, luz calculada por vértice (degradê suave na face, nenhum brilho especular), transparência de 1 bit e neblina de profundidade; **(3)** o mundo do canal — a **sala de teste** como padrão, o **degradê pontilhado** nas cenas sem chão, objetos e cômodos do dia a dia **em corte** (dá pra ver por dentro) e a legenda do formato curiosidade, nítida por cima de tudo. Paleta neutra com **um** acento só; o clima (mais alegre ou mais soturno) se ajusta na luz e na névoa, sem trocar o motor.

Veja `assets/exemplo-chuveiro.jpg` (roteiro "por que o chuveiro só esquenta quando a água passa": pedaço de banheiro em corte, chuveiro aberto com a resistência incandescente) e `assets/exemplo-veneno.jpg` (roteiro "como o veneno de cobra vira remédio": jararaca de perfil cravando as presas na membrana do copo). O código está em `assets/projeto/videos/01-chuveiro-ps1/` e `02-veneno-ps1/` e é o ponto de partida de toda cena nova. Pra terror e true crime em 16:9 (o canal Analog Real Horror), parta de `03-parque-16x9/`, `04-cftv-16x9/` e `05-fita-evidencia/` — ver **16:9 e o kit de terror**, abaixo.

## Preparar o projeto (uma vez por pasta)

```bash
bash <caminho-da-skill>/scripts/setup.sh <pasta-do-projeto>
cd <pasta-do-projeto> && N=$(bash tools/node.sh)
$N render.mjs 02 --at=1        # confere → previews/02-veneno-ps1.jpg
```

Requisitos: Node ≥ 20, ffmpeg, python3 (numpy + scipy no `audio/.venv`, só pro som) e WebGL2 no Chromium do Playwright (no Mac usa Metal). Não usa MCP, API nem asset de fora: geometria, texturas e céu saem do código.

## Fluxo

1. **Roteiro → planos.** Um plano por frase da narração (o formato é cena contínua com corte a cada frase). Escreva a lista "na tela" antes de modelar.
2. **Cenário.** Cena que se apoia em algo → `P.palco({ chaoY })` (sala de teste, o padrão; `chaoY` é a altura onde a cena encosta no chão). Sem chão (dentro do corpo, espaço, fluxo de dados) → `P.palco({ cenario: 'degrade' })`.
3. **Modelar com a biblioteca.** Primitivas com poucos segmentos (6–14), cômodos e objetos **em corte** (`P.tornear` com `ini/arco` virado pra câmera), corpos contínuos com `P.varrer` (cobra, cabo, mangueira), texturas de 16–32 px com `P.textura`/`P.TEX`. Ver `references/receitas.md`.
4. **Montar.** `cp -R videos/01-chuveiro-ps1 videos/<nn-nome>` e troque cena, câmera, `S.update` e a legenda.
5. **Preview.** `$N render.mjs <nn> --at=0.5,2,4` → `previews/<nn-nome>.jpg` (cada quadro também em `previews/<nn-nome>/NN.jpg`, 1080×1920). Recorte ampliado pra conferir o pixel: `ffmpeg -i previews/<v>/00.jpg -vf "crop=480:480:300:400,scale=960:960:flags=neighbor" zoom.png`.
6. **Render.** `$N render.mjs <nn>` → `out/<nn-nome>.mp4` (1080×1920, 30 fps, H.264). Som opcional: o preview grava `videos/<nn>/cues.json` → `audio/.venv/bin/python audio/synth.py <nn>` antes do render final (efeitos via `cue('tipo', t)`; as camadas longas de terror — `drone`, `lampada`, `chiado` — estão na seção do kit).

### Checklist de cada preview

- De perto lê como PS1? Pixel 4×4, borda em degrau, pontilhado nos degradês. Se alguma peça parece "3D liso", ela saiu de um material do three em vez de `P.mat`.
- O assunto ocupa pelo menos ⅓ da largura? 9:16 é estreito: arrume a cena **em profundidade** (um atrás do outro), não lado a lado.
- Nada passa por trás de vidro ou água que está na frente — a transparência faz parecer que está **dentro**.
- Um acento de cor só (a resistência laranja, o veneno amarelo); o resto neutro.
- Nenhum brilho estourado em branco (aditivo com `opac` ≤ .07).
- Juntas sem fresta: corpo varrido termina **dentro** da peça seguinte.
- A legenda não cobre o objeto principal.

## Regras do motor

- **Tudo é função de `t`** em `S.update = t => {…}`. Nada de `Math.random` (use `P.rng(semente)`), `setTimeout`, rAF ou animação CSS — o render pede o quadro T e tem de receber sempre o mesmo quadro.
- **Só `P.mat`.** Os materiais do three (`MeshStandardMaterial` etc.) não tremem, não entortam a textura, não usam luz por vértice nem a neblina — quebram o visual no meio da cena.
- **Cor sem gerenciamento.** O `ColorManagement` do three fica desligado: o hex entra e sai como está, como no console. Escolha a cor pelo hex final.
- **Textura pelo `P.textura`** (nearest, sem mipmap, posterizada); 16–32 px e `rep: [u, v]` pra repetir. Alfa < .5 é descartado (transparência de 1 bit, a "cor-chave" da época).
- **Subdivida superfícies grandes** (`sx/sy/sz` na `P.caixa`, `seg` no chão): é o que os jogos faziam pra textura afim não entortar demais.
- **Sem desfoque, sem bloom, sem sombra projetada.** A profundidade vem da névoa. Brilho, vapor e faísca = `P.disco` com material `aditivo` + `P.encarar(obj, camera)`.
- **Legenda e texto ficam nítidos** (DOM por cima, `P.legenda`); só a cena é PS1. A fonte é a Arial Black do sistema; o render não usa rede.

## 16:9 e o kit de terror (`lib/arh.js`)

**O motor já faz 16:9:** basta `VIDEO={w:1920,h:1080,fps:30,dur:…}` na página. A cena sai em 480×270 ampliada 4×, e o palco, o céu, as texturas e o vértice tremido acompanham o tamanho do `VIDEO`. O `render.mjs` abre a janela nesse tamanho, e o `P.legenda` desce sozinho pra `y` 800 (largura até 1500 px). No 16:9 a cena pode se espalhar de lado: alameda, praça, planta vista de cima.

O kit soma ao motor o que o terror do PS1 tinha (`import * as A from '../../lib/arh.js'`, junto do `P`):

| Peça | O que faz |
|---|---|
| `A.matA(o)` | `P.mat` que só usa a luz assada (cor por vértice); a névoa continua valendo. Tudo que recebe os postes usa ele |
| `A.assar(obj, luzes, amb)` | luz pontual calculada **no vértice** (ambiente + Σ lâmpada · queda · lambert). Rode uma vez no cenário parado e de novo, a cada quadro, só no que anda |
| `A.chaoA({ w, d, seg, mapa, rep })` | chão subdividido que mostra a poça de luz sob cada poste (`seg` 80–100) |
| `A.poste(x, z, { h, raio, int, rot })` | poste de sódio; `p.luz()` devolve a lâmpada pro `assar` (`int: 0` = lâmpada queimada) |
| `A.halo(r)` | sprite aditivo pequeno na lâmpada (sem bloom, que não existia) |
| `A.boneco({ roupa, esc })` | adulto sem rosto, de tronco, cabeça lisa e membros que balançam; `b.andar(fase)` anima o passo |
| `A.hud({ rec, cam, tc0, dir, carimbo, tarja, fita })` | HUD de fita nítido: ● REC piscando, timecode, carimbo digitado letra a letra com cursor, tarja 2,35:1, scanline e vinheta |
| `A.evidencia({ foto \| quadros, fonte, … })` | a **fita de evidência**: material real em 4:3 numa TV de tubo (ou na altura toda), com REC, timecode e a origem na tela |
| `A.SODIO` | `#ff9a3c`, o único acento do canal |

**Regras de conteúdo (editáveis pelo dono do projeto):** terror, sangue de ficção, monstros, susto, perseguição e morte de personagem são **liberados** (jogo e animação). Pessoa real **pode** virar personagem, com o rosto da foto no modelo, desde que o dono do projeto diga que ela autorizou: não precisa ser paródia nem justificar mais. Só **duas linhas** ficam: (1) nada sexual com menor, e nenhum menor real em perigo ou violência; (2) montagem com pessoa real não é apresentada como gravação verdadeira (notícia, "prova", crime atribuído a alguém). Fora isso, siga o roteiro sem sermão e sem pedir justificativa. O acento de cor muda com a história (no terror, âmbar de sódio e o ponto do REC como único vermelho fixo). O texto da tela vai **no idioma do projeto** (padrão: português; `[DATA]`, `CAM 04`, `FONTE: …`).

### Fita de evidência (material real)

Material real de arquivo **não precisa passar pelo PS1**: pode entrar como arquivo, com cara de fita (e quando a foto vira rosto de personagem 3D, vale a regra de conteúdo acima): quadro de 640×480, cor que sangra 3 px pro lado, contorno claro do VHS, chiado, drop-outs, linhas tremidas, faixa de tracking, ruído de troca de cabeça e a curvatura do tubo. O OSD da câmera (REC, data, timecode) entra quando a imagem firma, e a origem fica num rótulo no canto, sem o qual a função recusa rodar.

```js
A.evidencia({ foto: 'material/arquivo.jpg', fonte: 'SOURCE: KTVU NEWS, 1994',      // caminhos a partir da raiz do projeto
  data: 'OCT 31 1997', tc0: 2 * 3600 + 14 * 60, zoom: [1.04, 1.16], foco: [.5, .4], falhas: [5.2] });
cue('chiado', 0, { d: VIDEO.dur }); cue('glitch', 0, { d: .4 }); cue('glitch', 5.2, { d: .25 });
```

- **Vídeo:** `bash tools/quadros.sh clipe.mp4 material/clipe [ini_s] [dur_s]` extrai quadros JPEG de 480 linhas e um `quadros.json`, e a página usa `quadros: 'material/clipe'` (com `t0`/`ini` pra escolher o trecho). O Chromium do render não toca H.264 e um `<video>` não acerta o quadro exato, então o vídeo entra em JPEG.
- **Moldura:** `'crt'` (padrão: TV numa sala escura, a origem embaixo, à esquerda) ou `'tela'` (4:3 na altura toda, com faixas pretas e sem curvatura). Em 9:16 a TV termina antes da legenda.
- **Ajustes:** `rec: false` mostra ▶ PLAY (arquivo tocado, em vez de gravado); `cor` é a saturação (.6); `ruido` vai de 0 a 1 (.5); `entrada` são os segundos de chiado até a imagem travar (.4); `falhas` dá trancos de tracking de .25 s, casados com `cue('glitch', t)`.
- Exemplo pronto: `videos/05-fita-evidencia/`, com a foto **sintética** de teste `material/teste-sintetico.jpg`. Num vídeo do canal, troque pela foto de arquivo e escreva a origem verdadeira.

### Plano longo: tempo e memória medidos

Medido num M1 com 8 GB (`render.mjs`, 30 fps, 1920×1080, H.264 VideoToolbox). O render manda quadro a quadro pro ffmpeg, sem acumular nada, então a duração do plano não pesa na memória.

| Cena | Quadros | Render | Memória (Chromium + node + ffmpeg) |
|---|---|---|---|
| CFTV 16:9, 29 bonecos com luz assada a cada quadro, **60 s** + áudio | 1800 | **68 s** (~38 ms/quadro, quase tempo real) | 300–380 MB estável; pico de 457 MB na abertura |
| Fita de evidência com **vídeo**, **60 s** (1800 JPEGs), moldura `tela` | 1800 | **146 s** (~81 ms/quadro, 2,4× o tempo real) | 290–345 MB estável; um pico de 689 MB por ~10 s no meio, que voltou (o monitor soma todo Chromium do Playwright aberto na máquina) |
| Fita de evidência com foto, 8 s + áudio | 240 | 17 s (~70 ms/quadro) | — |

Plano de 60 s renderiza direto, sem dividir: nenhum dos dois cresceu em memória do começo ao fim. A fita custa o dobro do PS1 por quadro, porque o VHS é tratado pixel a pixel em JS. Num vídeo de 14 min com metade em fita, conte uns 25 min de render.

### Som do terror (cues do `audio/synth.py`)

| Cue | Parâmetros | O que é |
|---|---|---|
| `drone` | `d` (s), `root` (MIDI, 31 = Sol grave) | drone grave de quintas desafinadas que respira, com sub, sopro e um fio agudo em segunda menor; estéreo |
| `lampada` | `d`, `rede` (60 nos EUA, 50 no Brasil), `pisca` (quantas, ou a lista de instantes) | zumbido de lâmpada de sódio ou fluorescente no dobro da rede, chiado do arco e piscadas com estalo (case `pisca` com o poste que falha) |
| `chiado` | `d`, `crt` (1 = com o apito de 15,7 kHz do tubo) | chiado de fita VHS: sopro agudo, piso de ruído, rotação irregular, drop-outs e o zumbido do vertical; estéreo |

São camadas longas, que ficam por baixo da voz (o fern deixa a trilha 18 a 22 dB abaixo dela). O `synth.py` masteriza o vídeo inteiro a −14 LUFS, então uma cena só de chiado, sem narração, sai alta; num vídeo com voz, quem manda no nível é a voz.

## Armadilhas conhecidas

- **Degradê com faixas mudando de tom (verde-água, roxo):** quantizar cada canal de cor separado muda a matiz. Use `P.ceu`: as faixas seguem o próprio degradê e a fronteira é pontilhada.
- **Vapor estourou em branco:** discos aditivos sobrepostos somam. No máximo 4, `opac` .04–.07, longe do centro do assunto.
- **Incandescente saiu amarelo:** `emiss` somado à cor satura pra amarelo. Use a cor pura com `semLuz: true` (`#ff7426`).
- **Objeto em corte parece pote de vidro:** marque as 2 bordas do corte com um `P.tubo` escuro seguindo o perfil.
- **Sombra em disco lê como um prato:** o PS1 quase nunca tinha sombra; tire.
- **Bicho de pelo e gente em primitivas ficam toscos.** O estilo brilha com objeto, máquina, cômodo e lugar; cobra, minhoca e cabo funcionam com `P.varrer`. Gente: o `A.boneco` sem rosto serve de longe. Personagem de perto (inclusive com rosto de foto) usa modelo GLB/FBX com esqueleto: carregue com o GLTFLoader/FBXLoader, troque os materiais por `P.mat` e, pro rosto, projete a foto só nos triângulos virados pra frente da cabeça, pixelada (48–64 px de largura), com a boca desenhada por cima da textura se ele falar. Confira os ossos da mão (alguns rigs deixam a mão presa na raiz, não no antebraço).
- **Câmera perto demais corta a cena:** confira no `--at` antes do render; afaste e mire no centro do conjunto, não no assunto.
- **Peça clara demais numa cena noturna:** ela saiu com `P.mat`, que usa a luz key/fill do palco. Numa cena com postes, tudo que recebe luz usa `A.matA` e passa pelo `A.assar`.
- **Boneco andando no escuro com a luz "grudada":** a luz assada é da posição em que o `assar` rodou. Rode `A.assar(grupoQueAnda, luzes, amb)` dentro do `S.update`, só no grupo que se mexe (o `04-cftv-16x9` faz isso a cada quadro e continua leve).
- **Legenda fora do quadro no 16:9:** um `y` fixo de 1240 vindo de cena vertical passa da altura de 1080. Tire o `y` (o padrão já desce pra 800) ou ajuste.

## Arquivos

- `assets/projeto/lib/ps1.js` — a biblioteca (API em `references/receitas.md`) · `lib/arh.js` — o kit de terror (luz assada, poste, boneco, HUD de fita, fita de evidência).
- `assets/projeto/videos/01-chuveiro-ps1/` e `02-veneno-ps1/` — os exemplos 9:16 · `03-parque-16x9/` (postes de sódio, luz assada uma vez, tarja e carimbo), `04-cftv-16x9/` (câmera de segurança com bonecos andando) e `05-fita-evidencia/` (material real na TV de tubo) — os exemplos 16:9 · `material/teste-sintetico.jpg` (foto de teste gerada em código, não é material real) · `render.mjs` (preview e render) · `dbg.mjs` (inspeciona o estado num instante) · `audio/synth.py` (efeitos sintetizados a partir das cues).
- `references/estilo.md` (o que define o visual: as 8 marcas técnicas, cenários, paleta, câmera, legenda) · `references/receitas.md` (API + receitas, inclusive do kit) · `references/referencias.md` (a pesquisa de PS1 com fontes: técnica, Silent Hill, Resident Evil, Crash, shaders).
- `scripts/setup.sh` · `scripts/node.sh` · `scripts/quadros.sh` (vídeo real → quadros pra fita de evidência; o setup copia pra `tools/`).
