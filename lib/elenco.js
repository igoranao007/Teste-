// Elenco novo do THE GREEN PATH: Vegetti, Gusta, Ittu e Metalis (folhas de personagem em videos/97-elenco).
// Corpos: PSX Characters Sampler (csaf), que têm o mesmo molde de UV — o rosto fica deitado no atlas 256:
// testa em u≈198, queixo em u≈240; em volta dos olhos (216,143) [olho da esquerda da tela] e (216,120), boca em (233,131).
// Os globos dos olhos são polígonos à parte que leem 2 losangos pequenos em u 1–37, v 95–114 (centros ≈ (11,104) e (28,104)).
import * as P from './ps1.js';
import * as M from './modelo.js';
import * as T from './tgp.js';
const { THREE } = P;
const PASTA = 'material/modelos/itch/gente/csaf/';
const R = 4;                                                         // o atlas é ampliado 4× (1024 px) pra o rosto colado ficar nítido
const ALVO = { esq: [216 * R, 143 * R], dir: [216 * R, 120 * R], boca: [233.5 * R, 131 * R] };   // olho da esquerda da tela, olho da direita, boca
const C3 = h => { const c = new THREE.Color(h); return [c.r * 255, c.g * 255, c.b * 255]; };

function canvas(img, w = 256 * R, h = 256 * R) { const c = document.createElement('canvas'); c.width = w; c.height = h; const x = c.getContext('2d', { willReadFrequently: true }); x.imageSmoothingEnabled = false; if (img) x.drawImage(img, 0, 0, w, h); x.imageSmoothingEnabled = true; return [c, x]; }
function textura(cv) { const t = new THREE.CanvasTexture(cv); t.flipY = false; t.magFilter = t.minFilter = M.FILTRO.linear ? THREE.LinearFilter : THREE.NearestFilter; t.generateMipmaps = false; t.colorSpace = THREE.NoColorSpace; return t; }

