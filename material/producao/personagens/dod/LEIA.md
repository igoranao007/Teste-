# DOD — o gato preto do meme (cérebro exposto), de farda militar

- Código: `T.dod()` em `lib/tgp.js` (cabeça: `T.cabecaDod()`; bandeira: `T.patchIsrael()`) · folha: `videos/95-dod`
  (`?v=frente|tres|lado|costas|rosto|topo|bandeira`, `&boca=0..1`, `&corpo=gato` = corpo de pelo sem roupa) · `inspecao/folha_dod.jpg`.
- **Corpo: o PRIMEIRO modelo** (o mesmo do Igor/Floppa, `material/modelos/personagem-simples.glb`). Decisão do diretor: as fardas pesquisadas
  são só INSPIRAÇÃO — não usar modelo de outro pacote como corpo.
- **Cabeça (método do Floppa):** a foto `material/dod/dod.jpg` projetada de frente numa cabeça low-poly, pixelada (15 bits). Cara chapada (nada de bolha),
  topo cortado reto + **cúpula do cérebro** com a textura do cérebro da foto. O roxo do fundo do meme sai da textura (só olhos, nariz, língua e cérebro têm cor).
- **Boca redesenhada em pixel** (a da foto é um borrão; referência do diretor: gato de boca aberta): almofadas brancas dos bigodes com pontinhos, nariz rosa,
  risco + "ω" dos lábios, boca entreaberta com a língua; `animar(t, {boca})` abre mais com a voz (`FOTO_DOD.boca`, escala `B = 1.3`).
  O pescoço é fino e a cabeça fica alta (`cab.position.y = .2`): um pescoço largo tapava a boca.
- **Farda** (inspirada na farda verde-oliva de infantaria): tinta por osso no corpo base — verde-oliva escuro em manga e calça compridas, tecido liso com dobras
  (relevo próprio, sem o desenho de camiseta/bermuda), **luvas pretas** nas mãos. Peças presas aos ossos (medidas com raios contra a malha posada):
  colete porta-placas com 3 porta-carregadores, bolso do peito e alças (`spine.002`), cinto preto com fivela e bolsinhas (`spine`),
  **coturno** (bota + cano alto por cima da barra da calça; `foot`/`shin`), **bandeira de Israel** pequena no lado de fora do **braço ESQUERDO** (`upper_arm.L`).
  Os raios de lado batem no braço: a largura do colete vem dos ombros e a do cinto, do quadril.
- Rabo preso no quadril, balança. `assentar()` reposiciona cabeça/rabo a cada quadro e prende o equipamento nos ossos na 1ª chamada (depois de posar).
