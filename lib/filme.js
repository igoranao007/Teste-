// THE GREEN PATH — kit de cena: noite verde, carro, estrada, árvores, postes, textos nítidos por cima.
import * as P from './ps1.js';
import * as A from './arh.js';
import * as M from './modelo.js';
import * as T from './tgp.js';
const { THREE } = P;
export const VERDE = T.VERDE, SOMBRA = T.SOMBRA, AMARELO = '#ffd23a', NEVOA = '#05170c';

// palco noturno: céu quase preto que esverdeia no horizonte, névoa verde-escura, luz geral fraca e fria
export function noite(o = {}) {
  return P.palco({ fov: o.fov ?? 40, cam: o.cam ?? [0, 1.5, 6], alvo: o.alvo ?? [0, 1, 0],
    fundoTex: o.fundo ? undefined : P.ceu({ cores: [[0, '#010402'], [.5, '#04140a'], [1, '#124224']], faixas: 10 }), fundo: o.fundo,
    nevoa: { cor: o.nevoa ?? NEVOA, perto: o.perto ?? 6, longe: o.longe ?? 30 },
    luz: { keyDir: [-.3, .7, .5], keyCor: '#6f8f7a', fillDir: [.7, .2, .3], fillCor: '#123a20', amb: '#0b1a10', ...(o.luz || {}) } });
}

// ── texturas ──
export const TEX = {
  terra: () => P.textura(32, 32, (x, w, h, r) => { x.fillStyle = '#6a6250'; x.fillRect(0, 0, w, h); for (let i = 0; i < 260; i++) { x.fillStyle = ['#575040', '#7a715c', '#4a4436', '#63604a'][Math.floor(r() * 4)]; x.fillRect(Math.floor(r() * w), Math.floor(r() * h), 1 + Math.floor(r() * 3), 1); } }, { seed: 12 }),
  capim: () => P.textura(32, 32, (x, w, h, r) => { x.fillStyle = '#3d5a3c'; x.fillRect(0, 0, w, h); for (let i = 0; i < 300; i++) { x.fillStyle = ['#2f4a30', '#4a6a44', '#27402a', '#557a4c'][Math.floor(r() * 4)]; x.fillRect(Math.floor(r() * w), Math.floor(r() * h), 1, 1 + Math.floor(r() * 3)); } }, { seed: 5 }),
  madeira: () => P.textura(16, 32, (x, w, h, r) => { x.fillStyle = '#6b5238'; x.fillRect(0, 0, w, h); for (let i = 0; i < 40; i++) { x.fillStyle = r() < .5 ? '#5a442e' : '#7a6044'; x.fillRect(Math.floor(r() * w), 0, 1, h); } }, { seed: 8 }),
  brilho: () => P.textura(32, 32, (x, w, h) => { const g = x.createRadialGradient(16, 16, 0, 16, 16, 16); g.addColorStop(0, '#ffffff'); g.addColorStop(.5, '#777777'); g.addColorStop(1, '#000000'); x.fillStyle = g; x.fillRect(0, 0, w, h); }, { niveis: 0 }),
  // poça de luz do farol: forte perto do carro, some pra frente e pros lados
  farol: () => P.textura(32, 64, (x, w, h) => { const d = x.createImageData(w, h); for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) { const u = (i + .5) / w * 2 - 1, v = 1 - (j + .5) / h; const lar = .25 + .75 * v, k = Math.max(0, 1 - (u / lar) ** 2) * Math.min(1, v * 6) * (1 - v) ** 1.3 * 1.8; const c = Math.min(255, k * 255); d.data.set([c, c, c, 255], (j * w + i) * 4); } x.putImageData(d, 0, 0); }, { niveis: 0 }),
};

