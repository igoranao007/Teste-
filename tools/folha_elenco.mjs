// Folha de conferência das animações NO MOTOR (o que vai pro filme): uma linha por personagem, uma coluna por clipe.
// uso: node tools/folha_elenco.mjs <pasta-saida> "entrada,corsa,zangao" "u_Walk_Loop@0.5,m_walk_cautious@3,u_Sitting_Idle_Loop@1" [vista=tres]
//      depois: python3 tools/montar_folha_elenco.py <pasta-saida> folha.jpg "TÍTULO"
import { chromium } from 'playwright'; import http from 'http'; import { readFileSync, existsSync, statSync, writeFileSync, mkdirSync } from 'fs'; import path from 'path';
const [out, nomes, clipes, vista = 'tres'] = process.argv.slice(2), ROOT = process.cwd();
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.woff2': 'font/woff2', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.glb': 'model/gltf-binary' };
const s = http.createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); if (!existsSync(p) || statSync(p).isDirectory()) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' }); r.end(readFileSync(p)); });
await new Promise(r => s.listen(0, r)); mkdirSync(out, { recursive: true });
const b = await chromium.launch({ args: ['--enable-gpu', '--ignore-gpu-blocklist'] });
for (const n of nomes.split(',')) for (const [i, ct] of clipes.split(',').entries()) {
  const [clip, t] = ct.split('@');
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } }); p.on('pageerror', e => console.log('ERRO', n, clip, e.message));
  await p.addInitScript(() => { window.__render = true; });
  await p.goto(`http://127.0.0.1:${s.address().port}/videos/${process.env.PAGINA || '91-luan'}/index.html?p=${n}&v=${vista}&clip=${clip}`);
  await p.waitForFunction(() => window.__ready, null, { timeout: 120000 });
  await p.evaluate(t => window.__seek(+t), t || 1);
  writeFileSync(path.join(out, `${n}__${String(i).padStart(2, '0')}__${clip}.jpg`), await p.screenshot({ type: 'jpeg', quality: 88, clip: { x: 510, y: 90, width: 900, height: 900 } })); await p.close();
  console.log('ok', n, clip);
}
await b.close(); s.close();
