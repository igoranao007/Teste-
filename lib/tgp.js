// THE GREEN PATH — personagens e objetos do projeto (por cima de lib/ps1.js e lib/modelo.js).
import * as P from './ps1.js';
import * as M from './modelo.js';
const { THREE } = P;

export const VERDE = '#39ff6a', SOMBRA = '#04120a', AMARELO = '#ffd84a';
const CORPO = 'material/modelos/personagem-simples.glb';

// pinta a malha com esqueleto por osso dominante: f(nomeDoOsso) → '#hex'
export function pintarPorOsso(malha, f) {
  const g = malha.geometry, si = g.attributes.skinIndex, sw = g.attributes.skinWeight, n = g.attributes.position.count;
  const cor = new Float32Array(n * 3), c = new THREE.Color(), nr = g.attributes.normal, rnd = P.rng(9);
  for (let i = 0; i < n; i++) {
    let b = 0, w = -1;
    for (let k = 0; k < 4; k++) { const wk = sw.getComponent(i, k); if (wk > w) { w = wk; b = si.getComponent(i, k); } }
    c.set(f(malha.skeleton.bones[b].name));
    const nx = nr ? Math.abs(nr.getX(i)) : 0, k = (1 - .22 * nx * nx) * (.9 + .2 * rnd());     // sombra "pintada": laterais mais escuras + variação
    cor.set([c.r * k, c.g * k, c.b * k], i * 3);
  }
  g.setAttribute('color', new THREE.BufferAttribute(cor, 3));
}
const ehMao = n => /hand|palm|thumb|f_|findex|fmiddle|fring|fpinky/.test(n);
const ehPerna = n => /thigh|shin|foot|toe|heel|pelvis/.test(n);

const ehPe = n => /foot|toe|heel/.test(n);

// A textura pintada do modelo (dobras, costuras, sombra) vira um "relevo" em cinza: cada região (camiseta, pele, jeans)
// é normalizada pelo próprio tom, e a cor passa a vir da tinta por osso. Assim a roupa muda de cor sem perder o desenho.
async function relevo(tam = 128) {
  const img = await M.imagem('material/modelos/personagem-simples.png');
  const c = document.createElement('canvas'); c.width = c.height = tam;
  const x = c.getContext('2d'); x.drawImage(img, 0, 0, tam, tam);
  const d = x.getImageData(0, 0, tam, tam), q = d.data, R = P.rng(5);
  for (let i = 0; i < q.length; i += 4) {
    const r = q[i] / 255, g = q[i + 1] / 255, b = q[i + 2] / 255, lum = .3 * r + .59 * g + .11 * b, sat = Math.max(r, g, b) - Math.min(r, g, b);
    const linha = Math.floor(i / 4 / tam) / tam;
    let n;
    if (r > g && g > b && r - b > .12 && r > .4) n = lum / .66;                 // pele
    else if (b > r + .05) n = lum / .36;                                        // jeans
    else if (linha < .38) { const cu = (i / 4 % tam) / tam, est = (cu > .2 && cu < .32 && linha > .08 && linha < .19) || (cu > .46 && cu < .68 && linha > .04 && linha < .3); n = est ? P.clamp(lum / .86, .9, 1.1) : P.clamp(lum / .86, .55, 1.15); n = .5 + (n - .5) * 1.5; }   // camiseta: a estampa some, as dobras ficam mais fortes
    else if (sat < .14 && lum > .55) n = lum / .86;                                               // estampa da camiseta: some
    else n = lum / .45;                                                         // tênis, cabelo
    if (linha < .38 || (r > g && g > b && r - b > .12 && r > .4 && linha > .38 && linha < .75)) {      // tecido: dobras largas + trama mesclada
      const cu = (i / 4 % tam) / tam;
      n *= 1 + .1 * Math.sin(cu * 46 + Math.sin(linha * 31) * 2.2) * Math.sin(linha * 19 + cu * 7) + (R() - .5) * .16;
    }
    const v = Math.round(P.clamp(n, .25, 1.25) / 1.25 * 255); q[i] = q[i + 1] = q[i + 2] = v;
  }
  x.putImageData(d, 0, 0);
  const t = new THREE.CanvasTexture(c); t.flipY = false; t.magFilter = t.minFilter = THREE.NearestFilter; t.generateMipmaps = false; t.colorSpace = THREE.NoColorSpace;
  return t;
}