// afim de 3 pontos: leva (p1,p2,p3) da imagem de origem em (q1,q2,q3) do atlas
function afim([p1, p2, p3], [q1, q2, q3]) {
  const S = [[p1[0], p1[1], 1], [p2[0], p2[1], 1], [p3[0], p3[1], 1]], det = m => m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]);
  const D = det(S), res = k => [0, 1, 2].map(j => { const m = S.map((r, i) => r.map((v, c) => c === j ? [q1, q2, q3][i][k] : v)); return det(m) / D; });
  const [a, c, e] = res(0), [b, d, f] = res(1); return [a, b, c, d, e, f];
}
// cola um rosto (foto ou desenho) no atlas, com borda esfumada; pts = [olho esq. da imagem, olho dir., boca]
function colarRosto(x, img, pts, o = {}) {
  const [tc, tx] = canvas(null); tx.imageSmoothingEnabled = true; tx.setTransform(...afim(pts, [ALVO.esq, ALVO.dir, ALVO.boca])); if (o.filtro) tx.filter = o.filtro; tx.drawImage(img, 0, 0); tx.setTransform(1, 0, 0, 1, 0, 0);
  const [mc, mx] = canvas(null), g = mx.createRadialGradient(0, 0, 0, 0, 0, 1); g.addColorStop(0, '#fff'); g.addColorStop(o.duro ?? .72, '#fff'); g.addColorStop(1, 'rgba(255,255,255,0)');
  mx.setTransform((o.rx ?? 26) * R, 0, 0, (o.ry ?? 27) * R, (o.cx ?? 221) * R, (o.cy ?? 131.5) * R); mx.fillStyle = g; mx.beginPath(); mx.arc(0, 0, 1, 0, 7); mx.fill();
  if (o.chave) {                                                                // tira o fundo verde (chroma key) → pele
    const d = tx.getImageData(0, 0, 256 * R, 256 * R), q = d.data, k = C3(o.chave);
    for (let i = 0; i < q.length; i += 4) if (q[i + 3] > 0 && q[i + 1] > q[i] * 1.02 && q[i + 1] > q[i + 2] * 1.15) { q[i] = k[0]; q[i + 1] = k[1]; q[i + 2] = k[2]; }
    tx.putImageData(d, 0, 0);
  }
  tx.globalCompositeOperation = 'destination-in'; tx.drawImage(mc, 0, 0); x.drawImage(tc, 0, 0);
}
// repinta o atlas pixel a pixel: f(x, y, [r,g,b] 0–1, lum, sat) → [r,g,b] 0–255 ou null (mantém)
function repintar(x, f) {                    // f recebe a coordenada no atlas ORIGINAL (0–255)
  const W = 256 * R, d = x.getImageData(0, 0, W, W), q = d.data;
  for (let i = 0; i < q.length; i += 4) { const px = Math.floor(i / 4 % W / R), py = Math.floor(i / 4 / W / R), r = q[i] / 255, g = q[i + 1] / 255, b = q[i + 2] / 255;
    const c = f(px, py, [r, g, b], .3 * r + .59 * g + .11 * b, Math.max(r, g, b) - Math.min(r, g, b)); if (c) for (let k = 0; k < 3; k++) q[i + k] = P.clamp(c[k], 0, 255); }
  x.putImageData(d, 0, 0);
}
// globo do olho: pinta os 2 losangos (pele em volta, branco, íris, pupila, brilho) — vale pros dois olhos
function pintarOlhos(x, o = {}) {
  for (const [cu, cv] of [[11, 104.5], [28.5, 104.5]]) {
    x.fillStyle = o.pele ?? '#b07a5c'; x.fillRect((cu - 10) * R, (cv - 10) * R, 20 * R, 20 * R);
    const c = (r, cor) => { x.fillStyle = cor; x.beginPath(); x.ellipse(cu * R, cv * R, r * R, r * R * (o.alto ?? 1), 0, 0, 7); x.fill(); };
    c(6, o.branco ?? '#d8d0c2'); c(3.3, o.iris ?? '#4a2f1e'); c(1.5, '#0b0706'); x.fillStyle = 'rgba(255,255,255,.85)'; x.fillRect((cu - 1.6) * R, (cv - 1.6) * R, 1.1 * R, 1.1 * R);
  }
}
const ehCabeca = (x, y) => x > 163 && y > 36 && y < 212 && !(x < 200 && y < 64);
const ehPele = ([r, g, b], sat) => r > g * 1.08 && g > b * .95 && sat > .06 && r > .18;

async function carregar(n, atlas, o = {}) {
  const m = T.poses(await M.carregar(PASTA + n + '.glb', { esc: o.esc ?? .95, texMax: 1024 }));
  const tex = textura(atlas); m.mats().forEach(mt => { mt.uniforms.uMapa.value = tex; mt.uniforms.uTemMapa.value = 1; });
  m.braco('L', [.12, -1, .03], [.05, -1, .1]); m.braco('R', [-.12, -1, .03], [-.05, -1, .1]); m.guardar();
  m.cabeca = () => m.osso('head').getWorldPosition(new THREE.Vector3()).add(new THREE.Vector3(0, .1, 0));
  m.atlas = atlas; return m;
}

