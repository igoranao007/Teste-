// THE GREEN PATH v4 — peças comuns das cenas novas (carro com Adryan e Nicolas, voz → boca, sala do Igor com quadro/retrato/vídeo, pastas).
import * as P from './ps1.js';
import * as F from './filme.js';
import * as T from './tgp.js';
import * as E4 from './elenco4.js';
import * as M from './modelo.js';
const { THREE } = P;

// volume da voz por quadro (tools/som4.py → material/voz-v4.json): fala(plano, t)
export async function vozes() {
  const V = await fetch('../../material/voz-v4.json').then(r => r.ok ? r.json() : {}).catch(() => ({}));
  const fn = (plano, t, quem) => { let v = 0; for (const f of V[plano] ?? []) { if (quem && f.quem !== quem) continue; const q = Math.round((t - f.t) * 30); if (q >= 0 && q < f.env.length) v = Math.max(v, f.env[q]); } return v; };
  // quem está com a palavra (do começo da fala até .35 s depois do fim; entre falas, o último que falou)
  fn.quem = (plano, t) => { let q = null, ini = -1; for (const f of V[plano] ?? []) if (t >= f.t - .15 && f.t > ini) { ini = f.t; q = t <= f.t + f.env.length / 30 + .35 ? f.quem : q; } return q; };
  return fn;
}