// corpo humano com esqueleto; `cores` = { roupa, mao, perna, pe } · o.cabeca: true mantém a cabeça original
export async function corpo(cores, o = {}) {
  const m = await M.carregar(CORPO, { fora: ['Icosphere', ...(o.cabeca ? [] : ['head'])], esc: o.esc ?? .85, texMax: 128, mat: { corVertice: !o.atlas, ...(o.mat || {}) } });
  const rel = o.atlas ?? await relevo();
  for (const ml of m.malhas) {
    if (!ml.isSkinnedMesh) continue;
    if (!o.atlas) pintarPorOsso(ml, n => ehMao(n) ? cores.mao : ehPe(n) ? (cores.pe ?? '#26262a') : ehPerna(n) ? cores.perna : cores.roupa);
    const ms = Array.isArray(ml.material) ? ml.material : [ml.material];
    ms.forEach(mt => { if (mt.name === 'glass') return; mt.uniforms.uMapa.value = rel; mt.uniforms.uTemMapa.value = 1; if (!o.atlas) mt.uniforms.uCor.value.setRGB(1.25, 1.25, 1.25); });
  }
  m.mats = () => m.malhas.flatMap(ml => Array.isArray(ml.material) ? ml.material : [ml.material]);
  return poses(m);
}

// pose por direção (mundo): serve pra qualquer esqueleto com thigh/shin/foot/upper_arm/forearm/hand
export function poses(m) {
  const B = n => m.osso(n);
  m.sentar = () => { for (const s of ['L', 'R']) { M.apontar(B('thigh.' + s), B('shin.' + s), [s === 'L' ? .12 : -.12, -.08, 1]); M.apontar(B('shin.' + s), B('foot.' + s), [0, -1, .05]); } };
  m.braco = (s, bra, ante, mao, rol = 0) => { M.apontar(B('upper_arm.' + s), B('forearm.' + s), bra); M.apontar(B('forearm.' + s), B('hand.' + s), ante); if (rol) { B('forearm.' + s).rotateY(rol); B('forearm.' + s).updateWorldMatrix(false, true); } if (mao) M.apontar(B('hand.' + s), B('f_middle.01.' + s), mao); };
  m.girar = (nome, ang) => { const b = B(nome); b.rotateY(ang); b.updateWorldMatrix(false, true); };
  // IK de 2 ossos: a mão do lado s ('L'/'R') alcança o ponto `alvo` (mundo); `polo` diz pra onde o cotovelo aponta
  m.alcancar = (s, alvo, polo = [0, -1, 0], extra = .09) => {
    const U = B('upper_arm.' + s), Fo = B('forearm.' + s), H = B('hand.' + s), W = b => b.getWorldPosition(new THREE.Vector3());
    m.obj.updateMatrixWorld(true);
    const a = W(U), l1 = a.distanceTo(W(Fo)), l2 = W(Fo).distanceTo(W(H)) + extra, d = new THREE.Vector3(...alvo).sub(a), L = Math.min(d.length(), l1 + l2 - .002), dn = d.clone().normalize();
    const cosA = P.clamp((l1 * l1 + L * L - l2 * l2) / (2 * l1 * L), -1, 1), po = new THREE.Vector3(...polo); po.addScaledVector(dn, -po.dot(dn)).normalize();
    const cot = a.clone().addScaledVector(dn, l1 * cosA).addScaledVector(po, l1 * Math.sqrt(1 - cosA * cosA));
    M.apontar(U, Fo, cot.clone().sub(a).toArray()); const dir = new THREE.Vector3(...alvo).sub(W(Fo)).toArray();
    M.apontar(Fo, H, dir); M.apontar(H, B('f_middle.01.' + s), m.plana ? [dir[0], -.04, dir[2]] : dir);      // m.plana: a mão fica deitada (apoiada na mesa, no teclado)
    if (m.plana) {                                                                    // gira a mão no próprio eixo até a palma olhar pra baixo
      const dd = W(B('f_middle.01.' + s)).sub(W(H)).normalize(), v = W(B('f_index.01.' + s)).sub(W(B('f_pinky.01.' + s))); v.addScaledVector(dd, -v.dot(dd));
      const h = new THREE.Vector3(0, 1, 0).cross(dd).normalize(), u2 = dd.clone().cross(h); let ang = Math.atan2(v.dot(u2), v.dot(h)); if (s === 'L') ang += Math.PI;
      m.virar('hand.' + s, dd.toArray(), -ang);
    }
  };
  // guarda/repõe a pose (pra animar por cima a cada quadro): m.guardar() depois de posar; m.repor() no começo do quadro
  let salvo = null; const todos = () => Object.values(m.ossos);
  m.guardar = () => { salvo = todos().map(b => [b, b.quaternion.clone(), b.position.clone()]); };
  m.repor = () => { if (salvo) for (const [b, q, p] of salvo) { b.quaternion.copy(q); b.position.copy(p); } m.obj.updateMatrixWorld(true); };
  m.guardar();
  // gira um osso em torno de um eixo do MUNDO (cabeça olhando de lado, balanço)
  m.virar = (nome, eixo, ang) => { const b = B(nome), pq = b.parent.getWorldQuaternion(new THREE.Quaternion()), wq = b.getWorldQuaternion(new THREE.Quaternion()); b.quaternion.copy(pq.invert().multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(...eixo).normalize(), ang).multiply(wq))); b.updateWorldMatrix(false, true); };
  m.mats = () => m.malhas.flatMap(ml => Array.isArray(ml.material) ? ml.material : [ml.material]);
  return m;
}

