"""Rasteriza os triângulos (tris.json) na textura e devolve, pra cada texel: posição 3D, normal, objeto e cor original.
Usado pra repintar texturas prontas por regras de posição/cor. Uso como módulo."""
import json
def texels(tris, N):
    for t in tris:
        uv = [(u * N, (1 - v) * N) for u, v in t['uv']]; P = t['p']
        (x0, y0), (x1, y1), (x2, y2) = uv
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(den) < 1e-12: continue
        for y in range(int(min(y0, y1, y2)) - 1, int(max(y0, y1, y2)) + 2):
            for x in range(int(min(x0, x1, x2)) - 1, int(max(x0, x1, x2)) + 2):
                if not (0 <= x < N and 0 <= y < N): continue
                px, py = x + .5, y + .5
                a = ((y1 - y2) * (px - x2) + (x2 - x1) * (py - y2)) / den
                b = ((y2 - y0) * (px - x2) + (x0 - x2) * (py - y2)) / den
                c = 1 - a - b
                if min(a, b, c) < -0.35 / max(1, abs(den) ** 0.5): continue
                yield x, y, [a * P[0][i] + b * P[1][i] + c * P[2][i] for i in range(3)], t
