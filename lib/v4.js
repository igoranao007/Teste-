// THE GREEN PATH v4 — peças comuns das cenas novas (carro com Adryan e Nicolas, voz → boca, sala do Igor com quadro/retrato/vídeo, pastas).
import * as P from './ps1.js';
import * as F from './filme.js';
import * as T from './tgp.js';
import * as E4 from './elenco4.js';
import * as M from './modelo.js';
const { THREE } = P;

// volume da voz por quadro (tools/som4.py → material/voz-v4.json): fala(plano, t)
export async function vozes(nome = 'v4') {          // 'ep1' = material/voz-ep1.json (tools/som_ep1.py)
  const V = await fetch(`../../material/voz-${nome}.json`).then(r => r.ok ? r.json() : {}).catch(() => ({}));
  const fn = (plano, t, quem) => { let v = 0; for (const f of V[plano] ?? []) { if (quem && f.quem !== quem) continue; const q = Math.round((t - f.t) * 30); if (q >= 0 && q < f.env.length) v = Math.max(v, f.env[q]); } return v; };
  // quem está com a palavra (do começo da fala até .35 s depois do fim; entre falas, o último que falou)
  fn.quem = (plano, t) => { let q = null, ini = -1; for (const f of V[plano] ?? []) if (t >= f.t - .15 && f.t > ini) { ini = f.t; q = t <= f.t + f.env.length / 30 + .35 ? f.quem : q; } return q; };
  // peso suave de "está falando" (0–1) pela duração da fala inteira, com rampa: pra misturar a animação 'talk' sem ligar/desligar a cada sílaba
  fn.peso = (plano, t, quem, r = .3) => { let w = 0; for (const f of V[plano] ?? []) { if (quem && f.quem !== quem) continue; const a = f.t, b = f.t + f.env.length / 30; w = Math.max(w, P.suave(a - r, a + r * .5, t) * (1 - P.suave(b - r * .5, b + r, t))); } return w; };
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
  // passo natural: arranca e para devagar (ease nas pontas) e a cadência do passo segue a distância andada (sem patinar).
  // Transições sem tranco: a pose mistura parado↔andando no começo/fim (.3 s) e, com o.de (direção de antes), o corpo vira aos poucos
  const u0 = P.clamp((t - t0) / (t1 - t0)), andando = t > t0 && t < t1, e = o.ease ?? .18;
  const v = 1 / (1 - e), u = u0 < e ? v * u0 * u0 / (2 * e) : u0 > 1 - e ? 1 - v * (1 - u0) ** 2 / (2 * e) : v * (u0 - e / 2);
  const x = P.lerp(a[0], b[0], u), z = P.lerp(a[1], b[1], u), rumo = Math.atan2(b[0] - a[0], b[1] - a[1]);
  A.obj.position.set(x, 0, z);
  if (andando || o.virar !== false) { const dA = o.de == null ? 0 : Math.abs(angLerp(o.de, rumo, 1) - o.de), dT = Math.min((t1 - t0) * .6, Math.max(.3, dA * .3));   // virada proporcional ao ângulo (~3,3 rad/s no máx.)
    A.obj.rotation.y = o.rot != null ? o.rot : o.de == null ? rumo : angLerp(o.de, rumo, P.suave(t0, t0 + dT, t)); }   /* o.rot: direção fixa (passo de lado/de ré) */
  if (andando) { const L = Math.hypot(b[0] - a[0], b[1] - a[1]), passo = A.passada ?? (o.passo ?? 1.45) * (A.alt ?? 1.75) / 1.75;   // passada medida no clipe (sem deslize)
    const parado = o._semIdle ? 0 : 1 - Math.min(P.suave(t0, t0 + .15, t), 1 - P.suave(t1 - .15, t1, t));   // mistura curta: com o corpo já andando, pé meio-parado patinava
    A.pose('walk', (o.fase ?? 0) + (o.re ? -1 : 1) * u * L / passo * A.dur('walk') * (o.vel ?? 1), 'idle', parado, t);   /* o.re: de ré (clipe ao contrário) */
    if (!o._semTrava && o.travar !== false) travarPes(A, a, b, t, t0, t1, o, L, passo); }
  return andando;
}
// TRAVA DO PÉ (foot locking): no apoio, o pé fica onde tocou o chão. O ponto de contato é recalculado a cada quadro
// (pose no instante do toque) — função pura do tempo, sem estado entre quadros. IK de perna com o joelho pra frente;
// o pé mantém a orientação da animação. Rampas na entrada/saída do apoio (sem tranco).
const CONTATO = { metalis: [.325, .833] }, APOIO = .56;
const PERNA = s => [['thigh.' + s, 'shin.' + s, 'foot.' + s], [(s === 'L' ? 'Left' : 'Right') + 'UpLeg', (s === 'L' ? 'Left' : 'Right') + 'Leg', (s === 'L' ? 'Left' : 'Right') + 'Foot']];
function travarPes(A, a, b, t, t0, t1, o, L, passo) {
  const dur = A.dur('walk'), nome = (A.obj.name || '').replace('ator:', ''), [cL, cR] = CONTATO[nome] ?? [.35, .867];
  const e = o.ease ?? .18, v = 1 / (1 - e), U = tt => { const u0 = P.clamp((tt - t0) / (t1 - t0)); return u0 < e ? v * u0 * u0 / (2 * e) : u0 > 1 - e ? 1 - v * (1 - u0) ** 2 / (2 * e) : v * (u0 - e / 2); };
  const sg = o.re ? -1 : 1, fase = tt => (o.fase ?? 0) + sg * U(tt) * L / passo * dur * (o.vel ?? 1), fn = fase(t), cic = ((fn / dur) % 1 + 1) % 1;
  const pernas = [];
  for (const [s, c] of [['L', cL], ['R', cR]]) {
    const dentro = o.re ? ((c + APOIO - cic) % 1 + 1) % 1 : ((cic - c) % 1 + 1) % 1; if (dentro > APOIO) continue;   /* de ré o apoio começa no fim da janela */                    // pé no ar
    const nomes = PERNA(s).find(n => n.every(x => A.osso(x))); if (!nomes) continue;
    let w = P.suave(0, .04, dentro) * (1 - P.suave(APOIO - (o.re ? .05 : .16), APOIO, dentro));   /* de ré o apoio vai até o toque do calcanhar: solta só no fim */
    w *= Math.min(P.suave(t0, t0 + .12, t), 1 - P.suave(t1 - .2, t1, t));                       // solta perto do fim (a pose volta pro parado)
    if (w <= 0) continue;
    const alvoF = fn - sg * dentro * dur; let ts = t0 + 1e-4;                                     // (em t0 exato a caminhada ainda não posa)                                               // instante do toque: inverte a fase (monótona)
    if (sg * alvoF > sg * fase(t0)) { let lo = t0, hi = t; for (let i = 0; i < 22; i++) { const m = (lo + hi) / 2; sg * fase(m) < sg * alvoF ? lo = m : hi = m; } ts = hi; }
    pernas.push({ s, nomes, w, ts, antes: ts === t0 + 1e-4 });
  }
  if (!pernas.length) return;
  const Wp = n => A.osso(n).getWorldPosition(new THREE.Vector3()), trava = {};
  const rot = A.obj.rotation.y, py = A.obj.position.y;
  for (const p of pernas) { caminhar(A, a, b, p.ts, t0, t1, { ...o, _semTrava: true, _semIdle: p.antes });   /* apoio que começou antes de andar: trava onde a CAMINHADA põe o pé */ A.obj.position.y = py; A.obj.updateMatrixWorld(true); trava[p.s] = Wp(p.nomes[2]); }
  caminhar(A, a, b, t, t0, t1, { ...o, _semTrava: true }); A.obj.rotation.y = rot; A.obj.position.y = py; A.obj.updateMatrixWorld(true);
  const frente = A.obj.getWorldDirection(new THREE.Vector3()); frente.y = 0; frente.normalize();
  for (const p of pernas) {
    const pe = A.osso(p.nomes[2]), atual = pe.getWorldPosition(new THREE.Vector3()), alvo = trava[p.s].clone(); alvo.y = atual.y;
    const d = Math.hypot(alvo.x - atual.x, alvo.z - atual.z); if (d < .002) continue;
    const k = p.w * (1 - P.suave(.26, .5, d));                                                // desvio grande demais = não trava (evita perna esticada)
    const qMundo = pe.getWorldQuaternion(new THREE.Quaternion());
    ik2(A, p.nomes[0], p.nomes[1], p.nomes[2], alvo, frente.toArray(), k);
    const qp = pe.parent.getWorldQuaternion(new THREE.Quaternion()).invert(); pe.quaternion.copy(qp.multiply(qMundo)); A.obj.updateMatrixWorld(true);
  }
}
// interpola ângulo pelo caminho mais curto
export function angLerp(a, b, u) { const d = ((b - a + Math.PI * 3) % (Math.PI * 2)) - Math.PI; return a + d * u; }
// IK de 2 ossos pra qualquer esqueleto (Metalis: LeftArm/LeftForeArm/LeftHand). alvo e polo no mundo; k mistura com a pose atual
export function ik2(A, nU, nF, nH, alvo, polo = [0, -1, 0], k = 1) {
  // resolve a partir da pose NEUTRA do esqueleto (estável: sem o cotovelo virar quando o alvo cruza o braço animado)
  // e mistura com a animação por slerp (k 0–1)
  if (k <= 0) return; const U = A.osso(nU), Fo = A.osso(nF), H = A.osso(nH); if (!U || !Fo || !H) return;
  const W = b => b.getWorldPosition(new THREE.Vector3()), ossos = [U, Fo, H], anim = ossos.map(b => b.quaternion.clone());
  if (A.bind) ossos.forEach(b => { const q = A.bind(b); if (q) b.quaternion.copy(q); });
  A.obj.updateMatrixWorld(true);
  const alvoV = new THREE.Vector3(...[].concat(alvo.toArray ? alvo.toArray() : alvo));
  const a = W(U), l1 = a.distanceTo(W(Fo)), l2 = W(Fo).distanceTo(W(H)), d = alvoV.clone().sub(a), L = Math.min(d.length(), l1 + l2 - .002), dn = d.clone().normalize();
  const cosA = P.clamp((l1 * l1 + L * L - l2 * l2) / (2 * l1 * L), -1, 1), po = new THREE.Vector3(...polo); po.addScaledVector(dn, -po.dot(dn)).normalize();
  const cot = a.clone().addScaledVector(dn, l1 * cosA).addScaledVector(po, l1 * Math.sqrt(1 - cosA * cosA));
  M.apontar(U, Fo, cot.clone().sub(a).toArray()); A.obj.updateMatrixWorld(true); M.apontar(Fo, H, alvoV.clone().sub(W(Fo)).toArray());
  ossos.forEach((b, i) => { const ik = b.quaternion.clone(); b.quaternion.copy(anim[i]).slerp(ik, k); }); A.obj.updateMatrixWorld(true);
}
// fala com qualquer osso de cabeça (Metalis: 'Head')
export function falarOsso(A, osso, v, t, k = 1) { if (v > 0) { girar(A, osso, [1, 0, 0], -.05 * k * v * Math.sin(t * 6.1)); girar(A, osso, [0, 1, 0], .03 * k * v * Math.sin(t * 2.3 + 1)); } }
// olhos do Metalis acendendo em amarelo: a ÍRIS da textura do olho (verde) troca de cor pra amarelo brilhante,
// e um halo suave fica centrado em cada íris (achada pelos pixels verdes da própria textura). o.acender(k 0–1, câmera)
export function olhosMetalis(Me, o = {}) {
  const head = Me.osso('Head'), g = new THREE.Group(); head.add(g);
  const ml = Me.malhas.find(m => [].concat(m.material).some(x => /olho/.test(x.name))), mt = [].concat(ml.material).find(x => /olho/.test(x.name));
  const tx = mt.uniforms.uMapa.value, im = tx.image, W0 = im.width, H0 = im.height;
  const cv = document.createElement('canvas'); cv.width = W0; cv.height = H0; const cx = cv.getContext('2d'); cx.drawImage(im, 0, 0);
  const base = cx.getImageData(0, 0, W0, H0), brilho = new ImageData(W0, H0), mix = new ImageData(W0, H0);
  const ehIris = (r, g2, b) => g2 > 35 && g2 > r * 1.35 && g2 > b * 1.15;
  for (let i = 0; i < base.data.length; i += 4) { const r = base.data[i], g2 = base.data[i + 1], b = base.data[i + 2];
    if (ehIris(r, g2, b)) { const k = Math.min(1, .55 + g2 / 255); brilho.data[i] = 255 * k; brilho.data[i + 1] = 210 * k; brilho.data[i + 2] = 58 * k; }
    else { brilho.data[i] = r * .45; brilho.data[i + 1] = g2 * .45; brilho.data[i + 2] = b * .45; }
    brilho.data[i + 3] = base.data[i + 3];
    if (o.soIris && !ehIris(r, g2, b) && (r + g2 + b) > 75) brilho.data[i + 3] = 0; }      // só a íris (e a pupila): o resto do olho some
  const nova = new THREE.CanvasTexture(cv); for (const k of ['flipY', 'wrapS', 'wrapT']) nova[k] = tx[k]; nova.magFilter = nova.minFilter = THREE.NearestFilter; nova.generateMipmaps = false; nova.colorSpace = THREE.NoColorSpace;
  // centro das íris: vértices do olho cuja UV cai em pixel verde, em coordenada do Metalis → osso da cabeça
  Me.obj.updateMatrixWorld(true); const G = ml.geometry, pos = G.attributes.position, uv = G.attributes.uv, pts = [];
  for (let i = 0; i < pos.count; i++) { const u = uv.getX(i), v = uv.getY(i), px = Math.min(W0 - 1, Math.max(0, Math.floor(u * W0))), py = Math.min(H0 - 1, Math.max(0, Math.floor((tx.flipY ? 1 - v : v) * H0))), q = (py * W0 + px) * 4;
    if (!ehIris(base.data[q], base.data[q + 1], base.data[q + 2])) continue; const w = new THREE.Vector3(); ml.isSkinnedMesh ? ml.getVertexPosition(i, w) : w.fromBufferAttribute(pos, i); pts.push(ml.localToWorld(w)); }
  const inv = new THREE.Matrix4().copy(Me.obj.matrixWorld).invert(), loc = pts.map(p => p.clone().applyMatrix4(inv));
  const media = L => L.reduce((s2, p) => s2.add(p), new THREE.Vector3()).multiplyScalar(1 / Math.max(1, L.length));
  const lados = [loc.filter(p => p.x < 0), loc.filter(p => p.x >= 0)].filter(L => L.length).map(L => media(L).applyMatrix4(Me.obj.matrixWorld));
  const halo = P.mat({ mapa: F.TEX.brilho(), cor: '#ffd23a', opac: .5, aditivo: true, semLuz: true, lados: THREE.DoubleSide }), hs = [];
  const esc = head.getWorldScale(new THREE.Vector3()).x;
  for (const w of lados) { const h = P.disco(.07 / esc, halo, { seg: 10 }); h.position.copy(head.worldToLocal(w.clone())); g.add(h); hs.push(h); }
  let ultimo = -1;
  g.acender = (k, cam) => {
    k = P.clamp(k); hs.forEach(h => { h.visible = k > .01; if (cam) h.quaternion.copy(cam.quaternion).premultiply(head.getWorldQuaternion(new THREE.Quaternion()).invert()); });
    halo.uniforms.uOpac.value = .45 * k;
    const kk = Math.round(k * 24) / 24; if (kk === ultimo) return; ultimo = kk;
    if (kk <= 0 && !o.soIris) { cx.putImageData(base, 0, 0); nova.needsUpdate = true; mt.uniforms.uMapa.value = nova; mt.uniforms.uSemLuz.value = 0; return; }   /* olho normal pela MESMA textura (a original saía como bloco preto) */
    for (let i = 0; i < mix.data.length; i++) mix.data[i] = (i & 3) === 3 ? (o.soIris ? brilho.data[i] : base.data[i]) : base.data[i] * .45 * (1 - kk) + brilho.data[i] * kk;
    cx.putImageData(mix, 0, 0); nova.needsUpdate = true; mt.uniforms.uMapa.value = nova; mt.uniforms.uSemLuz.value = 1;
  };
  g.acender(0); g.pontos = lados; return g;
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
// mão fechada segurando algo (k 0–1): dobra as falanges de todos os dedos
export function punho(A, s, k = 1, sinal = 1) { if (k <= 0) return; for (const d of ['f_index', 'f_middle', 'f_ring', 'f_pinky']) for (const n of ['.01.', '.02.', '.03.']) girar(A, d + n + s, [1, 0, 0], sinal * 1.1 * k); for (const n of ['thumb.02.', 'thumb.03.']) girar(A, n + s, [1, 0, 0], sinal * .6 * k); }
// fala: balança a cabeça de leve com o volume
export function falar(A, v, t) { if (v > 0) { girar(A, 'spine.005', [1, 0, 0], -.035 * v * Math.sin(t * 6.1)); girar(A, 'spine.005', [0, 1, 0], .02 * v * Math.sin(t * 2.3)); } }

// ── a dupla no carro (serve por dentro e por fora): sentados, Adryan com as duas mãos no volante girando,
//    Nicolas com a maleta no colo segurando pelas laterais. dupla.atualizar(t, { giro, olhaAd, olhaNi, falaAd })
//    Medidas do sedã (m, local do carro): banco motorista x=+.35, passageiro x=−.35, teto y≈1.33, volante (.35,.84,.49)
export async function dupla(pai) {
  const Ad = await E4.ator('adryan'), Ni = await E4.ator('nicolas'); pai.add(Ad.obj, Ni.obj);
  Ad.obj.scale.setScalar(.74); Ni.obj.scale.setScalar(.72);
  T.poses(Ad.modelo); T.poses(Ni.modelo);
  const mal = T.maleta(); mal.scale.setScalar(.72); pai.add(mal);
  const BANCO = { x: .35, y: .6, z: .2 }, PASS = { x: -.35, y: .6, z: .29 }, V = new THREE.Vector3(.35, .84, .49);
  const W = (A, n) => A.osso(n).getWorldPosition(new THREE.Vector3());
  const loc = v => pai.worldToLocal(v.clone()), mun = v => pai.localToWorld(v.clone());
  function atualizar(t = 0, o = {}) {
    sentar(Ad, BANCO, { dy: 0 }); sentar(Ni, PASS, { dy: 0 });
    pai.updateMatrixWorld(true);
    // Adryan: mãos no volante a "10 e 2", girando junto com o volante
    const g = o.giro ?? (.14 * Math.sin(t * .7) + .05 * Math.sin(t * 1.9));
    const DIR = v => mun(new THREE.Vector3(...v)).sub(mun(new THREE.Vector3())).toArray();
    // MALETA / ENTREGA (o.entrega 0→1): Nicolas levanta do colo e oferece (0–.3) · Adryan solta o volante e pega na alça (.2–.5)
    //   · Nicolas solta e recolhe as mãos (.5–.68) · Adryan puxa pro colo dele (.55–.9). Depois fica com o Adryan.
    const en = o.entrega ?? 0, sobe = P.suave(0, .3, en), pegaA = P.suave(.2, .5, en), soltaN = P.suave(.5, .68, en), puxa = P.suave(.55, .9, en);
    const coxa = W(Ni, 'thigh.L').add(W(Ni, 'thigh.R')).multiplyScalar(.5), joe = W(Ni, 'shin.L').add(W(Ni, 'shin.R')).multiplyScalar(.5);
    const colo = loc(coxa).lerp(loc(joe), .5).add(new THREE.Vector3(0, .1, -.06)), MEIO = new THREE.Vector3(-.03, .97, .38), COLO_AD = new THREE.Vector3(.2, .8, .33);
    const mp = colo.clone().lerp(MEIO, sobe).lerp(COLO_AD, puxa); mp.y += Math.sin(puxa * Math.PI) * .05;
    mal.visible = !o.semMaleta; mal.position.copy(mp); mal.rotation.set(0, -.25 * sobe * (1 - puxa), .08 * Math.sin(sobe * Math.PI)); mal.deitar?.(1);
    const alca = mp.clone().add(new THREE.Vector3(.06, .09, -.02));
    for (const s of ['L', 'R']) {
      const lado = s === 'L' ? 1 : -1, h = mun(colo.clone().add(new THREE.Vector3(lado * .13, -.06, .02))), alvo = mun(new THREE.Vector3(mp.x + lado * .17, mp.y + .07, mp.z + .04));
      Ni.modelo.alcancar(s, (o.semMaleta ? h : alvo.lerp(h, soltaN)).toArray(), DIR([lado * .9, -.4, -.3]), .05); if (soltaN < .6 && !o.semMaleta) punho(Ni, s, .6 * (1 - soltaN));
    }
    // volante de verdade (peça separada do carro): gira com o giro e as mãos ficam presas no aro em 10h e 2h
    pai.girarVolante?.(-g); pai.updateMatrixWorld(true);
    const VO = pai.volanteObj, VL = pai.VOL;
    for (const [s, ang] of [['L', .5], ['R', Math.PI - .5]]) {
      let p = VO ? loc(VO.localToWorld(VL.X.clone().multiplyScalar(Math.cos(ang) * VL.r).addScaledVector(VL.U, Math.sin(ang) * VL.r).add(new THREE.Vector3(0, 0, -.015))))
        : new THREE.Vector3(V.x + Math.cos(ang + g) * .16, V.y + Math.sin(ang + g) * .13, V.z);
      if (s === 'L' && o.janela) p = p.lerp(new THREE.Vector3(.62, .86, .5), P.suave(0, .5, o.janela) * (1 - P.suave(.85, 1, o.janela)));   // botão do vidro na porta
      if (s === 'L' && o.bolso) p = p.lerp(new THREE.Vector3(.5, .6, .2), o.bolso);                     // mão no bolso (dinheiro)
      if (s === 'L' && o.maoFora) p = p.lerp(new THREE.Vector3(.98, .98, .3), o.maoFora);                  // mão pra fora da janela (pagar, dar a moeda)
      if (s === 'R' && pegaA > 0) p = p.lerp(alca, pegaA);                                                  // pega a maleta pela alça
      // pegada orientada no aro: dedos envolvem o aro pela frente, indicador apontando pro topo do volante (12h)
      let dW = null, iW = null;
      if (VO) { const e = VO.matrixWorld, dirW = v => v.clone().transformDirection(e);
        const rad = dirW(VL.X.clone().multiplyScalar(Math.cos(ang)).addScaledVector(VL.U, Math.sin(ang))), N = dirW(VL.N), T = dirW(VL.X.clone().multiplyScalar(-Math.sin(ang)).addScaledVector(VL.U, Math.cos(ang)));
        dW = N.clone().multiplyScalar(.75).addScaledVector(rad, -.55); iW = s === 'L' ? T : T.negate(); }
      const fora = s === 'L' ? Math.max(o.janela ? P.suave(0, .5, o.janela) * (1 - P.suave(.85, 1, o.janela)) : 0, o.bolso ?? 0, o.maoFora ?? 0) : pegaA;   // mão longe do aro
      // direção natural da mão em cada gesto (dedos seguem o antebraço; pulso quase reto): pra fora da janela, no bolso, no botão
      const dirC = v => mun(new THREE.Vector3(...v)).sub(mun(new THREE.Vector3())).normalize();
      let neutroD = dirC([0, -.3, 1]), neutroI = dirC([s === 'L' ? -1 : 1, 0, 0]);
      if (s === 'L') { const wb = P.suave(.1, .6, o.bolso ?? 0), wf = P.suave(.1, .6, o.maoFora ?? 0);         // misturas contínuas (antes: troca em degrau → salto de mão)
        neutroD = neutroD.lerp(dirC([.15, -1, .1]), wb).lerp(dirC([1, -.15, .25]), wf).normalize(); neutroI = neutroI.lerp(dirC([0, 0, 1]), wb).lerp(dirC([0, .2, 1]), wf).normalize(); }
      const fecha = s === 'R' ? P.lerp(P.lerp(.75, .25, P.suave(.3, .7, fora)), .9, P.suave(.7, .95, pegaA)) : P.lerp(.75, .25, P.suave(.3, .7, fora));
      if (dW) V_pegarMisto(Ad, s, mun(p), dW.lerp(neutroD, fora), iW.lerp(neutroI, fora), DIR([s === 'L' ? .9 : -.9, -.9, -.1]), fecha);
      else Ad.modelo.alcancar(s, mun(p).toArray(), DIR([s === 'L' ? .9 : -.9, -.9, -.1]), .05);
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
  // ESCRITÓRIO (PSX Office Pack, valsekamerplant, CC0): mesa de verdade com pernas até o chão, cadeira de escritório sob o Igor
  //   (gira junto com ele), estantes com livros no fundo, arquivo, luminária de mesa, relógio, carpete
  const OF = 'material/modelos/pacotes/psx_office/OFFICE/';
  const of = (n, o = {}) => peca(OF + n + '.glb', { tex: 256, verde: false, ...o });
  s.mesa.visible = false;
  const mesa = await of('desks/desk1'); const km = s.Y / mesa.tam.y; mesa.scale.setScalar(km); mesa.position.set(0, 0, .5); mesa.rotation.y = Math.PI; cena.add(mesa); mesa.traverse(n => { n.userData.vaoPernas = true; });   // mesa com vão pras pernas: quem está sentado nela não 'atravessa'
  const cad = await of('chairs/office_chair_black'); cad.scale.setScalar(.95); cad.traverse(n => { n.userData.assento = 'igor'; }); cena.add(cad);
  const cadeira = new THREE.Group(); cadeira.add(cad); cad.position.set(0, 0, -.1); cad.rotation.y = Math.PI; cena.add(cadeira);
  const girar0 = s.I.girar; s.I.girar = k => { girar0(k); cadeira.rotation.y = s.I.obj.rotation.y; };
  const est = await of('book_things/book_case_with_back'), livros = await Promise.all(['books', 'books_alt', 'books_alt2', 'file_binder', 'file_binder_alt3'].map(n => of('book_things/' + n)));
  for (const [x, sem] of [[1.42, 1], [-1.95, 2]]) {
    const e = est.clone(); e.scale.setScalar(.85); e.position.set(x, 0, -1.43); cena.add(e);
    for (let i = 0; i < 4; i++) for (let j = 0; j < 2; j++) { const l = livros[(i * 2 + j + sem) % livros.length].clone(); l.scale.setScalar(.85); l.position.set(x + (j - .5) * .78, .1 + i * .5, -1.42); l.rotation.y = Math.PI; cena.add(l); }
  }
  const arq = await of('file_cabinets/file_cabinet_smaller'); arq.position.set(-1.25, 0, .35); arq.rotation.y = Math.PI / 2; cena.add(arq);
  const lumi = await of('extras/square_desklamp'); lumi.position.set(-.72, s.Y, .72); lumi.rotation.y = Math.PI - .6; cena.add(lumi);
  const rel = await of('extras/wall_clock'); rel.scale.setScalar(.7); rel.position.set(-.3, 2.55, -1.64); cena.add(rel);
  const tap = await of('carpet_floor/floor_3x3'); for (const [x, z] of [[-1.5, -.2], [1.5, -.2], [-1.5, 2.8], [1.5, 2.8]]) { const c = tap.clone(); c.position.set(x, .006, z); cena.add(c); }
  s.I.obj.name = 'ator:igor'; s.c.torcaoAnte = false;                                  // v4: torção das mãos do Igor distribuída no antebraço
  window.SALA = s; return { ...s, quadro, retrato: ret, video, mesaNova: mesa, cadeira };
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
  // árvores do pacote vêm com TODAS as versões de detalhe (LOD0..3) visíveis ao mesmo tempo, e a LOD3 fica deslocada:
  // aparecia como um "arbusto preto" flutuando na estrada/na frente da loja (achado pelo tools/qa.mjs). Fica só a LOD0.
  m.obj.traverse(n => { if (/LOD[1-9]/.test(n.name)) n.visible = false; });
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
  for (const [x, z] of [[-4, -3.6], [4, -3.6], [-4, -1.6], [4, -1.6]]) { const p = pil.clone(); p.scale.set(.7, kp, .7); p.position.set(x, 0, z); g.add(p); }
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
  Object.assign(g, { loja, vitrine: vit, bombas, bico, ALT, luzes: () => [...luzes.map(([x, z]) => ({ pos: [x, ALT - .5, z], cor: '#dcffe6', raio: 7, int: 1.1 })), { pos: [2, 1.5, -6.5], cor: '#39ff6a', raio: 7, int: 1.2 }] });
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
export function segurarMaleta(A, mal, t = 0) {
  // a maleta pendura da mão FECHADA pela alça, alinhada com o corpo (antes ficava sem girar e com a mão aberta)
  const p = new THREE.Vector3(); A.osso('hand.R').getWorldPosition(p); punho(A, 'R', .9);
  const q = A.obj.getWorldQuaternion(new THREE.Quaternion()); mal.quaternion.copy(q).multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), Math.PI / 2));
  mal.rotateX(.04 * Math.sin(t * 5.3)); mal.position.set(p.x, p.y - mal.alca * mal.scale.y - .02, p.z);
}
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
  // porta com PORTINHOLA na altura dos olhos (lugar secreto: quem está dentro olha pela fresta antes de abrir)
  const PW = PX1 - PX0, PHt = PH - .05, FX0 = .37, FX1 = .67, FY0 = 1.62, FY1 = 1.77, esp2 = .07;   /* altura dos olhos do Gusta (1,70) */
  dob.add(P.caixa(PW, FY0, esp2, esc, { pos: [PW / 2, FY0 / 2, 0] }), P.caixa(PW, PHt - FY1, esp2, esc, { pos: [PW / 2, (PHt + FY1) / 2, 0] }),
    P.caixa(FX0, FY1 - FY0, esp2, esc, { pos: [FX0 / 2, (FY0 + FY1) / 2, 0] }), P.caixa(PW - FX1, FY1 - FY0, esp2, esc, { pos: [(PW + FX1) / 2, (FY0 + FY1) / 2, 0] }));
  const moldura = P.mat({ cor: '#2a2016' });                                                                    // moldura escura em volta da fresta (por fora)
  dob.add(P.caixa(FX1 - FX0 + .08, .035, .02, moldura, { pos: [(FX0 + FX1) / 2, FY1 + .017, .045] }), P.caixa(FX1 - FX0 + .08, .035, .02, moldura, { pos: [(FX0 + FX1) / 2, FY0 - .017, .045] }),
    P.caixa(.035, FY1 - FY0 + .07, .02, moldura, { pos: [FX0 - .022, (FY0 + FY1) / 2, .045] }), P.caixa(.035, FY1 - FY0 + .07, .02, moldura, { pos: [FX1 + .022, (FY0 + FY1) / 2, .045] }));
  const tampa = P.caixa(FX1 - FX0 + .06, FY1 - FY0 + .06, .025, P.mat({ cor: '#4a3c2c' }), { pos: [(FX0 + FX1) / 2, (FY0 + FY1) / 2, -.05] }); dob.add(tampa);   // tampa de correr (do lado de dentro)
  const tampaX = (FX0 + FX1) / 2;
  const mac = P.caixa(.05, .05, .08, P.mat({ cor: '#c9c19a' }), { pos: [PX1 - PX0 - .12, 1.05, .06] }); dob.add(mac);
  const h = P.disco(1.4, P.mat({ mapa: F.TEX.brilho(), cor: '#39ff6a', opac: .3, aditivo: true, semLuz: true, lados: THREE.DoubleSide }), { seg: 10, pos: [1.7, 1.6, D / 2 + .25] }); g.add(h); g.halo = h;
  // plataformas (local da cabana): degrau da varanda e piso interno — V.chao(x, z, cab.plataformas) dá a altura do pé
  g.plataformas = [{ x0: -1.8, x1: -.6, z0: 2.75, z1: 3.25, y: .2 }, { x0: -W / 2, x1: W / 2, z0: -D / 2, z1: D / 2, y: .08 }];
  const macD = P.caixa(.05, .05, .08, P.mat({ cor: '#c9c19a' }), { pos: [PX1 - PX0 - .12, 1.05, -.06] }); dob.add(macD);           // maçaneta de dentro
  Object.assign(g, { porta: dob, macaneta: mac, macanetaDentro: macD, abrir: k => { dob.rotation.y = 1.7 * k; },
    portinhola: k => { tampa.position.x = tampaX + .34 * P.clamp(k); },                                       // 0 fechada → 1 aberta (corre pro lado)
    fresta: () => { g.updateMatrixWorld(true); return dob.localToWorld(new THREE.Vector3((FX0 + FX1) / 2, (FY0 + FY1) / 2, 0)); },
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
  const Me = await E4.ator('metalis'); cena.add(Me.obj); Me.obj.visible = false;          // só aparece quando a cena dele chama (antes ficava parado no posto)
  // bicos: a bomba da esquerda perde os 4 bicos embutidos; no lugar, 3 bicos fixos + o que o frentista usa (suporte +x,+z, virado pro carro)
  const B0 = posto.bombas[0], kb = B0.scale.x; B0.traverse(n => { if (n.isMesh) { n.geometry.computeBoundingBox(); const bb = n.geometry.boundingBox; if (bb.min.y > .5 && bb.max.y < 1.05) n.visible = false; } });
  const SUP = (sx, sz) => new THREE.Vector3(B0.position.x + kb * .25 * sx, B0.position.y + kb * .618, B0.position.z + kb * .349 * sz);
  for (const [sx, sz] of [[-1, 1], [1, -1], [-1, -1]]) { const b = posto.bico.clone(); b.scale.setScalar(kb); b.position.copy(SUP(sx, sz)); if (sz < 0) b.rotation.y = Math.PI; cena.add(b); }
  const bico = posto.bico.clone(); bico.scale.setScalar(kb); cena.add(bico); bico.suporte = SUP(1, 1); bico.position.copy(bico.suporte);
  // mangueira: do alto da bomba até a traseira do bico, com barriga (refeita a cada quadro)
  const mangMat = P.mat({ cor: '#151816' }); let mang = null;
  bico.mangueira = () => {
    bico.updateMatrixWorld(true); const a = new THREE.Vector3(B0.position.x + kb * .32, B0.position.y + kb * 1.55, B0.position.z + kb * .3), b = bico.localToWorld(new THREE.Vector3(0, .02, .17));
    const m = a.clone().lerp(b, .5); m.y = Math.min(a.y, b.y) - .35 - a.distanceTo(b) * .15;
    // CONTORNA O CORPO: pontos da curva que caem dentro de um obstáculo (cápsulas do tronco e das pernas de quem está perto)
    // são empurrados pra fora, na horizontal; depois suaviza. Nunca abaixo do chão.
    // a mangueira sai do cabo e CAI primeiro (peso), afastando-se do corpo; depois faz a barriga até a bomba
    const caps = (bico.obstaculos ?? []).flatMap(f => f());
    const fora = new THREE.Vector3(); if (caps[0]) { const ab = caps[0].b.clone().sub(caps[0].a), q = caps[0].a.clone().addScaledVector(ab, P.clamp(b.clone().sub(caps[0].a).dot(ab) / ab.lengthSq())); fora.copy(b).sub(q); fora.y = 0; if (fora.lengthSq() > 1e-6) fora.normalize(); }
    const b2 = b.clone().add(new THREE.Vector3(0, -Math.min(.3, b.y - .05), 0)).addScaledVector(fora, .12);
    const base = new THREE.CatmullRomCurve3([b, b2, m, a].reverse()), N = 26, pts = []; for (let i = 0; i <= N; i++) pts.push(base.getPoint(i / N));
    for (let it = 0; it < 5; it++) {
      for (let i = 1; i < N; i++) { const p = pts[i]; for (const c of caps) { const ab = c.b.clone().sub(c.a), u = P.clamp(p.clone().sub(c.a).dot(ab) / ab.lengthSq()), q = c.a.clone().addScaledVector(ab, u);
        const dv = p.clone().sub(q); dv.y = 0; const d = dv.length(), r = c.r + .06; if (d < r) { if (d < 1e-4) dv.set(1, 0, 0); else dv.multiplyScalar(1 / d); p.x = q.x + dv.x * r; p.z = q.z + dv.z * r; } }
        p.y = Math.max(.02, p.y); }
      if (it < 4) for (let i = 1; i < N; i++) pts[i].lerp(pts[i - 1].clone().add(pts[i + 1]).multiplyScalar(.5), .35); }   /* última volta só afasta (a suavização puxava pra dentro) */
    const g = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 32, .016, 4, false);
    if (!mang) { mang = new THREE.Mesh(g, mangMat); mang.name = 'mangueira'; mang.userData.flexivel = true; cena.add(mang); } else { mang.geometry.dispose(); mang.geometry = g; }
  };
  bico.mangueira();
  // chegada: da estrada (z=9) até a bomba (0,0), freando; saída: volta pra estrada indo pra +x
  const curva = new THREE.CatmullRomCurve3([[-40, 0, 9], [-16, 0, 9], [-9.5, 0, 5.2], [-6.2, 0, 2.5], [-4, 0, 1.6], [-1.8, 0, .45], [0, 0, 0]].map(p => new THREE.Vector3(...p)));   // passa por fora do pilar (−4, −0,4)
  // saída: abre pra +z logo cedo pra passar LONGE do pilar da cobertura em (4, −0,4) (antes a lataria passava por dentro dele — achado pelo QA)
  const saida = new THREE.CatmullRomCurve3([[0, 0, 0], [2.6, 0, .9], [5.5, 0, 3.0], [10, 0, 6.3], [16, 0, 9], [60, 0, 9]].map(p => new THREE.Vector3(...p)));
  const naCurva = (cv, u, fim = 1) => { const p = cv.getPointAt(P.clamp(u)), q = cv.getTangentAt(P.clamp(u)); D.car.position.set(p.x, .02, p.z); D.car.rotation.y = P.lerp(Math.atan2(q.x, q.z), Math.PI / 2, fim === 1 ? P.suave(.9, 1, u) : 0); };
  return { ext, posto, D, Fr, Me, bico, B0, postes, curva, saida, naCurva,
    halos: cam => { for (const p of postes) p.halo.quaternion.copy(cam.quaternion).premultiply(p.getWorldQuaternion(new THREE.Quaternion()).invert()); D.car.encarar(cam); } };
}

// ── DINHEIRO: maço de cédulas (pagar o frentista) e moeda (Metalis). Segue a mão: d.naMao(A, 'L'|'R', k)
export function dinheiro(tipo = 'notas') {
  const g = new THREE.Group();
  if (tipo === 'notas') for (let i = 0; i < 3; i++) g.add(P.caixa(.12, .003, .055, P.mat({ cor: ['#7fa07a', '#b9b27a', '#8fb39a'][i], semLuz: true }), { pos: [i * .008, i * .004, i * .006], rot: [0, i * .12, 0] }));
  else g.add(P.cilindro(.013, .013, .003, P.mat({ cor: '#d9c46a', semLuz: true }), { seg: 8 }));
  g.naMao = (A, s, esc = 1) => { const h = A.osso('hand.' + s), f = A.osso('f_middle.01.' + s) || h, a = h.getWorldPosition(new THREE.Vector3()), b = f.getWorldPosition(new THREE.Vector3());
    g.position.copy(a.lerp(b, .7)); g.quaternion.copy(h.getWorldQuaternion(new THREE.Quaternion())); g.scale.setScalar(esc); };
  return g;
}

// ── PEGADA ORIENTADA (o "target rotation" do Two Bone IK): a mão vai até o ponto de contato JÁ com a orientação do objeto.
//   grip: ponto de contato (mundo, onde fica a palma) · dedos: pra onde os dedos apontam · indice: de que lado fica o indicador
//   (vetor mindinho→indicador) · polo: pra onde o cotovelo aponta · k: mistura com a pose atual (0–1) · fecha: dedos fechados (0–1)
//   A torção é dividida: 75% no antebraço (onde ela acontece de verdade: pronação/supinação), o resto no pulso (o pulso sozinho não gira 180°: era isso que deixava a mão "torcida").
const _v = () => new THREE.Vector3();
export function pegar(A, s, grip, dedos, indice, polo = [0, -1, 0], k = 1, fecha = .7) {
  if (k <= 0) return; const m = A.modelo; if (!m.alcancar) T.poses(m); const U = A.osso('upper_arm.' + s), Fo = A.osso('forearm.' + s), H = A.osso('hand.' + s), Mi = A.osso('f_middle.01.' + s);
  if (!U || !Fo || !H || !Mi) return;
  const W = b => b.getWorldPosition(_v()), ossos = [U, Fo, H], antes = ossos.map(b => b.quaternion.clone());
  A.obj.updateMatrixWorld(true);
  const D = new THREE.Vector3(...[].concat(dedos.toArray ? dedos.toArray() : dedos)).normalize(), G = new THREE.Vector3(...[].concat(grip.toArray ? grip.toArray() : grip));
  const palma = W(H).distanceTo(W(Mi)) * .55;                                       // do pulso até o meio da palma
  const pulso = G.clone().addScaledVector(D, -palma);
  m.alcancar(s, pulso.toArray(), polo, 0); A.obj.updateMatrixWorld(true);
  M.apontar(H, Mi, D.toArray()); A.obj.updateMatrixWorld(true);
  // gira em torno do eixo dos dedos até o lado do indicador casar; divide entre antebraço e pulso
  const lado = () => { const v = W(A.osso('f_index.01.' + s)).sub(W(A.osso('f_pinky.01.' + s))); return v.addScaledVector(D, -v.dot(D)).normalize(); };
  const I = new THREE.Vector3(...[].concat(indice.toArray ? indice.toArray() : indice)); I.addScaledVector(D, -I.dot(D)).normalize();
  const v = lado(), ang = Math.atan2(v.clone().cross(I).dot(D), v.dot(I));
  const eixoAnte = W(H).sub(W(Fo)).normalize();
  m.virar('forearm.' + s, eixoAnte.toArray(), ang * .75); A.obj.updateMatrixWorld(true);
  M.apontar(H, Mi, D.toArray()); A.obj.updateMatrixWorld(true);
  const v2 = lado(), ang2 = Math.atan2(v2.clone().cross(I).dot(D), v2.dot(I)); m.virar('hand.' + s, D.toArray(), ang2); A.obj.updateMatrixWorld(true);
  if (k < 1) { ossos.forEach((b, i) => { const q = b.quaternion.clone(); b.quaternion.copy(antes[i]).slerp(q, k); }); A.obj.updateMatrixWorld(true); }
  if (fecha > 0) punho(A, s, fecha * k);
}
// QA: torção e dobra do pulso (graus) de um lado — usado pelo tools/qa.mjs
export function pulso(A, s) {
  const W = n => A.osso(n).getWorldPosition(_v()), ante = W('hand.' + s).sub(W('forearm.' + s)).normalize(), mao = W('f_middle.01.' + s).sub(W('hand.' + s)).normalize();
  return Math.acos(P.clamp(ante.dot(mao), -1, 1)) * 180 / Math.PI;
}
// ── portinhola do tanque (lado do motorista, traseira): car local. t.abrir(0–1) gira na dobradiça da frente; boca preta com gargalo
export function tampaTanque(car) {
  const g = new THREE.Group(), C = new THREE.Vector3(.95, .88, -1.85); car.add(g);
  const boca = P.cilindro(.034, .034, .02, P.mat({ cor: '#060706' }), { seg: 10, pos: [C.x - .005, C.y, C.z], rot: [0, 0, Math.PI / 2] });
  const gargalo = P.cilindro(.022, .022, .03, P.mat({ cor: '#3a3d3a' }), { seg: 8, pos: [C.x - .01, C.y, C.z], rot: [0, 0, Math.PI / 2] });
  const dob = new THREE.Group(); dob.position.set(C.x + .003, C.y, C.z + .065);           // dobradiça na borda da frente (+z local)
  const porta = P.caixa(.008, .11, .13, P.mat({ cor: '#2b2e33' }), { pos: [0, 0, -.065] }); dob.add(porta);
  g.add(boca, gargalo, dob); g.abrir = k => { dob.rotation.y = -1.7 * P.clamp(k); };
  g.borda = () => porta.localToWorld(new THREE.Vector3(.004, 0, -.06));                  // onde os dedos pegam pra abrir/fechar
  g.abrir(0); return g;
}
// orientação de um objeto a partir de 2 direções do mundo: eixo Y do modelo → F, eixo Z do modelo → U (ajustado ⟂ F)
export function base(F, U) {
  const f = F.clone().normalize(), u = U.clone().addScaledVector(f, -U.dot(f)).normalize(), x = f.clone().cross(u);
  return new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().makeBasis(x, f, u));
}

