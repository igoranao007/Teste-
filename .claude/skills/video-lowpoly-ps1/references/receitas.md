# Receitas — API de `lib/ps1.js`

Página = módulo: `boot.js` no `<head>` e depois `<script type="module">import * as P from '../../lib/ps1.js'</script>`. `VIDEO = {w:1080, h:1920, fps:30, dur:5}`.

## Palco

```js
const S = P.palco({
  cenario: 'sala',          // 'sala' (padrão: céu + chão xadrez + névoa) | 'degrade' (sem chão)
  chaoY: -.98,              // altura do chão da sala de teste nessa cena
  fov: 40, cam: [x, y, z], alvo: [x, y, z],
  luz: { keyDir, keyCor, fillDir, fillCor, amb },   // direção [x,y,z] e cor hex
  divisor: 4, tremor: 1, niveis: 31, dither: 1,    // resolução 1/4, vértice no pixel, 15 bits, pontilhado
  // por cima do cenário (desligam o cenário): fundoTex: P.ceu({...}) | P.blueprint({...}), fundo: '#hex', nevoa: {cor, perto, longe}
});
S.scene; S.camera; S.update = t => { … };          // tudo que se mexe vem de t
```

## Material — `P.mat(o)`

`cor` · `mapa` (textura) · `rep: [u, v]` · `emiss` · `opac` (< 1 = transparente, sem escrever profundidade) · `aditivo` (brilho) · `semLuz` (não recebe luz: incandescente, água, brilho) · `interior: '#hex'` (cor do lado de dentro; liga dupla face — pra objetos em corte) · `lados` · `corVertice`.

## Texturas

- `P.textura(w, h, (ctx, w, h, rng) => {…}, { seed, niveis })` — canvas pequeno, nearest, posterizado (`niveis: 0` desliga).
- `P.TEX`: `azulejo({cor, rejunte})`, `piso`, `tijolo` (tijolo baiano visto no corte), `plastico({cor})`, `crivo` (furinhos em anéis, pra tampa de cilindro), `disco` (brilho/fumaça), `xadrez({cores})`, `concreto({cor, junta})`.
- Fundos: `P.ceu({ cores: [[0,'#hex'], [1,'#hex']], faixas, nuvens: { n, de, ate, tam } })`, `P.blueprint({...})`, `P.chao({ y, passo, cores | mapa, tam, seg })`.
- Textura de bicho em corpo varrido: `v .25` = dorso, `v .75` = barriga; com o flipY padrão, a linha do canvas é `y = (1 - v)·h`.

## Geometria (todas aceitam `{ pos, rot, esc }`)

- `P.caixa(w, h, d, mat | [6 mats], { sx, sy, sz })` — ordem das faces: +x, −x, +y, −y, +z, −z.
- `P.cilindro(rTopo, rBase, h, mat | [lado, topo, base], { seg, aberto, ini, arco })`.
- `P.esfera(r, mat, { seg, segV })` · `P.disco(r, mat, { seg })`.
- `P.tornear([[r, y], …], mat, { seg, ini, arco })` — sólido de revolução; `ini/arco` deixam só uma parte (corte).
- `P.tubo([[x,y,z], …], r, mat, { seg, lados })` · `P.espiral({ raio, de, ate, voltas, fio }, mat)`.
- `P.varrer([[x,y,z], …], u => raio | {x, y}, mat, { segs, rad })` — corpo contínuo com "pra cima" transportado sem torção.
- `P.malha(geo, mat, o)` pra geometria própria. `P.encarar(obj, camera)` vira o plano pra câmera.
- `P.legenda([{ t, txt }, …], { y, tam, contorno })`. Ajudantes: `P.clamp`, `P.lerp`, `P.suave`, `P.rng`.

## Receitas

**Objeto em corte, virado pra câmera** (chuveiro, panela, motor):
```js
const tc = Math.atan2(cam.position.x - obj.x, cam.position.z - obj.z);   // ângulo da câmera
const corte = { ini: tc + Math.PI / 2, arco: Math.PI };                  // fica só a metade de trás
grupo.add(P.tornear(perfil, P.mat({ cor: '#efefea', interior: '#b4bbc1' }), { seg: 14, ...corte }));
for (const a of [corte.ini, corte.ini + corte.arco])                     // marca a borda do corte
  grupo.add(P.tubo(perfil.map(([r, y]) => [Math.sin(a) * r, y, Math.cos(a) * r]), .014, P.mat({ cor: '#56606a' }), { lados: 4 }));
```

**Pedaço de cômodo em corte:** `P.caixa` da parede com `[tijolo, tijolo, tijolo, tijolo, azulejo, tijolo]` (o azulejo na face da frente, o tijolo aparece nas bordas) e `sx/sy` 4–6; piso igual com o `piso` na face de cima.

