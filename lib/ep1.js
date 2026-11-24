// ── THE GREEN PATH — A SILENT WAR · EPISÓDIO 1: cenários e peças novas (o v4 continua intacto em lib/v4.js) ──
// Objetos PSX convertidos: material/modelos/psx/<nome>.glb (tools/blender/psx_prop.py; Poly Haven = CC0, itch = ver ASSETS.md)
import * as P from './ps1.js';
import * as V from './v4.js';
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
  await P2('psx_tv', { pos: [3.6, .5, -3.95], altura: .42 });
  await P2('wall_clock', { pos: [2.6, 2.3, -4.88] });
  await P2('metal_trash_can', { pos: [1.2, 0, 2.4], altura: .55 });
  const ventilador = await P2('ceiling_fan', { pos: [2.3, 2.4, -.8], altura: .5 });
  const cal = placa(.42, .6, 96, (x, w, h, r) => { x.fillStyle = '#efe9da'; x.fillRect(0, 0, w, h); x.fillStyle = '#2f6b45'; x.fillRect(0, 0, w, h * .42);
    x.fillStyle = '#ffd23a'; x.font = `900 ${h * .09}px 'DejaVu Sans', sans-serif`; x.textAlign = 'center'; x.fillText('POSTO VERDE', w / 2, h * .25);
    x.fillStyle = '#333'; for (let i = 0; i < 5; i++) for (let j = 0; j < 7; j++) x.fillRect(4 + j * (w - 8) / 7, h * .48 + i * h * .1, (w - 8) / 7 - 2, h * .07); });
  cal.position.set(3.9, 1.65, -4.88); g.add(cal);
  // lado de fora: máquina de refrigerante, ar-condicionado na lateral, a lixeira já existente
  await P2('vending', { pos: [2.6, 0, 3.55], altura: 1.85, rot: 0 });
  await P2('ar_condicionado', { pos: [5.2, 2.35, 3.25], altura: .5, rot: 0 });
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

// ── COMPUTADOR NOVO DO IGOR (pedido do diretor: o antigo nem tinha mouse) — monitor CRT, torre, teclado e MOUSE do pacote de
//    escritório (OFFICE). A tela continua sendo o canvas do computador antigo (vídeo, código, chiado): só a carcaça muda.
//    Parâmetros de encaixe da tela no monitor: o.k (escala do monitor), o.tela [y, z, larg, alt].
export async function computadorNovo(sala, o = {}) {
  const { pc } = sala, OF = 'material/modelos/office/OFFICE/computers/';
  const tela = pc.children[3];
  pc.children.forEach((c, i) => { if (i !== 3 && c !== pc.teclado) c.visible = false; });
  pc.teclado.children.forEach(c => { c.visible = false; });                       // o teclado velho some (o objeto fica: a mão do Igor mira no Enter dele)
  const K = o.k ?? .78, mon = await V.peca(OF + 'computer_monitor.glb', { tex: 256, verde: false });
  mon.scale.setScalar(K); mon.rotation.y = o.rotMon ?? 0; mon.position.set(0, 0, o.zMon ?? .03); pc.add(mon);
  const [ty, tz, tw, th] = o.tela ?? [.25, -.2, .32, .24];
  tela.position.set(0, ty, tz); tela.scale.set(tw / .36, th / .27, 1);
  const torre = await V.peca(OF + 'computer_tower.glb', { tex: 256, verde: false }); torre.scale.setScalar(.75); torre.rotation.y = Math.PI / 2; torre.position.set(.5, -.09, .05); pc.add(torre);
  const tec = await V.peca(OF + 'computer_keyboard.glb', { tex: 256, verde: false }); tec.scale.setScalar(.66); tec.rotation.y = o.rotMon ?? 0; tec.position.set(0, -.09, -.36); pc.add(tec);
  const mouse = await V.peca(OF + 'computer_mouse.glb', { tex: 256, verde: false }); mouse.scale.setScalar(.9); mouse.rotation.y = o.rotMon ?? 0; mouse.position.set(.32, -.09, -.36); pc.add(mouse);
  const pad = P.caixa(.2, .004, .17, P.mat({ cor: '#1d2a22' }), { pos: [.32, -.088, -.36] }); pc.add(pad);
  return { mon, torre, teclado: tec, mouse, mousePad: pad };
}

