// ── THE GREEN PATH — A SILENT WAR · EPISÓDIO 1 (reformulado): cenários e peças novas (o v4 continua intacto em lib/v4.js) ──
// O alojamento veio da versão anterior (a única parte aprovada pelo diretor), sem os objetos de licença duvidosa.
// Objetos PSX convertidos: material/modelos/psx/<nome>.glb (tools/blender/psx_prop.py; Poly Haven = CC0, itch = ver ASSETS.md)
import * as P from './ps1.js';
import * as V from './v4.js';
import * as M from './modelo.js';
const { THREE } = P;
const PSX = n => 'material/modelos/psx/' + n + '.glb';

// objeto PSX com geometria PRÓPRIA (a luz assada fica nos vértices: clones não podem dividir a mesma geometria)
export async function prop(nome, o = {}) {
  const g = await V.peca(PSX(nome), { tex: o.tex ?? 128, verde: false, mat: { corVertice: true, ...(o.mat || {}) } });
  g.traverse(n => { if (n.isMesh) n.geometry = n.geometry.clone(); });
  if (o.altura) { const k = o.altura / g.tam.y; g.scale.setScalar(k); }
  if (o.esc) g.scale.multiplyScalar(o.esc);
  if (o.pos) g.position.set(...o.pos); if (o.rot != null) g.rotation.y = o.rot;
  return g;
}
const copia = g => { const c = g.clone(true); c.traverse(n => { if (n.isMesh) n.geometry = n.geometry.clone(); }); return c; };

// texto/placa desenhado num canvas (papel, aviso, calendário)
export function placa(w, h, px, desenha, o = {}) {
  const tx = P.textura(Math.round(w * px), Math.round(h * px), desenha, o);
  return new THREE.Mesh(new THREE.PlaneGeometry(w, h), P.mat({ mapa: tx, corVertice: true, lados: THREE.DoubleSide, ...(o.mat || {}) }));
}
// caixa com UV repetida pelo tamanho (tijolo/piso sem esticar) e cor por vértice (pra assar)
function bloco(w, h, d, tex, metro, pos) {
  const geo = new THREE.BoxGeometry(w, h, d), uv = geo.attributes.uv, nor = geo.attributes.normal;
  for (let i = 0; i < uv.count; i++) { const nx = Math.abs(nor.getX(i)), ny = Math.abs(nor.getY(i));
    const su = nx > .5 ? d : w, sv = ny > .5 ? d : h; uv.setXY(i, uv.getX(i) * su / metro[0], uv.getY(i) * sv / metro[1]); }
  const m = new THREE.Mesh(geo, P.mat({ mapa: tex, corVertice: true })); m.position.set(...pos); return m;
}