// logo da Toca do Anão recolorida pra verde (traço verde em fundo escuro, redonda; fora do círculo é transparente)
export async function logoVerde(tam = 48, fundo = '#0a2413') {
  const img = await M.imagem('material/logo-toca-do-anao.png');
  const c = document.createElement('canvas'); c.width = c.height = tam; const x = c.getContext('2d');
  x.drawImage(img, 0, 0, tam, tam); const d = x.getImageData(0, 0, tam, tam), q = d.data, F = new THREE.Color(fundo), V = new THREE.Color(VERDE);
  for (let i = 0; i < q.length; i += 4) {
    const px = i / 4 % tam, py = Math.floor(i / 4 / tam), rr = Math.hypot(px + .5 - tam / 2, py + .5 - tam / 2) / (tam / 2);
    const lum = (q[i] + q[i + 1] + q[i + 2]) / 765, tinta = rr < .88 ? lum < .45 : rr < .98;
    const k = tinta ? V : F; q[i] = k.r * 255; q[i + 1] = k.g * 255; q[i + 2] = k.b * 255; q[i + 3] = rr < 1 ? 255 : 0;
  }
  x.putImageData(d, 0, 0);
  const t = new THREE.CanvasTexture(c); t.magFilter = t.minFilter = THREE.NearestFilter; t.generateMipmaps = false; t.colorSpace = THREE.NoColorSpace;
  return t;
}

