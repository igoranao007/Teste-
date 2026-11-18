// uso: node tools/dbg_pagina.mjs <video> <t> "<query>" "<expressão JS>"  — imprime o valor da expressão depois do quadro t
import { chromium } from 'playwright'; import http from 'http'; import { readFileSync, existsSync, statSync } from 'fs'; import path from 'path';
const [name, t, query, expr] = process.argv.slice(2), ROOT = process.cwd();
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.glb': 'model/gltf-binary', '.woff2': 'font/woff2', '.css': 'text/css' };
const s = http.createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); if (!existsSync(p) || statSync(p).isDirectory()) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' }); r.end(readFileSync(p)); });
await new Promise(r => s.listen(0, r));
const b = await chromium.launch(); const p = await b.newPage(); p.on('pageerror', e => console.log('ERRO', e.message));
await p.addInitScript(() => { window.__render = true; });
await p.goto(`http://127.0.0.1:${s.address().port}/videos/${name}/index.html?${query}`); await p.waitForFunction(() => window.__ready);
await p.evaluate(t => window.__seek(+t), t);
console.log(JSON.stringify(await p.evaluate(e => eval(e), expr))); await b.close(); s.close();