// ── terno do Phantom (grafite, camisa branca, gravata verde) + pele e cabelo do rosto colado ──
async function terno(foto, pts, o) {
  const img = await M.imagem(PASTA + 'sy_boss.png'), [cv, x] = canvas(img);
  const PELE = C3(o.pele), CAB = C3(o.cabelo);
  repintar(x, (px, py, c, lum, sat) => {
    if (ehCabeca(px, py)) { if (sat < .16 && lum > .2) return CAB.map(v => v * (.55 + lum * .8)); if (ehPele(c, sat)) return PELE.map(v => v * P.clamp(lum / .3, .55, 1.25)); return null; }
    if (c[0] > c[1] * 1.5 && c[0] > c[2] * 1.25 && c[0] > .2 && py > 24 && py < 70 && px > 88 && px < 110) return [0x1c, 0x9a, 0x44].map(v => v * lum / .3);   // gravata → verde
    if (ehPele(c, sat)) return PELE.map(v => v * P.clamp(lum / .3, .55, 1.25));                                                                  // mãos
    if (sat < .14 && lum < .72) return [c[0] * 128, c[1] * 128, c[2] * 128 + 4];                                                                    // terno grafite
    return null;
  });
  colarRosto(x, foto, pts, o.rosto ?? {}); pintarOlhos(x, { pele: o.pele, iris: o.iris });
  if (new URLSearchParams(location.search).get('mapa')) { for (let u = 0; u < 256; u++) for (let v = 0; v < 256; v++) { x.fillStyle = `rgb(${u},150,${v})`; x.fillRect(u * R, v * R, R, R); } }
  if (new URLSearchParams(location.search).get('marca')) { x.fillStyle = '#ff0000'; for (const [u, v] of [ALVO.esq, ALVO.dir]) x.fillRect(u - 4, v - 4, 8, 8); x.fillStyle = '#0000ff'; x.fillRect(ALVO.boca[0] - 4, ALVO.boca[1] - 4, 8, 8); }
  return carregar('sy_boss', cv, o);
}

export async function criar(nome) {
  if (nome === 'vegetti') {
    const f = await M.imagem('material/personagens/vegetti-ref.jpg');
    return terno(f, [[343, 63], [386, 63], [364, 90]], { pele: '#d6a184', cabelo: '#3a2a20', rosto: { chave: '#d09a7c', ry: 23, filtro: 'contrast(1.25) saturate(1.1)' } });
  }
  if (nome === 'gusta') {        // a foto é de 3/4: espelha a metade visível do rosto (da linha do nariz pra orelha) pra ficar de frente
    const f = await M.imagem('material/personagens/gusta-ref.jpg'), [c, x] = canvas(null, 200, 170), L = 228;
    x.fillStyle = '#a87455'; x.fillRect(0, 0, 200, 170);                                       // embaixo do queixo a foto tem gramado: fica pele
    x.drawImage(f, L, 90, 100, 142, 100, 0, 100, 142); x.save(); x.translate(100, 0); x.scale(-1, 1); x.drawImage(f, L, 90, 100, 142, 0, 0, 100, 142); x.restore();
    return terno(c, [[60, 62], [140, 62], [100, 130]], { pele: '#b58463', cabelo: '#24190f', rosto: { chave: '#a87455', filtro: 'contrast(1.3) saturate(1.2) brightness(.88)' } });
  }
  if (nome === 'ittu') return ittu();
  if (nome === 'metalis') return metalis();
  if (nome.startsWith('cru:')) return T.poses(await M.carregar(PASTA + nome.slice(4) + '.glb', { texMax: 256 }));
}