// senta o ator com o quadril num ponto (mundo); pose 'sit' congelada
export function sentar(A, assento, o = {}) {
  A.quadro('sit', o.t ?? 2.2); A.obj.position.set(0, 0, 0); A.obj.rotation.y = o.rot ?? 0; A.obj.updateMatrixWorld(true);
  const h = new THREE.Vector3(); (A.osso('spine') || A.osso('Hips')).getWorldPosition(h);
  if (A.obj.parent) A.obj.parent.worldToLocal(h);                    // assento em coordenada do pai (ex.: dentro do carro)
  A.obj.position.set(assento.x - h.x, assento.y - h.y + (o.dy ?? .08), assento.z - h.z + (o.dz ?? 0));
}
// anda de A até B (mundo, chão) entre t0 e t1; fora disso fica parado na ponta; vira pra direção do passo
export function caminhar(A, a, b, t, t0, t1, o = {}) {
  const u = P.clamp((t - t0) / (t1 - t0)), andando = t > t0 && t < t1;
  const x = P.lerp(a[0], b[0], u), z = P.lerp(a[1], b[1], u);
  A.obj.position.set(x, 0, z); if (andando || o.virar !== false) A.obj.rotation.y = Math.atan2(b[0] - a[0], b[1] - a[1]);
  if (andando) A.pose('walk', t * (o.vel ?? 1)); return andando;
}
// ── POSTO DE GASOLINA isolado: cobertura com fluorescentes, 2 bombas, lojinha com vitrine verde, poste. Carro para em x=0 apontando +x ──
export function posto() {
  const g = new THREE.Group(), conc = P.TEX.concreto({ cor: '#56605a', junta: '#3a423c' }), branco = P.mat({ cor: '#c8d0c8' }), verde = P.mat({ cor: '#1f7a3c' });
  g.add(P.caixa(22, .04, 14, P.mat({ mapa: conc, rep: [8, 5] }), { pos: [0, .01, -3], sx: 10, sz: 8 }));
  // cobertura
  g.add(P.caixa(11, .5, 7, branco, { pos: [0, 4.4, -2.4], sx: 4, sz: 3 })); g.add(P.caixa(11.1, .18, 7.1, verde, { pos: [0, 4.12, -2.4] }));
  for (const [x, z] of [[-4.6, -5], [4.6, -5], [-4.6, .2], [4.6, .2]]) g.add(P.caixa(.3, 4, .3, branco, { pos: [x, 2, z] }));
  const luzes = []; for (const x of [-3, 0, 3]) for (const z of [-4.2, -.6]) { const l = P.caixa(1.2, .05, .2, P.mat({ cor: '#e6ffec', semLuz: true }), { pos: [x, 4.13, z] }); g.add(l); luzes.push(l); }
  // ilha + bombas (do lado do motorista: −z)
  g.add(P.caixa(5, .18, 1, P.mat({ mapa: conc, rep: [2, 1] }), { pos: [0, .09, -2.4] }));
  const bomba = x => { const b = new THREE.Group(); b.add(P.caixa(.7, 1.6, .5, P.mat({ cor: '#d9ddd6' }), { pos: [0, .98, 0] }), P.caixa(.72, .3, .52, verde, { pos: [0, 1.62, 0] }),
      P.caixa(.36, .2, .02, P.mat({ cor: '#39ff6a', semLuz: true }), { pos: [0, 1.25, .27] }), P.caixa(.08, .3, .08, P.mat({ cor: '#222' }), { pos: [.3, .9, .28] })); b.position.set(x, .18, -2.4); g.add(b); return b; };
  const bombas = [bomba(-1.4), bomba(1.4)];
  // lojinha
  g.add(P.caixa(7, 3, 4, P.mat({ cor: '#7d867e' }), { pos: [3, 1.5, -10], sx: 4, sy: 2 }));
  g.add(P.caixa(3.2, 1.4, .06, P.mat({ cor: '#39ff6a', semLuz: true, opac: .9 }), { pos: [2, 1.4, -7.98] }));
  g.add(P.caixa(1, 2.1, .06, P.mat({ cor: '#20261f' }), { pos: [5, 1.05, -7.98] }));
  g.add(P.caixa(4, .6, .1, P.mat({ cor: '#ffd23a', semLuz: true }), { pos: [3, 3.3, -7.94] }));
  g.luzes = () => [{ pos: [0, 3.8, -2.4], cor: '#d8ffe4', raio: 9, int: 1.4 }, { pos: [2, 1.4, -7], cor: '#39ff6a', raio: 6, int: 1.2 }];
  Object.assign(g, { bombas, bico: new THREE.Vector3(1.7, 1.1, -2.1) });
  return g;
}
// olhos amarelos na mata (os do Metalis): dois pontos que piscam; o.k(0–1) acende
export function olhos() {
  const g = new THREE.Group(), m = P.mat({ cor: '#ffd23a', semLuz: true });
  for (const s of [-1, 1]) g.add(P.caixa(.07, .035, .01, m, { pos: [s * .07, 0, 0] }));
  const h = P.disco(.35, P.mat({ mapa: F.TEX.brilho(), cor: '#ffd23a', opac: .25, aditivo: true, semLuz: true, lados: THREE.DoubleSide }), { seg: 10 }); g.add(h);
  g.acender = (k, pisca) => { m.uniforms.uCor.value.set('#ffd23a').multiplyScalar(k * (pisca ? .05 : 1)); h.material.uniforms.uOpac.value = .25 * k; };
  return g;
}
// cabeça/pescoço: gira um osso em torno de um eixo local (aditivo, depois da pose)
export function girar(A, nome, eixo, ang) { const b = A.osso(nome); if (!b) return; b.rotateOnAxis(new THREE.Vector3(...eixo).normalize(), ang); b.updateMatrixWorld(true); }
// fala: balança a cabeça de leve com o volume
export function falar(A, v, t) { if (v > 0) { girar(A, 'spine.005', [1, 0, 0], -.05 * v * Math.sin(t * 9)); girar(A, 'spine.005', [0, 1, 0], .04 * v * Math.sin(t * 5.3)); } }

