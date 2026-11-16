// THE GREEN PATH — personagens e objetos do projeto (por cima de lib/ps1.js e lib/modelo.js).
import * as P from './ps1.js';
import * as M from './modelo.js';
const { THREE } = P;

export const VERDE = '#39ff6a', SOMBRA = '#04120a', AMARELO = '#ffd84a';
const CORPO = 'material/modelos/personagem-simples.glb';

// pinta a malha com esqueleto por osso dominante: f(nomeDoOsso) → '#hex'
export function pintarPorOsso(malha, f) {
  const g = malha.geometry, si = g.attributes.skinIndex, sw = g.attributes.skinWeight, n = g.attributes.position.count;
  const cor = new Float32Array(n * 3), c = new THREE.Color();
  for (let i = 0; i < n; i++) {
    let b = 0, w = -1;
    for (let k = 0; k < 4; k++) { const wk = sw.getComponent(i, k); if (wk > w) { w = wk; b = si.getComponent(i, k); } }
    c.set(f(malha.skeleton.bones[b].name)); cor.set([c.r, c.g, c.b], i * 3);
  }
  g.setAttribute('color', new THREE.BufferAttribute(cor, 3));
}
const ehMao = n => /hand|palm|thumb|f_|findex|fmiddle|fring|fpinky/.test(n);
const ehPerna = n => /thigh|shin|foot|toe|heel|pelvis/.test(n);

// corpo humano com esqueleto, sem a cabeça original; `cores` = { roupa, mao, perna }
export async function corpo(cores, o = {}) {
  const m = await M.carregar(CORPO, { fora: ['Icosphere', ...(o.semCabeca === false ? [] : ['head'])], esc: o.esc ?? .85, mat: { corVertice: true, mapa: null, cor: '#ffffff', ...(o.mat || {}) } });
  const tecido = P.textura(16, 16, (x, w, h, r) => { x.fillStyle = '#f0f0f0'; x.fillRect(0, 0, w, h); for (let i = 0; i < 50; i++) { x.fillStyle = r() < .5 ? '#ffffff' : '#e2e2e2'; x.fillRect(Math.floor(r() * w), Math.floor(r() * h), 1, 1); } }, { seed: 7 });
  for (const ml of m.malhas) {
    if (ml.isSkinnedMesh) pintarPorOsso(ml, n => ehMao(n) ? cores.mao : ehPerna(n) ? cores.perna : cores.roupa);
    const ms = Array.isArray(ml.material) ? ml.material : [ml.material];
    ms.forEach(mt => { mt.uniforms.uMapa.value = tecido; mt.uniforms.uTemMapa.value = 1; mt.uniforms.uRep.value.set(6, 6); });
  }
  const B = n => m.osso(n);
  // sentado: coxas pra frente, canelas pra baixo
  m.sentar = () => { for (const s of ['L', 'R']) { M.apontar(B('thigh.' + s), B('shin.' + s), [s === 'L' ? .12 : -.12, -.08, 1]); M.apontar(B('shin.' + s), B('foot.' + s), [0, -1, .05]); } };
  // braço: direções (mundo) do braço, do antebraço e da mão
  m.braco = (s, bra, ante, mao, rol = 0) => { M.apontar(B('upper_arm.' + s), B('forearm.' + s), bra); M.apontar(B('forearm.' + s), B('hand.' + s), ante); if (rol) { B('forearm.' + s).rotateY(rol); B('forearm.' + s).updateWorldMatrix(false, true); } if (mao) M.apontar(B('hand.' + s), B('f_middle.01.' + s), mao); };
  m.girar = (nome, ang) => { const b = B(nome); b.rotateY(ang); b.updateWorldMatrix(false, true); };   // torce o osso no próprio eixo
  return m;
}

