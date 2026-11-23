// ───────────────────────── DOD ─────────────────────────
// Gato preto do meme (material/dod/dod.jpg) feito DO MESMO JEITO do Igor (Floppa): a foto projetada de frente numa cabeça
// low-poly, pixelada, em corpo de gente. O topo do crânio é o CÉREBRO exposto (cúpula com a textura do cérebro da foto).
// A BOCA da foto é um borrão: ela é redesenhada em pixel (focinho branco, nariz rosa, "ω" dos lábios, boca entreaberta com a língua).
// Corpo: o MESMO do Igor (o primeiro modelo), de FARDA militar verde-oliva escuro, colete, cinto, luvas e coturno pretos e a
// bandeira de Israel pequena no braço ESQUERDO. ?corpo=gato: o corpo de pelo. Medidas em px da foto (720×720).
const FOTO_DOD = { cx: 365, cy: 400, rec: [110, 130, 600, 470], tw: 240, th: 188, cer: [383, 265, 112, 45], boca: [356, 498] };   // cer: centro x, y, meia-largura, meia-altura do cérebro
export async function cabecaDod(o = {}) {
  const foto = await M.imagem('material/dod/dod.jpg'), F = FOTO_DOD, [rx, ry, rw, rh] = F.rec;
  const cv = document.createElement('canvas'); cv.width = F.tw; cv.height = F.th;
  const cx = cv.getContext('2d', { willReadFrequently: true });
  cx.filter = 'brightness(1.4) contrast(1.25)'; cx.drawImage(foto, rx, ry, rw, rh, 0, 0, cv.width, cv.height);
  { const [ux, uy] = [(F.cer[0] - rx) / rw * cv.width, (F.cer[1] - ry) / rh * cv.height];                // o cérebro com mais contraste (as dobras aparecem)
    cx.save(); cx.beginPath(); cx.ellipse(ux, uy, F.cer[2] / rw * cv.width * 1.05, F.cer[3] / rh * cv.height * 1.2, 0, 0, Math.PI * 2); cx.clip();
    cx.filter = 'brightness(1.05) contrast(1.6) saturate(1.3)'; cx.drawImage(foto, rx, ry, rw, rh, 0, 0, cv.width, cv.height); cx.restore(); }
  cx.filter = 'none';
  const base = cx.getImageData(0, 0, cv.width, cv.height), q = base.data, rr = P.rng(4);
  for (let i = 0; i < q.length; i += 4) {
    const r = q[i] / 255, g = q[i + 1] / 255, b = q[i + 2] / 255, lum = .3 * r + .59 * g + .11 * b, sat = Math.max(r, g, b) - Math.min(r, g, b);
    let c = [r, g, b];
    if (r < b + .1) {                                                           // tudo que não é quente (roxo, azul, magenta) = luz do fundo do meme
      if (b >= r && lum > .3 && sat > .28) { const v = .09 + rr() * .03; c = [v, v * .95, v * 1.08]; }   // o fundo em si vira pelo preto
      else { const v = lum; c = [v, v * .98, v * 1.03]; }                       // reflexo no pelo: tira a cor (o gato é preto e branco)
    }                                                                            // quentes ficam: olhos âmbar, nariz, língua, cérebro
    for (let k = 0; k < 3; k++) q[i + k] = Math.round(Math.round(P.clamp(c[k]) * 31) / 31 * 255);                                   // cor de 15 bits
  }
  // BOCA redesenhada em pixel (referência: gato de boca aberta). Tudo em px da foto; cada texel é testado pelo centro.
  const S = cv.width / rw, [mx, my] = F.boca, LIN = .62 / S, B = 1.3;      // B: a boca desenhada é 30% maior que a da foto (aparece de longe)
  const pintar = (x0, y0, x1, y1, f, img = base) => {
    const u0 = Math.floor((x0 - rx) * S), u1 = Math.ceil((x1 - rx) * S), v0 = Math.floor((y0 - ry) * S), v1 = Math.ceil((y1 - ry) * S);
    for (let v = v0; v <= v1; v++) for (let u = u0; u <= u1; u++) {
      const X = rx + (u + .5) / S, Y = ry + (v + .5) / S, c = f(X, Y); if (!c) continue;
      const j = (v * cv.width + u) * 4; img.data[j] = c[0]; img.data[j + 1] = c[1]; img.data[j + 2] = c[2];
    } };
  const el = (X, Y, ex, ey, ax, ay) => ((X - ex) / ax) ** 2 + ((Y - ey) / ay) ** 2;
  // focinho branco: as duas almofadas dos bigodes + o queixo
  pintar(mx - 60 * B, my - 22 * B, mx + 60 * B, my + 40 * B, (X, Y) => {
    const d = Math.min(el(X, Y, mx - 24 * B, my + 4 * B, 30 * B, 19 * B), el(X, Y, mx + 24 * B, my + 4 * B, 30 * B, 19 * B), el(X, Y, mx, my + 22 * B, 26 * B, 16 * B));
    if (d > 1) return null; const sombra = Y > my + 14 * B ? .86 : 1, v = (d > .7 ? 196 : 228) * sombra; return [v, v * .97, v * .95];
  });
  for (const s of [-1, 1]) for (let k = 0; k < 3; k++) {                      // pontinhos dos bigodes
    const bx = mx + s * (18 + k * 9) * B, by = my + (2 + (k % 2) * 6) * B; pintar(bx - 2, by - 2, bx + 2, by + 2, (X, Y) => el(X, Y, bx, by, 1.6, 1.6) < 1 ? [120, 112, 112] : null);
  }
  // nariz rosa (triângulo com a ponta pra baixo) + brilho
  pintar(mx - 16 * B, my - 22 * B, mx + 16 * B, my - 4 * B, (X, Y) => { const t = (Y - (my - 20 * B)) / (15 * B); if (t < 0 || t > 1) return null; const meia = (13 * (1 - t) + 1.5) * B; if (Math.abs(X - mx) > meia) return null; return t < .25 && X < mx ? [236, 160, 168] : Math.abs(X - mx) > meia - LIN ? [150, 70, 82] : [212, 118, 130]; });
  // risco do nariz até a boca + o "ω" dos lábios
  pintar(mx - 30 * B, my - 6 * B, mx + 30 * B, my + 14 * B, (X, Y) => {
    if (Math.abs(X - mx) < LIN * .8 && Y > my - 6 * B && Y < my + 4 * B) return [46, 24, 28];
    for (const s of [-1, 1]) { const d = Math.hypot(X - (mx + s * 11 * B), Y - (my + 3 * B)); if (Y > my + 2 * B && Math.abs(d - 11 * B) < LIN) return [46, 24, 28]; }
    return null;
  });
  cx.putImageData(base, 0, 0);
  const comBoca = cx.getImageData(0, 0, cv.width, cv.height);
  const tex = new THREE.CanvasTexture(cv); tex.magFilter = tex.minFilter = THREE.NearestFilter; tex.generateMipmaps = false; tex.colorSpace = THREE.NoColorSpace;
  const px = (x, y) => [(x - rx) / rw * cv.width, (y - ry) / rh * cv.height];
  const uvDe = (x, y) => [(F.cx + x - rx) / rw, 1 - (F.cy - y - ry) / rh];
  const uvCer = (x, z) => [(F.cer[0] + x - rx) / rw, 1 - (F.cer[1] + z * (F.cer[3] / 100) - ry) / rh];      // cérebro visto de cima: frente (z+) = parte de baixo da elipse da foto

  const PRETO = '#1c1a20';
  const matFoto = P.mat({ mapa: tex, lados: THREE.DoubleSide });
  const matPelo = P.mat({ cor: PRETO, mapa: P.textura(16, 16, (x, w, h, r) => { x.fillStyle = '#ffffff'; x.fillRect(0, 0, w, h); for (let i = 0; i < 60; i++) { x.fillStyle = r() < .5 ? '#bdb6c4' : '#ffffff'; x.fillRect(Math.floor(r() * w), Math.floor(r() * h), 1, 2); } }), rep: [3, 3] });
  const matOrelha = P.mat({ cor: '#141217', lados: THREE.DoubleSide }), matDentro = P.mat({ cor: '#3a2430', lados: THREE.DoubleSide });

  const cab = new THREE.Group();
  // CRÂNIO: largo e achatado como o do meme, focinho pra frente, topo cortado reto (ali entra o cérebro)
  const RX = 215, RY = 165, RZ = 150, TOPO = 100;
  const gi0 = new THREE.SphereGeometry(1, 12, 9), pi = gi0.attributes.position;
  for (let i = 0; i < pi.count; i++) {
    let x = pi.getX(i) * RX, y = pi.getY(i) * RY, z = pi.getZ(i) * RZ;
    if (z > 0) z = z * .62 + 38 * Math.exp(-((x / 70) ** 2)) * Math.exp(-(((y + 100) / 45) ** 2));            // cara CHAPADA (estilo PS1, nada de bolha) + focinho
    if (y < -40) { const k = Math.min(1, (-40 - y) / 110); x *= 1 - .12 * k; }                                  // queixo um pouco mais estreito
    if (y > TOPO) { const k = (y - TOPO) / (RY - TOPO); y = TOPO + (y - TOPO) * .25; x *= 1 - .12 * k; z *= 1 - .12 * k; }   // topo achatado
    pi.setXYZ(i, x, y, z);
  }
  gi0.computeVertexNormals();
  const g0 = gi0.toNonIndexed(), p = g0.attributes.position, nn = g0.attributes.normal, ord = [[], []], nor = [[], []];
  for (let t = 0; t < p.count; t += 3) {
    const zc = (p.getZ(t) + p.getZ(t + 1) + p.getZ(t + 2)) / 3, gi = zc > -20 ? 0 : 1;
    for (let k = 0; k < 3; k++) { ord[gi].push(p.getX(t + k), p.getY(t + k), p.getZ(t + k)); nor[gi].push(nn.getX(t + k), nn.getY(t + k) * .4 + .25, nn.getZ(t + k)); }
  }
  const todos = [...ord[0], ...ord[1]], uvs = [];
  for (let i = 0; i < todos.length; i += 3) uvs.push(...uvDe(todos[i] * .95, todos[i + 1] * (todos[i + 1] < 0 ? 1.12 : .95)));   /* embaixo pega mais da foto: o queixo branco */
  const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.Float32BufferAttribute(todos, 3)); geo.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
  geo.setAttribute('normal', new THREE.Float32BufferAttribute([...nor[0], ...nor[1]], 3)); geo.addGroup(0, ord[0].length / 3, 0); geo.addGroup(ord[0].length / 3, ord[1].length / 3, 1);
  cab.add(new THREE.Mesh(geo, [matFoto, matPelo]));

  // CÉREBRO: cúpula sobre o topo cortado, com a textura do cérebro da foto vista de cima
  const CX = 150, CZ = 118, CH = 88, cz0 = -8;
  const gc = new THREE.SphereGeometry(1, 12, 5, 0, Math.PI * 2, 0, Math.PI / 2), pc = gc.attributes.position, uc = gc.attributes.uv;
  for (let i = 0; i < pc.count; i++) {
    const x = pc.getX(i) * CX, y = pc.getY(i) * CH, z = pc.getZ(i) * CZ;
    const dobra = 1 + .05 * Math.sin(Math.atan2(z, x) * 7);                                                  // contorno ondulado (dobras)
    pc.setXYZ(i, x * dobra, TOPO * .98 + y, z * dobra + cz0); uc.setXY(i, ...uvCer(x * .9, z * .8));
  }
  gc.computeVertexNormals();
  const cerebro = new THREE.Mesh(gc, matFoto); cab.add(cerebro);
  cab.add(P.cilindro(CX * 1.02, CX * 1.02, 6, P.mat({ cor: '#5a2a26' }), { seg: 12, pos: [0, TOPO * .98, cz0], esc: [1, 1, CZ / CX] }));   // borda do crânio aberto

  // ORELHAS: grandes, pretas, abertas pra fora (como no meme), com o miolo rosado escuro
  const orelhas = [];
  for (const s of [-1, 1]) {
    const ext = [s * 200, 50], int = [s * 100, 125], pta = [s * 255, 230], piv = [s * 150, 90];
    const loc = v => [v[0] - piv[0], v[1] - piv[1]];
    const a = loc(ext), b = loc(int), c = loc(pta), tras = [(a[0] + b[0]) / 2 + s * 10, (a[1] + b[1]) / 2 + 20, -40];
    const tri = (pts, m) => { const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(new Array(pts.length / 3 * 2).fill(0), 2)); g.computeVertexNormals(); return new THREE.Mesh(g, m); };
    const og = new THREE.Group(); og.position.set(piv[0], piv[1], -10);
    const m = (u, v, k) => [u[0] + (v[0] - u[0]) * k, u[1] + (v[1] - u[1]) * k];
    const ai = m(a, c, .25), bi = m(b, c, .25), ci = m(c, [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2], .2);
    og.add(tri([a[0], a[1], 6, b[0], b[1], 14, c[0], c[1], 0], matOrelha), tri([...ai, 9, ...bi, 16, ...ci, 4], matDentro));
    og.add(tri([a[0], a[1], 6, c[0], c[1], 0, ...tras, b[0], b[1], 14, ...tras, c[0], c[1], 0], matOrelha));
    cab.add(og); orelhas.push(og);
  }
  const k = (o.largura ?? .46) / 430; cab.scale.setScalar(k);
  const animar = (t, { boca = 0, pisca = 0 } = {}) => {
    const img = new ImageData(new Uint8ClampedArray(comBoca.data), cv.width, cv.height); abrirImg(img, P.clamp(boca)); cx.putImageData(img, 0, 0);
    if (pisca > .5) for (const [ex, ey] of [[255, 345], [480, 362]]) { const [u, v] = px(ex - 30, ey - 14); cx.fillStyle = '#1a181e'; cx.fillRect(Math.round(u), Math.round(v), Math.round(60 * S), Math.round(26 * S)); }
    tex.needsUpdate = true;
    orelhas[0].rotation.z = Math.sin(t * 1.5) * .03 + (Math.sin(t * .8 + 1) > .94 ? .14 : 0);
    orelhas[1].rotation.z = -Math.sin(t * 1.2 + 2) * .03 - (Math.sin(t * .6 + 4) > .95 ? .14 : 0);
    cab.rotation.set(Math.sin(t * .7) * .02 + boca * .03, Math.sin(t * .45) * .05, Math.sin(t * .55 + 1) * .015);
  };
  const abrirImg = (img, a) => {                                                // a boca: 0 = entreaberta (como no meme), 1 = bem aberta (falando); pinta na imagem do quadro
    const h = (10 + 16 * a) * B, topo = my + 10 * B, w0 = (17 + 4 * a) * B;
    pintar(mx - w0 - 2, topo - 2, mx + w0 + 2, topo + h + 2, (X, Y) => {
      const t = (Y - topo) / h; if (t < 0 || t > 1) return null; const meia = w0 * Math.sqrt(Math.max(0, 1 - (2 * t - 1) ** 2 * .35)) * (1 - .45 * t);
      if (Math.abs(X - mx) > meia) return null;
      if (Math.abs(X - mx) > meia - LIN * .9 || t < .12) return [58, 14, 22];    // contorno escuro (lábio)
      return t > .48 ? (t > .8 && Math.abs(X - mx) < meia * .5 ? [236, 132, 146] : [214, 98, 116]) : [92, 22, 34];
    }, img);
  };
  animar(0);
  return { cab, orelhas, cerebro, tex, animar, matPelo };
}

