// QA (MANUAL DE DIREÇÃO, regra 5 — física): acha OBJETOS FLUTUANDO numa cena. Pra cada objeto pequeno (caixa < 0,9 m) que não está no
// chão, lança um raio pra baixo a partir da base dele: se não bater em nada até 3 cm abaixo, está flutuando (ou apoiado no nada).
// uso: node tools/qa_flutuando.mjs <pasta-da-cena> [t]      (ex.: 65-ep1-computador 2)
import { chromium } from 'playwright'; import http from 'http'; import { readFileSync, existsSync, statSync } from 'fs'; import path from 'path';
const [nome, t = '1'] = process.argv.slice(2), ROOT = process.cwd();
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.glb': 'model/gltf-binary' };
const s = http.createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); if (!existsSync(p) || statSync(p).isDirectory()) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' }); r.end(readFileSync(p)); });
await new Promise(r => s.listen(0, r));
const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 640, height: 360 } }); pg.on('pageerror', e => console.log('ERRO', e.message));
await pg.addInitScript(() => { window.__render = true; });
await pg.goto(`http://127.0.0.1:${s.address().port}/videos/${nome}/index.html`); await pg.waitForFunction(() => window.__ready, null, { timeout: 180000 });
await pg.evaluate(t => window.__seek(+t), t);
// THREE não é global: usa a própria cena pra construir Box3/Raycaster via import dinâmico do módulo da página
const out = await pg.evaluate(async () => {
  const P = await import('/lib/ps1.js'); const { THREE } = P; const S = window.__S, cena = S.scene; cena.updateMatrixWorld(true);
  const malhas = []; cena.traverse(o => { if (o.isMesh && o.visible) { let v = true, p = o; while (p) { if (!p.visible) { v = false; break; } p = p.parent; } if (v) malhas.push(o); } });
  const ray = new THREE.Raycaster(), achados = [];
  // "objeto" = o filho direto de um grupo de cenário (ou a própria malha solta); agrupa por ancestral mais alto abaixo da cena
  const raizDe = o => { let p = o; while (p.parent && p.parent !== cena) p = p.parent; return p; };
  const vistos = new Set();
  for (const m of malhas) {
    const r = raizDe(m), alvo = m;
    const bb = new THREE.Box3().setFromObject(alvo); const tam = bb.getSize(new THREE.Vector3());
    if (!isFinite(tam.x) || Math.max(tam.x, tam.y, tam.z) > .9 || bb.min.y < .03 || tam.y < .004) continue;
    if (alvo.isSkinnedMesh || /ator:|igor|dom|pistola|porta|tomba|luz|halo|aura/i.test((r.name || '') + (alvo.name || ''))) continue;
    if (alvo.material?.uniforms?.uOpac?.value < .5) continue;                 // brilho/vidro aditivo não conta
    const c = bb.getCenter(new THREE.Vector3()), base = new THREE.Vector3(c.x, bb.min.y + .005, c.z);
    ray.set(base, new THREE.Vector3(0, -1, 0)); ray.far = 3;
    const hits = ray.intersectObjects(malhas.filter(x => x !== alvo), false);
    const d = hits.length ? hits[0].distance : 99;
    const chave = alvo.uuid; if (vistos.has(chave)) continue; vistos.add(chave);
    if (d > .03) achados.push({ nome: (r.name || r.type) + ' › ' + (alvo.name || alvo.type), pos: [c.x, bb.min.y, c.z].map(v => +v.toFixed(2)), tam: [tam.x, tam.y, tam.z].map(v => +v.toFixed(2)), vao: d === 99 ? 'nada embaixo' : +d.toFixed(2) + ' m', embaixo: hits[0] ? (raizDe(hits[0].object).name || hits[0].object.name || hits[0].object.type) : '-' });
  }
  // objetos do TAMPO da mesa que se atravessam (caixas se cruzando > 3 cm nos três eixos)
  const tampo = cena.children.filter(r => { if (!r.visible || r.isLight) return false; const bb = new THREE.Box3().setFromObject(r); const tm = bb.getSize(new THREE.Vector3());
    return isFinite(bb.min.x) && bb.min.y > .6 && bb.min.y < .9 && Math.max(tm.x, tm.z) < .9 && bb.max.x > -.9 && bb.min.x < .9 && bb.max.z > .05 && bb.min.z < .95 && !/ator|igor/i.test(r.name || ''); });
  for (let i = 0; i < tampo.length; i++) for (let j = i + 1; j < tampo.length; j++) { const a = new THREE.Box3().setFromObject(tampo[i]), b = new THREE.Box3().setFromObject(tampo[j]);
    const x = Math.min(a.max.x, b.max.x) - Math.max(a.min.x, b.min.x), y = Math.min(a.max.y, b.max.y) - Math.max(a.min.y, b.min.y), z = Math.min(a.max.z, b.max.z) - Math.max(a.min.z, b.min.z);
    if (x > .03 && y > .01 && z > .03) achados.push({ nome: 'SE ATRAVESSAM: ' + a.getCenter(new THREE.Vector3()).toArray().map(v => v.toFixed(2)) + ' × ' + b.getCenter(new THREE.Vector3()).toArray().map(v => v.toFixed(2)), pos: [x, y, z].map(v => +v.toFixed(2)), tam: ['-'], vao: '-', embaixo: '-' }); }
  return achados;
});
console.log('assentados:', JSON.stringify(await pg.evaluate(() => window.__assentados ?? null)), 'livros:', JSON.stringify(await pg.evaluate(() => window.__livros ?? null)));
console.log(`QA FLUTUANDO · ${nome} @ ${t}s · ${out.length} suspeitos`);
for (const a of out) console.log(' ·', a.nome, 'base', a.pos.join(', '), 'tam', a.tam.join('×'), '→ vão', a.vao, '(embaixo:', a.embaixo + ')');
await b.close(); s.close();