// corpo de moletom: o modelo de terno (sy_boss) repintado — paletó vira moletom azul-acinzentado liso (sem lapela nem botões),
// mãos e pescoço viram pelo, e a cabeça humana é encolhida pra dentro do pescoço (a de caracal entra no lugar).
export async function corpoMoletom(o = {}) {
  const img = await M.imagem('material/modelos/itch/gente/csaf-sy_boss.png'), T = 256;
  const cv = document.createElement('canvas'); cv.width = cv.height = T; const cx = cv.getContext('2d', { willReadFrequently: true });
  cx.drawImage(img, 0, 0); cx.filter = 'blur(2.2px)'; cx.drawImage(img, 14, 8, 150, 138, 14, 8, 150, 138); cx.filter = 'none';     // tronco e mangas: apaga lapela, botões e bolsos
  const d = cx.getImageData(0, 0, T, T), q = d.data, MOL = [0x6a, 0x7a, 0xb2], PELO = [0xc7, 0x9a, 0x62], CAL = [0x30, 0x36, 0x48], R = P.rng(3);
  for (let i = 0; i < q.length; i += 4) {
    const x = i / 4 % T, y = Math.floor(i / 4 / T), r = q[i] / 255, g = q[i + 1] / 255, b = q[i + 2] / 255, lum = .3 * r + .59 * g + .11 * b, sat = Math.max(r, g, b) - Math.min(r, g, b);
    const cabeca = x > 163 && y > 36 && y < 212 && !(x < 200 && y < 64), gola = x > 82 && x < 118 && y > 2 && y < 78;
    let c;
    if (cabeca) c = PELO.map(v => v * .8);
    else if (r > g * 1.18 && g > b && r > .22 && !gola) c = PELO.map(v => v * P.clamp(lum / .42, .6, 1.15));                 // pele → pelo
    else if (y > 148 && y < 216 && sat < .2) c = CAL.map(v => v * P.clamp(lum / .4, .5, 1.3));                              // calça
    else if (y >= 216) c = [q[i] * .8, q[i + 1] * .8, q[i + 2] * .8];                                                         // sapatos
    else c = MOL.map(v => v * P.clamp((gola ? .46 : lum) / .46, .62, 1.18) * (.94 + R() * .12));                             // moletom mesclado (a gola/gravata some)
    for (let k = 0; k < 3; k++) q[i + k] = Math.round(P.clamp(c[k], 0, 255) / 255 * 31) / 31 * 255;
  }
  cx.putImageData(d, 0, 0);
  const tex = new THREE.CanvasTexture(cv); tex.flipY = false; tex.magFilter = tex.minFilter = THREE.NearestFilter; tex.generateMipmaps = false; tex.colorSpace = THREE.NoColorSpace;
  const c = poses(await M.carregar('material/modelos/itch/gente/csaf-sy_boss.glb', { esc: o.esc ?? .9, texMax: 256 }));
  c.mats().forEach(m => { m.uniforms.uMapa.value = tex; m.uniforms.uTemMapa.value = 1; });
  c.osso('head').scale.setScalar(.02); c.guardar();
  return c;
}

