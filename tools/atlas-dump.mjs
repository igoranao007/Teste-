// uso: node tools/atlas-dump.mjs <personagem> <saida.png> — salva o atlas do personagem (videos/97-elenco)
import { chromium } from 'playwright'; import http from 'http'; import { readFileSync, existsSync, statSync, writeFileSync } from 'fs'; import path from 'path';
const ROOT = process.cwd(), [nome, out] = process.argv.slice(2);
const s = http.createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); if (!existsSync(p) || statSync(p).isDirectory()) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css' }[path.extname(p)] || 'application/octet-stream' }); r.end(readFileSync(p)); });
await new Promise(r => s.listen(0, r)); const b = await chromium.launch();
const pg = await b.newPage(); pg.on('pageerror', e => console.log('ERRO', e.message)); await pg.addInitScript(() => { window.__render = true; });
await pg.goto(`http://127.0.0.1:${s.address().port}/videos/97-elenco/index.html?p=${nome}`); await pg.waitForFunction(() => window.__ready);
const url = await pg.evaluate(() => p.atlas.toDataURL('image/png')); writeFileSync(out, Buffer.from(url.split(',')[1], 'base64'));
await b.close(); s.close();
