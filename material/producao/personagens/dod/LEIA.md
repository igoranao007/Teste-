# DOD — o gato preto do meme (cérebro exposto), de farda militar

- Código: `T.dod()` em `lib/tgp.js` (cabeça: `T.cabecaDod()`; bandeira: `T.patchIsrael()`) · folha: `videos/95-dod`
  (`?v=frente|tres|lado|costas|rosto|topo|bandeira`, `&boca=0..1`, `&corpo=gato` = o primeiro corpo, de pelo) · `inspecao/folha_dod.jpg`.
- **Cabeça (método do Igor/Floppa):** a foto `material/dod/dod.jpg` projetada de frente numa cabeça low-poly, pixelada (15 bits). Cara chapada (nada de bolha),
  topo cortado reto + **cúpula do cérebro** com a textura do cérebro da foto. O roxo do fundo do meme sai da textura (fica preto e branco; só olhos, nariz, língua e cérebro têm cor).
- **Boca redesenhada em pixel** (a da foto é um borrão; referência: gato de boca aberta): almofadas brancas dos bigodes com pontinhos, nariz rosa em triângulo,
  risco + "ω" dos lábios, boca entreaberta com a língua; `animar(t, {boca})` abre mais com a voz. Tudo em px da foto (`FOTO_DOD.boca`), escala `B = 1.3`.
- **Corpo: soldado** `fv_rifleman` (PSX Characters Sampler, CSAF — uso livre, sem redistribuir; o arquivo NÃO vai pro git). Textura repintada (`fardaDod`):
  camuflado → **verde-oliva escuro** liso (dobras ficam), colete com bolsos e alça, cinto preto, coturno preto, **luvas pretas**.
  As mãos são achadas pela POSIÇÃO na pose de bind (além do pulso), não pelo osso (o osso da mão desse modelo pesa até no antebraço);
  a cabeça humana pelo osso `head` (ela encolhe pra dentro do pescoço). O decote mostra o peito branco do gato.
- **Bandeira de Israel** pequena (patch com costura verde) no lado de fora do **braço ESQUERDO**, logo abaixo do ombro: raio contra a malha acha a superfície e o patch é preso ao osso `upper_arm.L`.
- Rabo preso no quadril, balança. `assentar()` prende cabeça, rabo e bandeira nos ossos uma vez (depois de posar); daí eles seguem as animações.
