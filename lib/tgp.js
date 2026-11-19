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
      if (m.torcaoAnte) {                                                             // v4: 70% da torção no antebraço (pronação), o resto no pulso
        const ea = W(B('hand.' + s)).sub(W(B('forearm.' + s))).normalize(); m.virar('forearm.' + s, ea.toArray(), -ang * .7);
        M.apontar(H, B('f_middle.01.' + s), [dir[0], -.04, dir[2]]);
        const dd2 = W(B('f_middle.01.' + s)).sub(W(H)).normalize(), v2 = W(B('f_index.01.' + s)).sub(W(B('f_pinky.01.' + s))); v2.addScaledVector(dd2, -v2.dot(dd2));
        const h2 = new THREE.Vector3(0, 1, 0).cross(dd2).normalize(), u3 = dd2.clone().cross(h2); let a2 = Math.atan2(v2.dot(u3), v2.dot(h2)); if (s === 'L') a2 += Math.PI;
        m.virar('hand.' + s, dd2.toArray(), -a2);
      } else m.virar('hand.' + s, dd.toArray(), -ang);
    }
  };
  // ORIENTA a mão (o "target rotation" do IK): dedos apontam pra `dedos`, o lado do indicador fica pra `indice`.
  // A torção vai `ta` no antebraço (pronação/supinação) e o resto no pulso. Não muda nada se não for chamada (v3 intacta).
  m.orientar = (s, dedos, indice, ta = .75) => {
    const Hh = B('hand.' + s), Mi = B('f_middle.01.' + s), Fo = B('forearm.' + s), W = b => b.getWorldPosition(new THREE.Vector3());
    const D = new THREE.Vector3(...dedos).normalize(), I = new THREE.Vector3(...indice); I.addScaledVector(D, -I.dot(D)).normalize();
    const lado = () => { const v = W(B('f_index.01.' + s)).sub(W(B('f_pinky.01.' + s))); return v.addScaledVector(D, -v.dot(D)).normalize(); };
    m.obj.updateMatrixWorld(true); M.apontar(Hh, Mi, D.toArray());
    let v = lado(), a = Math.atan2(v.clone().cross(I).dot(D), v.dot(I));
    m.virar('forearm.' + s, W(Hh).sub(W(Fo)).normalize().toArray(), a * ta); M.apontar(Hh, Mi, D.toArray());
    v = lado(); a = Math.atan2(v.clone().cross(I).dot(D), v.dot(I)); m.virar('hand.' + s, D.toArray(), a);
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

// ───────────────────────── DOM ─────────────────────────
// Homem de uns 50 anos com chapéu cônico laranja e branco (火 na frente), véu branco caindo nos ombros, casaco branco
// de gola alta por cima de uma blusa preta de zíper, fivela laranja. Rosto: a foto (material/dom/dom.jpg) projetada
// de frente numa cabeça low-poly, pixelada (mesmo método do Igor). Medidas em px da foto: centro do rosto (362, 285).
const FOTO_DOM = { cx: 362, cy: 285, rec: [228, 150, 274, 282], tw: 88, th: 92 };
function chapeuTex() {                          // cone: u dá a volta (u=.5 = frente, depois de girar π), v sobe da aba à ponta
  return P.textura(128, 32, (x, w, h) => {
    x.fillStyle = '#e8711d'; x.fillRect(0, 0, w, h);
    x.fillStyle = '#ece8df'; x.beginPath(); x.moveTo(w * .5, 0); x.lineTo(w * .36, h); x.lineTo(w * .64, h); x.closePath(); x.fill();   // painel branco da frente
    x.fillRect(0, h - 3, w, 3);                                                                                                    // borda branca da aba
    x.strokeStyle = '#e8711d'; x.lineWidth = 2.2; x.lineCap = 'square';                                                          // 火 desenhado em traços
    const cx = w * .5, cy = h * .58, k = 4.2;
    x.beginPath(); x.moveTo(cx, cy - 2.2 * k); x.lineTo(cx, cy + .3 * k); x.lineTo(cx - 2.1 * k, cy + 2.4 * k); x.moveTo(cx, cy + .3 * k); x.lineTo(cx + 2.1 * k, cy + 2.4 * k);
    x.moveTo(cx - 1.9 * k, cy - 1.4 * k); x.lineTo(cx - 1.3 * k, cy - .2 * k); x.moveTo(cx + 1.9 * k, cy - 1.5 * k); x.lineTo(cx + 1.2 * k, cy - .3 * k); x.stroke();
  }, { seed: 4 });
}
// ROSTO PLANO do Dom (estilo PS1, como as caras chapadas dos jogos): uma placa quase plana com a foto recortada justa
// (testa → queixo, bochecha → bochecha) preenchendo tudo. Usa a foto já alinhada (olhos nivelados): material/dom/rosto_alinhado.png
export async function rostoPlanoDom(o = {}) {
  const foto = await M.imagem('material/dom/rosto_alinhado.png'), R = o.recorte ?? [382, 318, 192, 222], TW = 72, TH = Math.round(72 * R[3] / R[2]);
  const cv = document.createElement('canvas'); cv.width = TW; cv.height = TH;
  const cx = cv.getContext('2d', { willReadFrequently: true }); cx.filter = 'contrast(1.18) saturate(1.1)'; cx.drawImage(foto, R[0], R[1], R[2], R[3], 0, 0, TW, TH); cx.filter = 'none';
  const base = cx.getImageData(0, 0, TW, TH);
  for (let i = 0; i < base.data.length; i += 4) for (let k = 0; k < 3; k++) base.data[i + k] = Math.round(Math.round(base.data[i + k] / 255 * 31) / 31 * 255);
  cx.putImageData(base, 0, 0);
  const tex = new THREE.CanvasTexture(cv); tex.magFilter = tex.minFilter = THREE.NearestFilter; tex.generateMipmaps = false; tex.colorSpace = THREE.NoColorSpace;
  const L = o.largura ?? .16, H = L * R[3] / R[2], geo = new THREE.CircleGeometry(1, 20), ps = geo.attributes.position, uvA = geo.attributes.uv;   // contorno OVAL (como as caras chapadas de PS1)
  for (let i = 0; i < ps.count; i++) { let x = ps.getX(i), y = ps.getY(i); const sq = 1 + .18 * (1 - Math.abs(y)) * Math.abs(x);   // oval um pouco quadrado nas bochechas
    x = Math.max(-1, Math.min(1, x * sq)); uvA.setXY(i, (x + 1) / 2, (y + 1) / 2); ps.setXYZ(i, x * L / 2, y * H / 2, 0); }
  for (let i = 0; i < ps.count; i++) { const x = ps.getX(i) / (L / 2), y = ps.getY(i) / (H / 2); ps.setZ(i, -(x * x) * L * (o.curva ?? .12) - (y < 0 ? y * y : 0) * L * .05); }   // quase plana: só as bordas recuam um pouco
  geo.computeVertexNormals();
  const cab = new THREE.Group(), face = new THREE.Mesh(geo, P.mat({ mapa: tex })); cab.add(face);
  const px = (x, y) => [(x - R[0]) / R[2] * TW, (y - R[1]) / R[3] * TH];     // px da foto alinhada → textura
  const animar = (t, { boca = 0, pisca = 0 } = {}) => {
    cx.putImageData(base, 0, 0);
    if (pisca > .5) for (const ex of [435, 521]) { const [u, v] = px(ex - 13, 372); cx.fillStyle = '#8a5f48'; cx.fillRect(Math.round(u), Math.round(v), Math.round(26 / R[2] * TW), Math.round(10 / R[3] * TH)); }
    const ab = Math.round(P.clamp(boca) * 3); if (ab > 0) { const [u, v] = px(472, 466); cx.fillStyle = '#241210'; cx.fillRect(Math.round(u), Math.round(v), Math.round(32 / R[2] * TW), ab); }
    tex.needsUpdate = true; };
  return { cab, kc: 1, RY: H / 2, tex, animar, L, H };
}

// cabeça do Dom (a foto projetada na frente de uma cabeça low-poly): usada no primeiro modelo e no "Frankenstein" (corpo do elenco)
export async function cabecaDom(o = {}) {
  const foto = await M.imagem('material/dom/dom.jpg'), F = FOTO_DOM, [rx, ry, rw, rh] = F.rec;
  const cv = document.createElement('canvas'); cv.width = F.tw; cv.height = F.th;
  const cx = cv.getContext('2d', { willReadFrequently: true }); cx.filter = 'contrast(1.15) saturate(1.1)'; cx.drawImage(foto, rx, ry, rw, rh, 0, 0, cv.width, cv.height); cx.filter = 'none';
  const base = cx.getImageData(0, 0, cv.width, cv.height);
  for (let i = 0; i < base.data.length; i += 4) for (let k = 0; k < 3; k++) base.data[i + k] = Math.round(Math.round(base.data[i + k] / 255 * 31) / 31 * 255);   // cor de 15 bits
  cx.putImageData(base, 0, 0);
  const tex = new THREE.CanvasTexture(cv); tex.magFilter = tex.minFilter = THREE.NearestFilter; tex.generateMipmaps = false; tex.colorSpace = THREE.NoColorSpace;
  const px = (x, y) => [(x - rx) / rw * cv.width, (y - ry) / rh * cv.height];
  const uvDe = (x, y) => [(F.cx + x - rx) / rw, 1 - (F.cy - y - ry) / rh];
  const PELE = '#b98466', CABELO = '#2a2420';
  const matFoto = P.mat({ mapa: tex }), matCabelo = P.mat({ cor: CABELO }), matPele = P.mat({ cor: PELE });

  // CABEÇA humana: esfera alongada, nariz e queixo; frente = foto, trás = cabelo
  const cab = new THREE.Group(), RX = 108, RY = 128, RZ = 112;
  const gi0 = new THREE.SphereGeometry(1, 12, 10), pi = gi0.attributes.position;
  for (let i = 0; i < pi.count; i++) {
    let x = pi.getX(i) * RX, y = pi.getY(i) * RY, z = pi.getZ(i) * RZ;
    if (z > 0) { z += 26 * Math.exp(-((x / 22) ** 2)) * Math.exp(-(((y + 2) / 30) ** 2)); z += 8 * Math.exp(-((x / 40) ** 2)) * Math.exp(-(((y + 110) / 26) ** 2)); }   // nariz · queixo
    if (y < -40) { const q = Math.min(1, (-40 - y) / 90); x *= 1 - .22 * q; z *= 1 - .1 * q; }                                      // mandíbula afinando
    if (Math.abs(x) > 70 && y > -30 && y < 50 && z > 0) z *= .9;                                                                   // têmporas
    pi.setXYZ(i, x, y, z);
  }
  gi0.computeVertexNormals();
  const g0 = gi0.toNonIndexed(), p = g0.attributes.position, nn = g0.attributes.normal, ord = [[], []], nor = [[], []];
  for (let t = 0; t < p.count; t += 3) {
    const zc = (p.getZ(t) + p.getZ(t + 1) + p.getZ(t + 2)) / 3, yc = (p.getY(t) + p.getY(t + 1) + p.getY(t + 2)) / 3, xc = (p.getX(t) + p.getX(t + 1) + p.getX(t + 2)) / 3, gi = zc > -10 && yc < 105 ? 0 : 1;
    if (o.soFrente && !(zc > 18 && yc < 100 && Math.abs(xc) < 96)) continue;      // só a FRENTE do rosto (máscara): da orelha pra trás fica a cabeça do corpo
    if (o.meiaFrente && zc < (o.corteZ ?? -4)) continue;                          // METADE DA FRENTE (cabelo da testa + rosto): da linha das orelhas pra trás fica a cabeça do corpo
    for (let k = 0; k < 3; k++) { ord[gi].push(p.getX(t + k), p.getY(t + k), p.getZ(t + k)); nor[gi].push(nn.getX(t + k), nn.getY(t + k) * .5 + .2, nn.getZ(t + k)); }
  }
  const todos = [...ord[0], ...ord[1]], uvs = [];
  for (let i = 0; i < todos.length; i += 3) uvs.push(...uvDe(todos[i] * .97, todos[i + 1] * .97));
  const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.Float32BufferAttribute(todos, 3)); geo.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
  geo.setAttribute('normal', new THREE.Float32BufferAttribute([...nor[0], ...nor[1]], 3)); geo.addGroup(0, ord[0].length / 3, 0); geo.addGroup(ord[0].length / 3, ord[1].length / 3, 1);
  cab.add(new THREE.Mesh(geo, [matFoto, matCabelo]));
  if (!o.soFrente && !o.meiaFrente) for (const sx of [-1, 1]) cab.add(P.esfera(1, matPele, { seg: 6, pos: [sx * 112, -8, -6], esc: [12, 26, 16] }));                // orelhas
  const kc = (o.largura ?? .17) / 216; cab.scale.setScalar(kc);

  const animar = (t, { boca = 0, pisca = 0 } = {}) => {
    cx.putImageData(base, 0, 0); const W = cv.width / 274;
    if (pisca > .5) for (const [ex, ey] of [[307, 231], [407, 217]]) { const [u, v] = px(ex - 14, ey - 6); cx.fillStyle = '#8a5f48'; cx.fillRect(Math.round(u), Math.round(v), Math.round(28 * W), Math.round(11 * W)); }
    const ab = Math.round(P.clamp(boca) * 3);
    if (ab > 0) { const [u, v] = px(352, 324); cx.fillStyle = '#241210'; cx.fillRect(Math.round(u), Math.round(v), Math.round(36 * W), ab); }
    tex.needsUpdate = true; };
  return { cab, kc, RY, tex, animar, matPele };
}
export async function dom(o = {}) {
  const { cab, kc, RY, tex, animar: animarCab, matPele } = await cabecaDom(o);
  // CHAPÉU cônico (kasa) + VÉU branco caindo nos ombros (aberto na frente)
  const chapeu = new THREE.Group();
  const cone = P.cilindro(0, .31, .15, P.mat({ mapa: chapeuTex(), lados: THREE.DoubleSide }), { seg: 16, pos: [0, .075, 0], rot: [0, Math.PI, 0] }); chapeu.add(cone);
  chapeu.add(P.cilindro(.31, .312, .012, P.mat({ cor: '#ece8df', lados: THREE.DoubleSide }), { seg: 16, pos: [0, -.002, 0] }));                   // aba
  chapeu.add(P.cilindro(.014, .014, .006, P.mat({ cor: '#c9c4b8' }), { seg: 6, pos: [.25, .012, .16], rot: [Math.PI / 2, 0, .6] }));                                                         // argola do lado
  const veuTex = P.textura(64, 32, (x, w, h, r) => { for (let i = 0; i < w; i++) { const v = 215 + 30 * Math.sin(i * .55) + 10 * Math.sin(i * 1.7) + (r() - .5) * 8; x.fillStyle = `rgb(${v},${v - 2},${v - 6})`; x.fillRect(i, 0, 1, h); } }, { seed: 8 });
  const veu = new THREE.Mesh(new THREE.CylinderGeometry(.165, .27, .46, 14, 3, true, Math.PI / 2 + .72, Math.PI * 2 - 1.44), P.mat({ mapa: veuTex, lados: THREE.DoubleSide }));
  veu.position.set(0, -.22, -.02); veu.rotation.y = -Math.PI / 2; chapeu.add(veu);                // abertura na frente (+z)

  // CORPO: casaco branco, mãos de pele, calça escura
  const c = await corpo({ roupa: '#d9d5cc', mao: '#b98466', perna: '#26272c', pe: '#1a1a1d' });
  const g = c.obj; g.scale.x *= 1.05;
  const pesc = new THREE.Group(); pesc.scale.set(1 / g.scale.x, 1 / g.scale.y, 1 / g.scale.z); g.add(pesc);
  pesc.add(P.cilindro(.05, .056, .08, matPele, { seg: 8, pos: [0, .045, .0] }));                                                           // pescoço
  const branco = P.mat({ cor: '#dedad1', lados: THREE.DoubleSide }), preto = P.mat({ cor: '#141416' }), laranja = P.mat({ cor: '#e8711d' });
  // gola alta do casaco (aberta na frente) + blusa preta de zíper aparecendo no decote + fivela laranja
  pesc.add(new THREE.Mesh(new THREE.CylinderGeometry(.115, .135, .13, 12, 1, true, Math.PI / 2 + .55, Math.PI * 2 - 1.1), branco).rotateY(-Math.PI / 2));
  pesc.add(P.cilindro(.07, .085, .09, preto, { seg: 8, pos: [0, -.005, .01] }));                                                         // gola da blusa preta
  pesc.add(P.caixa(.12, .2, .02, preto, { pos: [0, -.14, .1] }), P.caixa(.006, .2, .022, P.mat({ cor: '#8a8c90' }), { pos: [0, -.14, .112] }));   // peito preto + zíper
  pesc.add(P.caixa(.07, .022, .02, laranja, { pos: [0, -.25, .118] }), P.caixa(.022, .03, .022, laranja, { pos: [-.02, -.25, .12] }), P.caixa(.022, .03, .022, laranja, { pos: [.02, -.25, .12] }));
  pesc.add(cab, chapeu);
  // parte de baixo do casaco: longa até os joelhos, aberta na frente
  const saia = new THREE.Mesh(new THREE.CylinderGeometry(.155, .235, .72, 12, 3, true, Math.PI / 2 + .3, Math.PI * 2 - .6), branco); saia.rotation.y = -Math.PI / 2;
  const saiaG = new THREE.Group(); saiaG.add(saia); saia.position.y = -.36; g.add(saiaG); saiaG.scale.set(1 / g.scale.x, 1 / g.scale.y, 1 / g.scale.z);

  const D = { obj: g, corpo: c, cabeca: cab, chapeu, veu, pescoco: pesc, tex, casaco: saiaG,
    assentar() {
      g.updateMatrixWorld(true);
      const w = new THREE.Vector3(); c.osso('spine.004').getWorldPosition(w); g.worldToLocal(w); pesc.position.copy(w);
      cab.position.set(0, .162, .025); chapeu.position.set(0, .162 + RY * kc * .8, .0); chapeu.rotation.x = -.06;
      const q2 = new THREE.Vector3(); c.osso('spine').getWorldPosition(q2); g.worldToLocal(q2); saiaG.position.set(q2.x, q2.y + .2, q2.z);
    },
    animar(t, { boca = 0, pisca = 0 } = {}) {
      animarCab(t, { boca, pisca });
      cab.rotation.set(Math.sin(t * .7) * .015 + boca * .03, Math.sin(t * .45) * .05, Math.sin(t * .6) * .01);
      veu.rotation.z = Math.sin(t * .9) * .015;
    } };
  D.assentar();
  return D;
}