// ── PORTA-BUNKER da sala do Igor (pedido: "a porta é quase um bunker"). A sala não tinha parede na frente: agora tem parede de concreto
//    em z = 4,1 com o vão da porta (x de −1,85 a −0,55); porta de aço de 22 cm, dobradiça do lado −x, volante de trava, 4 ferrolhos, faixa
//    zebrada amarela/preta no batente e uma luz de alarme vermelha em cima. b.fechar(0 aberta → 1 fechada) · b.trancar(0–1: volante gira
//    e os ferrolhos entram) · b.alarme(k, t) · b.puxador (mundo) pra as mãos.
export function portaBunker(cena) {
  const g = new THREE.Group(); g.name = 'porta-bunker'; cena.add(g);
  const Z = 4.1, X0 = -1.85, X1 = -.55, H = 2.25, W = X1 - X0;
  const conc = P.mat({ mapa: P.TEX.concreto({ cor: '#3d4440', junta: '#2b302d' }), rep: [3, 2] }), aco = P.mat({ cor: '#4b5550' }), acoE = P.mat({ cor: '#2a302d' });
  for (const [a, b] of [[-4.2, X0 - .12], [X1 + .12, 4.2]]) g.add(P.caixa(b - a, 3.4, .35, conc, { pos: [(a + b) / 2, 1.7, Z] }));
  g.add(P.caixa(W + .24, 3.4 - H - .12, .35, conc, { pos: [(X0 + X1) / 2, (3.4 + H + .12) / 2, Z] }));
  const zeb = P.textura(16, 16, (x, w, h) => { for (let i = -h; i < w; i += 8) { x.fillStyle = '#e8c21a'; x.beginPath(); x.moveTo(i, 0); x.lineTo(i + 4, 0); x.lineTo(i + 4 + h, h); x.lineTo(i + h, h); x.fill(); } }, { niveis: 0 });
  const zm = P.mat({ mapa: zeb, cor: '#ffffff' }); zm.uniforms.uRep.value.set(1, 8);
  g.add(P.caixa(.12, H + .12, .4, zm, { pos: [X0 - .06, (H + .12) / 2, Z] }), P.caixa(.12, H + .12, .4, zm, { pos: [X1 + .06, (H + .12) / 2, Z] }));
  const topo = P.caixa(W + .24, .12, .4, P.mat({ mapa: zeb }), { pos: [(X0 + X1) / 2, H + .06, Z] }); topo.material.uniforms.uRep.value.set(8, 1); g.add(topo);
  // a porta (abre pra FORA, +z): pivô na dobradiça
  const piv = new THREE.Group(); piv.position.set(X0, 0, Z - .05); g.add(piv);
  piv.add(P.caixa(W - .02, H - .02, .22, aco, { pos: [W / 2, H / 2, 0] }));
  for (const y of [.35, 1.1, 1.85]) piv.add(P.caixa(W - .14, .1, .03, acoE, { pos: [W / 2, y, -.125] }));              // reforços do lado de dentro
  for (const [x, y] of [[.12, .12], [W - .12, .12], [.12, H - .12], [W - .12, H - .12]]) piv.add(P.cilindro(.025, .025, .03, acoE, { seg: 6, pos: [x, y, -.125], rot: [Math.PI / 2, 0, 0] }));
  const vol = new THREE.Group(); vol.position.set(W * .55, 1.1, -.17); piv.add(vol);
  vol.add(new THREE.Mesh(new THREE.TorusGeometry(.2, .022, 4, 12), P.mat({ cor: '#b8261c' })));
  for (let i = 0; i < 3; i++) vol.add(P.caixa(.4, .03, .03, P.mat({ cor: '#7a1a14' }), { rot: [0, 0, i * Math.PI / 3] }));
  vol.add(P.cilindro(.05, .05, .08, acoE, { seg: 8, rot: [Math.PI / 2, 0, 0], pos: [0, 0, .03] }));
  const ferr = []; for (const y of [.4, .9, 1.4, 1.9]) { const f = P.caixa(.22, .05, .05, P.mat({ cor: '#9aa49c' }), { pos: [W - .1, y, -.13] }); piv.add(f); ferr.push(f); }
  // luz de alarme em cima da porta
  const lampG = new THREE.Group(); lampG.position.set((X0 + X1) / 2, H + .32, Z - .2); g.add(lampG);
  lampG.add(P.caixa(.16, .06, .1, acoE)); const bulbo = P.esfera(.06, P.mat({ cor: '#3a0806', semLuz: true }), { seg: 6, segV: 4, pos: [0, .06, 0] }); lampG.add(bulbo);
  const A = (k, t) => { const gira = (Math.sin(t * 9.5) + 1) / 2; bulbo.material.uniforms.uCor.value.set('#3a0806').lerp(new THREE.Color('#ff3018'), k * (.3 + .7 * gira)); };
  return { grupo: g, piv, vol, Z, X0, X1,
    fechar: k => { piv.rotation.y = -1.55 * (1 - P.clamp(k)); },                      // 0 = aberta (escancarada pra fora), 1 = fechada
    trancar: k => { vol.rotation.z = P.clamp(k) * Math.PI * 2.5; ferr.forEach(f => { f.position.x = W - .1 + .16 * P.clamp(k); }); },
    alarme: A, puxador: () => piv.localToWorld(new THREE.Vector3(W - .12, 1.1, -.17)), volante: () => vol.getWorldPosition(new THREE.Vector3()) };
}