// ── a dupla no carro (serve por dentro e por fora): sentados, Adryan com as duas mãos no volante girando,
//    Nicolas com a maleta no colo segurando pelas laterais. dupla.atualizar(t, { giro, olhaAd, olhaNi, falaAd })
//    Medidas do sedã (m, local do carro): banco motorista x=+.35, passageiro x=−.35, teto y≈1.33, volante (.35,.84,.49)
export async function dupla(pai) {
  const Ad = await E4.ator('adryan'), Ni = await E4.ator('nicolas'); pai.add(Ad.obj, Ni.obj);
  Ad.obj.scale.setScalar(.74); Ni.obj.scale.setScalar(.72);
  T.poses(Ad.modelo); T.poses(Ni.modelo);
  const mal = T.maleta(); mal.scale.setScalar(.72); pai.add(mal);
  const BANCO = { x: .35, y: .6, z: .27 }, PASS = { x: -.35, y: .6, z: .29 }, V = new THREE.Vector3(.35, .84, .49);
  const W = (A, n) => A.osso(n).getWorldPosition(new THREE.Vector3());
  const loc = v => pai.worldToLocal(v.clone()), mun = v => pai.localToWorld(v.clone());
  function atualizar(t = 0, o = {}) {
    sentar(Ad, BANCO, { dy: 0 }); sentar(Ni, PASS, { dy: 0 });
    pai.updateMatrixWorld(true);
    // Adryan: mãos no volante a "10 e 2", girando junto com o volante
    const g = o.giro ?? (.14 * Math.sin(t * .7) + .05 * Math.sin(t * 1.9));
    const DIR = v => mun(new THREE.Vector3(...v)).sub(mun(new THREE.Vector3())).toArray();
    for (const [s, ang] of [['L', .9], ['R', Math.PI - .9]]) {
      const a = ang + g; let p = new THREE.Vector3(V.x + Math.cos(a) * .16, V.y + Math.sin(a) * .15 * .85, V.z - .02 - Math.sin(a) * .15 * .45);
      if (s === 'L' && o.maoFora) p = p.lerp(new THREE.Vector3(.98, .98, .3), o.maoFora);                  // mão pra fora da janela (pagar, dar a moeda)
      if (s === 'R' && o.entrega) p = p.lerp(new THREE.Vector3(.02, .86, .36), P.suave(0, .45, o.entrega)); // pega a maleta do Nicolas
      Ad.modelo.alcancar(s, mun(p).toArray(), DIR([s === 'L' ? .9 : -.9, -.8, -.2]), .06);
    }
    // Nicolas: maleta deitada no colo, uma mão de cada lado
    const coxa = W(Ni, 'thigh.L').add(W(Ni, 'thigh.R')).multiplyScalar(.5), joe = W(Ni, 'shin.L').add(W(Ni, 'shin.R')).multiplyScalar(.5);
    const c = loc(coxa).lerp(loc(joe), .5); mal.visible = !o.semMaleta;
    const e = P.suave(.15, .75, o.entrega ?? 0);                                                     // entrega: do colo dele pro meio, onde o Adryan pega
    mal.position.set(P.lerp(c.x, -.02, e), c.y + .1 + Math.sin(e * Math.PI) * .12, P.lerp(c.z - .06, .3, e)); mal.rotation.set(0, 0, 0); mal.deitar?.(1);
    if (!o.semMaleta && e < .98) for (const s of ['L', 'R']) {
      const lado = s === 'L' ? 1 : -1, alvo = mun(new THREE.Vector3(mal.position.x + lado * .17, mal.position.y + .07, mal.position.z + .04));
      Ni.modelo.alcancar(s, alvo.toArray(), DIR([lado * .9, -.4, -.3]), .05);
    }
    // cabeça
    if (o.olhaAd) girar(Ad, 'spine.005', [0, 1, 0], o.olhaAd);
    if (o.falaAd) falar(Ad, o.falaAd, t);
    if (o.olhaNi) girar(Ni, 'spine.005', [0, 1, 0], o.olhaNi);
    if (o.acenaNi) girar(Ni, 'spine.005', [1, 0, 0], o.acenaNi);
    const bal = Math.sin(t * 5.1) * .01; girar(Ad, 'spine.003', [0, 0, 1], bal); girar(Ni, 'spine.003', [0, 0, 1], bal);
    mal.pulsar?.(t);
  }
  atualizar(0);
  return { Ad, Ni, mal, atualizar, cabecas: () => [W(Ad, 'spine.005'), W(Ni, 'spine.005')], topo: () => { const b = new THREE.Box3(); return [Ad, Ni].map(A => { b.setFromObject(A.obj, true); return +pai.worldToLocal(b.max.clone()).y.toFixed(3); }); } };
}
export async function carroComDupla(cena) { const car = await F.interiorCarro(); car.children[0].scale.y *= 1.07; cena.add(car); const d = await dupla(car); return { car, ...d }; }
export async function carroFora(cena) { const car = await F.carro(); car.children[0].scale.y *= 1.07; cena.add(car); const d = await dupla(car); return { car, ...d }; }
// sala do Igor v4: a de antes + quadro do aniversário no fundo, retrato na mesa, vídeo no monitor, pastas
export async function salaIgor4(cena) {
  const s = await F.salaIgor(cena);
  const tex = async (arq, max = 256) => { const im = await M.imagem(arq); const t = new THREE.Texture(im); t.magFilter = t.minFilter = THREE.NearestFilter; t.generateMipmaps = false; t.colorSpace = THREE.NoColorSpace; t.needsUpdate = true; return t; };
  // quadro grande na parede do fundo (atrás da câmera do plano médio fica o lado +z; o fundo do Igor é −z)
  const q = await tex('material/cenarios/sala-igor/texturas/quadro_aniversario_128.png');
  const quadro = new THREE.Group(); quadro.add(P.caixa(1.38, 1.14, .05, P.mat({ cor: '#2a2016' }), { pos: [0, 0, -.03] }), P.malha(new THREE.PlaneGeometry(1.24, 1.0), P.mat({ mapa: q }), { pos: [0, 0, .001] }));
  quadro.position.set(-.3, 1.75, -1.6); cena.add(quadro);
  cena.add(P.caixa(6, 3.4, .1, P.mat({ cor: '#0f1511' }), { pos: [0, 1.7, -1.7] }));                               // parede do fundo
  // retrato na mesa (porta-retrato em pé)
  const r = await tex('material/cenarios/sala-igor/texturas/retrato_mesa_64.png');
  const ret = new THREE.Group(); ret.add(P.caixa(.17, .2, .015, P.mat({ cor: '#3a2a1a' })), P.malha(new THREE.PlaneGeometry(.14, .17), P.mat({ mapa: r }), { pos: [0, 0, .009] }));
  ret.position.set(-.55, s.Y + .1, .62); ret.rotation.set(-.15, .5, 0); cena.add(ret);
  // vídeo no monitor: quadros pré-extraídos numa folha (tools/v4_video_tela.sh)
  const folha = await M.imagem('material/cenarios/sala-igor/texturas/tela_quadros.png').catch(() => null);
  const video = t => { if (!folha) return; const n = 16 * 15, k = Math.min(n - 1, Math.max(0, Math.floor(t * 15))), cx = k % 16, cy = Math.floor(k / 16);
    const x = s.pc.ctx; x.fillStyle = '#000'; x.fillRect(0, 0, 96, 72); x.drawImage(folha, cx * 96, cy * 72, 96, 72, 0, 0, 96, 72); s.pc.tex.needsUpdate = true; };
  return { ...s, quadro, retrato: ret, video };
}
export async function pastaFicha(nome) { const im = await M.imagem(`material/cenarios/sala-igor/pastas/${nome}_psx_256.png`); const t = new THREE.Texture(im); t.magFilter = t.minFilter = THREE.NearestFilter; t.generateMipmaps = false; t.colorSpace = THREE.NoColorSpace; t.needsUpdate = true; return t; }

