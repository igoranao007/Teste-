// uso: node tools/fotos.mjs <video> "t1,t2,..." "<query>" <saida.jpg> [larg=480]  — vários quadros numa folha (revisão rápida)
import { chromium } from 'playwright'; import http from 'http'; import { readFileSync, existsSync, statSync } from 'fs'; import path from 'path';
const [name, ts, query, out, larg = '480'] = process.argv.slice(2), ROOT = process.cwd();
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.woff2': 'font/woff2', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.glb': 'model/gltf-binary' };
const s = http.createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); if (!existsSync(p) || statSync(p).isDirectory()) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' }); r.end(readFileSync(p)); });
await new Promise(r => s.listen(0, r));
const b = await chromium.launch({ args: ['--enable-gpu', '--ignore-gpu-blocklist'] });
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } }); p.on('pageerror', e => console.log('ERRO:', e.message)); p.on('console', m => { if (m.type() === 'error' || m.text().startsWith('DBG')) console.log(m.text()); });
await p.addInitScript(() => { window.__render = true; });
await p.goto(`http://127.0.0.1:${s.address().port}/videos/${name}/index.html?${query}`); await p.waitForFunction(() => window.__ready, null, { timeout: 120000 });
if (process.env.PRE) await p.evaluate(e => eval(e), process.env.PRE);
const L = ts.split(',').map(Number), imgs = [];
for (const t of L) { await p.evaluate(t => window.__seek(+t), t); await p.waitForTimeout(30); imgs.push((await p.screenshot({ type: 'jpeg', quality: 85 })).toString('base64')); }
const W = +larg, H = Math.round(W * 9 / 16), C = Math.min(4, L.length), R = Math.ceil(L.length / C);
await p.setViewportSize({ width: W * C, height: H * R });
await p.setContent(`<body style="margin:0;background:#000;display:grid;grid-template-columns:repeat(${C},${W}px);font:14px monospace">${imgs.map((d, i) => `<div style="position:relative;width:${W}px;height:${H}px"><img src="data:image/jpeg;base64,${d}" style="width:100%;height:100%"><b style="position:absolute;left:4px;top:2px;color:#ff0;text-shadow:0 0 3px #000">${L[i]}s</b></div>`).join('')}</body>`);
await p.screenshot({ path: out, type: 'jpeg', quality: 85 }); await b.close(); s.close();