// ───────────────────────── IGOR ANÃO ─────────────────────────
// Cabeça de caracal: a foto (material/floppa.jpg) projetada de frente numa cabeça low-poly, pixelada.
// Tudo medido em pixels da foto e depois escalado: centro do rosto (240, 232), largura ~280 px.
const FOTO = { cx: 240, cy: 232, rec: [50, 22, 360, 345], tw: 112, th: 107 };   // recorte [x, y, w, h] → textura tw×th
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
  const k = (o.largura ?? .44) / 280; cab.scale.setScalar(k);

  // corpo: moletom azul-acinzentado, mãos de pelo
  const c = await corpo({ roupa: '#6473a8', mao: '#c79a62', perna: '#2a3040' });     // o corpo aprovado (personagem-simples)
  const g = c.obj;                                   // grupo raiz (escala .85)
  g.scale.x *= 1.14; g.scale.z *= 1.1;             // tronco mais largo, como na foto
  const pesc = new THREE.Group(); pesc.scale.set(1 / g.scale.x, 1 / g.scale.y, 1 / g.scale.z); g.add(pesc); pesc.add(cab);
  // gola e capuz do moletom + microfone de lapela
  const mol = P.mat({ cor: '#56659a' }), molEsc = P.mat({ cor: '#465383' });
  // pescoço de pelo largo (a cabeça nasce dos ombros, como na foto) e gola baixa do moletom
  pesc.add(P.cilindro(.15, .14, .11, matPelo, { seg: 9, pos: [0, .04, .012] }));
  pesc.add(P.tornear([[.118, -.035], [.152, -.022], [.156, .004], [.132, .016]], mol, { seg: 9, pos: [0, 0, .01] }));
  const mic = new THREE.Group();
  mic.add(P.caixa(.022, .034, .02, P.mat({ cor: '#0c0c0e' })), P.caixa(.014, .012, .016, P.mat({ cor: '#3a3d42' }), { pos: [0, .022, .002] }));
  mic.add(P.tubo([[0, -.017, 0], [.012, -.06, .004], [.04, -.1, -.01], [.07, -.16, -.03]], .003, P.mat({ cor: '#0c0c0e' }), { seg: 6, lados: 3 }));
  pesc.add(mic);
  const emblema = P.disco(.036, P.mat({ mapa: await logoVerde(40, '#2c3a66'), semLuz: false }), { seg: 10 }); pesc.add(emblema);

  const I = { obj: g, corpo: c, cabeca: cab, orelhas, pescoco: pesc, mic, tex,
    // posiciona cabeça/gola no osso do pescoço (chame depois de mexer na pose)
    assentar() {
      g.updateMatrixWorld(true);
      const w = new THREE.Vector3(); c.osso('spine.004').getWorldPosition(w); g.worldToLocal(w);
      pesc.position.copy(w); cab.position.set(0, .175, .05); mic.position.set(.075, -.2, .15); emblema.position.set(-.1, -.15, .155); emblema.rotation.set(-.12, -.25, 0);
    },
    // boca (0–1, volume da voz), piscada (0–1), tempo (orelhas e cabeça mexem de leve)
    animar(t, { boca = 0, pisca = 0 } = {}) {
      cx.putImageData(base, 0, 0);
      const F = cv.width / 72, R = v => Math.round(v * F);
      if (pisca > .5) for (const ex of [190, 291]) { const [u, v] = px(ex - 26, 166); cx.fillStyle = '#b08752'; cx.fillRect(Math.round(u), Math.round(v), R(10), R(5)); const [u2, v2] = px(ex - 24, 188); cx.fillStyle = '#3b2a1c'; cx.fillRect(Math.round(u2), Math.round(v2), R(9), Math.max(1, R(.8))); }
      const ab = Math.round(P.clamp(boca) * R(3.4));
      if (ab > 0) { const [u, v] = px(240, 282); cx.fillStyle = '#170b0a'; cx.fillRect(Math.round(u) - R(2.2), Math.round(v), R(4.4), ab); cx.fillRect(Math.round(u) - R(1.4), Math.round(v) + ab, R(2.8), R(.7)); if (ab > R(2)) { cx.fillStyle = '#6b4a44'; cx.fillRect(Math.round(u) - R(1), Math.round(v) + ab - R(.8), R(2), R(.8)); } }
      tex.needsUpdate = true;
      orelhas[0].rotation.z = Math.sin(t * 1.7) * .035 + (Math.sin(t * .9 + 1) > .93 ? .16 : 0);
      orelhas[1].rotation.z = -Math.sin(t * 1.3 + 2) * .035 - (Math.sin(t * .7 + 4) > .95 ? .16 : 0);
      cab.rotation.set(Math.sin(t * .8) * .018 + boca * .03, Math.sin(t * .5) * .04, Math.sin(t * .6 + 1) * .012);
    } };
  return I;
}