// ── peças dos pacotes (3D Retro World, postes, PSX Nostalgia): carrega e alinha (centro em x/z, base em y=0) ──
const RW = 'material/modelos/pacotes/retro_world/';
export async function peca(arq, o = {}) {
  const m = await M.carregar(arq.startsWith('material/') ? arq : RW + arq, { texMax: o.tex ?? 128, mat: o.mat });
  if (o.verde !== false) for (const ml of m.malhas) for (const mt of [].concat(ml.material)) {     // vermelho do pacote → verde do filme
    const tx = mt.uniforms?.uMapa?.value; if (!tx?.image || tx.__verde) continue;
    const c = document.createElement('canvas'); c.width = tx.image.width; c.height = tx.image.height; const x = c.getContext('2d'); x.drawImage(tx.image, 0, 0);
    const d = x.getImageData(0, 0, c.width, c.height), q = d.data;
    for (let i = 0; i < q.length; i += 4) { const r = q[i], g = q[i + 1], b = q[i + 2]; if (r > 90 && r > g * 1.7 && r > b * 1.7) { q[i] = g * .45; q[i + 1] = Math.min(255, r * 1.05); q[i + 2] = Math.min(255, r * .42); } }
    x.putImageData(d, 0, 0); const n = new THREE.CanvasTexture(c); n.flipY = tx.flipY; n.wrapS = tx.wrapS; n.wrapT = tx.wrapT; n.magFilter = n.minFilter = THREE.NearestFilter; n.generateMipmaps = false; n.colorSpace = THREE.NoColorSpace; n.__verde = 1; mt.uniforms.uMapa.value = n;
  }
  const g = new THREE.Group(); g.add(m.obj); if (o.esc) m.obj.scale.multiplyScalar(o.esc);
  g.updateMatrixWorld(true); const b = new THREE.Box3().setFromObject(m.obj);
  if (o.alinhar !== false) m.obj.position.set(-(b.min.x + b.max.x) / 2, -b.min.y, -(b.min.z + b.max.z) / 2);
  g.tam = b.getSize(new THREE.Vector3()); g.modelo = m;
  if (o.pos) g.position.set(...o.pos); if (o.rot != null) g.rotation.y = o.rot; return g;
}

