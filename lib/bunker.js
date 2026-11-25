// ── SEQUÊNCIA DO BUNKER (cenas 63–68 do EP1) — tudo o que as cenas COMPARTILHAM, pra continuidade (MANUAL DE DIREÇÃO, regra 2):
//    a mesma sala, as mesmas posições (entrega/ep1/PLANO_SEQUENCIA_BUNKER.md), a câmera = OLHOS DO ADRYAN (regra 1), a caminhada por
//    percurso e a tela do monitor mostrando o terminal DENTRO do monitor (nada de "tela cheia de fora").
import * as P from './ps1.js';
import * as F from './filme.js';
import * as V from './v4.js';
import * as T from './tgp.js';
import * as E4 from './elenco4.js';
import * as E from './ep1.js';
import * as K from './terminal.js';
const { THREE } = P;
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);

// GEOGRAFIA ÚNICA (metros, mundo). Igor de frente pro PC = rotação ANG (1,1); frente dele f = (0,89; 0,45); a ESQUERDA dele aponta pro fundo.
export const GEO = {
  PORTA: [-.7, 3.6], AD_FRENTE: [-.12, 1.32], GU_FRENTE: [-.95, 1.62],
  A: [-.85, .2],                                                              // ao lado do ombro DIREITO do Igor, entre a ponta da mesa e o arquivo: tela e MOUSE à vista (linhas de visão conferidas)
  CAMINHO_A: [[-.12, 1.32], [-.86, 1.12], [-.85, .2]],                        // entra pelo corredor entre a mesa e o arquivo
  RECUO: [-.35, 1.25], CAMINHO_RECUO: [[-.85, .2], [-.82, .88], [-.35, 1.25]],          // 67: com a sirene, o Adryan sai do corredor pra sala aberta
  IG_PE: [-.8, -.82],                                                       // 67→68: onde o Igor se levanta e fica
  FICHAS: [.06, .56],                                                          // a pasta com as 4 fichas (63: o Igor abre; 64–68: fechada no mesmo lugar)
  MALETA: [-.45, .6],                                                         // na frente da mesa, à direita do Igor (fora da linha de visão do mouse)
  BOTAO: [-.48, .2], IG_LEVANTA: [-.9, -.3],
};

// caminhada contínua por um percurso (sem parar em cada canto): arranca e para só nas pontas; o corpo vira suave na direção do passo
export function caminharPor(A, pts, t, t0, t1, o = {}) {
  const seg = [], L = [0]; for (let i = 1; i < pts.length; i++) { const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); seg.push(d); L.push(L[i - 1] + d); }
  const tot = L[L.length - 1], u0 = P.clamp((t - t0) / (t1 - t0)), e = o.ease ?? .12, v = 1 / (1 - e);
  const u = u0 < e ? v * u0 * u0 / (2 * e) : u0 > 1 - e ? 1 - v * (1 - u0) ** 2 / (2 * e) : v * (u0 - e / 2), s = u * tot;
  let i = 0; while (i < seg.length - 1 && s > L[i + 1]) i++;
  const k = seg[i] ? (s - L[i]) / seg[i] : 0, x = P.lerp(pts[i][0], pts[i + 1][0], k), z = P.lerp(pts[i][1], pts[i + 1][1], k);
  A.obj.position.set(x, 0, z);
  const dirDe = j => Math.atan2(pts[j + 1][0] - pts[j][0], pts[j + 1][1] - pts[j][1]), ang = (a, b, w) => { let d = ((b - a + Math.PI * 3) % (Math.PI * 2)) - Math.PI; return a + d * w; };
  let r = dirDe(i); if (i < seg.length - 1) { const falta = L[i + 1] - s; if (falta < .35) r = ang(r, dirDe(i + 1), (1 - falta / .35) * .5); }
  if (i > 0) { const andou = s - L[i]; if (andou < .35) r = ang(dirDe(i - 1), r, .5 + andou / .35 * .5); }
  A.obj.rotation.y = r;
  const andando = t > t0 && t < t1, passo = A.passada ?? 1.3;
  if (andando) { const parado = 1 - Math.min(P.suave(t0, t0 + .2, t), 1 - P.suave(t1 - .2, t1, t)); A.pose('walk', s / passo * A.dur('walk'), 'idle', parado, t); }
  return andando;
}