// pegar() com posição pronta no mundo (atalho usado no volante)
function V_pegarMisto(A, s, grip, dedos, indice, polo, fecha) { pegar(A, s, grip, dedos, indice, polo, 1, fecha); }

// altura do chão em (x, z) pelas plataformas [{x0,x1,z0,z1,y}] (a primeira que contém o ponto vence); borda com rampa de 10 cm = o pé sobe o degrau
export function chao(x, z, plats = [], rampa = .18) {
  let y = 0; for (const p of plats) { const dx = Math.min(x - p.x0, p.x1 - x), dz = Math.min(z - p.z0, p.z1 - z), d = Math.min(dx, dz);
    if (d > -rampa) { y = p.y * P.clamp((d + rampa) / rampa); if (d >= 0) return p.y; } }
  return y;
}
// ── LUZ DA SALA DO IGOR (pedido do diretor): esverdeada e escura, como depois do VHS — a luz vem do MONITOR (verde, tremulando
//    de leve), o resto é penumbra verde; a lâmpada do teto fica quase apagada. extra: { fillCor } pra somar um brilho (maleta)
export function luzSalaVerde(sala, t, cam, extra = {}) {
  sala.lamp.acender(.12, cam);
  const tremor = .78 + .22 * Math.sin(t * 23) * Math.sin(t * 7), c = new THREE.Color('#39ff6a').multiplyScalar(tremor * (extra.k ?? 1));
  P.luz({ ...F.LUZ_SALA, keyDir: sala.rot(0, .1, 1), keyCor: '#' + c.getHexString(), fillDir: extra.fillDir ?? sala.rot(-.6, .6, -.4), fillCor: extra.fillCor ?? '#16321f', amb: extra.amb ?? '#12241a' });
}

// cápsulas do corpo de um ator (tronco + pernas), pra coisas flexíveis (mangueira) desviarem dele
export function capsulasCorpo(A) {
  const W = n => A.osso(n)?.getWorldPosition(new THREE.Vector3()); const q = W('spine') ?? W('Hips'), pe = W('spine.004') ?? W('Head'), oL = W('upper_arm.L'), oR = W('upper_arm.R');
  if (!q || !pe || !oL || !oR) return []; const r = oL.distanceTo(oR) * .42, fL = W('foot.L'), fR = W('foot.R'), kL = W('shin.L'), kR = W('shin.R');
  const out = [{ a: q, b: pe, r }]; if (kL && fL) out.push({ a: q.clone().lerp(kL, .1), b: fL, r: .09 }); if (kR && fR) out.push({ a: q.clone().lerp(kR, .1), b: fR, r: .09 }); return out;
}