// bandeira de Israel (patch de farda): fundo branco, duas faixas azuis, estrela de Davi no meio, borda de costura
export function patchIsrael(w = .075, h = .054) {
  const tx = P.textura(44, 32, (x, W, H) => {
    x.fillStyle = '#5a6248'; x.fillRect(0, 0, W, H); x.fillStyle = '#ecebe6'; x.fillRect(1, 1, W - 2, H - 2);   // costura verde + fundo branco
    x.fillStyle = '#1b3f9c'; x.fillRect(1, 4, W - 2, 4); x.fillRect(1, H - 8, W - 2, 4);                         // faixas azuis
    const c = [W / 2, H / 2], r = 7.2, pts = k => [0, 1, 2].map(i => { const a = -Math.PI / 2 + k * Math.PI / 3 + i * 2 * Math.PI / 3; return [c[0] + r * Math.cos(a), c[1] + r * Math.sin(a)]; });
    x.strokeStyle = '#1b3f9c'; x.lineWidth = 1.6;
    for (const k of [0, 1]) { const p = pts(k); x.beginPath(); x.moveTo(...p[0]); x.lineTo(...p[1]); x.lineTo(...p[2]); x.closePath(); x.stroke(); }   // dois triângulos = estrela de Davi
  });
  return new THREE.Mesh(new THREE.PlaneGeometry(w, h), P.mat({ mapa: tx, lados: THREE.DoubleSide }));
}

