// CONTROLE DE QUALIDADE (THE GREEN PATH) — roda um plano quadro a quadro e reprova o que for fisicamente/anatomicamente errado.
// uso: node tools/qa.mjs <video> [passo=1 (quadros)] [t0] [t1]     → imprime o resumo e grava material/qa/<video>.json
// Testes:
//  ANATOMIA   pulso dobrado (>80°) · mão torcida em relação ao antebraço (>60° vs. pose neutra do rig) · pescoço torcido (>75°)
//             · salto de mão/antebraço (>28° num quadro, dentro do mesmo plano de câmera) · pé abaixo do chão (<−4 cm)
//  CONTINUIDADE  personagem que pula >25 cm num quadro dentro do mesmo plano de câmera (teletransporte)
//  COLISÃO    corpo (cápsula r=.16 m nos quadris) dentro de peça sólida do cenário (paredes, móveis, carro, árvores, bombas)
//             · dois personagens a menos de 30 cm um do outro
// Exceções conhecidas: personagem dentro do carro (o carro é ancestral dele), peças pequenas (<45 cm: maleta, bico, copo),
// chão/teto/terreno. Personagem invisível não conta.
import { chromium } from 'playwright'; import http from 'http'; import { readFileSync, existsSync, statSync, mkdirSync, writeFileSync } from 'fs'; import path from 'path';
const [name, passo = '1', a = '0', b = '999'] = process.argv.slice(2), ROOT = process.cwd();
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.glb': 'model/gltf-binary', '.woff2': 'font/woff2', '.css': 'text/css' };
const s = http.createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); if (!existsSync(p) || statSync(p).isDirectory()) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' }); r.end(readFileSync(p)); });
await new Promise(r => s.listen(0, r));
const br = await chromium.launch(); const p = await br.newPage(); await p.addInitScript(() => { window.__render = true; });
p.on('pageerror', e => console.log('ERRO', e.message));
await p.goto(`http://127.0.0.1:${s.address().port}/videos/${name}/index.html`); await p.waitForFunction(() => window.__ready, null, { timeout: 180000 });
const res = await p.evaluate(async ([t0, t1, passo]) => {
  const S = window.__S, sc = S.scene, V3 = S.camera.position.constructor, Q = S.camera.quaternion.constructor, M4 = S.camera.matrixWorld.constructor, B3 = (() => { let B; sc.traverse(n => { if (!B && n.geometry) { n.geometry.computeBoundingBox(); B = n.geometry.boundingBox.constructor; } }); return B; })();
  const dur = window.VIDEO.dur; t1 = Math.min(t1, dur);
  // atores = raízes com SkinnedMesh; ossos do braço/pescoço/pé e pose neutra (bind) de cada osso
  const atores = [];
  sc.traverse(n => { if (!n.isSkinnedMesh) return; let r = n; while (r.parent && r.parent !== sc && !r.parent.isScene) { if (r.parent.children.some(c => c.isSkinnedMesh) && r.parent !== n.parent) break; r = r.parent; }
    const sk = n.skeleton; if (atores.some(x => x.sk === sk || x.ossos.has(sk.bones[0]))) return;
    const bind = new Map(); sk.bones.forEach((bo, i) => bind.set(bo, new M4().copy(sk.boneInverses[i]).invert()));
    let nome = null; for (let x = n; x; x = x.parent) if (/^ator:|^igor|Igor/.test(x.name || '')) { nome = x.name.replace('ator:', ''); r = x; break; }
    nome ??= (n.name || r.name || 'ator') + '#' + atores.length;
    atores.push({ sk, raiz: r, nome, ossos: new Set(sk.bones), bind, mesh: n });
  });
  // agrupa malhas skinned do mesmo esqueleto/raiz (um ator pode ter várias malhas)
  const raizDe = new Map(); for (const at of atores) at.raiz.traverse(x => raizDe.set(x, at));
  const osso = (at, re) => at.sk.bones.find(b => re.test(b.name));
  for (const at of atores) {
    at.o = {}; for (const [k, re] of Object.entries({ hL: /^(hand\.?L|LeftHand)$/, hR: /^(hand\.?R|RightHand)$/, fL: /^(forearm\.?L|LeftForeArm)$/, fR: /^(forearm\.?R|RightForeArm)$/,
      mL: /^f_middle\.?01\.?L$/, mR: /^f_middle\.?01\.?R$/, cab: /^(spine\.?005|Head|head)$/, pesc: /^(spine\.?004|Neck|neck)$/, pL: /^(foot\.?L|LeftFoot)$/, pR: /^(foot\.?R|RightFoot)$/, qd: /^(spine|Hips|hips)$/ })) at.o[k] = osso(at, re);
  }
  // local "neutro" de um osso = bind do pai⁻¹ · bind do osso
  const neutroLocal = (at, bo) => { const bw = at.bind.get(bo), pw = at.bind.get(bo.parent); const l = pw ? new M4().copy(pw).invert().multiply(bw) : bw.clone(); const q = new Q(); l.decompose(new V3(), q, new V3()); return q; };
  const torcao = (at, bo) => { if (!bo) return 0; const qn = at._n?.get(bo) ?? (at._n ??= new Map()).set(bo, neutroLocal(at, bo)).get(bo); const r = qn.clone().invert().multiply(bo.quaternion.clone().normalize()); // twist no eixo Y (osso)
    return Math.abs(2 * Math.atan2(r.y, r.w) * 180 / Math.PI) % 360; };
  const tw = d => d > 180 ? 360 - d : d;
  const dir = (a, b) => b.getWorldPosition(new V3()).sub(a.getWorldPosition(new V3())).normalize();
  const visivel = o => { for (let x = o; x; x = x.parent) if (x.visible === false) return false; return true; };
  // obstáculos: malhas não-ator, sólidas (>=45 cm em alguma dimensão horizontal ou altura), fora chão/teto/terreno
  const obst = []; sc.traverse(n => { if (!n.isMesh || n.isSkinnedMesh || raizDe.has(n)) return; if (n.material?.transparent && !(n.material.uniforms?.uOpac?.value > .9)) return; obst.push(n); });
  const caixa = n => { if (!n.geometry.boundingBox) n.geometry.computeBoundingBox(); return n.geometry.boundingBox.clone().applyMatrix4(n.matrixWorld); };   // só a própria peça (sem os filhos: porta aberta não 'engorda' o carro)
  const veic = o => { for (let x = o; x; x = x.parent) if (x.userData?.veiculo) return x; return null; };
  const anc = (n, at) => { const va = veic(at.raiz) || at.raiz.userData?.noVeiculo; if (va && veic(n) === va) return true; if (n.userData?.flexivel) return true; for (let x = at.raiz; x; x = x.parent) if (x === n) return true; for (let x = n; x; x = x.parent) if (x === at.raiz) return true; return false; };
  const out = { anat: [], cont: [], col: [], atores: atores.map(a => a.nome) }, ant = new Map(); let camAnt = null;
  const add = (lista, t, quem, oque, val) => lista.push([+t.toFixed(2), quem, oque, Math.round(val)]);
  for (let t = t0; t <= t1 + 1e-6; t += passo / 30) {
    await window.__seek(t); sc.updateMatrixWorld(true);
    const cp = S.camera.position.clone(), corte = camAnt && cp.distanceTo(camAnt) > .35; camAnt = cp;
    // caixas dos obstáculos neste quadro (o carro anda)
    const cx = obst.filter(visivel).map(n => [n, caixa(n)]).filter(([n, b]) => { const sz = b.getSize(new V3()); if (!isFinite(sz.x)) return false;
      if (sz.y < .08 || b.min.y > 1.9) return false; if (sz.x > 7 && sz.z > 7) return false; if (Math.max(sz.x, sz.y, sz.z) < .55) return false;   // peças pequenas/carregáveis (maleta .5, bico, copo)
      if (sz.y > 3 && sz.x < 9 && sz.z < 9 && /LOD|Tree|Pine|arvore|Birch|Oak/i.test(n.name + n.parent?.name)) { const c = b.getCenter(new V3()); b.min.x = c.x - .3; b.max.x = c.x + .3; b.min.z = c.z - .3; b.max.z = c.z + .3; }   // árvore: só o tronco
      return true; });
    const vis = atores.filter(at => visivel(at.mesh));
    for (const at of vis) {
      const O = at.o, k = at.nome, pa = ant.get(at) ?? {};
      // anatomia
      for (const sd of ['L', 'R']) { const H = O['h' + sd], F = O['f' + sd], Mi = O['m' + sd]; if (!H || !F) continue;
        if (Mi) { const ang = Math.acos(Math.max(-1, Math.min(1, dir(F, H).dot(dir(H, Mi))))) * 180 / Math.PI; if (ang > 80) add(out.anat, t, k, 'pulso dobrado ' + sd, ang); }
        const tm = tw(torcao(at, H)); if (tm > 60) add(out.anat, t, k, 'mão torcida ' + sd, tm);
        const e = H.matrixWorld.elements, ax = [e[4], e[5], e[6]], l = Math.hypot(...ax) || 1, axn = ax.map(x => x / l);
        const pv = pa['ax' + sd]; if (pv && !corte) { const d = Math.acos(Math.max(-1, Math.min(1, axn[0] * pv[0] + axn[1] * pv[1] + axn[2] * pv[2]))) * 180 / Math.PI; if (d / passo > 28) add(out.anat, t, k, 'salto de mão ' + sd, d / passo); }
        pa['ax' + sd] = axn; }
      const tc = tw(torcao(at, O.cab)) + tw(torcao(at, O.pesc)); if (tc > 75) add(out.anat, t, k, 'pescoço torcido', tc);
      const raizY = at.raiz.getWorldPosition(new V3()).y;
      for (const pe of [O.pL, O.pR]) if (pe && Math.abs(raizY) < .05) { const y = pe.getWorldPosition(new V3()).y; if (y < -.04) add(out.anat, t, k, 'pé abaixo do chão', y * 100); }
      // continuidade
      const q = (O.qd ?? at.raiz).getWorldPosition(new V3()), ql = at.raiz.parent ? at.raiz.parent.worldToLocal(q.clone()) : q;   // relativo a quem carrega (carro)
      if (pa.q && !corte && ql.distanceTo(pa.q) / passo > .25) add(out.cont, t, k, 'teletransporte (cm)', ql.distanceTo(pa.q) * 100); pa.q = ql;
      ant.set(at, pa);
      // colisão: cápsula vertical nos quadris (r .16), de 20 cm a 1,5 m
      for (const [n, bx] of cx) { if (anc(n, at)) continue; const c = bx.clone().expandByScalar(.16);
        if (!(q.x > c.min.x && q.x < c.max.x && q.z > c.min.z && q.z < c.max.z && c.max.y > .2 && c.min.y < Math.max(.3, q.y))) continue;
        if (n.userData?.assento === at.nome || n.userData?.vaoPernas) continue;
        if (raizY >= bx.max.y - .03) continue;                                       // em pé EM CIMA da peça (degrau, ilha): apoiado, não atravessando
        if (bx.max.y - bx.min.y <= .26 && raizY > .03) continue;                      // subindo um degrau (≤ 25 cm): o pé já está saindo do chão
        const nm = [n, n.parent, n.parent?.parent].map(x => x?.name).filter(x => x && x !== 'Scene').join('<') || ('peça@' + bx.getCenter(new V3()).toArray().map(v => v.toFixed(1)).join(',') + ' ' + bx.getSize(new V3()).toArray().map(v => v.toFixed(1)).join('×'));
        add(out.col, t, k, 'atravessa ' + nm, Math.round(bx.max.y * 100)); }
    }
    // VEÍCULOS: a lataria (malha principal) contra o cenário
    sc.traverse(v => { if (!v.userData?.veiculo || !visivel(v)) return; let corpo = null; v.traverse(n => { if (!corpo && n.isMesh && /^sedan_blue$/.test(n.name)) corpo = n; }); if (!corpo) return;
      if (!corpo.geometry.boundingBox) corpo.geometry.computeBoundingBox();
      const bl = corpo.geometry.boundingBox.clone().expandByScalar(-.05), inv = new M4().copy(corpo.matrixWorld).invert();   // caixa ORIENTADA: obstáculo levado pro espaço do carro
      for (const [n, bx] of cx) { if (veic(n) === v) continue; const sz = bx.getSize(new V3()); if (sz.y <= .26) continue;
        const ol = new B3(); for (let k = 0; k < 8; k++) ol.expandByPoint(new V3(k & 1 ? bx.max.x : bx.min.x, k & 2 ? bx.max.y : bx.min.y, k & 4 ? bx.max.z : bx.min.z).applyMatrix4(inv));
        if (bl.intersectsBox(ol)) add(out.col, t, 'carro', 'lataria atravessa ' + ([n, n.parent].map(x => x?.name).filter(x => x && x !== 'Scene').join('<') || 'peça'), 0); } });
    for (let i = 0; i < vis.length; i++) for (let j = i + 1; j < vis.length; j++) { const A = (vis[i].o.qd ?? vis[i].raiz).getWorldPosition(new V3()), B = (vis[j].o.qd ?? vis[j].raiz).getWorldPosition(new V3());
      A.y = B.y = 0; if (A.distanceTo(B) < .3) add(out.col, t, vis[i].nome + '×' + vis[j].nome, 'corpos sobrepostos (cm)', A.distanceTo(B) * 100); }
  }
  return out;
}, [+a, +b, +passo]);
// resumo: agrupa por (quem, o quê) com faixa de tempo
const resumo = {}; for (const cat of ['anat', 'cont', 'col']) { const g = {}; for (const [t, q, o, v] of res[cat]) { const k = q + ' · ' + o; (g[k] ??= { n: 0, t0: t, t1: t, max: v }); g[k].n++; g[k].t1 = t; g[k].max = Math.max(g[k].max, v); } resumo[cat] = g; }
const tot = Object.values(resumo).reduce((s, g) => s + Object.keys(g).length, 0);
console.log(`QA ${name}: ${tot ? tot + ' problema(s)' : 'APROVADO'}  (atores: ${res.atores.join(', ')})`);
for (const [cat, rot] of [['anat', 'ANATOMIA'], ['cont', 'CONTINUIDADE'], ['col', 'COLISÃO']]) for (const [k, v] of Object.entries(resumo[cat])) console.log(`  ${rot}  ${k}  ×${v.n}  ${v.t0}–${v.t1}s  máx ${v.max}`);
mkdirSync('material/qa', { recursive: true }); writeFileSync(`material/qa/${name}.json`, JSON.stringify({ quando: new Date().toISOString(), resumo }, null, 1));
await br.close(); s.close();