// ── ALOJAMENTO DO POSTO (pedido do diretor): antes era só um bloco verde transparente na frente da lojinha, sem porta,
//    sem nada dentro. Agora: fachada de tijolo com DUAS JANELAS de verdade (caixilho, travessa, vidro), PORTA de metal que
//    abre pra dentro (a.porta(0–1)), lâmpada fluorescente acesa e o quarto do frentista: cama com colchão e cobertor, cômoda,
//    estante com enlatados e caixas, mesa com rádio e luminária, cadeira de plástico, TV de tubo, ventilador de teto girando,
//    relógio, calendário, lixeira; do lado de fora máquina de refrigerante, ar-condicionado e aviso "SÓ FUNCIONÁRIOS".
//    Porta no centro da fachada: mundo (2, 0, −7) com o posto na origem; a.dentro / a.fora = pontos pra caminhar.
export async function alojamento(C) {
  const { posto } = C, loja = posto.loja, A = await import('./arh.js');
  posto.vitrine.visible = false;
  for (let i = 0; i < 3; i++) loja.children[i].visible = false;                          // janela/porta/janela soltas do pacote
  const parede = loja.children.find((c, i) => i >= 3 && c.isObject3D && c.modelo);
  let tij = null; parede?.traverse(n => { if (!tij && n.isMesh && n.material.uniforms?.uMapa?.value) tij = n.material.uniforms.uMapa.value; });
  if (tij) { tij.wrapS = tij.wrapT = THREE.RepeatWrapping; tij.needsUpdate = true; }
  const T = tij ?? P.TEX.concreto({ cor: '#6b4a3a', junta: '#3d2a22' }), MT = [4, 3];
  const g = new THREE.Group(); g.name = 'alojamento'; loja.add(g);
  const Z = 3, E = .2;                                                                    // fachada (z local da lojinha) e espessura
  // fachada: [x0, x1, y0, y1] dos pedaços de parede em volta de 2 janelas e da porta
  const JAN = [[-4.6, -1.9], [1.9, 4.6]], PORTA = [-.55, .55], PH = 2.15, J0 = .95, J1 = 2.25;
  const pedacos = [[-6, -4.6, 0, 3], [-1.9, PORTA[0], 0, 3], [PORTA[1], 1.9, 0, 3], [4.6, 6, 0, 3], [PORTA[0], PORTA[1], PH, 3]];
  for (const [a, b] of JAN) pedacos.push([a, b, 0, J0], [a, b, J1, 3]);
  for (const [x0, x1, y0, y1] of pedacos) g.add(bloco(x1 - x0, y1 - y0, E, T, MT, [(x0 + x1) / 2, (y0 + y1) / 2, Z]));
  // janelas: caixilho de metal escuro, travessa no meio, vidro esverdeado (dá pra ver dentro)
  const caix = P.mat({ cor: '#2b302d', corVertice: true }), vidro = P.mat({ cor: '#a9d9c4', opac: .16, lados: THREE.DoubleSide });
  for (const [a, b] of JAN) { const cx = (a + b) / 2, w = b - a, h = J1 - J0, cy = (J0 + J1) / 2;
    for (const [px, py, sx, sy] of [[cx, J0 + .03, w, .06], [cx, J1 - .03, w, .06], [a + .03, cy, .06, h], [b - .03, cy, .06, h], [cx, cy, .05, h], [cx, J0 + h * .55, w, .04]])
      g.add(P.caixa(sx, sy, .08, caix, { pos: [px, py, Z] }));
    g.add(P.caixa(w - .06, .05, .3, caix, { pos: [cx, J0 - .02, Z + .1] }));            // peitoril
    g.add(P.caixa(w, h, .01, vidro, { pos: [cx, cy, Z] })); }
  // porta de metal com visor, maçaneta e o aviso; dobradiça do lado −x, abre pra DENTRO (−z)
  const dob = new THREE.Group(); dob.position.set(PORTA[0], 0, Z); g.add(dob);
  const matPorta = P.mat({ cor: '#56645c', corVertice: true }), matEsc = P.mat({ cor: '#1d211f', corVertice: true });
  dob.add(P.caixa(PORTA[1] - PORTA[0] - .02, PH - .02, .05, matPorta, { pos: [(PORTA[1] - PORTA[0]) / 2, PH / 2, 0] }));
  dob.add(P.caixa(.28, .34, .06, vidro, { pos: [.55, 1.55, 0] }), P.caixa(.32, .38, .055, matEsc, { pos: [.55, 1.55, -.002] }));
  dob.add(P.caixa(.12, .03, .05, P.mat({ cor: '#c9c3a8', corVertice: true }), { pos: [.95, 1.0, .05] }), P.caixa(.12, .03, .05, P.mat({ cor: '#c9c3a8', corVertice: true }), { pos: [.95, 1.0, -.05] }));
  const aviso = placa(.5, .16, 320, (x, w, h) => { x.fillStyle = '#e8d34a'; x.fillRect(0, 0, w, h); x.fillStyle = '#111'; x.font = `900 ${h * .42}px 'DejaVu Sans', sans-serif`;
    x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText('SÓ FUNCIONÁRIOS', w / 2, h / 2 + 1, w * .92); }, { mat: { semLuz: true } });
  aviso.position.set(.55, 1.22, .03); dob.add(aviso);
  for (const [px, sy, py] of [[PORTA[0] - .04, PH, PH / 2], [PORTA[1] + .04, PH, PH / 2]]) g.add(P.caixa(.08, sy, E + .04, caix, { pos: [px, py, Z] }));
  g.add(P.caixa(PORTA[1] - PORTA[0] + .16, .08, E + .04, caix, { pos: [0, PH + .04, Z] }));
  // interior: piso, forro, lâmpada
  g.add(bloco(11.8, .02, 7.8, P.TEX.azulejo({ cor: '#8f9a8a', rejunte: '#5f685c' }), [.6, .6], [0, .011, -1]));
  g.add(bloco(11.8, .02, 7.8, P.TEX.concreto({ cor: '#6f716c', junta: '#5a5c58' }), [1.2, 1.2], [0, 2.93, -1]));
  for (const x of [-3.6, 2.4]) { g.add(P.caixa(1.25, .06, .12, P.mat({ cor: '#3a3d3a' }), { pos: [x, 2.89, -1] })); g.add(P.caixa(1.15, .04, .06, P.mat({ cor: '#fff6dc', semLuz: true }), { pos: [x, 2.85, -1] })); }
  // móveis e objetos (posições locais da lojinha: frente z=3, fundo z=−5, laterais x=±6)
  const P2 = async (n, o) => { const p = await prop(n, o); g.add(p); return p; };
  const cama = await P2('old_bed_frame', { pos: [5.05, 0, -3.35] });
  const colch = P.caixa(.82, .16, 1.88, P.mat({ cor: '#c9c4b0', corVertice: true }), { pos: [5.05, .5, -3.35] }); g.add(colch);
  g.add(P.caixa(.86, .06, 1.3, P.mat({ cor: '#2f5a3d', corVertice: true }), { pos: [5.05, .6, -2.95] }));                     // cobertor verde
  g.add(P.caixa(.55, .1, .32, P.mat({ cor: '#e7e2d2', corVertice: true }), { pos: [5.05, .62, -4.1] }));                     // travesseiro
  await P2('drawer_cabinet', { pos: [2.9, 0, -4.65] });
  const est = await P2('steel_frame_shelves_02', { pos: [-5.55, 0, -4.6], altura: 2.0 });
  const latas = await prop('russian_food_cans_01'), caixa = await prop('cardboard_box_01', { altura: .32 });
  for (const [k, y] of [[0, .62], [1, 1.07], [2, 1.52]]) { const l = copia(latas); l.position.set(-5.55 + (k - 1) * .12, y, -4.6); g.add(l); }
  for (const [x, z, y, r] of [[-5.3, -2.6, 0, .2], [-5.35, -2.55, .32, -.3], [-4.8, -3.2, 0, .9]]) { const c = copia(caixa); c.position.set(x, y, z); c.rotation.y = r; g.add(c); }
  await P2('metal_jerrycan_green', { pos: [-4.9, 0, -4.7], altura: .45 });
  // parede divisória: à direita (x > −1,3) o QUARTO do frentista, à esquerda o DEPÓSITO (estante, caixas, galão)
  g.add(bloco(.15, 2.9, 7.8, P.TEX.concreto({ cor: '#b8ad94', junta: '#9e947d' }), [1.2, 1.2], [-1.3, 1.45, -1]));
  // armários de metal encostados na divisória (4 portas com respiro e cadeado)
  const texArm = P.textura(16, 48, (x, w, h) => { x.fillStyle = '#56655d'; x.fillRect(0, 0, w, h); x.fillStyle = '#3c4741'; x.fillRect(0, 0, 1, h); x.fillRect(w - 1, 0, 1, h);
    for (let i = 0; i < 4; i++) x.fillRect(4, 5 + i * 2, w - 8, 1); x.fillStyle = '#c9c3a8'; x.fillRect(w - 4, h * .5, 2, 3); });
  for (let i = 0; i < 4; i++) g.add(P.caixa(.5, 1.85, .48, P.mat({ mapa: texArm, corVertice: true }), { pos: [-.98, .925, 1.6 - i * .52], rot: [0, Math.PI / 2, 0] }));
  // escrivaninha no fundo com rádio, luminária e fichário; cadeira; mesa do meio com 2 cadeiras e tapete
  await P2('metal_office_desk', { pos: [.75, 0, -4.55], esc: .7 });
  await P2('boombox', { pos: [.2, .56, -4.6], altura: .26 });
  await P2('desk_lamp_arm_01', { pos: [1.4, .56, -4.6], altura: .5, rot: -.4 });
  await P2('binder_notebook', { pos: [.8, .56, -4.45], esc: .8, rot: .3 });
  await P2('plastic_monobloc_chair_01', { pos: [.8, 0, -3.7], rot: Math.PI + .25 });
  g.add(P.caixa(2.2, .01, 1.6, P.mat({ mapa: P.TEX.concreto({ cor: '#6a3b2c', junta: '#4d2a20' }), corVertice: true }), { pos: [2.3, .022, -.8] }));     // tapete
  g.add(P.caixa(1.1, .05, .75, P.mat({ cor: '#7a5a3c', corVertice: true }), { pos: [2.3, .74, -.8] }));
  for (const [x, z] of [[1.85, -1.1], [2.75, -.5], [1.85, -.5], [2.75, -1.1]]) g.add(P.caixa(.05, .72, .05, P.mat({ cor: '#3a2c20', corVertice: true }), { pos: [x, .36, z] }));
  await P2('plastic_monobloc_chair_01', { pos: [2.3, 0, -1.55], rot: .1 });
  await P2('plastic_monobloc_chair_01', { pos: [3.25, 0, -.7], rot: -Math.PI / 2 - .2 });
  const marmita = P.caixa(.18, .06, .14, P.mat({ cor: '#c8ccc8', corVertice: true }), { pos: [2.1, .8, -.9] }); g.add(marmita);
  await P2('can_rusted', { pos: [2.55, .77, -.65], altura: .12 });
  await P2('side_table_01', { pos: [3.6, 0, -3.9], esc: .9 });
  await P2('crt_tv', { pos: [3.6, .5, -3.95], altura: .42, rot: Math.PI });   // PS1-Style CRT TV (pepperonijabroni, CC0)
  await P2('wall_clock', { pos: [2.6, 2.3, -4.88] });
  await P2('metal_trash_can', { pos: [1.2, 0, 2.4], altura: .55 });
  const ventilador = await P2('ceiling_fan', { pos: [2.3, 2.4, -.8], altura: .5 });
  const cal = placa(.42, .6, 96, (x, w, h, r) => { x.fillStyle = '#efe9da'; x.fillRect(0, 0, w, h); x.fillStyle = '#2f6b45'; x.fillRect(0, 0, w, h * .42);
    x.fillStyle = '#ffd23a'; x.font = `900 ${h * .09}px 'DejaVu Sans', sans-serif`; x.textAlign = 'center'; x.fillText('POSTO VERDE', w / 2, h * .25);
    x.fillStyle = '#333'; for (let i = 0; i < 5; i++) for (let j = 0; j < 7; j++) x.fillRect(4 + j * (w - 8) / 7, h * .48 + i * h * .1, (w - 8) / 7 - 2, h * .07); });
  cal.position.set(3.9, 1.65, -4.88); g.add(cal);
  // luz de dentro (fluorescente quente) + a luz do posto que bate na fachada
  const mun = (x, y, z) => loja.localToWorld(new THREE.Vector3(x, y, z)).toArray();
  posto.updateMatrixWorld(true);
  A.assar(g, [{ pos: mun(-3.6, 2.6, -1), cor: '#d8d0b0', raio: 5, int: 1.6 }, { pos: mun(2.4, 2.6, -1), cor: '#ffe2a8', raio: 7.5, int: 3.2 },
    ...posto.luzes().map(l => ({ ...l, int: (l.int ?? 1) * .8 }))], '#1a2620');
  return {
    grupo: g, porta: k => { dob.rotation.y = 1.45 * P.clamp(k); }, cama,
    // pontos no MUNDO pro frentista: fora da porta, logo depois da porta, perto da cama
    fora: mun(0, 0, Z + .75), soleira: mun(0, 0, Z - .1), dentro: mun(.3, 0, Z - 1.6), cama2: mun(4.2, 0, -2.6), mesa: mun(2.3, 0, -1.6),
    macaneta: () => dob.localToWorld(new THREE.Vector3(.95, 1.0, .07)),
    atualizar: t => { ventilador.rotation.y = t * 3.2; },
  };
}