// MANUAL regra 5 (física): todo objeto solto da sala DESCE até a superfície que estiver embaixo (mesa, prateleira ou chão). Os itens da sala
// vieram da mesa antiga (maior): na mesa nova alguns ficavam no ar (copo, pasta) e os livros boiavam 5–15 cm acima das prateleiras.
// Não mexe no que é preso em parede/teto (relógio, quadro, luminária pendurada) nem nos personagens.
export function assentarSoltos(cena, fora = []) {
  cena.updateMatrixWorld(true);
  const visivel = o => { for (let p = o; p; p = p.parent) if (!p.visible) return false; return true; };   // peça de objeto ESCONDIDO não apoia nada (a mesa antiga)
  const malhas = []; cena.traverse(o => { if (o.isMesh && visivel(o)) malhas.push(o); });
  const raizDe = o => { let p = o; while (p.parent && p.parent !== cena) p = p.parent; return p; };
  const ray = new THREE.Raycaster(), movidos = [];
  for (const r of [...cena.children]) {
    if (fora.includes(r) || !r.visible || r.isLight) continue;
    const bb = new THREE.Box3().setFromObject(r); if (!isFinite(bb.min.x)) continue;
    const tam = bb.getSize(V3(0, 0, 0)), nome = (r.name || '');
    if (Math.max(tam.x, tam.z) > .9 || tam.y > 1.2 || bb.min.y < .02 || bb.min.y > 2.2 || /relogio|clock|quadro|lamp|luz|porta|parede|sala-secreta|ator/i.test(nome)) continue;
    let k = null;
    r.traverse(o => { if (o.isMesh && /wall_clock|hanging|ceiling/i.test(o.name)) k = 'parede'; }); if (k) continue;
    const c = bb.getCenter(V3(0, 0, 0)); let menor = 99;
    for (const [dx, dz] of [[0, 0], [-.3, -.3], [.3, -.3], [-.3, .3], [.3, .3]]) {           // centro e 4 cantos: apoia no ponto mais alto embaixo
      ray.set(V3(c.x + dx * tam.x, bb.min.y + .004, c.z + dz * tam.z), V3(0, -1, 0)); ray.far = 2.5;
      const h = ray.intersectObjects(malhas.filter(m => raizDe(m) !== r), false)[0]; if (h) menor = Math.min(menor, h.distance - .004); }
    if (menor > .015 && menor < 2.4) { r.position.y -= menor; movidos.push([nome || r.type, +menor.toFixed(2)]); }
  }
  cena.updateMatrixWorld(true); window.__assentados = movidos; return movidos;
}

// ESTANTES: a sala põe os livros/fichários de 50 em 50 cm, mas as prateleiras da estante não têm esse passo — blocos de livros ficavam no
// meio do vão, em cima da ponta de um fichário. Aqui cada item vai pra PRATELEIRA da sua fileira (as tábuas são achadas por raio).
export function arrumarEstantes(cena) {
  cena.updateMatrixWorld(true);
  const tem = (r, re) => { let s = false; r.traverse(o => { if (o.isMesh && re.test(o.name)) s = true; }); return s; };
  const estantes = cena.children.filter(r => r.visible && tem(r, /book_case/)), itens = cena.children.filter(r => r.visible && !tem(r, /book_case/) && tem(r, /^books|file_binder/));
  const log = [];
  for (const e of estantes) {
    const be = new THREE.Box3().setFromObject(e), malhas = []; e.traverse(o => { if (o.isMesh) malhas.push(o); });
    for (const it of itens) {
      const bi = new THREE.Box3().setFromObject(it), c = bi.getCenter(V3(0, 0, 0)), h = bi.max.y - bi.min.y;
      if (c.x < be.min.x || c.x > be.max.x || c.z < be.min.z - .2 || c.z > be.max.z + .2) continue;
      const hits = new THREE.Raycaster(V3(c.x, be.max.y + .2, c.z), V3(0, -1, 0), 0, 5).intersectObjects(malhas, false)
        .filter(x => x.face && x.face.normal.clone().transformDirection(x.object.matrixWorld).y > .5).map(x => x.point.y).sort((a, b) => a - b);
      const tabuas = []; for (const y of hits) if (!tabuas.length || y - tabuas[tabuas.length - 1] > .05) tabuas.push(y);
      const fila = Math.max(0, Math.round((it.position.y - .1) / .5)), base = tabuas[fila]; if (base === undefined) { it.visible = false; continue; }
      const teto = tabuas[fila + 1] ?? be.max.y; if (base + h > teto - .01) { const k = (teto - .02 - base) / h; it.scale.multiplyScalar(k); }
      it.updateMatrixWorld(true); const b2 = new THREE.Box3().setFromObject(it); it.position.y += base - b2.min.y; it.updateMatrixWorld(true);
      log.push([+c.x.toFixed(2), fila, +base.toFixed(2)]);
    }
  }
  window.__estantes = log; return log;
}