// ───────── ITTU: personagem original (garota de cabelo preto comprido com duas marias-chiquinhas baixas), de terno como o Phantom ─────────
function rostoDesenhado(o) {            // rosto frontal desenhado em código (200×220): olhos em (64,96) e (136,96), boca em (100,168)
  const [c, x] = canvas(null, 200, 220); x.fillStyle = o.pele; x.fillRect(0, 0, 200, 220);
  x.fillStyle = 'rgba(220,120,120,.18)'; for (const cx of [52, 148]) { x.beginPath(); x.ellipse(cx, 132, 18, 9, 0, 0, 7); x.fill(); }   // corado leve
  x.strokeStyle = '#1a1414'; x.lineCap = 'round';
  for (const [cx, s] of [[64, -1], [136, 1]]) {
    x.lineWidth = 3; x.beginPath(); x.moveTo(cx - 20, 70 + (s < 0 ? 2 : 0)); x.quadraticCurveTo(cx, 64, cx + 20, 70 + (s > 0 ? 2 : 0)); x.stroke();         // sobrancelha fina
    x.fillStyle = '#f4efe8'; x.beginPath(); x.ellipse(cx, 97, 17, 10, 0, 0, 7); x.fill();                                                         // branco
    x.fillStyle = '#2a1d1a'; x.beginPath(); x.ellipse(cx + s * 1, 98, 9, 10, 0, 0, 7); x.fill();                                                  // íris
    x.fillStyle = '#0a0606'; x.beginPath(); x.ellipse(cx + s * 1, 98, 4.5, 5.5, 0, 0, 7); x.fill();
    x.fillStyle = '#ffffff'; x.fillRect(cx - 4 + s, 92, 3, 3);
    x.lineWidth = 4.5; x.beginPath(); x.moveTo(cx - 19, 95); x.quadraticCurveTo(cx, 82, cx + 19, 93); x.stroke();                                  // cílio de cima, grosso
    x.lineWidth = 1.5; x.beginPath(); x.moveTo(cx - 13, 108); x.quadraticCurveTo(cx, 112, cx + 13, 107); x.stroke();                               // pálpebra de baixo
  }
  x.lineWidth = 2.2; x.beginPath(); x.moveTo(86, 167); x.quadraticCurveTo(100, 171, 114, 166); x.stroke();                                         // boca séria
  return c;
}
async function ittu() {
  const img = await M.imagem(PASTA + 'so_head_nurse.png'), [cv, x] = canvas(img);
  const PELE = '#e9cdb9', P3 = C3(PELE), CAB = [22, 18, 20];
  repintar(x, (px, py, c, lum, sat) => {
    if (ehCabeca(px, py)) { if (ehPele(c, sat) && lum > .3) return P3.map(v => v * P.clamp(lum / .62, .7, 1.12)); return CAB.map(v => v * (.7 + lum * .9)); }   // cabelo e touca → preto
    if (px > 96 && px < 104 && py > 26 && py < 62 && !(lum > .8)) return [0x1c, 0x9a, 0x44].map(v => v * (.85 + lum * .4));                                // gravata verde
    if (ehPele(c, sat)) return P3.map(v => v * P.clamp(lum / .62, .6, 1.12));                                                                              // mãos
    if (lum > .8 && sat < .1) return null;                                                                                                                  // gola branca
    return [c[0] * 70 + 14, c[1] * 70 + 14, c[2] * 60 + 16];                                                                                              // uniforme → terno preto
  });
  colarRosto(x, rostoDesenhado({ pele: PELE }), [[64, 96], [136, 96], [100, 168]], { rx: 25, ry: 26 });
  pintarOlhos(x, { pele: PELE, iris: '#2a1d1a' });
  // franja reta e preta na testa (atlas: u 196–207 atravessando o rosto)
  x.fillStyle = 'rgb(22,18,20)'; x.fillRect(190 * R, 104 * R, 15.5 * R, 56 * R);   // franja reta
  const m = await carregar('so_head_nurse', cv, { esc: .92 });
  // tira a touca de enfermeira: achata os vértices acima do topo da cabeça pra dentro do cabelo
  for (const ml of m.malhas) { if (!ml.isSkinnedMesh) continue; const pp = ml.geometry.attributes.position;
    for (let i = 0; i < pp.count; i++) { const y = pp.getY(i); if (y > 1.795) { pp.setY(i, 1.78); pp.setX(i, pp.getX(i) * .55); pp.setZ(i, (pp.getZ(i) + .01) * .55 - .01); } }
    pp.needsUpdate = true; ml.geometry.computeVertexNormals(); }
  // duas marias-chiquinhas baixas, atrás das orelhas, caindo até o peito
  const cab = m.osso('head'), cabelo = P.mat({ cor: '#161214' }); m.obj.updateMatrixWorld(true);
  const hp = cab.getWorldPosition(new THREE.Vector3()).add(new THREE.Vector3(0, .1, 0));          // o osso da cabeça fica na nuca: sobe pro meio da cabeça
  for (const s of [-1, 1]) {
    const pts = [[s * .075, -.02, -.06], [s * .11, -.07, -.04], [s * .135, -.15, .0], [s * .145, -.26, .04], [s * .13, -.36, .06]].map(([a, b, c]) => [hp.x + a, hp.y + b, hp.z + c]);
    const t = P.varrer(pts, u => .034 * (1 - u * .55) + .014 * Math.sin(u * Math.PI), cabelo, { segs: 14, rad: 7 });
    const laco = P.esfera(.022, P.mat({ cor: '#1c9a44' }), { seg: 6, segV: 4, pos: [hp.x + s * .108, hp.y - .07, hp.z - .045] });
    cab.attach(t); cab.attach(laco);
  }
  return m;
}