// ── POSTO (3D Retro World): cobertura 5×3 módulos de 2 m sobre 4 pilares, 2 bombas na ilha, piso, lojinha, placa de preço.
//    Carro para em x=0, z=0 apontando +x; a bomba fica do lado do motorista (−z). p.luzes() pra assar.
export async function postoRetro() {
  const g = new THREE.Group(), GS = 'Props/Gas_Station/', ST = 'Props/Gas_Store/', ALT = 4.6;
  // piso
  const piso = await peca(GS + 'Pavement_0.glb');
  for (let i = -9; i <= 9; i++) for (let j = -9; j <= 5; j++) { const p = piso.clone(); p.position.set(i * 1, 0, j * 1); g.add(p); }
  // cobertura
  const r1 = await peca(GS + 'GasRoof_1.glb'), r4 = await peca(GS + 'GasRoof_4.glb');
  for (let i = -2; i <= 2; i++) for (let j = -1; j <= 1; j++) { const t = (j === 1 ? r1 : j === -1 ? r1 : r4).clone(); t.position.set(i * 2, ALT, -2 + j * 2); if (j === -1) t.rotation.y = Math.PI; g.add(t); }
  const pil = await peca(GS + 'Gas_Pilar.glb'); const kp = ALT / pil.tam.y;
  for (const [x, z] of [[-4, -3.6], [4, -3.6], [-4, -.4], [4, -.4]]) { const p = pil.clone(); p.scale.set(.7, kp, .7); p.position.set(x, 0, z); g.add(p); }
  const lamp = await peca(GS + 'Lamp_01.glb'); const luzes = [];
  for (const x of [-3, 0, 3]) for (const z of [-3.2, -.8]) { const l = lamp.clone(); l.position.set(x, ALT - .12, z); g.add(l); luzes.push([x, z]); }
  // ilha + bombas do lado do motorista
  const ilha = await peca(GS + 'Pavement_1.glb'); for (const i of [-4, -3, -2, 2, 3, 4]) { const p = ilha.clone(); p.position.set(i, 0, -2.6); g.add(p); }
  const bomba = await peca(GS + 'Gas_Pump.glb'); const kb = 1.75 / bomba.tam.y; const bombas = [];
  for (const x of [-3, 3]) { const b = bomba.clone(); b.scale.setScalar(kb); b.position.set(x, .2, -2.6); b.rotation.y = 0; g.add(b); bombas.push(b); }
  const bico = await peca(GS + 'Gas _Pump_Handler.glb'); bico.scale.setScalar(.8);
  // lixeira, extintor, placa luminosa e preço
  const lix = await peca(GS + 'Trash_Can.glb'); lix.position.set(4.6, 0, -2.6); g.add(lix);
  const ext = await peca(GS + 'FireExtinguisher.glb'); ext.scale.setScalar(.8); ext.position.set(-3.7, 0, -3.3); g.add(ext);
  const luz = await peca(GS + 'Light_Sign.glb'); luz.scale.setScalar(1.1); luz.position.set(0, ALT + .9, 0.05); g.add(luz);
  // lojinha ao fundo (−z): paredes 4×3 com janela e porta
  const W = n => peca(ST + n + '.glb');
  const parede = await W('Wall_4x3_A'), jan = await W('Window_4x3_A'), porta = await W('Door_A');
  const loja = new THREE.Group(); loja.position.set(2, 0, -10); g.add(loja);
  const frente = [jan, porta, jan]; frente.forEach((p, i) => { const c = p.clone(); c.rotation.y = Math.PI; c.position.set((i - 1) * 4, 0, 3); loja.add(c); });
  for (const s of [-1, 1]) for (let k = 0; k < 2; k++) { const c = parede.clone(); c.rotation.y = Math.PI / 2; c.position.set(s * 6, 0, 1 - k * 4); loja.add(c); }
  for (let i = -1; i <= 1; i++) { const c = parede.clone(); c.position.set(i * 4, 0, -5); loja.add(c); }
  loja.add(P.caixa(12.4, .3, 8.4, P.mat({ cor: '#3f4542' }), { pos: [0, 3.1, -1] }));
  loja.add(P.caixa(6, .7, .12, P.mat({ cor: '#ffd23a', semLuz: true }), { pos: [0, 3.6, 3.15] }));
  const vit = P.caixa(10.5, 1.6, .05, P.mat({ cor: '#39ff6a', semLuz: true, opac: .35 }), { pos: [0, 1.4, 2.9] }); loja.add(vit);
  Object.assign(g, { bombas, bico, ALT, luzes: () => [...luzes.map(([x, z]) => ({ pos: [x, ALT - .5, z], cor: '#dcffe6', raio: 7, int: 1.1 })), { pos: [2, 1.5, -6.5], cor: '#39ff6a', raio: 7, int: 1.2 }] });
  return g;
}