// os LIVROS são filhos das estantes (não soltos na cena): cada bloco de livros desce até a prateleira embaixo dele.
export function assentarLivros(cena) {
  cena.updateMatrixWorld(true);
  const visivel = o => { for (let p = o; p; p = p.parent) if (!p.visible) return false; return true; };
  const malhas = []; cena.traverse(o => { if (o.isMesh && visivel(o)) malhas.push(o); });
  const livros = []; cena.traverse(o => { if (/^books/i.test(o.name) && visivel(o)) livros.push(o); });
  const ray = new THREE.Raycaster(), feitos = [];
  for (const l of livros) {
    const meus = new Set(); l.traverse(o => meus.add(o));
    const bb = new THREE.Box3().setFromObject(l), tam = bb.getSize(V3(0, 0, 0)), c = bb.getCenter(V3(0, 0, 0)); let menor = 99;
    for (const [dx, dz] of [[0, 0], [-.3, -.3], [.3, -.3], [-.3, .3], [.3, .3]]) {
      ray.set(V3(c.x + dx * tam.x, bb.min.y + .004, c.z + dz * tam.z), V3(0, -1, 0)); ray.far = .6;
      const h = ray.intersectObjects(malhas.filter(m => !meus.has(m)), false)[0]; if (h) menor = Math.min(menor, h.distance - .004); }
    if (menor > .01 && menor < .5) { l.position.y -= menor / (l.parent.getWorldScale(V3(0, 0, 0)).y || 1); l.updateMatrixWorld(true); feitos.push(+menor.toFixed(2)); }
  }
  window.__livros = feitos; return feitos;
}

// a PASTA das fichas, FECHADA (capa), no lugar fixo da mesa — mesma das cenas 63/64 (continuidade)
export function pastaFichas(cena, Y) { const c = P.caixa(.42, .012, .32, P.mat({ cor: '#7a6a44' }), { pos: [GEO.FICHAS[0], Y + .006, GEO.FICHAS[1]] }); cena.add(c); return c; }

// MANUAL regra 5 — a sala do Igor arrumada (vale pra TODAS as cenas do bunker, 63 a 68: mesma sala, mesmos objetos nos mesmos lugares).
// Chamar DEPOIS de V.salaIgor4 + E.computadorNovo e ANTES de pôr maleta/objetos animados na cena (ou passá-los em 'fora').
export function arrumarSala(cena, sala, fora = []) {
  const { Y, pc } = sala;
  // a mesa nova tinha o tampo 4 cm ABAIXO da altura onde a sala põe os objetos (Y): tudo em cima boiava. Estica a mesa até Y (pés no chão).
  { const mn = sala.mesaNova; cena.updateMatrixWorld(true); const bbM = new THREE.Box3().setFromObject(mn); let topo = 0;
    for (let i = 0; i < 5; i++) for (let j = 0; j < 5; j++) { const x = P.lerp(bbM.min.x + .05, bbM.max.x - .05, i / 4), z = P.lerp(bbM.min.z + .05, bbM.max.z - .05, j / 4);
      const h = new THREE.Raycaster(V3(x, Y + .5, z), V3(0, -1, 0), 0, 1.2).intersectObject(mn, true)[0]; if (h) topo = Math.max(topo, h.point.y); }
    if (topo > .3 && topo < Y - .003) { mn.scale.y *= Y / topo; cena.updateMatrixWorld(true); } }
  // o COPO d'água ficava no ar FORA da mesa nova (era da mesa antiga, maior) e o CELULAR ficava onde vai a pasta das fichas:
  // os dois vão pro canto direito da frente do tampo, entre o computador e a luminária
  if (sala.copo) { sala.copo.position.set(.40, Y, .86); }
  if (sala.cel) { sala.cel.position.set(.33, Y, .68); }
  // a pilha de pastas da mesa antiga ficava pra fora da mesa nova: vai pra cima do ARQUIVO de metal, logo ao lado
  for (const r of [...cena.children]) { const bb = new THREE.Box3().setFromObject(r); if (!isFinite(bb.min.x)) continue; const c = bb.getCenter(V3(0, 0, 0)), tm = bb.getSize(V3(0, 0, 0));
    if (c.x < -.85 && c.x > -1.1 && Math.abs(c.z - .5) < .1 && tm.y < .06 && Math.abs(bb.min.y - Y) < .05) { r.position.x -= .27; r.position.y += 1.2; } }   // sobe acima do arquivo; o assentar desce até o tampo dele
  // a MALETA aberta ocupa o meio-esquerdo do tampo (GEO.MALETA): o porta-retrato, a pilha de pastas e a luminária de mesa da mesa antiga
  // ficavam DENTRO dela. Retrato → frente-centro (virado pro Igor); luminária → canto frente-direito; pastas → em cima da outra pilha, no arquivo de metal.
  for (const r of [...cena.children]) { const bb = new THREE.Box3().setFromObject(r); if (!isFinite(bb.min.x)) continue; const c = bb.getCenter(V3(0, 0, 0)), tm = bb.getSize(V3(0, 0, 0));
    const em = (x, z) => Math.abs(c.x - x) < .06 && Math.abs(c.z - z) < .06 && Math.abs(bb.min.y - Y) < .06;
    if (em(-.55, .62) && tm.y < .3) { r.position.x += -.02 - c.x; r.position.z += .86 - c.z; }                                    // porta-retrato
    else if (em(-.66, .80) && tm.y < .05) { r.position.x += -1.25 - c.x; r.position.z += .5 - c.z; r.position.y += 1.3; }        // pastas → arquivo
    else if (em(-.72, .72) && tm.y > .25 && tm.y < .5) { r.position.x += .64 - c.x; r.position.z += .74 - c.z; } }              // luminária de mesa
  arrumarEstantes(cena);
  for (let k = 0; k < 4; k++) if (!assentarSoltos(cena, [sala.I.obj, sala.cadeira, sala.est, sala.pc, ...fora]).length) break;   // MANUAL regra 5: nada flutuando (passadas até assentar a pilha)
  assentarLivros(cena);
  // o gabinete do computador novo vai pro CHÃO, ao lado da mesa (estava a 80 cm do chão, fora do tampo)
  if (pc.gabinete) { cena.updateMatrixWorld(true); const bb = new THREE.Box3().setFromObject(pc.gabinete); pc.gabinete.position.y -= bb.min.y / (pc.gabinete.parent.getWorldScale(V3(0, 0, 0)).y || 1); }
}