// ───────────────────────── IGOR ANÃO ─────────────────────────
// Cabeça de caracal: a foto (material/floppa.jpg) projetada de frente numa cabeça low-poly, pixelada.
// Tudo medido em pixels da foto e depois escalado: centro do rosto (240, 232), largura ~280 px.
const FOTO = { cx: 240, cy: 232, rec: [50, 22, 360, 345], tw: 72, th: 69 };   // recorte [x, y, w, h] → textura tw×th
export async function igor(o = {}) {
  const foto = await M.imagem('material/floppa.jpg');
  const [rx, ry, rw, rh] = FOTO.rec;
  // textura da cabeça (canvas vivo: a boca e a piscada são desenhadas por cima a cada quadro)
  const cv = document.createElement('canvas'); cv.width = FOTO.tw; cv.height = FOTO.th;
  const cx = cv.getContext('2d', { willReadFrequently: true }); cx.imageSmoothingEnabled = true;
  cx.filter = 'contrast(1.3) saturate(1.25) brightness(1.12)'; cx.drawImage(foto, rx, ry, rw, rh, 0, 0, cv.width, cv.height); cx.filter = 'none';
  const base = cx.getImageData(0, 0, cv.width, cv.height);
  for (let i = 0; i < base.data.length; i += 4) for (let k = 0; k < 3; k++) base.data[i + k] = Math.round(Math.round(base.data[i + k] / 255 * 31) / 31 * 255);
  const tex = new THREE.CanvasTexture(cv); tex.magFilter = tex.minFilter = THREE.NearestFilter; tex.generateMipmaps = false; tex.colorSpace = THREE.NoColorSpace;
  const px = (x, y) => [(x - rx) / rw * cv.width, (y - ry) / rh * cv.height];                  // foto → textura
  const uvDe = (x, y) => [(FOTO.cx + x - rx) / rw, 1 - (FOTO.cy - y - ry) / rh];              // cabeça (px, y pra cima) → uv

  const PELO = '#b78d58', PELO_ESC = '#8a6a40';
  const matFoto = P.mat({ mapa: tex, lados: THREE.DoubleSide });
  const matPelo = P.mat({ cor: PELO, mapa: P.textura(16, 16, (x, w, h, r) => { x.fillStyle = '#ffffff'; x.fillRect(0, 0, w, h); for (let i = 0; i < 60; i++) { x.fillStyle = r() < .5 ? '#e2d6c4' : '#fff6e6'; x.fillRect(Math.floor(r() * w), Math.floor(r() * h), 1, 2); } }), rep: [3, 3] });
  const matPreto = P.mat({ cor: '#2b2723', lados: THREE.DoubleSide });

  const cab = new THREE.Group();
  // crânio: esfera achatada com o focinho empurrado pra frente; frente = foto, trás = pelo
  const RX = 126, RY = 114, RZ = 118;
  const gi0 = new THREE.SphereGeometry(1, 12, 9), pi = gi0.attributes.position, ord = [[], []], nor = [[], []];
  for (let i = 0; i < pi.count; i++) {
    let x = pi.getX(i) * RX, y = pi.getY(i) * RY, z = pi.getZ(i) * RZ;
    if (z > 0) { const f = Math.exp(-((x / 62) ** 2)) * Math.exp(-(((y + 42) / 50) ** 2)); z += 46 * f; }   // focinho
    if (y < -20) { const q = Math.min(1, (-20 - y) / 70); x *= 1 + .16 * q; z *= 1 + .08 * q; }             // bochecha e papada largas
    pi.setXYZ(i, x, y, z);
  }
  gi0.computeVertexNormals();                                   // normais suaves (Gouraud), antes de separar frente e trás
  const g0 = gi0.toNonIndexed(), p = g0.attributes.position, nn = g0.attributes.normal;
  const uvs = [];
  for (let t = 0; t < p.count; t += 3) {
    const zc = (p.getZ(t) + p.getZ(t + 1) + p.getZ(t + 2)) / 3, gi = zc > -18 ? 0 : 1;
    for (let k = 0; k < 3; k++) { ord[gi].push(p.getX(t + k), p.getY(t + k), p.getZ(t + k)); nor[gi].push(nn.getX(t + k), nn.getY(t + k) * .35 + .25, nn.getZ(t + k)); }   // normal puxada pra cima: o queixo não some no escuro
  }
  const geo = new THREE.BufferGeometry();
  const todos = [...ord[0], ...ord[1]];
  for (let i = 0; i < todos.length; i += 3) uvs.push(...uvDe(todos[i] * .93, todos[i + 1] * .93));     // .93: a borda pega pelo, não o fundo preto
  geo.setAttribute('position', new THREE.Float32BufferAttribute(todos, 3)); geo.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
  geo.addGroup(0, ord[0].length / 3, 0); geo.addGroup(ord[0].length / 3, ord[1].length / 3, 1); geo.setAttribute('normal', new THREE.Float32BufferAttribute([...nor[0], ...nor[1]], 3));
  cab.add(new THREE.Mesh(geo, [matFoto, matPelo]));

  // orelhas: frente com a foto, costas pretas, tufo preto na ponta. Pontos em px da foto (x, y) relativos ao centro
  const orelhas = [];
  for (const s of [-1, 1]) {
    const ext = [s * 124, 78], int = [s * 44, 104], pta = [s * 112, 192], piv = [s * 84, 88];
    const loc = q => [q[0] - piv[0], q[1] - piv[1]];
    const a = loc(ext), b = loc(int), c = loc(pta), tras = [(a[0] + b[0]) / 2, 8, -34];
    const gf = new THREE.BufferGeometry();
    gf.setAttribute('position', new THREE.Float32BufferAttribute([a[0], a[1], 6, b[0], b[1], 14, c[0], c[1], 0], 3));
    gf.setAttribute('uv', new THREE.Float32BufferAttribute([...uvDe(...ext), ...uvDe(...int), ...uvDe(pta[0] * .99, pta[1] * .97)], 2));
    gf.setAttribute('normal', new THREE.Float32BufferAttribute([0, .5, 1, 0, .5, 1, 0, .5, 1], 3));
    const gt = new THREE.BufferGeometry();
    gt.setAttribute('position', new THREE.Float32BufferAttribute([a[0], a[1], 6, c[0], c[1], 0, ...tras, b[0], b[1], 14, ...tras, c[0], c[1], 0], 3));
    gt.setAttribute('uv', new THREE.Float32BufferAttribute(new Array(12).fill(0), 2)); gt.computeVertexNormals();
    const tufo = new THREE.BufferGeometry();          // tufo: fita fina que sobe e cai pra fora
    tufo.setAttribute('position', new THREE.Float32BufferAttribute([c[0] - 5, c[1] - 6, 0, c[0] + 5, c[1] - 6, 0, c[0] + s * 4, c[1] + 26, -2,
      c[0] + s * 4, c[1] + 26, -2, c[0] + s * 1, c[1] + 10, -1, c[0] + s * 34, c[1] + 40, -8], 3));
    tufo.setAttribute('uv', new THREE.Float32BufferAttribute(new Array(12).fill(0), 2)); tufo.computeVertexNormals();
    const og = new THREE.Group(); og.position.set(piv[0], piv[1], -6);
    og.add(new THREE.Mesh(gf, matFoto), new THREE.Mesh(gt, matPreto), new THREE.Mesh(tufo, matPreto));
    cab.add(og); orelhas.push(og);
  }
  const k = (o.largura ?? .4) / 280; cab.scale.setScalar(k);

  // corpo: moletom azul-acinzentado, mãos de pelo
  const c = await corpo({ roupa: '#5d6c9c', mao: PELO, perna: '#1b1d24' });
  const g = c.obj;                                   // grupo raiz (escala .85)
  g.scale.x *= 1.2; g.scale.z *= 1.12;             // tronco mais largo, como na foto
  const pesc = new THREE.Group(); pesc.scale.set(1 / g.scale.x, 1 / g.scale.y, 1 / g.scale.z); g.add(pesc); pesc.add(cab);
  // gola e capuz do moletom + microfone de lapela
  const mol = P.mat({ cor: '#56659a' }), molEsc = P.mat({ cor: '#465383' });
  const gola = P.tornear([[.11, -.05], [.165, -.03], [.17, .0], [.14, .012]], mol, { seg: 8 }); pesc.add(gola);
  const capuz = P.esfera(.13, molEsc, { seg: 7, segV: 5, pos: [0, -.03, -.1], esc: [1.25, .7, .8] }); pesc.add(capuz);
  const mic = new THREE.Group();
  mic.add(P.caixa(.022, .034, .02, P.mat({ cor: '#0c0c0e' })), P.caixa(.014, .012, .016, P.mat({ cor: '#3a3d42' }), { pos: [0, .022, .002] }));
  mic.add(P.tubo([[0, -.017, 0], [.012, -.06, .004], [.04, -.1, -.01], [.07, -.16, -.03]], .003, P.mat({ cor: '#0c0c0e' }), { seg: 6, lados: 3 }));
  pesc.add(mic);

  const I = { obj: g, corpo: c, cabeca: cab, orelhas, pescoco: pesc, mic, tex,
    // posiciona cabeça/gola no osso do pescoço (chame depois de mexer na pose)
    assentar() {
      g.updateMatrixWorld(true);
      const w = new THREE.Vector3(); c.osso('spine.004').getWorldPosition(w); g.worldToLocal(w);
      pesc.position.copy(w); cab.position.set(0, .15, .045); mic.position.set(.075, -.2, .15);
    },
    // boca (0–1, volume da voz), piscada (0–1), tempo (orelhas e cabeça mexem de leve)
    animar(t, { boca = 0, pisca = 0 } = {}) {
      cx.putImageData(base, 0, 0);
      if (pisca > .5) { cx.fillStyle = '#a5804f'; for (const ex of [190, 291]) { const [u, v] = px(ex - 26, 168); cx.fillRect(Math.round(u), Math.round(v), 10, 5); const [u2, v2] = px(ex - 24, 186); cx.fillStyle = '#3b2a1c'; cx.fillRect(Math.round(u2), Math.round(v2), 9, 1); cx.fillStyle = '#a5804f'; } }
      const ab = Math.round(P.clamp(boca) * 5);
      if (ab > 0) { const [u, v] = px(240, 283); cx.fillStyle = '#170b0a'; cx.fillRect(Math.round(u) - 3, Math.round(v), 6, ab); cx.fillRect(Math.round(u) - 2, Math.round(v) + ab, 4, 1); if (ab > 2) { cx.fillStyle = '#6b4a44'; cx.fillRect(Math.round(u) - 1, Math.round(v) + ab - 1, 3, 1); } }
      tex.needsUpdate = true;
      orelhas[0].rotation.z = Math.sin(t * 1.7) * .035 + (Math.sin(t * .9 + 1) > .93 ? .16 : 0);
      orelhas[1].rotation.z = -Math.sin(t * 1.3 + 2) * .035 - (Math.sin(t * .7 + 4) > .95 ? .16 : 0);
      cab.rotation.set(Math.sin(t * .8) * .018 + boca * .03, Math.sin(t * .5) * .04, Math.sin(t * .6 + 1) * .012);
    } };
  return I;
}

