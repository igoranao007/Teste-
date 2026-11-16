# Referências — a pesquisa de PlayStation 1 por trás da skill

## As 8 marcas técnicas do visual PS1

1. **Vértice tremido (vertex snapping).** O PS1 não tinha precisão abaixo do pixel: cada vértice "pula" pro pixel inteiro mais próximo, e a geometria treme quando a câmera ou o objeto se mexe devagar. No motor: arredondar `clip.xy / w` pra grade da resolução baixa.
2. **Textura entortada (mapeamento afim).** Sem correção de perspectiva, as linhas retas da textura dobram em chão e parede. No motor: passar `uv * w` e `w` como varyings e fazer `uv = v.xy / v.z` no fragment. Os devs subdividiam o chão pra controlar o exagero, e a gente faz igual.
3. **Resolução baixa.** O original era 320×240. Pro 9:16: renderizar em **270×480** e ampliar **4× sem suavização**, o que dá 1080×1920 exato.
4. **Textura pequena e sem filtro.** O máximo era 256×256 e o comum, 128×128 ou menos. Filtro nearest, sem mipmap, com paleta de 16 ou 256 cores (CLUT de 4 ou 8 bits).
5. **Cor de 15 bits + dithering.** 5 bits por canal, com dithering ordenado Bayer 4×4, que aparece nos degradês escuros.
6. **Gouraud.** Luz calculada por vértice e interpolada na face, sem brilho especular realista. Muita cor por vértice.
7. **Neblina de profundidade.** Esconde o limite de distância de desenho. Em Silent Hill, virou a assinatura do jogo.
8. **Sem z-buffer.** A ordenação era por polígono e às vezes eles trocavam de ordem e piscavam. Isso fica só como efeito opcional.

E mais: poucos polígonos (personagem com algumas centenas de triângulos) e proporções blocadas (FF7).

## As 3 direções de arte

- **Silent Hill (1999).** Escuro, verde-cinza dessaturado, a escuridão e a neblina engolem o fundo, ruído por cima, luz de lanterna e personagem quase em silhueta.
- **Resident Evil (1996, 1999).** Câmera fixa e alta, no canto do cômodo. Fundo pré-renderizado cheio de detalhe com personagens e objetos low-poly por cima. Azul saturado com acentos vermelhos (RE1) ou ferrugem e tijolo (RE3).
- **Crash Bandicoot (1997, 1998).** Cor saturada e quente, luz forte por vértice, caixotes com textura chapada minúscula, névoa colorida no horizonte (laranja e roxo no Warped) e câmera atrás e acima.

## Como foi implementado (sem MCP)

- **Mesma matemática do `RetroPassNode` oficial do three.js**, que já está em `node_modules/three/examples/jsm/tsl/display/RetroPassNode.js`. O oficial só roda no renderizador WebGPU, então a técnica é portada pro WebGL do motor.
- **Material `ps1()`:** vértice tremido, textura afim, Gouraud, neblina, cor por vértice e textura nearest.
- **Passe final:** renderizar em 270×480, quantizar pra 15 bits com Bayer 4×4 e ampliar 4× com nearest.
- **Texturas geradas em código:** canvas de 32 a 128 px com paleta reduzida (tijolo, madeira de caixote, azulejo, asfalto, metal enferrujado, água).
- **Câmera:** planos fixos no estilo Resident Evil ou movimentos lentos (onde o tremido aparece mais), com corte a cada frase.

## Fontes

- Técnica: [Pikuma — how to make PS1 graphics](https://pikuma.com/blog/how-to-make-ps1-graphics) · [PSXDev — por que os modelos tremem](https://www.psxdev.net/forum/viewtopic.php?p=20520) · [Especificações técnicas do PlayStation](https://en.wikipedia.org/wiki/PlayStation_technical_specifications) · [Polycount — limites de textura e paleta](https://polycount.com/discussion/226167/) · [Fabien Sanglard — Doom no PSX](https://fabiensanglard.net/doom_psx/)
- Shaders: [RetroPassNode (three.js)](https://threejs.org/docs/pages/RetroPassNode.html) · [psx_visuals (Godot, Unlicense)](https://github.com/snotbane/psx_visuals) · [playshader-one (three.js, MPL-2.0, parado desde 2022)](https://github.com/BucketOSoftware/playshader-one) · [Codrops — jitter estilo PS1](https://tympanus.net/codrops/?p=80278) · [Godot Shaders — PS1 Shader](https://godotshaders.com/shader/ps1-shader/)
- Jogos: [Silent Hill — a neblina](https://iota.msp.org/the-silent-hill-fog-more-than-just-a-visual-trick) · [Superjump — Through Mist, Light, and Darkness](https://www.superjumpmagazine.com/drafting-through-the-mists/) · [Giant Bomb — fundos pré-renderizados](https://giantbomb.com/wiki/Concepts/Pre_rendered_Backgrounds) · [Andy Gavin — Crash](https://all-things-andy-gavin.com/tag/video-game-console/) · [Automaton — o programador de FFX sobre o charme do warping](https://automaton-media.com/en/news/final-fantasy-x-programmer-doesnt-get-why-devs-want-to-replicate-low-poly-ps1-era-games-we-worked-so-hard-to-avoid-warping-but-now-they-say-its-charming/)
- Capturas usadas como referência visual (Wikipédia): [Silent Hill](https://en.wikipedia.org/wiki/File:SH1_rifle.jpg) · [Resident Evil](https://en.wikipedia.org/wiki/File:Resident_Evil_original_version.png) · [Resident Evil 3](https://en.wikipedia.org/wiki/File:Resident_Evil_3_Nemesis_Gameplay.png) · [Crash 2](https://en.wikipedia.org/wiki/File:Crash2snow.JPG) · [Crash Warped](https://en.wikipedia.org/wiki/File:Crash_screen_shot.png) · [Final Fantasy VII](https://en.wikipedia.org/wiki/File:FFVIIbattleexample.png)

## Decisões de direção de arte tomadas no projeto

- Clima **neutro** por padrão (as referências são escuras, mas o canal não precisa ser soturno); ajusta-se por vídeo na luz e na névoa.
- Fundo: o blueprint do formato de curiosidade (azul do Zack D. Films, amarelo, azul-escuro, preto) foi testado e **descartado** — é linguagem de infográfico plano e não combina com o mundo 3D do PS1. Ficou a **sala de teste** como padrão e o **degradê pontilhado** nas cenas sem chão, escolhidos entre 4 fundos nativos de PS1 (sala de teste, degradê, névoa clara, céu de nuvens).
- A legenda continua nítida por cima (leitura no celular), e só a cena passa pelo tratamento PS1.