export async function montar(S, o = {}) {
  const cena = S.scene; S.camera.near = .03;
  const sala = await V.salaIgor4(cena), { I, Y, pc, rot, ANG, cadeira } = sala;
  await E.computadorNovo(sala);
  const Ad = await E4.ator('adryan'), Gu = await E4.ator('gusta'); cena.add(Ad.obj, Gu.obj); T.poses(Ad.modelo); T.poses(Gu.modelo);
  const f = V3(Math.sin(ANG), 0, Math.cos(ANG)), dir = V3(-Math.cos(ANG), 0, Math.sin(ANG));
  // pivô da QUEDA do Igor (pé de trás da cadeira): Igor + cadeira giram juntos
  I.girar(1); const tomba = new THREE.Group(); tomba.position.copy(f.clone().multiplyScalar(-.32)); cena.add(tomba);
  cena.updateMatrixWorld(true); tomba.attach(I.obj); tomba.attach(cadeira);
  // TELA: o terminal (480×270) vira a textura do próprio monitor (recorte 4:3 do centro)
  const term = K.terminal(); term.el.style.display = 'none';
  const texT = new THREE.CanvasTexture(term.cv); texT.magFilter = texT.minFilter = THREE.NearestFilter; texT.generateMipmaps = false; texT.colorSpace = THREE.NoColorSpace;
  texT.repeat.set(.75, 1); texT.offset.set(.125, 0);
  const tela = pc.children.find(c => c.isMesh && c.material?.uniforms?.uMapa?.value === pc.tex);
  const usarTerminal = sim => { tela.material.uniforms.uMapa.value = sim ? texT : pc.tex; };
  arrumarSala(cena, sala, [Ad.obj, Gu.obj, tomba]); const capa = pastaFichas(cena, Y);
  const B = { S, cena, sala, I, Y, pc, rot, ANG, cadeira, Ad, Gu, f, dir, tomba, capa, term, usarTerminal, GEO,
    tombar: a => tomba.quaternion.setFromAxisAngle(dir, a),
    telaAtualizar: () => { texT.needsUpdate = true; },
    // CÂMERA = OLHOS DO ADRYAN: logo à frente do rosto (a cabeça fica atrás da lente), mirando o alvo; respiração sutil
    olho: () => { Ad.obj.updateMatrixWorld(true); const r = Ad.obj.rotation.y; return Ad.osso('spine.005').getWorldPosition(V3(0, 0, 0)).add(V3(Math.sin(r) * .15, .09, Math.cos(r) * .15)); },
    pov: (t, alvo, o2 = {}) => { const e = B.olho(); if (o2.dy) e.y += o2.dy; e.y += .004 * Math.sin(t * 2.1);
      S.camera.position.copy(e); S.camera.lookAt(alvo.x ?? alvo[0], alvo.y ?? alvo[1], alvo.z ?? alvo[2]); S.camera.fov = o2.fov ?? 52; S.camera.updateProjectionMatrix(); },
    // o corpo do Adryan vira na direção do que ele olha (o POV nunca olha "pelas costas")
    virarPara: (alvo, w = 1) => { const p = Ad.obj.position, a = Math.atan2((alvo.x ?? alvo[0]) - p.x, (alvo.z ?? alvo[2]) - p.z), r0 = Ad.obj.rotation.y;
      let d = ((a - r0 + Math.PI * 3) % (Math.PI * 2)) - Math.PI; Ad.obj.rotation.y = r0 + d * w; },
  };
  return B;
}