// ── árvore em silhueta (some na névoa) ──
export function arvore(r, o = {}) {
  const g = new THREE.Group(), h = (o.h ?? 5) * (.8 + r() * .5), cor = o.cor ?? '#030a05', m = P.mat({ cor, semLuz: true });
  g.add(P.cilindro(.09, .16, h * .45, m, { seg: 5, pos: [0, h * .22, 0] }));
  if (r() < (o.pinheiro ?? .6)) for (let i = 0; i < 3; i++) g.add(P.cilindro(0, h * (.3 - i * .06), h * .36, m, { seg: 6, pos: [0, h * (.45 + i * .2), 0] }));
  else { g.add(P.esfera(h * .26, m, { seg: 6, segV: 4, pos: [0, h * .68, 0], esc: [1, .85, 1] })); g.add(P.esfera(h * .18, m, { seg: 5, segV: 4, pos: [h * .16, h * .52, .1] })); }
  g.rotation.y = r() * 6; return g;
}
export function mata(cena, r, { x0, x1, z0, z1, n, h, cor }) { for (let i = 0; i < n; i++) { const a = arvore(r, { h, cor }); a.position.set(P.lerp(x0, x1, r()), 0, P.lerp(z0, z1, r())); cena.add(a); } }

// ── poste de luz VERDE (luz assada) ──
export function posteVerde(x, z, o = {}) {
  const p = A.poste(x, z, { cor: VERDE, raio: o.raio ?? 9, int: o.int ?? 1.5, h: o.h ?? 4, rot: o.rot });
  p.children[p.children.length - 1].material.uniforms.uCor.value.set('#b9ffc9');
  const h = A.halo(o.halo ?? .5, VERDE, .28); h.position.set(.42, (o.h ?? 4) - .1, 0); p.add(h); p.halo = h; return p;
}

// ── cerca de madeira ao longo de x ──
export function cerca(x0, x1, z, o = {}) {
  const g = new THREE.Group(), m = A.matA({ mapa: TEX.madeira(), cor: '#8a8a80' });
  for (let x = x0; x <= x1; x += 2.4) g.add(P.caixa(.12, 1.15, .12, m, { pos: [x, .57, z], sy: 2 }));
  for (const y of [.45, .9]) g.add(P.caixa(x1 - x0, .09, .05, m, { pos: [(x0 + x1) / 2, y, z], sx: Math.ceil((x1 - x0) / 2.4) }));
  if (o.rot) g.rotation.y = o.rot; return g;
}