// ───────────────────────── PHANTOM ─────────────────────────
// 19 anos, mudo, pele negra, de terno escuro, quase invisível: transparência pontilhada de 1 bit que pulsa + contorno verde fraco.
// Modelo: "sy_boss" (PSX Characters Sampler, Core Systems Asset Factory). A textura é repintada: terno mais escuro,
// gravata verde (o roteiro não tem vermelho), cabelo preto e sem barba (ele tem 19 anos); olhos e boca são redesenhados a cada quadro.
// No atlas o rosto está deitado (testa pra esquerda): olhos em (213, 125) e (213, 137), boca em (230, 131).
export async function phantom(o = {}) {
  const img = await M.imagem('material/modelos/itch/gente/csaf-sy_boss.png'), T = 256;
  const cv = document.createElement('canvas'); cv.width = cv.height = T;
  const cx = cv.getContext('2d', { willReadFrequently: true }); cx.drawImage(img, 0, 0);
  const d = cx.getImageData(0, 0, T, T), q = d.data, PELE = [0x6e, 0x46, 0x33];
  for (let i = 0; i < q.length; i += 4) {
    const x = i / 4 % T, y = Math.floor(i / 4 / T), r = q[i] / 255, g = q[i + 1] / 255, b = q[i + 2] / 255;
    const lum = .3 * r + .59 * g + .11 * b, sat = Math.max(r, g, b) - Math.min(r, g, b), cabeca = x > 163 && y > 36 && y < 212 && !(x < 200 && y < 64), rosto = x >= 194 && x <= 247 && y >= 106 && y <= 156;
    let c = [q[i], q[i + 1], q[i + 2]];
    if (cabeca) {
      if (sat < (rosto ? .2 : .14) && lum > (rosto ? .04 : .28) && !(rosto && x < 216)) {                                              // grisalho → barba some, cabelo fica preto
        c = rosto ? PELE.map(v => v * .94) : [26, 21, 18].map(v => v * (.55 + lum));
      }
    } else if (r > g * 1.5 && r > b * 1.25 && r > .2 && y > 24 && y < 70 && x > 88 && x < 110) c = [0x1c * (lum / .3), 0x9a * (lum / .3), 0x44 * (lum / .3)];   // gravata vinho → verde
    else if (sat < .14 && lum < .72) c = c.map(v => v * .5 + 2);                 // terno cinza → grafite
    for (let k = 0; k < 3; k++) q[i + k] = Math.round(P.clamp(c[k], 0, 255) / 255 * 31) / 31 * 255;
  }
  cx.putImageData(d, 0, 0);
  { const tmp = document.createElement('canvas'); tmp.width = 34; tmp.height = 56; const tx = tmp.getContext('2d'); tx.filter = 'blur(1.2px)'; tx.drawImage(cv, 216, 104, 34, 56, 0, 0, 34, 56); cx.drawImage(tmp, 2, 2, 30, 52, 218, 106, 30, 52); }   // alisa onde estava a barba
  cx.fillStyle = '#4a2c20'; cx.fillRect(230, 126, 1, 10); cx.fillStyle = '#7a4c3a'; cx.fillRect(231, 127, 1, 8);    // boca fechada: linha + lábio de baixo
  const base = cx.getImageData(0, 0, T, T);
  const tex = new THREE.CanvasTexture(cv); tex.flipY = false; tex.magFilter = tex.minFilter = THREE.NearestFilter; tex.generateMipmaps = false; tex.colorSpace = THREE.NoColorSpace;
  const c = poses(await M.carregar('material/modelos/itch/gente/csaf-sy_boss.glb', { esc: o.esc ?? .95, texMax: 256 }));
  const mats = c.mats(); mats.forEach(m => { m.uniforms.uMapa.value = tex; m.uniforms.uTemMapa.value = 1; });
  // contorno: casca um pouco maior, só as faces de trás, verde fraco e também pontilhado
  // (estêncil: a silhueta inteira marca 1; a casca só pinta onde NÃO é silhueta, então nunca risca o rosto por dentro)
  const mascara = P.mat({}); mascara.colorWrite = false; mascara.depthWrite = false; mascara.depthTest = false;
  Object.assign(mascara, { stencilWrite: true, stencilRef: 1, stencilFunc: THREE.AlwaysStencilFunc, stencilZPass: THREE.ReplaceStencilOp, stencilZFail: THREE.ReplaceStencilOp });
  const contorno = P.mat({ cor: VERDE, semLuz: true, lados: THREE.BackSide, inflar: o.contorno ?? .011, pont: .3 });
  Object.assign(contorno, { stencilWrite: true, stencilRef: 1, stencilFunc: THREE.NotEqualStencilFunc, stencilZPass: THREE.KeepStencilOp, stencilFail: THREE.KeepStencilOp, stencilZFail: THREE.KeepStencilOp });
  const limpa = P.mat({}); limpa.colorWrite = false; limpa.depthWrite = false; limpa.depthTest = false;      // zera o estêncil depois (outro fantasma, outra cena)
  Object.assign(limpa, { stencilWrite: true, stencilRef: 0, stencilFunc: THREE.AlwaysStencilFunc, stencilZPass: THREE.ReplaceStencilOp, stencilZFail: THREE.ReplaceStencilOp, uniforms: { ...limpa.uniforms, uInflar: { value: .05 } } });
  for (const ml of [...c.malhas]) {
    if (!ml.isSkinnedMesh) continue;
    ml.renderOrder = 22;
    for (const [mt, ro] of [[mascara, 20], [contorno, 21], [limpa, 23]]) { const k = new THREE.SkinnedMesh(ml.geometry, mt); k.bind(ml.skeleton, ml.bindMatrix); k.frustumCulled = false; k.renderOrder = ro; ml.parent.add(k); }
  }
  const olho = (y0, pisca) => {            // olho bem legível: branco, íris escura, sobrancelha; a pálpebra desce com `pisca`
    cx.fillStyle = '#5c3a2a'; cx.fillRect(211, y0 - 2, 5, 9); cx.fillStyle = '#d2cdbd'; cx.fillRect(212, y0 - 1, 2, 7); cx.fillStyle = '#120a08'; cx.fillRect(212, y0 + 1, 2, 3); cx.fillStyle = '#2a1a12'; cx.fillRect(211, y0 - 1, 1, 7);
    cx.fillStyle = '#20140f'; cx.fillRect(209, y0 - 2, 1, 9);
    const pl = Math.round(P.clamp(pisca) * 3); if (pl > 0) { cx.fillStyle = '#5c3a2a'; cx.fillRect(212, y0 - 2, pl, 9); }
  };
  const F = { obj: c.obj, corpo: c, tex, contorno,
    // boca 0–1 (mexe sem som), pisca 0–1 (pálpebra descendo), pont = quanto dele aparece (0–1)
    animar(t, { boca = 0, pisca = 0, pont } = {}) {
      const v = pont ?? (.36 + .07 * Math.sin(t * 2.1) + .025 * Math.sin(t * 5.3));
      mats.forEach(m => { m.uniforms.uPont.value = v; }); contorno.uniforms.uPont.value = v * .55; contorno.uniforms.uCor.value.set(VERDE).multiplyScalar(.4 + .2 * Math.sin(t * 2.1 + 1));
      cx.putImageData(base, 0, 0); olho(123, pisca); olho(135, pisca);
      const ab = Math.round(P.clamp(boca) * 3);
      if (ab > 0) { cx.fillStyle = '#160b09'; cx.fillRect(230, 128, ab + 1, 7); }
      tex.needsUpdate = true;
    } };
  return F;
}