// estrada de asfalto (Road_01, módulos de 10 m) ao longo de x, centrada em z
export async function asfalto(g, x0, x1, z = 0) { const r = await peca('Roads/Road_01.glb'); for (let x = x0; x <= x1; x += 10) { const c = r.clone(); c.rotation.y = Math.PI / 2; c.position.set(x, -.17, z); g.add(c); } }
// árvores do pacote (eucalipto e pinheiro), escuras e grandes, espalhadas numa faixa
export async function arvoresRetro(g, R, { x0, x1, z0, z1, n, evitar }) {
  const tipos = [await peca('Vegetation/Trees/Eucalyptus_A.glb'), await peca('Vegetation/Trees/Eucalyptus_B.glb'), await peca('Vegetation/Trees/Scoth Pine/Scoth_Pine_A.glb'), await peca('Vegetation/Trees/Scoth Pine/Scoth_Pine_E.glb')];
  for (let i = 0; i < n; i++) { const t = tipos[Math.floor(R() * tipos.length)].clone(); const h = 7 + R() * 5; t.scale.setScalar(h / 24); let x, z, k = 0; do { x = P.lerp(x0, x1, R()); z = P.lerp(z0, z1, R()); } while (evitar && evitar(x, z) && ++k < 20); t.position.set(x, 0, z); t.rotation.y = R() * 6; g.add(t); }
}
// segura a maleta (em pé, pela alça) na mão direita de um ator do elenco v4
export function segurarMaleta(A, mal) { const p = new THREE.Vector3(); A.osso('hand.R').getWorldPosition(p); mal.position.set(p.x, p.y - mal.alca * mal.scale.y - .02, p.z); }
// ── CABANA isolada: madeira, telhado, uma janela verde acesa, porta de madeira que abre (c.abrir(0–1)). Frente olha pra +z ──
export function cabana() {
  const g = new THREE.Group(), mad = (r = 5) => P.mat({ mapa: F.TEX.madeira(), rep: [r, 1], cor: '#8f8a7a', lados: THREE.DoubleSide }), esc = P.mat({ mapa: F.TEX.madeira(), rep: [2, 1], cor: '#5a4a38' });
  const W = 7, H = 2.9, D = 5.5, e = .12, PX0 = -1.72, PX1 = -.68, PH = 2.15;
  // paredes ocas: fundo, lados, frente com o vão da porta
  g.add(P.caixa(W, H, e, mad(), { pos: [0, H / 2, -D / 2] }));
  for (const s of [-1, 1]) g.add(P.caixa(e, H, D, mad(4), { pos: [s * W / 2, H / 2, 0] }));
  g.add(P.caixa(PX0 + W / 2, H, e, mad(2), { pos: [(-W / 2 + PX0) / 2, H / 2, D / 2] }));
  g.add(P.caixa(W / 2 - PX1, H, e, mad(3), { pos: [(PX1 + W / 2) / 2, H / 2, D / 2] }));
  g.add(P.caixa(PX1 - PX0, H - PH, e, mad(1), { pos: [(PX0 + PX1) / 2, (H + PH) / 2, D / 2] }));
  g.add(P.caixa(W, .08, D, P.mat({ cor: '#2a2018' }), { pos: [0, .04, 0] }));                                // piso
  g.add(P.caixa(W, .08, D, P.mat({ cor: '#14100c' }), { pos: [0, H, 0] }));                                    // forro
  g.add(P.cilindro(3.9, 3.9, 7.8, P.mat({ cor: '#2b2f2b' }), { seg: 3, pos: [0, 3.6, 0], rot: [0, 0, Math.PI / 2], esc: [.42, 1, .9] }));
  g.add(P.caixa(1.2, .2, .5, esc, { pos: [-1.2, .1, 3] }));                                                     // degrau
  // por dentro: luz verde fraca, uma estante e o alçapão do elevador no fundo
  g.add(P.caixa(1.6, 2.2, .5, P.mat({ cor: '#3a2e22' }), { pos: [2.2, 1.1, -2.4] }));
  g.add(P.caixa(1.4, 2.2, .1, P.mat({ cor: '#7f8a82' }), { pos: [-1.2, 1.1, -2.68] }), P.caixa(.3, .12, .03, P.mat({ cor: '#39ff6a', semLuz: true }), { pos: [-1.2, 2.35, -2.62] }));
  const jan = P.caixa(1.3, 1, .06, P.mat({ cor: '#39ff6a', semLuz: true }), { pos: [1.7, 1.6, D / 2 + .02] }); g.add(jan);
  g.add(P.caixa(1.4, .06, .1, P.mat({ cor: '#0c1a10', semLuz: true }), { pos: [1.7, 1.6, D / 2 + .05] }), P.caixa(.06, 1.1, .1, P.mat({ cor: '#0c1a10', semLuz: true }), { pos: [1.7, 1.6, D / 2 + .05] }));
  const dob = new THREE.Group(); dob.position.set(PX0, 0, D / 2 + .05); g.add(dob);                               // dobradiça à esquerda
  const porta = P.caixa(PX1 - PX0, PH - .05, .07, esc, { pos: [(PX1 - PX0) / 2, (PH - .05) / 2, 0] }); dob.add(porta);
  const mac = P.caixa(.05, .05, .08, P.mat({ cor: '#c9c19a' }), { pos: [PX1 - PX0 - .12, 1.05, .06] }); dob.add(mac);
  const h = P.disco(1.4, P.mat({ mapa: F.TEX.brilho(), cor: '#39ff6a', opac: .3, aditivo: true, semLuz: true, lados: THREE.DoubleSide }), { seg: 10, pos: [1.7, 1.6, D / 2 + .25] }); g.add(h); g.halo = h;
  Object.assign(g, { porta: dob, macaneta: mac, abrir: k => { dob.rotation.y = 1.7 * k; },
    luzes: () => { g.updateMatrixWorld(true); return [{ pos: g.localToWorld(new THREE.Vector3(1.7, 1.4, 4.2)).toArray(), cor: '#39ff6a', raio: 10, int: 1.5 }, { pos: g.localToWorld(new THREE.Vector3(0, 2.2, 0)).toArray(), cor: '#39ff6a', raio: 5, int: .9 }]; } });
  return g;
}
// ── chão da cabana (planos 7, 8, 9): clareira, caminho de terra, mata fechada, a cabana; o carro estaciona na frente ──
export async function montarCabana(S) {
  const cena = S.scene, R = P.rng(71), A = await import('./arh.js');
  const ext = new THREE.Group(); cena.add(ext);
  ext.add(A.chaoA({ w: 220, d: 220, seg: 80, mapa: F.TEX.capim(), rep: [70, 70], y: -.02 }));
  const cam2 = A.chaoA({ w: 4, d: 60, seg: 30, mapa: F.TEX.terra(), rep: [1, 18], y: .01, z: 32 }); ext.add(cam2);          // caminho de terra até a porta (ao longo de z)
  const cab = cabana(); cab.position.set(0, 0, 0); ext.add(cab);
  await arvoresRetro(ext, R, { x0: -60, x1: 60, z0: -60, z1: 60, n: 90, evitar: (x, z) => (Math.abs(x) < 9 && z > -6 && z < 60) || (Math.abs(x) < 6 && z < 0 && z > -8) });
  A.assar(ext, cab.luzes(), '#1b3022');
  return { ext, cab };
}