// ───────────────────────── objetos de cena ─────────────────────────
export const feltro = () => P.textura(16, 16, (x, w, h, r) => { x.fillStyle = '#1d6a38'; x.fillRect(0, 0, w, h); for (let i = 0; i < 80; i++) { x.fillStyle = r() < .5 ? '#19602f' : '#227540'; x.fillRect(Math.floor(r() * w), Math.floor(r() * h), 1, 1); } }, { seed: 3 });
export function mesaFeltro(o = {}) {
  const g = new THREE.Group(), w = o.w ?? 2.6, d = o.d ?? 1.1, y = o.y ?? .72;
  g.add(P.caixa(w, .05, d, P.mat({ mapa: feltro(), rep: [w * 5, d * 5] }), { pos: [0, y - .025, 0], sx: 12, sz: 6 }));
  g.add(P.caixa(w + .04, .07, d + .04, P.mat({ cor: '#0e2416' }), { pos: [0, y - .07, 0] }));
  g.topo = y; return g;
}
export function copoAgua() {
  const g = new THREE.Group(), r = .034, h = .1;
  g.add(P.caixa(.1, .006, .1, P.mat({ cor: '#6b5a40' }), { pos: [0, .003, 0] }));                                       // porta-copos
  g.add(P.cilindro(r * .92, r * .8, h * .62, P.mat({ cor: '#9fc9c0', opac: .45, semLuz: true }), { seg: 8, pos: [0, .012 + h * .31, 0] }));   // água
  g.add(P.cilindro(r, r * .86, h, P.mat({ cor: '#dcedf3', opac: .3, lados: THREE.DoubleSide }), { seg: 8, aberto: true, pos: [0, .008 + h / 2, 0] }));
  g.add(P.cilindro(r * 1.02, r * 1.02, .004, P.mat({ cor: '#eef6f8', opac: .6 }), { seg: 8, aberto: true, pos: [0, .008 + h, 0] }));
  return g;
}
export function celular() {
  const g = new THREE.Group();
  g.add(P.caixa(.07, .008, .14, P.mat({ cor: '#0b0c0e' }), { pos: [0, .004, 0] }));
  g.add(P.caixa(.06, .002, .125, P.mat({ cor: '#1a2a24' }), { pos: [0, .009, 0] }));
  return g;
}