// ── SALA SECRETA atrás da estante da direita (pedido: o botão vermelho aciona o alerta e "uma sala secreta se abre, tomada pela luz verde
//    da tela"). A parede do fundo (caixa 6 × 3,4 em z = −1,7) é trocada por uma com abertura em x 0,95–1,9; a estante (com os livros) desliza
//    pra +x. Lá dentro: paredes de metal, bancada com 3 monitores verdes, servidores com LEDs. s.abrir(0–1) · s.luz(t) devolve a cor/força
//    da luz verde pra P.luz · s.botao: o botão vermelho (com tampa amarela) na quina da mesa; s.apertar(k).
export async function salaSecreta(cena, Y) {
  let parede = null; cena.traverse(n => { const p = n.geometry?.parameters; if (n.isMesh && p && Math.abs(p.width - 6) < .01 && Math.abs(p.height - 3.4) < .01 && Math.abs(n.position.z + 1.7) < .01) parede = n; });
  if (parede) parede.visible = false;
  const g = new THREE.Group(); g.name = 'sala-secreta'; cena.add(g);
  const pm = P.mat({ cor: '#0f1511' }), A0 = .95, A1 = 1.9, AH = 2.3;
  g.add(P.caixa(A0 + 3, 3.4, .1, pm, { pos: [(A0 - 3) / 2, 1.7, -1.7] }), P.caixa(3 - A1, 3.4, .1, pm, { pos: [(A1 + 3) / 2, 1.7, -1.7] }), P.caixa(A1 - A0, 3.4 - AH, .1, pm, { pos: [(A0 + A1) / 2, (3.4 + AH) / 2, -1.7] }));
  // a estante e os livros dela (x ≈ 1,42, z ≈ −1,43) passam pra um grupo que desliza
  const corre = new THREE.Group(); cena.add(corre); const mover = [];
  cena.traverse(n => { if (n.parent === cena && n !== corre && n !== g && Math.abs(n.position.z + 1.425) < .03 && n.position.x > 0.9 && n.position.x < 1.95) mover.push(n); });
  mover.forEach(n => corre.attach(n));
  // dentro: corredor de metal com bancada e telas verdes
  const met = P.mat({ mapa: P.TEX.concreto({ cor: '#2c3631', junta: '#1d2420' }), rep: [2, 2] }), dent = new THREE.Group(); dent.position.set((A0 + A1) / 2, 0, -1.75); g.add(dent);
  dent.add(P.caixa(3.2, .05, 3, met, { pos: [0, .025, -1.5] }), P.caixa(3.2, .05, 3, met, { pos: [0, 2.6, -1.5] }), P.caixa(.1, 2.6, 3, met, { pos: [-1.6, 1.3, -1.5] }), P.caixa(.1, 2.6, 3, met, { pos: [1.6, 1.3, -1.5] }), P.caixa(3.2, 2.6, .1, met, { pos: [0, 1.3, -3] }));
  dent.add(P.caixa(2.4, .08, .7, P.mat({ cor: '#232a26' }), { pos: [0, .78, -2.55] }));
  const telas = [];
  for (const [x, y] of [[-.75, 1.25], [0, 1.3], [.75, 1.25], [0, 1.85]]) { const tx = P.textura(32, 24, (c, w, h, r) => { c.fillStyle = '#021006'; c.fillRect(0, 0, w, h); c.fillStyle = '#39ff6a'; for (let j = 2; j < h - 2; j += 3) c.fillRect(2 + Math.floor(r() * 4), j, 6 + Math.floor(r() * 18), 1); }, { seed: Math.floor(x * 10 + y * 7) });
    const t = P.malha(new THREE.PlaneGeometry(.62, .44), P.mat({ mapa: tx, semLuz: true }), { pos: [x, y, -2.86] }); dent.add(t, P.caixa(.7, .52, .08, P.mat({ cor: '#111513' }), { pos: [x, y, -2.92] })); telas.push(t); }
  for (const x of [-1.35, 1.35]) { dent.add(P.caixa(.4, 2.0, .6, P.mat({ cor: '#161b18' }), { pos: [x, 1.0, -2.2] }));
    for (let i = 0; i < 8; i++) dent.add(P.caixa(.03, .02, .01, P.mat({ cor: i % 3 ? '#39ff6a' : '#ffd23a', semLuz: true }), { pos: [x + (x > 0 ? -.21 : .21), .4 + i * .2, -2.2], rot: [0, Math.PI / 2, 0] })); }
  const brilho = P.malha(new THREE.PlaneGeometry(A1 - A0, AH), P.mat({ cor: '#39ff6a', semLuz: true, aditivo: true, opac: 0, lados: THREE.DoubleSide }), { pos: [(A0 + A1) / 2, AH / 2, -1.66] }); g.add(brilho);
  // BOTÃO VERMELHO na quina direita da mesa (lado do Igor): caixa amarela, cogumelo vermelho
  const botao = new THREE.Group(); botao.position.set(.95, Y, .2); cena.add(botao);
  botao.add(P.caixa(.12, .05, .12, P.mat({ cor: '#e8c21a' }), { pos: [0, .025, 0] }));
  const cog = P.cilindro(.035, .04, .035, P.mat({ cor: '#d01a12' }), { seg: 8, pos: [0, .068, 0] }); botao.add(cog);
  const botaoLuz = P.cilindro(.036, .041, .002, P.mat({ cor: '#ff3018', semLuz: true, aditivo: true, opac: 0 }), { seg: 8, pos: [0, .087, 0] }); botao.add(botaoLuz);
  return { grupo: g, corre, botao: () => cog.getWorldPosition(new THREE.Vector3()),
    apertar: k => { cog.position.y = .068 - .016 * P.clamp(k); botaoLuz.material.uniforms.uOpac.value = .9 * P.clamp(k); },
    abrir: k => { corre.position.x = 1.15 * P.suave(0, 1, k); brilho.material.uniforms.uOpac.value = .55 * P.suave(.05, .6, k); },
    telas: t => telas.forEach((s, i) => { s.material.uniforms.uCor.value.setScalar(.85 + .15 * Math.sin(t * 7 + i)); }) };
}
