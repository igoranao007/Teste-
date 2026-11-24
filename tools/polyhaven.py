"""Baixa modelos do Poly Haven (TODOS CC0) em glTF na resolução de textura pedida (padrão 1k).
uso: RES=1k python3 tools/polyhaven.py <pasta-saida> <id> [<id> ...]     (ids: https://polyhaven.com/models)
Cada modelo vai pra <pasta>/<id>/<id>.gltf + .bin + texturas. Depois: converter/reduzir pro estilo PSX no Blender
(ex.: tools/blender/psx_prop.py) — os originais têm milhares de polígonos e texturas grandes."""
import sys, os, json, urllib.request
out, ids = sys.argv[1], sys.argv[2:]; RES = os.environ.get('RES', '1k')
UA = {"User-Agent": "Mozilla/5.0 asset-fetch"}
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=180).read()
for i in ids:
    try:
        f = json.loads(get(f'https://api.polyhaven.com/files/{i}'))['gltf']
        r = f.get(RES) or f[sorted(f)[0]]; g = r['gltf']; d = os.path.join(out, i); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, os.path.basename(g['url'])), 'wb').write(get(g['url'])); tam = g['size']
        for rel, inc in g.get('include', {}).items():
            p = os.path.join(d, rel); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'wb').write(get(inc['url'])); tam += inc['size']
        open(os.path.join(d, 'LICENCA.txt'), 'w').write(f'{i} — Poly Haven (https://polyhaven.com/a/{i}) — CC0 (domínio público)\n')
        print(f'ok {i} ({tam / 1e6:.1f} MB)')
    except Exception as e: print(f'-- {i}: ERRO {type(e).__name__}: {str(e)[:120]}')
