// uso: node tools/tremor.mjs <video> <ator> [t0] [t1]  — mede TREMOR (vai-e-volta rápido) de mão/antebraço/cabeça de um ator:
// por osso, conta os quadros em que a velocidade inverte de sentido com amplitude > 4 mm (posição) ou > 2° (direção)
import { chromium } from 'playwright'; import http from 'http'; import { readFileSync, existsSync, statSync } from 'fs'; import path from 'path';
const [name, ator, a = '0', b = '999'] = process.argv.slice(2), ROOT = process.cwd();
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.glb': 'model/gltf-binary', '.woff2': 'font/woff2', '.css': 'text/css' };
const s = http.createServer((q, r) => { const p = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); if (!existsSync(p) || statSync(p).isDirectory()) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' }); r.end(readFileSync(p)); });
await new Promise(r => s.listen(0, r));
const br = await chromium.launch(); const p = await br.newPage(); await p.addInitScript(() => { window.__render = true; });
await p.goto(`http://127.0.0.1:${s.address().port}/videos/${name}/index.html?${process.env.Q ?? ""}`); await p.waitForFunction(() => window.__ready, null, { timeout: 180000 });
const res = await p.evaluate(async ([ator, t0, t1]) => {
  const S = window.__S; let raiz = null; S.scene.traverse(n => { if (!raiz && n.name === 'ator:' + ator) { let v = true; for (let x = n; x; x = x.parent) if (x.visible === false) v = false; raiz = n; } });
  if (!raiz) return { erro: 'sem ator' };
  const ossos = []; raiz.traverse(n => { if (n.isBone && /^(hand|forearm|upper_arm)[.]?[LR]$|^spine[.]?005$/.test(n.name)) ossos.push(n); });
  const V = S.camera.position.constructor, hist = new Map(); t1 = Math.min(t1, window.VIDEO.dur);
  for (let t = t0; t <= t1; t += 1 / 30) { await window.__seek(t); S.scene.updateMatrixWorld(true);
    let vis = true; for (let x = raiz; x; x = x.parent) if (x.visible === false) vis = false;
    for (const o of ossos) { const par = o.parent; const REF = (new URLSearchParams(location.search).get("ref") === "pai" && raiz.parent) ? raiz.parent : raiz; const rel = REF.worldToLocal(o.getWorldPosition(new V()));   // relativo ao corpo (ou ao pai: ?ref=pai)
      const e = o.matrixWorld.elements, ax = new V(e[4], e[5], e[6]).normalize(); const ri = REF.matrixWorld.clone().invert(); ax.transformDirection(ri); rel.addScaledVector(ax, .1);   // + direção do osso (10 cm de alavanca): pega giro também
      (hist.get(o) ?? hist.set(o, []).get(o)).push(vis ? [t, rel.x, rel.y, rel.z] : null); } }
  const out = {};
  for (const [o, h] of hist) { let n = 0, mx = 0; const quando = [];
    for (let i = 2; i < h.length; i++) { const A = h[i - 2], B = h[i - 1], C = h[i]; if (!A || !B || !C) continue;
      const v1 = [B[1] - A[1], B[2] - A[2], B[3] - A[3]], v2 = [C[1] - B[1], C[2] - B[2], C[3] - B[3]], d = v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2];
      const m1 = Math.hypot(...v1), m2 = Math.hypot(...v2);
      if (d < 0 && Math.min(m1, m2) > .003) { n++; mx = Math.max(mx, Math.min(m1, m2)); if (quando.length < 12) quando.push(+B[0].toFixed(2)); } }
    if (n) out[o.name] = { inversões: n, máx_mm: Math.round(mx * 1000), quando }; }
  return out;
}, [ator, +a, +b]);
console.log(name, ator, JSON.stringify(res)); await br.close(); s.close();