export async function dod(o = {}) {
  const C = await cabecaDod(o), { cab } = C, gato = o.corpo === 'gato';
  const BRANCO = '#e4e0da', OLIVA = '#3a4a2a', OLIVA2 = '#283020', LUVA = '#1d1e1b', BOTA = '#161618';
  const matBranco = P.mat({ cor: BRANCO, mapa: P.textura(16, 16, (x, w, h, r) => { x.fillStyle = '#ffffff'; x.fillRect(0, 0, w, h); for (let i = 0; i < 50; i++) { x.fillStyle = r() < .5 ? '#d6d0c8' : '#fffaf2'; x.fillRect(Math.floor(r() * w), Math.floor(r() * h), 1, 2); } }), rep: [2, 2] });
  let c;
  if (gato) {                                                                  // o corpo "como ele é": pelo preto, patas brancas
    const pelagem = P.textura(64, 64, (x, w, h, r) => { for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) { const v = 196 + Math.round((r() - .5) * 40); x.fillStyle = `rgb(${v},${v},${v})`; x.fillRect(i, j, 1, 1); } }, { seed: 21 });
    pelagem.flipY = false;
    c = await corpo({ roupa: '#1c1a20', mao: BRANCO, perna: '#1c1a20', pe: BRANCO }, { relevo: pelagem });
  } else {                                                                     // FARDA: verde-oliva escuro (manga e calça compridas), luvas e coturno pretos
    const tecido = P.textura(64, 64, (x, w, h, r) => { for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) { const v = 192 + Math.round(14 * Math.sin(i * .45 + Math.sin(j * .21) * 2) * Math.sin(j * .13 + i * .05) + (r() - .5) * 26); x.fillStyle = `rgb(${v},${v},${v})`; x.fillRect(i, j, 1, 1); } }, { seed: 33 });
    tecido.flipY = false;                                                      // tecido liso com dobras (sem o desenho de camiseta/bermuda do corpo base)
    c = await corpo({ roupa: OLIVA, mao: LUVA, perna: '#34422a', pe: BOTA }, { relevo: tecido });   /* o coturno (peças por cima) cobre a borda serrilhada da tinta por osso */
  }
  const g = c.obj; g.scale.x *= 1.1; g.scale.z *= 1.06;
  const pesc = new THREE.Group(); pesc.scale.set(1 / g.scale.x, 1 / g.scale.y, 1 / g.scale.z); g.add(pesc); pesc.add(cab);
  pesc.add(P.cilindro(.085, .1, .12, C.matPelo, { seg: 9, pos: [0, .04, .0] }));                                      // pescoço (fino: não tapa a boca)
  const peito = P.esfera(1, matBranco, { seg: 8, segV: 6, esc: gato ? [.12, .16, .045] : [.07, .05, .03] }); pesc.add(peito);   // peito branco (na farda, só aparece no decote)
  const rabo = P.tubo([[0, 0, 0], [0, -.12, -.12], [0, -.2, -.3], [.04, -.12, -.46], [.08, .04, -.52]], .028, C.matPelo, { seg: 14, lados: 5 });
  const raboG = new THREE.Group(); raboG.add(rabo); g.add(raboG); raboG.scale.copy(pesc.scale);
  const bandeira = gato ? null : patchIsrael();
  let equipado = gato;
  // EQUIPAMENTO (inspirado em farda de infantaria: colete porta-placas com porta-carregadores, cinto de guarnição, gola, bandeira no braço esquerdo).
  // Medido no corpo POSADO com raios contra a malha; cada peça é presa ao osso e segue as animações.
  const equipar = () => {
    equipado = true; g.updateMatrixWorld(true);
    const W = n => c.osso(n).getWorldPosition(new THREE.Vector3()), ray = new THREE.Raycaster(), raiz = g.parent || g;
    const sup = (de, dir) => { ray.set(de, dir.clone().normalize()); ray.far = 1; const h = ray.intersectObjects(c.malhas, false)[0]; return h ? h.point : null; };
    const rot = g.rotation.y, fr = new THREE.Vector3(Math.sin(rot), 0, Math.cos(rot)), esq = new THREE.Vector3(Math.cos(rot), 0, -Math.sin(rot)), cima = new THREE.Vector3(0, 1, 0);
    const meia = (p, mx, lados) => {                                           // meia-profundidade do corpo na altura p; a largura vem dos ossos (raio de lado bate no braço), ou do raio de lado (lados: perna)
      const L = lados ? sup(p.clone().addScaledVector(esq, .095), esq.clone().negate()) : null, R = lados ? sup(p.clone().addScaledVector(esq, -.095), esq) : null, F = sup(p.clone().addScaledVector(fr, .5), fr.clone().negate()), B = sup(p.clone().addScaledVector(fr, -.5), fr);
      const cx = L && R ? L.clone().add(R).multiplyScalar(.5) : p.clone(), cz = F && B ? F.clone().add(B).multiplyScalar(.5) : p.clone();
      const cen = p.clone(); cen.addScaledVector(esq, cx.clone().sub(p).dot(esq)); cen.addScaledVector(fr, cz.clone().sub(p).dot(fr));
      return { cen, x: L && R ? L.distanceTo(R) / 2 : mx, z: F && B ? F.distanceTo(B) / 2 : .11 };
    };
    const prender = (m, osso, pos) => { m.position.copy(pos); m.rotation.y = rot; raiz.add(m); c.osso(osso).attach(m); return m; };
    const mVest = P.mat({ cor: OLIVA2, mapa: P.textura(32, 32, (x, w, h, r) => { x.fillStyle = '#fff'; x.fillRect(0, 0, w, h); for (let j = 0; j < h; j += 4) { x.fillStyle = '#d8d8d0'; x.fillRect(0, j, w, 1); } for (let i = 0; i < 90; i++) { x.fillStyle = r() < .5 ? '#e6e6de' : '#c8c8be'; x.fillRect(Math.floor(r() * w), Math.floor(r() * h), 1, 1); } }), rep: [2, 2] });
    const mPreto = P.mat({ cor: '#1a1b18' }), mMetal = P.mat({ cor: '#6e6a58' }), mBolso = P.mat({ cor: '#3e4b2c' });
    // colete: anel elíptico em volta do peito (da barriga até o peito), com porta-carregadores na frente
    const yPeito = W('spine.003').y, yBarriga = W('spine.001').y, alt = (yPeito - yBarriga) + .07, pc = W('spine.002').clone(); pc.y = (yPeito + yBarriga) / 2 + .02;
    const mp = meia(pc, W('upper_arm.L').distanceTo(W('upper_arm.R')) / 2 * .8), colete = new THREE.Group();
    colete.add(P.cilindro(1, 1, alt, mVest, { seg: 10, esc: [mp.x + .018, 1, mp.z + .022] }));
    for (const k of [-1, 0, 1]) colete.add(P.caixa(.062, .085, .035, mBolso, { pos: [k * .07, -alt * .22, mp.z + .035] }), P.caixa(.064, .018, .038, mVest, { pos: [k * .07, -alt * .22 + .045, mp.z + .036] }));   // 3 porta-carregadores com tampa
    colete.add(P.caixa(.1, .06, .02, mBolso, { pos: [0, alt * .26, mp.z + .028] }));                                                                          // bolso do peito
    for (const s of [-1, 1]) colete.add(P.caixa(.05, .03, mp.z * 2 + .06, mVest, { pos: [s * mp.x * .55, alt / 2 + .005, 0] }));                         // alças por cima dos ombros
    prender(colete, 'spine.002', mp.cen);
    // cinto preto com fivela, na altura do quadril
    const pq = W('spine').clone(); pq.y += .03; const mq = meia(pq, W('thigh.L').distanceTo(W('thigh.R')) / 2 + .07), cinto = new THREE.Group();
    cinto.add(P.cilindro(1, 1, .045, mPreto, { seg: 12, esc: [mq.x + .008, 1, mq.z + .01] }), P.caixa(.05, .034, .012, mMetal, { pos: [0, 0, mq.z + .012] }));
    for (const s of [-1, 1]) cinto.add(P.caixa(.05, .06, .035, mBolso, { pos: [s * (mq.x + .01) * .8, -.02, mq.z * .55] }));                             // bolsinhas no cinto
    prender(cinto, 'spine', mq.cen);
    // bandeira de Israel: lado de fora do braço ESQUERDO, logo abaixo do ombro
    const a = W('upper_arm.L'), b = W('forearm.L'), dir = b.clone().sub(a).normalize(), p0 = a.clone().lerp(b, .3), s0 = sup(p0.clone().addScaledVector(esq, .4), esq.clone().negate()) || p0.clone().addScaledVector(esq, .05);
    bandeira.position.copy(s0).addScaledVector(esq, .005); bandeira.up.copy(dir.clone().negate()); bandeira.lookAt(s0.clone().addScaledVector(esq, 1)); raiz.add(bandeira); c.osso('upper_arm.L').attach(bandeira);
    // barra da calça por dentro do coturno: cano do coturno
    // COTURNO: bota (caixa do calcanhar até a ponta do pé) + cano alto até a canela, presos ao pé e à canela
    const mBota = P.mat({ cor: BOTA, mapa: P.textura(16, 16, (x, w, h, r) => { x.fillStyle = '#fff'; x.fillRect(0, 0, w, h); for (let i = 0; i < 40; i++) { x.fillStyle = r() < .5 ? '#d0d0d0' : '#f4f4f4'; x.fillRect(Math.floor(r() * w), Math.floor(r() * h), 1, 1); } x.fillStyle = '#9a9a9a'; x.fillRect(0, h - 2, w, 2); }) });
    for (const s of ['L', 'R']) {
      const pf = W('foot.' + s), pt = W('toe.' + s), ps = W('shin.' + s), fd = pt.clone().sub(pf); fd.y = 0; const comp = fd.length() + .1, ang = Math.atan2(fd.x, fd.z);
      const bota = P.caixa(.125, .11, comp + .03, mBota); const cb = pf.clone().lerp(pt, .5).addScaledVector(fd.clone().normalize(), .01); cb.y = .055;
      bota.position.copy(cb); bota.rotation.y = ang; raiz.add(bota); c.osso('foot.' + s).attach(bota);
      const pb = pf.clone().lerp(ps, .35), mb = meia(pb, .05, true), cano = P.cilindro(1.25, 1, .27, mBota, { seg: 8, esc: [Math.max(mb.x, .045) + .022, 1, Math.max(mb.z, .045) + .022] });
      cano.position.copy(mb.cen); cano.position.y = pf.y + .1; cano.rotation.y = rot; raiz.add(cano); c.osso('shin.' + s).attach(cano);
    }
  };
  const D = { obj: g, corpo: c, cabeca: cab, cerebro: C.cerebro, orelhas: C.orelhas, pescoco: pesc, rabo: raboG, bandeira, tex: C.tex,
    // cabeça/rabo seguem o pescoço e o quadril a cada quadro; o equipamento é preso aos ossos na primeira chamada (chame depois de posar)
    assentar() {
      g.updateMatrixWorld(true);
      const w = new THREE.Vector3(); c.osso('spine.004').getWorldPosition(w); g.worldToLocal(w);
      pesc.position.copy(w); cab.position.set(0, .2, .05); peito.position.set(0, gato ? -.1 : -.035, gato ? .085 : .075);
      const q2 = new THREE.Vector3(); c.osso('spine').getWorldPosition(q2); g.worldToLocal(q2); raboG.position.set(q2.x, q2.y - .02, q2.z - .1);
      if (!equipado) equipar();
    },
    animar(t, f = {}) { C.animar(t, f); rabo.rotation.y = Math.sin(t * 1.1) * .35; rabo.rotation.x = Math.sin(t * .7) * .08; } };
  return D;
}