// ── CARRO: sedã preto (PSX Vehicles Free, heyheythere, CC BY 4.0), com interior de verdade. Frente = +z, volante à esquerda (+x) ──
const SEDAN = 'material/modelos/itch/carros/hey-sedan-blue.glb';
async function sedan(cor) {
  const m = await M.carregar(SEDAN, { texMax: 256, mat: { cor, lados: THREE.DoubleSide } });
  for (const mt of m.malhas.flatMap(x => [].concat(x.material))) {                    // textura em cinza: carro preto, nada de lanterna vermelha
    const tx = mt.uniforms.uMapa.value; if (!tx?.image) continue;
    const c = document.createElement('canvas'); c.width = tx.image.width; c.height = tx.image.height; const x = c.getContext('2d'); x.filter = 'grayscale(1)'; x.drawImage(tx.image, 0, 0);
    const k = c.width / 1024; x.clearRect(Math.round(800 * k), 0, Math.round(64 * k), Math.round(32 * k));              // o ladrilho do vidro fica transparente (1 bit): dá pra ver dentro
    const n = new THREE.CanvasTexture(c); n.flipY = tx.flipY; n.wrapS = tx.wrapS; n.wrapT = tx.wrapT; n.magFilter = n.minFilter = THREE.NearestFilter; n.generateMipmaps = false; n.colorSpace = THREE.NoColorSpace; mt.uniforms.uMapa.value = n;
  }
  m.rodas = []; m.obj.traverse(n => { if (/wheel/.test(n.name)) m.rodas.push(n); });
  return m;
}
// por fora: faróis amarelos com poça de luz no chão, lanternas apagadas. c.luzes(k) · c.rodar(distância) gira as rodas
export async function carro(o = {}) {
  const m = await sedan(o.cor ?? '#33363d'), g = new THREE.Group(); g.add(m.obj);
  const L = 4.68, W = 2, H = 1.39; Object.assign(g, { comp: L, larg: W, alt: H });
  const amarelo = P.mat({ cor: AMARELO, semLuz: true }), far = [];
  for (const s of [-1, 1]) {
    const f = P.caixa(.3, .13, .04, amarelo, { pos: [s * .66, .6, L / 2 + .005] }); g.add(f);
    const h = P.disco(.55, P.mat({ mapa: TEX.brilho(), cor: AMARELO, opac: .5, aditivo: true, semLuz: true, lados: THREE.DoubleSide }), { seg: 10, pos: [s * .66, .6, L / 2 + .05] }); g.add(h); far.push(h);
  }
  const poca = P.malha(new THREE.PlaneGeometry(7.5, 15, 6, 12), P.mat({ mapa: TEX.farol(), cor: AMARELO, opac: .55, aditivo: true, semLuz: true, lados: THREE.DoubleSide }), { pos: [0, .03, L / 2 + 7.4], rot: [-Math.PI / 2, 0, Math.PI] });
  g.add(poca);
  g.farois = far; g.poca = poca;
  g.encarar = cam => far.forEach(h => h.quaternion.copy(cam.quaternion).premultiply(g.getWorldQuaternion(new THREE.Quaternion()).invert()));
  g.luzes = k => { far.forEach(h => { h.material.uniforms.uOpac.value = .5 * k; }); poca.material.uniforms.uOpac.value = .55 * k; amarelo.uniforms.uCor.value.set(AMARELO).multiplyScalar(.25 + .75 * k); };
  g.rodar = d => m.rodas.forEach(r => { r.rotation.x = d / .32; });
  return g;
}
// por dentro: o MESMO sedã, mais claro, com o botão e o LED do roteiro no painel. Medidas (m): assento do motorista
// em x=+.35 (topo y=.67, z≈.15–.5), volante em (.35, .82, .5), painel em z≈.61, teto em y=1.33.
export async function interiorCarro() {
  const m = await sedan('#8f9c94'), g = new THREE.Group(); g.add(m.obj);
  const led = P.caixa(.03, .03, .02, P.mat({ cor: '#0f3a1c', semLuz: true }), { pos: [.1, .74, .6] }); g.add(led);
  const botao = P.caixa(.06, .06, .03, P.mat({ cor: '#59615c' }), { pos: [.1, .81, .598] }); g.add(botao);
  g.add(P.caixa(.2, .07, .02, P.mat({ cor: VERDE, semLuz: true }), { pos: [.35, .92, .625] }));    // mostradores (brilho verde)
  g.add(P.caixa(.16, .04, .02, P.mat({ cor: '#1f8f3c', semLuz: true }), { pos: [-.12, .8, .602] })); // rádio
  Object.assign(g, { led, botao, volante: new THREE.Vector3(.35, .84, .49), assento: new THREE.Vector3(.35, .67, .3), passageiro: new THREE.Vector3(-.35, .67, .32) });
  return g;
}

// ── textos nítidos por cima (DOM): não passam pelo PS1 ──
export function camada(css = '') { const d = document.createElement('div'); d.className = 'layer'; d.style.cssText = 'pointer-events:none;' + css; document.getElementById('stage').appendChild(d); return d; }
export const TITULO = "font-family:'Geist',sans-serif;font-weight:900;letter-spacing:.04em;";
export const TERMINAL = "font-family:'JetBrains Mono',monospace;font-weight:700;";
export const digitado = (txt, t, t0, vel = 14) => txt.slice(0, Math.max(0, Math.floor((t - t0) * vel)));

