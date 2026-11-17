import { chromium } from 'playwright'; import http from 'http'; import { readFileSync, existsSync, statSync } from 'fs'; import path from 'path';
const ROOT = process.cwd(), nomes = process.argv.slice(2);
const s = http.createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); if (!existsSync(p) || statSync(p).isDirectory()) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css' }[path.extname(p)] || 'application/octet-stream' }); r.end(readFileSync(p)); });
await new Promise(r => s.listen(0, r)); const b = await chromium.launch();
for (const n of nomes) {
  const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } }); pg.on('pageerror', e => console.log('ERRO', e.message)); await pg.addInitScript(() => { window.__render = true; });
  await pg.goto(`http://127.0.0.1:${s.address().port}/videos/97-elenco/index.html?p=cru:${n}`); await pg.waitForFunction(() => window.__ready);
  const r = await pg.evaluate(() => { const v = E.uvRosto(p), fr = v.filter(x => x.nz > .55); const lim = a => [Math.min(...a), Math.max(...a)]; const ys = v.map(x => x.y);
    // olhos/boca: frente; quebra por altura
    const ymin = Math.min(...ys), ymax = Math.max(...ys), H = ymax - ymin;
    const faixa = (a, b) => fr.filter(x => x.y > ymin + a * H && x.y < ymin + b * H);
    const res = f => f.length ? { u: lim(f.map(x => x.u)), v: lim(f.map(x => x.v)), n: f.length } : null;
    return { total: v.length, frente: res(fr), olhos: res(faixa(.5, .66)), boca: res(faixa(.2, .35)), testa: res(faixa(.7, .85)), queixo: res(faixa(.05, .2)), alt: [ymin, ymax] }; });
  console.log(n, JSON.stringify(r)); await pg.close();
}
await b.close(); s.close();
