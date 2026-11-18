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
  return (plano, t, quem) => { let v = 0; for (const f of V[plano] ?? []) { if (quem && f.quem !== quem) continue; const q = Math.round((t - f.t) * 30); if (q >= 0 && q < f.env.length) v = Math.max(v, f.env[q]); } return v; };
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
// carro por fora com os dois dentro (o vidro do sedã é vazado): Adryan ao volante, Nicolas no passageiro
export async function carroFora(cena) {
  const car = await F.carro(); cena.add(car);
  const Ad = await E4.ator('adryan'), Ni = await E4.ator('nicolas'); car.add(Ad.obj, Ni.obj);
  Ad.obj.scale.setScalar(.88); Ni.obj.scale.setScalar(.86);
  const banco = { x: .35, y: .67, z: .3 }, pass = { x: -.35, y: .67, z: .32 };
  const mal = T.maleta(); mal.scale.setScalar(.85); car.add(mal);
  const sentados = () => { sentar(Ad, banco, { dy: -.03 }); sentar(Ni, pass, { dy: -.03 }); mal.position.set(-.35, .78, .52); mal.rotation.set(-.05, 0, 0); };
  sentados();
  return { car, Ad, Ni, mal, sentados };
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

// carro por dentro com os dois sentados: Adryan dirige (x=+.35), Nicolas no passageiro com a maleta no colo
export async function carroComDupla(cena) {
  const car = await F.interiorCarro(); cena.add(car);
  const Ad = await E4.ator('adryan'), Ni = await E4.ator('nicolas'); cena.add(Ad.obj, Ni.obj);
  Ad.obj.scale.setScalar(.88); Ni.obj.scale.setScalar(.86);
  sentar(Ad, car.assento, { dy: -.03 }); sentar(Ni, car.passageiro, { dy: -.03 });
  const mal = T.maleta(); mal.scale.setScalar(.85); cena.add(mal);
  const colo = () => { Ni.obj.updateMatrixWorld(true); const a = new THREE.Vector3(), b = new THREE.Vector3(); Ni.osso('thigh.L').getWorldPosition(a); Ni.osso('thigh.R').getWorldPosition(b); const p = a.add(b).multiplyScalar(.5); mal.position.set(p.x, p.y + .1, p.z + .14); mal.rotation.set(-.05, 0, 0); };
  colo();
  return { car, Ad, Ni, mal, colo };
}

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