// chiado verde de TV (canvas pequeno, ampliado): c.desenha(quadro, força 0–1, { faixas, rasgos })
export function chiadoVerde(o = {}) {
  const el = camada(), cv = document.createElement('canvas'); cv.width = 240; cv.height = 135;
  cv.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;image-rendering:pixelated'; el.appendChild(cv);
  const x = cv.getContext('2d'), d = x.createImageData(240, 135);
  el.desenha = (q, f = 1, p = {}) => {
    const r = P.rng(q * 7919 + 13), a = d.data; el.style.opacity = f <= 0 ? 0 : 1; if (f <= 0) return;
    const ty = Math.floor(r() * 135), th = 6 + Math.floor(r() * 14);
    for (let j = 0; j < 135; j++) { const faixa = p.faixas && j >= ty && j < ty + th ? 1.8 : 1, lin = (j % 2 ? .75 : 1) * faixa;
      for (let i = 0; i < 240; i++) { const v = r(), k = (j * 240 + i) * 4, on = v < (p.dens ?? .5) * f; const c = on ? (.35 + r() * .65) * lin : 0; a[k] = c * 40; a[k + 1] = Math.min(255, c * 255); a[k + 2] = c * 90; a[k + 3] = on ? Math.min(255, 255 * f * (p.alfa ?? 1)) : (p.fundo ?? 0) * 255; } }
    x.putImageData(d, 0, 0);
  };
  return el;
}

// ── placa amarela "CASMIRON CITY" em dois postes (pórtico): a face com o texto olha pra −x ──
export function placaCidade(o = {}) {
  const g = new THREE.Group(), w = o.w ?? 7, h = 1.5, y = o.y ?? 4.9;
  const tx = P.textura(288, 64, (x, W, H) => {
    x.fillStyle = '#ffd23a'; x.fillRect(0, 0, W, H); x.fillStyle = '#1a1606'; x.fillRect(3, 3, W - 6, 2); x.fillRect(3, H - 5, W - 6, 2); x.fillRect(3, 3, 2, H - 6); x.fillRect(W - 5, 3, 2, H - 6);
    x.font = "900 40px 'Geist', 'DejaVu Sans', sans-serif"; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText('CASMIRON CITY', W / 2, H / 2 + 2, W - 22);
    const d = x.getImageData(0, 0, W, H), q = d.data; for (let i = 0; i < q.length; i += 4) { const esc = q[i] < 150; q[i] = esc ? 26 : 255; q[i + 1] = esc ? 22 : 210; q[i + 2] = esc ? 6 : 58; } x.putImageData(d, 0, 0);
  }, { niveis: 0 });
  const ferro = P.mat({ cor: '#3a4a40' });
  g.add(P.caixa(.08, h, w, [P.mat({ cor: '#6a5a18' }), P.mat({ mapa: tx, semLuz: true }), ferro, ferro, ferro, ferro], { pos: [0, y, 0] }));
  for (const s of [-1, 1]) { g.add(P.cilindro(.11, .14, y + h / 2, ferro, { seg: 6, pos: [.08, (y + h / 2) / 2, s * (w / 2 + .25)] })); g.add(P.caixa(.1, .1, .5, ferro, { pos: [.04, y, s * (w / 2 + .1)] })); }
  g.add(P.caixa(.1, .1, w + .6, ferro, { pos: [.08, y + h / 2 + .05, 0] }));
  return g;
}