// ── a cena do posto inteira (planos 3, 4 e 5): posto, estrada, mato, carro com a dupla, frentista, Metalis ──
export async function montarPosto(S, o = {}) {
  const cena = S.scene, R = P.rng(53), A = await import('./arh.js');
  const ext = new THREE.Group(); cena.add(ext);
  ext.add(A.chaoA({ w: 260, d: 200, seg: 80, mapa: F.TEX.capim(), rep: [80, 60], y: -.03 }));
  await asfalto(ext, -120, 130, 9);
  const posto = await postoRetro(); ext.add(posto);
  await arvoresRetro(ext, R, { x0: -80, x1: 90, z0: -14, z1: -60, n: 40 });
  await arvoresRetro(ext, R, { x0: -80, x1: 90, z0: 16, z1: 50, n: 26 });
  const postes = [-40, -15, 25, 50].map(x => F.posteVerde(x, 14.5, { rot: -Math.PI / 2 })); postes.forEach(p => ext.add(p));
  A.assar(ext, [...posto.luzes(), ...postes.map(p => p.luz())], '#1d3324');
  const D = await carroFora(cena); D.car.rotation.y = Math.PI / 2;
  const Fr = await E4.ator('frentista'); cena.add(Fr.obj); T.poses(Fr.modelo);
  const Me = await E4.ator('metalis'); cena.add(Me.obj);
  const bico = posto.bico.clone(); cena.add(bico);
  // chegada: da estrada (z=9) até a bomba (0,0), freando; saída: volta pra estrada indo pra +x
  const curva = new THREE.CatmullRomCurve3([[-40, 0, 9], [-16, 0, 9], [-9, 0, 5.5], [-5, 0, 1.2], [-2.5, 0, 0], [0, 0, 0]].map(p => new THREE.Vector3(...p)));
  const saida = new THREE.CatmullRomCurve3([[0, 0, 0], [6, 0, .3], [11, 0, 4.5], [16, 0, 9], [60, 0, 9]].map(p => new THREE.Vector3(...p)));
  const naCurva = (cv, u, fim = 1) => { const p = cv.getPointAt(P.clamp(u)), q = cv.getTangentAt(P.clamp(u)); D.car.position.set(p.x, .02, p.z); D.car.rotation.y = P.lerp(Math.atan2(q.x, q.z), Math.PI / 2, fim === 1 ? P.suave(.9, 1, u) : 0); };
  return { ext, posto, D, Fr, Me, bico, postes, curva, saida, naCurva,
    halos: cam => { for (const p of postes) p.halo.quaternion.copy(cam.quaternion).premultiply(p.getWorldQuaternion(new THREE.Quaternion()).invert()); D.car.encarar(cam); } };
}