// ───────── METALIS: personagem original — criatura de pelo azul com juba espetada pra todo lado, mendigo ─────────
async function metalis() {
  const img = await M.imagem(PASTA + 'af_scavenger.png'), [cv, x] = canvas(img), AZUL = C3('#2f5fd0'), R0 = P.rng(4);
  repintar(x, (px, py, c, lum, sat) => {
    if (ehCabeca(px, py)) return AZUL.map(v => v * .8);
    if (ehPele(c, sat) && c[0] > c[1] * 1.1 && (py > 200 || (px > 84 && px < 116 && py < 42))) return AZUL.map(v => v * P.clamp(lum / .55, .6, 1.2) * (.9 + R0() * .2));      // mãos e pele → pelo azul
    if (py > 150 && py < 216) return [c[0] * 120 + 20, c[1] * 110 + 20, c[2] * 100 + 22].map(v => v * (.85 + R0() * .3));                // calça cinza encardida
    if (py >= 216) return [c[0] * 140, c[1] * 120, c[2] * 100];                                                                               // sapato gasto
    return [44 + lum * 95, 34 + lum * 72, 22 + lum * 44].map(v => v * (.8 + R0() * .35));                                                     // casaco marrom sujo
  });
  // remendos e rasgos no casaco e na calça
  for (const [u, v, w, h, cor] of [[40, 40, 14, 10, '#6b6a3a'], [120, 70, 10, 12, '#4a5a6a'], [60, 175, 12, 8, '#141414'], [150, 190, 9, 7, '#141414'], [95, 120, 8, 9, '#7a5a3a']]) {
    x.fillStyle = cor; x.fillRect(u * R, v * R, w * R, h * R); x.strokeStyle = '#d8c8a0'; x.setLineDash([R, R]); x.strokeRect(u * R, v * R, w * R, h * R); x.setLineDash([]);
  }
  const m = await carregar('af_scavenger', cv, { esc: .95 });
  // esconde a cabeça humana e põe a cabeça da criatura no lugar
  const hb = m.osso('head'); m.obj.updateMatrixWorld(true); const hp = hb.getWorldPosition(new THREE.Vector3()); hb.scale.setScalar(.02); m.guardar();
  const g = new THREE.Group(); g.position.copy(hp).add(new THREE.Vector3(0, .1, .01));
  // textura do rosto (frente): pelo azul, focinho cinza-azulado, olhos cansados com olheira, nariz, boca com dente faltando, barba por fazer
  const [fc, fx] = canvas(null, 128, 128); fx.fillStyle = '#2f5fd0'; fx.fillRect(0, 0, 128, 128);
  for (let i = 0; i < 500; i++) { fx.fillStyle = R0() < .5 ? '#244db0' : '#3a6be0'; fx.fillRect(R0() * 128, R0() * 128, 1, 2); }
  fx.fillStyle = '#9bb0c8'; fx.beginPath(); fx.ellipse(64, 88, 34, 26, 0, 0, 7); fx.fill();                                                   // focinho
  for (let i = 0; i < 260; i++) { const a = R0() * 7, r = 18 + R0() * 18; fx.fillStyle = 'rgba(30,40,60,.55)'; fx.fillRect(64 + Math.cos(a) * r * 1.2, 96 + Math.sin(a) * r * .6, 1, 1); }   // barba por fazer
  for (const cx of [44, 84]) {
    fx.fillStyle = '#1b3a8a'; fx.beginPath(); fx.ellipse(cx, 62, 14, 11, 0, 0, 7); fx.fill();                                                  // olheira
    fx.fillStyle = '#e8e2d2'; fx.beginPath(); fx.ellipse(cx, 58, 11, 8, 0, 0, 7); fx.fill();
    fx.fillStyle = '#2b6a3a'; fx.beginPath(); fx.arc(cx + 1, 60, 4.5, 0, 7); fx.fill(); fx.fillStyle = '#080808'; fx.beginPath(); fx.arc(cx + 1, 60, 2.2, 0, 7); fx.fill();
    fx.fillStyle = '#2f5fd0'; fx.fillRect(cx - 12, 48, 24, 7);                                                                                 // pálpebra caída
    fx.fillStyle = '#16307a'; fx.fillRect(cx - 12, 54, 24, 2);
  }
  fx.fillStyle = '#141820'; fx.beginPath(); fx.ellipse(64, 78, 7, 5, 0, 0, 7); fx.fill();                                                     // nariz
  fx.strokeStyle = '#141820'; fx.lineWidth = 2; fx.beginPath(); fx.moveTo(48, 98); fx.quadraticCurveTo(64, 103, 82, 96); fx.stroke();       // boca torta
  fx.fillStyle = '#e8e0c8'; fx.fillRect(56, 99, 4, 3); fx.fillRect(66, 100, 4, 3);                                                            // dentes (com um faltando)
  const ftex = new THREE.CanvasTexture(fc); ftex.magFilter = ftex.minFilter = M.FILTRO.linear ? THREE.LinearFilter : THREE.NearestFilter; ftex.generateMipmaps = false; ftex.colorSpace = THREE.NoColorSpace;
  const geo = new THREE.SphereGeometry(.12, 14, 10), pp = geo.attributes.position, uv = geo.attributes.uv;
  for (let i = 0; i < pp.count; i++) { let X = pp.getX(i), Y = pp.getY(i), Z = pp.getZ(i); if (Z > 0 && Y < .02) Z += .035 * Math.exp(-((X / .06) ** 2)) * Math.exp(-(((Y + .045) / .05) ** 2)); pp.setXYZ(i, X, Y * 1.08, Z * .95);
    uv.setXY(i, .5 + X / .26, .5 + Y / .28); }
  geo.computeVertexNormals();
  const frente = P.mat({ mapa: ftex }), pelo = P.mat({ cor: '#2f5fd0' });
  g.add(new THREE.Mesh(geo, frente));
  // juba espetada pra todo lado (não é pra trás: é bagunçada, de quem dorme na rua)
  for (let i = 0; i < 26; i++) {
    const a = R0() * Math.PI * 2, up = .35 + R0() * .9, dir = new THREE.Vector3(Math.cos(a) * (1 - up * .6), up, Math.sin(a) * (1 - up * .6) - .25).normalize();
    if (dir.z > .5 && dir.y < .5) continue;
    const L = .09 + R0() * .11, sp = P.cilindro(0, .03 + R0() * .015, L, R0() < .5 ? pelo : P.mat({ cor: '#2552b8' }), { seg: 4 });
    sp.position.copy(dir.clone().multiplyScalar(.1 + L / 2)); sp.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir); g.add(sp);
  }
  for (const s of [-1, 1]) { const e = P.esfera(.035, pelo, { seg: 6, segV: 4, pos: [s * .115, .05, -.01], esc: [.5, 1, .8] }); g.add(e); }   // orelhas pequenas
  // gorro de lã velho por cima, com a juba saindo
  g.add(P.tornear([[.122, 0], [.126, .03], [.112, .06], [.07, .085], [0, .09]], P.mat({ cor: '#4a3226', mapa: P.TEX.xadrez?.({ cores: ['#4a3226', '#3d2a20'] }) }), { seg: 10, pos: [0, .06, -.012], rot: [-.18, 0, 0] }));
  m.obj.attach(g); m.criatura = g;
  m.cabeca = () => g.getWorldPosition(new THREE.Vector3());
  return m;
}