**Cobra:** espiral de pontos no chão (rabo no centro → pra fora), depois 2–3 pontos subindo e a nuca. `raio(u)` afina no rabo (`√(u/.1)`) e no pescoço. Cabeça de víbora = esfera achatada (.14 × .036 × .1) afunilada no focinho; mandíbula num grupo com pivô atrás; presas = `P.cilindro(0, .011, .09)`. Posicione a cabeça, calcule a ponta da presa com `localToWorld`, corrija a altura pra tocar o alvo e **só então** termine o corpo varrido **dentro** do crânio.

**Água caindo:** filetes = `P.caixa(.014, comprimento, .014)` com `cor '#9fd1ec', opac .5, semLuz`; gotas = `P.esfera(.012–.024, …, { seg: 4, segV: 3 })` descendo em `(t·vel + fase) % 1`; poça = `P.disco` deitado com `opac .35`.

**Incandescente / brilho:** a peça com `P.mat({ cor: '#ff7426', semLuz: true })` + um `P.disco(r, P.mat({ mapa: P.TEX.disco(), cor, opac: .35, aditivo: true, semLuz: true }))` atrás, com `P.encarar`.

**Vidro com líquido:** `P.cilindro(r, r, h, P.mat({ cor: '#dcedf3', opac: .3, lados: THREE.DoubleSide }), { aberto: true })` + fundo `P.disco` + borda `P.cilindro` fino `opac .6` + o líquido como `P.cilindro` baixo opaco.

**Encaixar uma peça num ponto:** `cena.updateMatrixWorld(true); const p = new THREE.Vector3(x, y, z); grupo.localToWorld(p);` → corrija a posição do grupo pela diferença e recalcule.

**Câmera:** fixa (estilo Resident Evil) ou lenta: `S.update = t => { S.camera.position.x = x0 + Math.sin(t * .4) * .05; S.camera.lookAt(...alvo); }`.

# Kit de terror — `lib/arh.js` (16:9, canal Analog Real Horror)

Página 16:9: `VIDEO = {w:1920, h:1080, fps:30, dur:6}` e, no módulo, `import * as P from '../../lib/ps1.js'` + `import * as A from '../../lib/arh.js'`. Nada mais muda: a cena sai em 480×270 ampliada 4×.

## Luz assada (postes, lâmpada pendurada)

- `A.matA(o)` — `P.mat` com `corVertice` + `semLuz`: a cor vem só do `assar` (e a névoa vale). Use em **tudo** que a lâmpada ilumina; `P.mat` comum fica de fora (céu, letreiro aceso, a própria lâmpada).
- `A.assar(obj, luzes, amb = '#16181d')` — percorre as malhas com cor por vértice e grava `amb + Σ cor · (1 − d/raio)² · int · (.75·lambert + .25)`. `luzes = [{ pos: [x,y,z], cor, raio, int }]`. Subdivida o que recebe a poça de luz (chão `seg` 80–100, parede `sy/sz` 3–4): a luz só existe nos vértices.
- `A.chaoA({ w, d, tam, seg, x, y, z, mapa, rep, cor })` — chão de concreto (ou `mapa`) subdividido, já com `matA`.
- `A.poste(x, z, { h: 3.2, raio: 5, int: 1.25, cor: A.SODIO, rot })` — haste, braço, luminária e o disco aceso; `p.luz()` devolve a lâmpada em coordenadas do mundo.
- `A.halo(r, cor = A.SODIO, op = .22)` — disco aditivo pra pôr na lâmpada com `P.encarar(h, camera)`.

**Rua com postes (luz assada uma vez):**
```js
const S = P.palco({ fov: 52, cam: [0, 1.55, 7], alvo: [0, 1.35, -10],
  fundoTex: P.ceu({ cores: [[0, '#04060a'], [.55, '#0d1219'], [1, '#1b222b']], faixas: 10 }), nevoa: { cor: '#161c24', perto: 5, longe: 27 } });
S.scene.add(A.chaoA({ w: 26, d: 46, z: -10, seg: 90 }));
const postes = [-1, 1].flatMap(s => [0, 1, 2, 3].map(i => A.poste(s * 3.4, 4.6 - i * 4.4, { rot: s > 0 ? Math.PI : 0, int: i === 2 && s < 0 ? 0 : 1.9 })));
postes.forEach(p => S.scene.add(p));
const luzes = postes.map(p => p.luz()).filter(l => l.int > 0);
A.assar(S.scene, luzes, '#11141a');                                                  // tudo parado: uma vez só
for (const l of luzes) { const h = A.halo(.34); h.position.set(...l.pos); h.position.y += .2; S.scene.add(h); P.encarar(h, S.camera); }
```
Um poste apagado (`int: 0`) no meio da fileira faz mais pelo clima que dez acesos.