// maleta preta com linhas verdes finas, como circuito, que pulsam devagar: m.pulsar(t)
// De pé (padrão): base no chão, alça pra cima. m.deitar(k) deita na mesa (alça pra −z, a tampa abre pro lado da câmera);
// m.abrir(a) gira a tampa (rad); m.dentro é o grupo do fundo (pra pôr a fita); m.brilho(k) acende o verde lá dentro.
export function maleta() {
  const g = new THREE.Group(), in_ = new THREE.Group(), w = .46, h = .32, d = .11; g.add(in_);
  const circ = P.textura(64, 64, (x, W, H, r) => {
    x.fillStyle = '#000000'; x.fillRect(0, 0, W, H); x.fillStyle = '#ffffff';
    for (let i = 0; i < 12; i++) { let px = Math.floor(r() * W), py = Math.floor(r() * H); for (let s = 0; s < 4; s++) { const L = 5 + Math.floor(r() * 16); if (s % 2) { x.fillRect(px, py, 1, L); py += L; } else { x.fillRect(px, py, L, 1); px += L; } } x.fillRect(px - 1, py - 1, 2, 2); }
  }, { seed: 21, niveis: 0 });
  const corpoM = P.mat({ cor: '#0b0d0c', interior: '#06140b' }), linhas = P.mat({ mapa: circ, cor: VERDE, aditivo: true, opac: .99, semLuz: true, lados: THREE.DoubleSide });
  const metade = z => { const k = new THREE.Group(); k.add(P.caixa(w, h, d / 2, corpoM, { pos: [0, h / 2, z], sx: 2, sy: 2 }), P.caixa(w + .004, h + .004, d / 2 + .003, linhas, { pos: [0, h / 2, z] })); return k; };
  const fundo = metade(-d / 4), tampa = metade(d / 4); in_.add(fundo, tampa);
  fundo.add(P.caixa(w - .03, h - .03, .004, P.mat({ cor: '#051209', semLuz: true }), { pos: [0, h / 2, .001] }));                 // forro
  for (const s of [-1, 1]) tampa.add(P.caixa(.03, .022, .012, P.mat({ cor: '#7a8580' }), { pos: [s * .13, h - .02, d / 2 + .006] }));   // fechos
  fundo.add(P.tubo([[-.07, h, -.02], [-.06, h + .05, -.02], [.06, h + .05, -.02], [.07, h, -.02]], .009, P.mat({ cor: '#161a18' }), { seg: 8, lados: 4 }));   // alça
  const luzD = P.disco(.3, P.mat({ mapa: P.TEX.disco(), cor: VERDE, opac: 0, aditivo: true, semLuz: true, lados: THREE.DoubleSide }), { seg: 10, pos: [0, h / 2, .03] }); fundo.add(luzD);
  const dentro = new THREE.Group(); dentro.position.set(0, h / 2, .004); fundo.add(dentro);
  Object.assign(g, { alca: h + .05, dentro, tampa, larg: w, alt: h, esp: d,
    pulsar: t => { linhas.uniforms.uCor.value.set(VERDE).multiplyScalar(.35 + .65 * (.5 + .5 * Math.sin(t * 1.6)) ** 2); },
    deitar: k => { in_.rotation.x = -Math.PI / 2 * k; in_.position.y = d / 2 * k; in_.position.z = h / 2 * k; },
    abrir: a => { tampa.rotation.x = a; },
    brilho: k => { luzD.material.uniforms.uOpac.value = .5 * k; } });
  return g;
}
// fita VHS com a logo da Toca do Anão em verde no rótulo (deitada: a face do rótulo olha pra +z)
export async function fitaVHS() {
  const logo = await logoVerde(64, '#0a2413');
  const tx = P.textura(128, 72, (x, W, H) => {
    x.fillStyle = '#2b302d'; x.fillRect(0, 0, W, H); x.fillStyle = '#1b1f1d'; x.fillRect(0, 0, W, 3); x.fillRect(0, H - 3, W, 3);
    x.fillStyle = '#d9e8dc'; x.fillRect(10, 7, 108, 40);                                                                      // rótulo
    x.drawImage(logo.image, 14, 9, 36, 36); x.fillStyle = '#0c3a1c'; for (const y of [15, 23, 31]) x.fillRect(58, y, 52, 2); x.fillStyle = '#1f9a45'; x.fillRect(58, 38, 26, 4);
    x.fillStyle = '#050606'; x.fillRect(26, 52, 26, 14); x.fillRect(76, 52, 26, 14); x.fillStyle = '#59615c'; x.fillRect(34, 56, 10, 6); x.fillRect(84, 56, 10, 6);   // janelas dos carretéis
  }, { niveis: 0 });
  const lado = P.mat({ cor: '#2b302d' });
  return P.caixa(.19, .105, .025, [lado, lado, lado, lado, P.mat({ mapa: tx, semLuz: true, cor: '#d0d0d0' }), lado]);
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