// ── casa afastada de um andar, com UMA janela verde acesa (a frente olha pra +z) ──
export function casa(o = {}) {
  const g = new THREE.Group(), par = A.matA({ mapa: TEX.madeira(), rep: [6, 1], cor: '#9a9a8a' }), tel = A.matA({ cor: '#3a3f3a' });
  g.add(P.caixa(8, 2.8, 6, par, { pos: [0, 1.4, 0], sx: 6, sy: 3, sz: 5 }));
  g.add(P.cilindro(4.2, 4.2, 8.6, tel, { seg: 3, pos: [0, 3.55, 0], rot: [0, 0, Math.PI / 2], esc: [.42, 1, .92] }));
  g.add(P.caixa(1, 2, .08, A.matA({ cor: '#3a2e22' }), { pos: [-1.6, 1, 3.02] }));
  const jan = P.caixa(1.5, 1.1, .08, P.mat({ cor: VERDE, semLuz: true }), { pos: [1.7, 1.55, 3.02] }); g.add(jan);
  g.add(P.caixa(1.6, .06, .1, P.mat({ cor: '#0c1a10', semLuz: true }), { pos: [1.7, 1.55, 3.05] }), P.caixa(.06, 1.2, .1, P.mat({ cor: '#0c1a10', semLuz: true }), { pos: [1.7, 1.55, 3.05] }));
  g.add(P.caixa(.6, .9, .6, A.matA({ cor: '#5a5048' }), { pos: [2.6, 4.4, -.8] }));
  const h = A.halo(1.6, VERDE, .3); h.position.set(1.7, 1.55, 3.2); g.add(h); g.halo = h;
  g.luz = () => { g.updateMatrixWorld(true); const p = new THREE.Vector3(1.7, 1.3, 4.2); g.localToWorld(p); return { pos: p.toArray(), cor: VERDE, raio: 11, int: 1.6 }; };
  return g;
}

// ── cidade ao fundo: prédios com janelas acesas em verde e amarelo, sumindo na névoa ──
export function cidade(r, o = {}) {
  const g = new THREE.Group(), n = o.n ?? 26;
  const jan = P.textura(16, 32, (x, w, h, rr) => { x.fillStyle = '#07120b'; x.fillRect(0, 0, w, h); for (let j = 2; j < h; j += 5) for (let i = 2; i < w; i += 4) { const v = rr(); x.fillStyle = v < .2 ? '#39ff6a' : v < .3 ? '#ffd23a' : '#0d2414'; x.fillRect(i, j, 2, 3); } }, { seed: 31, niveis: 0 });
  for (let i = 0; i < n; i++) { const w = 4 + r() * 7, h = 6 + r() * 22, d = 4 + r() * 6; g.add(P.caixa(w, h, d, P.mat({ mapa: jan, rep: [Math.round(w / 3), Math.round(h / 6)], semLuz: true }), { pos: [(i - n / 2) * 6.5 + r() * 4, h / 2, -r() * 30] })); }
  return g;
}

// ── caminhada: balança pernas e braços a partir da fase (rad); a mão direita fica reta se carrega a maleta ──
export function andar(c, fase, o = {}) {
  const a = Math.sin(fase) * (o.amp ?? .42), B = n => c.osso(n);
  for (const [s, k] of [['L', 1], ['R', -1]]) {
    const ang = a * k, dobra = Math.max(0, -Math.cos(fase) * k) * .55 + .08;
    M.apontar(B('thigh.' + s), B('shin.' + s), [0, -Math.cos(ang), Math.sin(ang)]);
    M.apontar(B('shin.' + s), B('foot.' + s), [0, -Math.cos(ang - dobra), Math.sin(ang - dobra)]);
    const sx = s === 'L' ? .1 : -.1;
    if (s === 'R' && o.maleta) c.braco('R', [sx, -1, .02], [sx * .4, -1, .06]);
    else c.braco(s, [sx, -Math.cos(-ang * .7), Math.sin(-ang * .7)], [sx * .3, -Math.cos(-ang * .7 + .25), Math.sin(-ang * .7 + .25)]);
  }
  return Math.abs(Math.sin(fase)) * .018;        // sobe e desce do passo
}
// põe a maleta (de pé) pendurada na mão direita
export function segurar(c, mal) { const p = new THREE.Vector3(); c.osso('f_middle.01.R').getWorldPosition(p); mal.position.set(p.x, p.y - mal.alca - .03, p.z + .02); }

