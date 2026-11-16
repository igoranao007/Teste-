// uso: node tools/foto.mjs <video> <t> "<query>" <saida.jpg>  — um quadro com parâmetros na URL (?v=perto etc.)
import { chromium } from 'playwright'; import http from 'http'; import { readFileSync, existsSync, statSync, writeFileSync } from 'fs'; import path from 'path';
const [name, t, query, out] = process.argv.slice(2), ROOT = process.cwd();
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.woff2': 'font/woff2', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.glb': 'model/gltf-binary' };
const s = http.createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); if (!existsSync(p) || statSync(p).isDirectory()) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' }); r.end(readFileSync(p)); });
await new Promise(r => s.listen(0, r));
const b = await chromium.launch({ args: ['--enable-gpu', '--ignore-gpu-blocklist'] });
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } }); p.on('pageerror', e => console.log('ERRO:', e.message));
await p.addInitScript(() => { window.__render = true; });
await p.goto(`http://127.0.0.1:${s.address().port}/videos/${name}/index.html?${query}`); await p.waitForFunction(() => window.__ready);
await p.evaluate(t => window.__seek(+t), t);
writeFileSync(out, await p.screenshot({ type: 'jpeg', quality: 90 })); await b.close(); s.close();