// Dom no MESMO modelo base do elenco (JashiPSX, E4.ator('dom')): chapéu cônico + véu presos ao osso da cabeça
// (acompanham andar, falar, sentar...). Roupa e rosto estão na textura (tools/pintar_jashi_vasco.py ROUPA=dom).
export async function acessoriosDom(A, o = {}) {
  A.obj.updateMatrixWorld(true);
  const cab = A.osso('spine.005'); let topo = new THREE.Box3().setFromObject(A.obj).max.y, c = cab.getWorldPosition(new THREE.Vector3());
  // "Frankenstein": a cabeça do corpo do elenco some e entra a cabeça da FOTO (a do primeiro modelo), presa ao mesmo osso
  let rosto = null;
  const malhaCab = o.cabecaOriginal ? null : A.malhas.find(m => /head/i.test(m.name) && m.isSkinnedMesh);
  if (malhaCab) {
    malhaCab.computeBoundingBox(); const bb = malhaCab.boundingBox.clone().applyMatrix4(malhaCab.matrixWorld), cen = bb.getCenter(new THREE.Vector3()), tam = bb.getSize(new THREE.Vector3());
    // padrão (escolha do diretor): a FRENTE da cabeça do primeiro modelo (cabelo da testa + rosto da foto); da linha das orelhas pra trás
    // (nuca, cabelo de trás, orelhas) é a cabeça do corpo do elenco. ?cabeca=inteira (cabeça toda do 1º) · ?cabeca=mascara (só o rosto)
    const mascara = o.cabeca === 'mascara', inteira = o.cabeca === 'inteira', meia = o.cabeca === 'meia', plano = !mascara && !inteira && !meia;
    // padrão: ROSTO PLANO (placa com a foto preenchendo a frente, estilo PS1) na frente da cabeça do elenco
    rosto = plano ? await rostoPlanoDom({ largura: tam.x * (o.escRosto ?? .9) })
      : await cabecaDom({ largura: (meia ? tam.x : Math.min(tam.x, tam.z)) * (o.escRosto ?? (mascara ? .95 : meia ? .94 : .98)), soFrente: mascara, meiaFrente: meia, corteZ: o.corteZ ?? 10 });
    rosto.cab.position.copy(cen).add(new THREE.Vector3(0, o.dy ?? (plano ? -.03 : mascara ? -.022 : -.012), 0).add(new THREE.Vector3(Math.sin(A.obj.rotation.y), 0, Math.cos(A.obj.rotation.y)).multiplyScalar(o.dz ?? (plano ? tam.z * .5 + .006 : mascara ? .035 : meia ? .03 : .012))));
    rosto.cab.rotation.y = A.obj.rotation.y; A.obj.parent.add(rosto.cab); cab.attach(rosto.cab);
    if (inteira) malhaCab.visible = false;   /* cabeça inteira do 1º: a do corpo some */
    if (!mascara && !plano) topo = cen.y + rosto.RY * rosto.kc + .04;
    c = cen;
  }
  const g = new THREE.Group(); g.position.set(c.x, topo - .045, c.z + .005); A.obj.parent.add(g);
  g.add(P.cilindro(0, .31, .15, P.mat({ mapa: chapeuTex(), lados: THREE.DoubleSide }), { seg: 16, pos: [0, .075, 0], rot: [0, Math.PI, 0] }));
  g.add(P.cilindro(.31, .312, .012, P.mat({ cor: '#ece8df', lados: THREE.DoubleSide }), { seg: 16, pos: [0, -.002, 0] }));
  g.add(P.cilindro(.014, .014, .006, P.mat({ cor: '#c9c4b8' }), { seg: 6, pos: [.25, .012, .16], rot: [Math.PI / 2, 0, .6] }));
  const veuTex = P.textura(64, 32, (x, w, h, r) => { for (let i = 0; i < w; i++) { const v = 215 + 30 * Math.sin(i * .55) + 10 * Math.sin(i * 1.7) + (r() - .5) * 8; x.fillStyle = `rgb(${v},${v - 2},${v - 6})`; x.fillRect(i, 0, 1, h); } }, { seed: 8 });
  const veu = new THREE.Mesh(new THREE.CylinderGeometry(.15, .26, .44, 14, 3, true, Math.PI / 2 + .72, Math.PI * 2 - 1.44), P.mat({ mapa: veuTex, lados: THREE.DoubleSide }));
  veu.position.set(0, -.22, -.02); veu.rotation.y = -Math.PI / 2; g.add(veu);
  g.rotation.y = A.obj.rotation.y; cab.attach(g);                                  // a partir daqui segue a cabeça
  // CAPA de Hokage: branca, chamas AMARELAS na barra, "小人の隠れ家" (Toca do Anão) na vertical nas costas + gola alta
  const capaTex = P.textura(256, 384, (x, w, h, r) => {
    x.fillStyle = '#ece8de'; x.fillRect(0, 0, w, h);
    for (let i = 0; i < w; i += 2) { const k = .5 + .5 * Math.sin(i * .21) * Math.sin(i * .053 + 1); x.fillStyle = `rgba(150,140,120,${.08 * k})`; x.fillRect(i, 0, 2, h); }   // dobras
    const AM = '#f0c020', AM2 = '#c98a10', base = h * .86;
    x.fillStyle = AM; x.fillRect(0, base, w, h - base);
    for (let i = -1; i < 13; i++) {                                                   // línguas de fogo subindo da barra
      const cx = (i + .5) * w / 12 + (r() - .5) * 6, alt = h * (.1 + .08 * r()), lg = w / 12 * .55;
      x.beginPath(); x.moveTo(cx - lg, base + 2); x.quadraticCurveTo(cx - lg * .8, base - alt * .5, cx + lg * .3 * (r() < .5 ? -1 : 1), base - alt);
      x.quadraticCurveTo(cx + lg * .4, base - alt * .45, cx + lg, base + 2); x.closePath(); x.fill();
    }
    x.fillStyle = '#ece8de';                                                          // chamas brancas por dentro (como na capa da referência)
    for (let i = 0; i < 12; i++) { const cx = (i + .5) * w / 12 + 4, lg = w / 12 * .22, alt = h * .06;
      x.beginPath(); x.moveTo(cx - lg, h - 4); x.quadraticCurveTo(cx - lg, h - alt * .6, cx, h - alt); x.quadraticCurveTo(cx + lg * .5, h - alt * .5, cx + lg, h - 4); x.closePath(); x.fill(); }
    x.strokeStyle = AM2; x.lineWidth = 1; x.strokeRect(0, base, w, 1);
    x.fillStyle = '#a8740c'; x.font = 'bold 30px IPAGothic, "WenQuanYi Zen Hei", sans-serif'; x.textAlign = 'center'; x.textBaseline = 'top';
    [...'小人の隠れ家'].forEach((ch, i) => x.fillText(ch, w * .5, 26 + i * 33));         // vertical, no meio das costas
  }, { seed: 12 });
  const capaMat = P.mat({ mapa: capaTex, lados: THREE.DoubleSide }), VAO = 1.25;
  const capa = new THREE.Mesh(new THREE.CylinderGeometry(.2, .34, 1.02, 20, 4, true, Math.PI / 2 + VAO / 2, Math.PI * 2 - VAO), capaMat);
  capa.rotation.y = -Math.PI / 2;
  const tronco = A.osso('spine.003'), pt = tronco.getWorldPosition(new THREE.Vector3()), capaG = new THREE.Group();
  capaG.position.set(pt.x, pt.y + .08 - .51, pt.z - .02); capaG.rotation.y = A.obj.rotation.y; capaG.add(capa); A.obj.parent.add(capaG); tronco.attach(capaG);
  const gola = new THREE.Mesh(new THREE.CylinderGeometry(.1, .12, .1, 14, 1, true, Math.PI / 2 + .45, Math.PI * 2 - .9), P.mat({ cor: '#ece8de', lados: THREE.DoubleSide }));
  gola.rotation.y = -Math.PI / 2; const pesc = A.osso('spine.004'), pp = pesc.getWorldPosition(new THREE.Vector3()), golaG = new THREE.Group();
  golaG.position.set(pp.x, pp.y + .01, pp.z - .005); golaG.rotation.y = A.obj.rotation.y; golaG.add(gola); A.obj.parent.add(golaG); pesc.attach(golaG);
  if (o.semVeu) { g.visible = false; capaG.visible = false; }                    // inspeção da cabeça (sem chapéu, véu e capa)
  return { chapeu: g, veu, rosto, atualizar: (t, f = {}) => { veu.rotation.z = Math.sin(t * .9) * .015; rosto?.animar(t, f); } };
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
    if (cabeca) {                                                                 // só o grisalho muda: cabelo e barba ficam pretos; o rosto original fica como é
      const barba = x >= 220 && x <= 248 && y >= 106 && y <= 154;
      if (sat < (barba ? .16 : .105) && lum > (barba ? .38 : .3)) { const olho = Math.abs(x - 213) <= 3 && (Math.abs(y - 125) <= 4 || Math.abs(y - 137) <= 4); if (!olho) c = [30, 24, 20].map(v => v * (.5 + lum * .9)); }
    } else if (r > g * 1.5 && r > b * 1.25 && r > .2 && y > 24 && y < 70 && x > 88 && x < 110) c = [0x1c * (lum / .3), 0x9a * (lum / .3), 0x44 * (lum / .3)];   // gravata vinho → verde
    else if (sat < .14 && lum < .72) c = c.map(v => v * .5 + 2);                 // terno cinza → grafite
    for (let k = 0; k < 3; k++) q[i + k] = Math.round(P.clamp(c[k], 0, 255) / 255 * 31) / 31 * 255;
  }
  cx.putImageData(d, 0, 0);
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
  const olho = (y0, pisca) => {            // os olhos são os do modelo; aqui só a pálpebra desce com `pisca`
    const pl = Math.round(P.clamp(pisca) * 4); if (pl > 0) { cx.fillStyle = '#4e3024'; cx.fillRect(211, y0 - 2, pl, 9); }
  };
  const F = { obj: c.obj, corpo: c, tex, contorno,
    // boca 0–1 (mexe sem som), pisca 0–1 (pálpebra descendo), pont = quanto dele aparece (0–1)
    animar(t, { boca = 0, pisca = 0, pont } = {}) {
      const v = pont ?? (.36 + .07 * Math.sin(t * 2.1) + .025 * Math.sin(t * 5.3));
      mats.forEach(m => { m.uniforms.uPont.value = v; }); contorno.uniforms.uPont.value = v * .55; contorno.uniforms.uCor.value.set(VERDE).multiplyScalar(.4 + .2 * Math.sin(t * 2.1 + 1));
      cx.putImageData(base, 0, 0); olho(123, pisca); olho(135, pisca);
      const ab = Math.round(P.clamp(boca) * 3);
      if (ab > 0) { cx.fillStyle = '#160b09'; cx.fillRect(229, 128, ab, 6); }
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