// ── corredor subterrâneo de concreto com elevador no fundo (−z). e.portas(k) abre; e.lamp(k) é a fluorescente verde ──
export function corredor(o = {}) {
  const g = new THREE.Group(), L = o.comp ?? 16, W = 3.2, H = 2.9, conc = P.TEX.concreto({ cor: '#5d6860', junta: '#3c443e' }), m = () => A.matA({ mapa: conc, rep: [L / 2, 1.5] });
  g.add(P.caixa(W, .1, L, A.matA({ mapa: conc, rep: [2, L / 1.6] }), { pos: [0, -.05, -L / 2 + 3], sx: 6, sz: 24 }));
  g.add(P.caixa(W, .1, L, m(), { pos: [0, H + .05, -L / 2 + 3], sx: 6, sz: 24 }));
  for (const s of [-1, 1]) g.add(P.caixa(.1, H, L, m(), { pos: [s * (W / 2 + .05), H / 2, -L / 2 + 3], sy: 5, sz: 24 }));
  const zf = -L + 3, metal = A.matA({ cor: '#8a948c' });
  g.add(P.caixa(W, H, .1, A.matA({ mapa: conc, rep: [2, 2] }), { pos: [0, H / 2, zf - 1.9], sx: 4, sy: 4 }));           // fundo da cabine
  for (const s of [-1, 1]) { g.add(P.caixa(.8, H, .2, A.matA({ mapa: conc, rep: [1, 2] }), { pos: [s * 1.2, H / 2, zf], sy: 4 })); g.add(P.caixa(.1, H, 1.9, metal, { pos: [s * .85, H / 2, zf - .95], sy: 4 })); }
  g.add(P.caixa(1.6, H - 2.15, .2, A.matA({ mapa: conc, rep: [1, 1] }), { pos: [0, 2.15 + (H - 2.15) / 2, zf] }));
  g.add(P.caixa(1.7, .08, 1.9, metal, { pos: [0, 2.2, zf - .95] }));
  const portas = [-1, 1].map(s => { const p = P.caixa(.8, 2.15, .06, A.matA({ cor: '#9aa69c' }), { pos: [s * .4, 1.075, zf + .02], sy: 4 }); g.add(p); return p; });
  const visor = P.caixa(.3, .12, .03, P.mat({ cor: VERDE, semLuz: true }), { pos: [0, 2.4, zf + .12] }); g.add(visor);
  const lamps = (o.lamps ?? [-1.5, -7.5]).map(z => { const l = P.caixa(.16, .05, 1.3, P.mat({ cor: '#c9ffd6', semLuz: true }), { pos: [0, H - .03, z] }); g.add(l); return l; });
  const cab = P.caixa(.5, .04, .5, P.mat({ cor: '#e4ffe9', semLuz: true }), { pos: [0, 2.15, zf - .95] }); g.add(cab);
  Object.assign(g, { zf, portasM: portas,
    portas: k => portas.forEach((p, i) => { p.position.x = (i ? 1 : -1) * (.4 + .78 * k); }),
    luzes: (k, aberta = 1) => { lamps.forEach(l => l.material.uniforms.uCor.value.set('#c9ffd6').multiplyScalar(.15 + .85 * k));
      return [...lamps.map(l => ({ pos: [0, H - .5, l.position.z], cor: VERDE, raio: 7, int: .95 * k })), { pos: [0, 1.9, zf - .9], cor: '#b9ffcf', raio: 4 + 4 * aberta, int: 1.5 * aberta + .15 }]; } });
  return g;
}