## Bonecos sem rosto

`A.boneco({ cor, roupa, esc })` — adulto de ~1,7 m: tronco, pescoço, cabeça lisa, pernas e braços em pivô. `b.andar(fase)` balança os membros; avance a posição em `S.update` e passe `fase ∝ distância`.

**Praça vista por câmera de segurança (12 qps, luz que acompanha quem anda):**
```js
const gente = new THREE.Group(); S.scene.add(gente);
S.update = t => {
  const tq = Math.floor(t * 12) / 12;                              // câmera de segurança: 12 quadros por segundo
  for (const a of andam) { const s = ((tq * a.v + a.off) % 24) - 12;
    a.b.position.set(a.x0 + a.dx * s, 0, a.z0 + a.dz * s); a.b.rotation.y = Math.atan2(a.dx, a.dz); a.b.andar(tq * a.v * 5.5 + a.fase); }
  A.assar(gente, luzes, '#3a3e45');                                 // só o grupo que anda, a cada quadro
};
```
Imagem de CFTV: `#stage canvas { filter: grayscale(.88) contrast(1.18) brightness(1.15) }` no `<style>` da página + `A.hud({ cam: 'CAM 04', dir: '[DATE]', tc0: 0, fita: true })`.

## HUD de fita — `A.hud(o)`

DOM nítido por cima do PS1 (como a legenda). `rec` (padrão true: ● REC piscando; `false` esconde) · `cam` (texto ao lado do REC) · `dir` (canto superior direito) · `tc0` (timecode HH:MM:SS:QQ no canto inferior direito, começando em `tc0` s) · `carimbo: [{ t, txt, vel }]` (digitado letra a letra numa etiqueta escura com cursor vermelho, no canto inferior esquerdo — o carimbo do fern) · `tarja: 2.35` (faixas pretas de cinema) · `fita: true` (scanline + vinheta). Som do carimbo: um `cue('type', t0 + i / 22)` por letra.

## Fita de evidência — `A.evidencia(o)`

Foto ou vídeo **real** em 4:3, tratado como VHS (não passa pelo PS1) numa TV de tubo ou na altura toda.

| Opção | Padrão | |
|---|---|---|
| `foto` / `quadros` | — | caminho a partir da raiz do projeto: `'material/x.jpg'` ou a pasta do `tools/quadros.sh` |
| `fonte` | **obrigatória** | `'SOURCE: …'` no rótulo do canto; sem ela a função dá erro |
| `moldura` | `'crt'` | `'crt'` TV numa sala escura (curvatura .07) · `'tela'` 4:3 na altura toda, faixas pretas, sem curvatura |
| `rec` | `true` | `false` troca o ● REC por ▶ PLAY |
| `tc0`, `data`, `dir` | 0, —, — | timecode, data no canto inferior esquerdo da imagem, texto no superior direito |
| `zoom`, `foco` | `[1, 1]`, `[.5, .5]` | aproximação lenta ao longo do vídeo, centrada no ponto `foco` (0–1 da imagem) |
| `t0`, `ini` | 0, 0 | vídeo: quando o clipe começa na cena e de que segundo do clipe |
| `cor`, `ruido`, `curva` | .6, .5, .07 | saturação, quantidade de defeito (0–1), barril do tubo |
| `entrada` | .4 | segundos de chiado com a imagem rolando até travar |
| `falhas` | `[]` | instantes de tracking forte (.25 s cada); case com `cue('glitch', t, { d: .25 })` |

Devolve o elemento; `el.tela` é a tela 4:3, pra pôr mais coisa por cima (um círculo marcando alguém, por exemplo).

**Vídeo real:** `bash tools/quadros.sh <clipe.mp4> material/<nome> [ini_s] [dur_s] [fps]` → `material/<nome>/00001.jpg…` + `quadros.json` (`{fps, n, w, h}`). 60 s a 30 qps ≈ 1800 quadros, ~40 MB. A página carrega um quadro por vez.

**Imagem de teste sem baixar nada:** `material/teste-sintetico.jpg` foi gerada em numpy (portão de parque à noite, postes de sódio, alambrado, grão). Não é material real: o rótulo do exemplo diz `SOURCE: TEST IMAGE (SYNTHETIC)`.

## Som do terror (`audio/synth.py`)

`cue('drone', 0, { d: VIDEO.dur, root: 31 })` · `cue('lampada', 0, { d, rede: 60, pisca: [2.1, 4.3] })` · `cue('chiado', 0, { d, crt: 1 })`. Camadas longas, abertas no estéreo (o drone e o chiado), por baixo da voz. Pra fazer o poste piscar junto, use os mesmos instantes na cena (`int` do poste a 0 e `A.assar` de novo naquele quadro) e no `pisca`.
