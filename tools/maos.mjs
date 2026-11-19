// uso: node tools/maos.mjs <video> [t0] [t1] [limiar°]  — mede o giro das mãos/antebraços quadro a quadro e lista os saltos (mão girando = bug)
import { chromium } from 'playwright'; import http from 'http'; import { readFileSync, existsSync, statSync } from 'fs'; import path from 'path';
const [name, a = '0', b = '999', lim = '20'] = process.argv.slice(2), ROOT = process.cwd();
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.glb': 'model/gltf-binary', '.woff2': 'font/woff2', '.css': 'text/css' };
const s = http.createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); if (!existsSync(p) || statSync(p).isDirectory()) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' }); r.end(readFileSync(p)); });
await new Promise(r => s.listen(0, r));
const br = await chromium.launch(); const p = await br.newPage(); await p.addInitScript(() => { window.__render = true; });
await p.goto(`http://127.0.0.1:${s.address().port}/videos/${name}/index.html`); await p.waitForFunction(() => window.__ready, null, { timeout: 120000 });
const dur = await p.evaluate(() => window.VIDEO.dur), t1 = Math.min(+b, dur);
const res = await p.evaluate(async ([t0, t1, lim]) => {
  const ossos = []; __S.scene.traverse(n => { if (n.isBone && /^(hand|forearm|RightHand|LeftHand|RightForeArm|LeftForeArm)/.test(n.name)) { let r = n; while (r.parent && r.parent !== __S.scene) r = r.parent; ossos.push([n, r]); } });
  const ant = new Map(), out = [], Q = () => new (ossos[0][0].quaternion.constructor)();
  for (let t = t0; t <= t1; t += 1 / 30) { await window.__seek(t);
    for (const [o, r] of ossos) { if (!r.visible) { ant.delete(o); continue; } let vis = true, x = o; while (x) { if (x.visible === false) vis = false; x = x.parent; } if (!vis) { ant.delete(o); continue; }
      const e = o.matrixWorld.elements, ax = [[e[0], e[1], e[2]], [e[4], e[5], e[6]]].map(v => { const l = Math.hypot(...v) || 1; return v.map(x => x / l); });
      const q = ax; const prev = ant.get(o); ant.set(o, q);
      if (prev) { const d = Math.max(...[0, 1].map(i => Math.acos(Math.max(-1, Math.min(1, q[i][0] * prev[i][0] + q[i][1] * prev[i][1] + q[i][2] * prev[i][2]))) * 180 / Math.PI)); if (d > lim) { const pos = r.position; out.push([+t.toFixed(2), o.name + '@' + [pos.x, pos.z].map(v => v.toFixed(1)).join(','), Math.round(d)]); } } } }
  return out;
}, [+a, t1, +lim]);
const agrup = {}; for (const [t, n, d] of res) { const k = n; (agrup[k] ??= []).push(`${t}s:${d}°`); }
console.log(name, res.length ? '' : 'ok — nenhum salto'); for (const [k, v] of Object.entries(agrup)) console.log(' ', k, v.length, 'saltos:', v.slice(0, 12).join(' '), v.length > 12 ? '…' : '');
await br.close(); s.close();