// ── monitor de tubo com tela verde (canvas vivo em m.tela/m.ctx) e teclado. A tela olha pra −z (pro Igor) ──
export function computador() {
  const g = new THREE.Group(), bege = P.mat({ cor: '#a9a48c' }), esc = P.mat({ cor: '#6f6b5a' });
  const cv = document.createElement('canvas'); cv.width = 96; cv.height = 72; const ctx = cv.getContext('2d');
  const tx = new THREE.CanvasTexture(cv); tx.magFilter = tx.minFilter = THREE.NearestFilter; tx.generateMipmaps = false; tx.colorSpace = THREE.NoColorSpace;
  g.add(P.caixa(.46, .38, .4, bege, { pos: [0, .27, .05], sx: 2, sy: 2 }), P.caixa(.3, .08, .3, esc, { pos: [0, .04, .05] }), P.caixa(.36, .3, .14, bege, { pos: [0, .27, .3] }));
  g.add(P.malha(new THREE.PlaneGeometry(.36, .27), P.mat({ mapa: tx, semLuz: true }), { pos: [0, .28, -.175], rot: [0, Math.PI, 0] }));
  g.add(P.caixa(.42, .34, .02, P.mat({ cor: '#1a1c18' }), { pos: [0, .28, -.16] }));
  const tec = new THREE.Group(); tec.add(P.caixa(.44, .025, .16, bege, { pos: [0, .0125, 0] }));
  const tk = P.textura(32, 12, (x, w, h) => { x.fillStyle = '#8e8a76'; x.fillRect(0, 0, w, h); x.fillStyle = '#d9d5c0'; for (let j = 1; j < h; j += 3) for (let i = 1; i < w; i += 3) x.fillRect(i, j, 2, 2); }, { niveis: 0 });
  tec.add(P.caixa(.42, .012, .14, [esc, esc, P.mat({ mapa: tk }), esc, esc, esc], { pos: [0, .03, 0] }));
  const enter = P.caixa(.045, .016, .03, P.mat({ cor: '#e4e0cc' }), { pos: [-.17, .038, .01] }); tec.add(enter);
  tec.position.set(0, 0, -.36); g.add(tec);
  Object.assign(g, { ctx, cv, tex: tx, teclado: tec, enter });
  return g;
}
// texto de terminal no canvas do monitor: linhas verdes rolando
export function telaCodigo(pc, t, titulo = '') {
  const x = pc.ctx, W = pc.cv.width, H = pc.cv.height, r = P.rng(77); x.fillStyle = '#021006'; x.fillRect(0, 0, W, H);
  const rol = Math.floor(t * 9);
  for (let j = 0; j < 12; j++) { const rr = P.rng(1000 + j + rol); let px = 3 + Math.floor(rr() * 3) * 4; x.fillStyle = j === 11 ? '#b9ffc9' : '#39ff6a'; const n = 2 + Math.floor(rr() * 5); for (let k = 0; k < n; k++) { const L = 3 + Math.floor(rr() * 14); x.fillRect(px, 4 + j * 5, L, 2); px += L + 3; if (px > W - 8) break; } }
  if (Math.floor(t * 3) % 2) { x.fillStyle = '#b9ffc9'; x.fillRect(4, 65, 4, 3); }
  pc.tex.needsUpdate = true;
}

// ── a sala do Igor: sala preta, mesa de feltro verde, copo, celular, Igor sentado. Devolve as peças ──
export async function salaIgor(cena, o = {}) {
  const I = await T.igor(); cena.add(I.obj); I.obj.position.set(0, -.36, 0);
  const c = I.corpo; c.sentar();
  c.braco('R', [-.3, -.88, .38], [.86, -.22, .46], [.95, -.06, .3], -1.5); c.braco('L', [.3, -.85, .3], [-.25, -.55, .8], [-.4, -.2, .9]);
  I.assentar(); c.guardar();
  const hw = new THREE.Vector3(); c.osso('hand.R').getWorldPosition(hw); const Y = hw.y - .035;
  const mesa = T.mesaFeltro({ y: Y, d: .9 }); mesa.position.z = .5; cena.add(mesa);
  const copo = T.copoAgua(); copo.position.set(.72, Y, .62); cena.add(copo);
  const cel = T.celular(); cel.position.set(.42, Y, .6); cel.rotation.y = -.9; cena.add(cel);
  return { I, c, Y, mesa, copo, cel };
}
export const LUZ_SALA = { keyDir: [-.25, .8, .55], keyCor: '#e6efe2', fillDir: [.8, .1, .3], fillCor: '#1d5f37', amb: '#243a2b' };