// ── PISTOLA (feita aqui, sem pacote): ferrolho, armação, cano, coronha inclinada e guarda-mato, metal escuro.
//    Eixos locais: cano pra +x, coronha pra −y; a origem é o ponto onde a coronha encontra a armação (onde a mão fecha).
export function pistola(o = {}) {
  const g = new THREE.Group(); g.name = 'pistola';
  const metal = P.mat({ cor: o.cor ?? '#1f2225', corVertice: true }), escuro = P.mat({ cor: '#151719', corVertice: true });
  g.add(P.caixa(.19, .032, .028, metal, { pos: [.075, .036, 0] }));                      // ferrolho
  g.add(P.caixa(.012, .012, .012, escuro, { pos: [.172, .036, 0] }));                    // boca do cano
  for (let i = 0; i < 6; i++) g.add(P.caixa(.004, .026, .03, escuro, { pos: [-.005 + i * .009, .036, 0] }));   // serrilha
  g.add(P.caixa(.15, .022, .026, metal, { pos: [.055, .008, 0] }));                      // armação
  const coronha = P.caixa(.034, .115, .03, escuro, { pos: [0, -.055, 0] }); coronha.rotation.z = .22; g.add(coronha);
  g.add(P.caixa(.05, .006, .02, metal, { pos: [.055, -.03, 0] }), P.caixa(.006, .03, .02, metal, { pos: [.08, -.015, 0] }));   // guarda-mato
  g.add(P.caixa(.006, .018, .008, escuro, { pos: [.045, -.012, 0] }));                   // gatilho
  if (o.esc) g.scale.setScalar(o.esc);
  return g;
}
