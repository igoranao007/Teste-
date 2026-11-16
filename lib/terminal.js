// Tela cheia de terminal verde, pixelada (canvas 480×270 ampliado 4× sem suavizar) + defeitos de sinal de TV.
import * as P from './ps1.js';
export const VERDE = '#39ff6a', CLARO = '#b9ffc9', ESC = '#0c3a1c';
export function terminal() {
  const el = document.createElement('div'); el.className = 'layer'; el.style.cssText = 'pointer-events:none;background:#000';
  const cv = document.createElement('canvas'); cv.width = 480; cv.height = 270; cv.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;image-rendering:pixelated';
  el.appendChild(cv); document.getElementById('stage').appendChild(el);
  const x = cv.getContext('2d', { willReadFrequently: true }); x.textBaseline = 'top';
  const T = { el, cv, x,
    limpar(cor = '#010a04') { x.fillStyle = cor; x.fillRect(0, 0, 480, 270); },
    txt(s, px, py, tam = 10, cor = VERDE, o = {}) { x.font = `${o.peso ?? 700} ${tam}px 'JetBrains Mono', monospace`; x.textAlign = o.alinhar ?? 'left'; x.fillStyle = cor; x.fillText(s, px, py); },
    caixa(px, py, w, h, cor = VERDE) { x.fillStyle = cor; x.fillRect(px, py, w, h); },
    moldura(px, py, w, h, cor = VERDE) { x.fillStyle = cor; x.fillRect(px, py, w, 1); x.fillRect(px, py + h - 1, w, 1); x.fillRect(px, py, 1, h); x.fillRect(px + w - 1, py, 1, h); },
    // linhas de "código" rolando pra cima
    codigo(t, o = {}) { const lh = 9, rol = t * (o.vel ?? 60), i0 = Math.floor(rol / lh);
      for (let j = -1; j < 31; j++) { const r = P.rng(500 + i0 + j), y = j * lh - (rol % lh); let s = ''; const n = 1 + Math.floor(r() * 6);
        for (let k = 0; k < n; k++) s += ['0x' + Math.floor(r() * 65535).toString(16).padStart(4, '0').toUpperCase(), 'MOV', 'JMP', 'LOAD', 'MOGG', 'SEG', 'ACK', '>>', 'FED.SYS', 'KEY', 'OK', '::', 'READ', 'VHS', '#' + Math.floor(r() * 999)][Math.floor(r() * 15)] + ' ';
        T.txt(s, 8 + Math.floor(r() * 3) * 12, y, 8, r() < .12 ? CLARO : (r() < .3 ? '#1f9a45' : VERDE)); } },
    // deixa o traço duro (sem meio-tom): tudo vira verde cheio ou fundo
    pixelar() { const d = x.getImageData(0, 0, 480, 270), q = d.data; for (let i = 0; i < q.length; i += 4) { const g = q[i + 1]; if (g > 150) { const cl = q[i] > 120; q[i] = cl ? 185 : 57; q[i + 1] = 255; q[i + 2] = cl ? 201 : 106; } else if (g > 70) { q[i] = 12; q[i + 1] = 110; q[i + 2] = 44; } else { q[i] = 1; q[i + 1] = 10; q[i + 2] = 4; } } x.putImageData(d, 0, 0); },
    // sinal ruim: chiado, faixa de tracking, rasgos horizontais, cor sangrando pra verde. f = 0–1
    sinal(quadro, f) { if (f <= 0) return; const r = P.rng(quadro * 131 + 7), d = x.getImageData(0, 0, 480, 270), q = d.data, o = new Uint8ClampedArray(q);
      const nr = Math.floor(f * 22), rasgos = Array.from({ length: nr }, () => [Math.floor(r() * 270), 2 + Math.floor(r() * (4 + 26 * f)), Math.floor((r() - .5) * 2 * (6 + 150 * f * f))]);
      const ty = Math.floor(r() * 270), th = 8 + Math.floor(f * 40), rolo = Math.floor(f > .6 ? r() * 60 * (f - .6) : 0);
      for (let y = 0; y < 270; y++) { let dx = Math.floor(Math.sin(y * .13 + quadro * .9) * f * 5); for (const [ry, rh, rx] of rasgos) if (y >= ry && y < ry + rh) dx += rx; const ys = (y + rolo) % 270, tr = y >= ty && y < ty + th;
        for (let xx = 0; xx < 480; xx++) { const sx = ((xx + dx) % 480 + 480) % 480, a = (ys * 480 + sx) * 4, b = (y * 480 + xx) * 4, sg = (ys * 480 + ((sx + 3 + Math.floor(f * 6)) % 480)) * 4;
          let R = o[a], G = Math.max(o[a + 1], o[sg + 1] * (.5 + .4 * f)), B = o[a + 2];
          const n = r(); if (n < .06 + f * .42) { const v = 60 + r() * 195 * (.4 + f * .6); R = v * .2; G = Math.max(G, v); B = v * .35; } if (tr) { G = Math.min(255, G * 1.4 + 50 * f); R *= .6; }
          G = Math.min(255, G + 26 * f); q[b] = R; q[b + 1] = G; q[b + 2] = B; } }
      x.putImageData(d, 0, 0); } };
  return T;
}
// barra de blocos + porcentagem
export function carregando(T, p, t) {
  T.txt('PROJETO MOGG', 240, 46, 30, VERDE, { alinhar: 'center', peso: 800 });
  T.txt('CARREGANDO' + '.'.repeat(1 + Math.floor(t * 2.5) % 3), 240, 112, 16, CLARO, { alinhar: 'center' });
  T.moldura(88, 146, 304, 24); const n = Math.floor(p * 24); for (let i = 0; i < n; i++) T.caixa(92 + i * 12.4, 150, 10, 16);
  T.txt(String(Math.floor(p * 100)).padStart(2, '0') + '%', 240, 182, 16, VERDE, { alinhar: 'center' });
}
