"""Baixa pacotes do OpenGameArt.org pela página do conteúdo, imprimindo a LICENÇA e o autor de cada um.
uso: python3 tools/oga.py <pasta-saida> <slug-ou-url> [...]     (slug = o fim de opengameart.org/content/<slug>)
Grava <pasta>/<slug>/ com os arquivos e um LICENCA.txt (licença, autor, link). Zips são descompactados ao lado."""
import sys, re, os, html, zipfile, urllib.request
out, itens = sys.argv[1], sys.argv[2:]
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) asset-fetch"}
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120)
for it in itens:
    slug = it.rstrip('/').split('/content/')[-1]; url = 'https://opengameart.org/content/' + slug
    try:
        pg = get(url).read().decode('utf-8', 'replace')
        titulo = html.unescape((re.search(r'<title>([^<|]+)', pg) or [None, slug])[1]).strip()
        bloco = lambda campo: (re.search(r'field-name-field-' + campo + r'.*?</div>\s*</div>\s*</div>', pg, re.S) or [''])[0]
        lic = sorted(set(html.unescape(x).strip() for x in re.findall(r'>\s*((?:CC0|CC-BY[^<]*|CC BY[^<]*|GPL[^<]*|OGA-BY[^<]*|LGPL[^<]*))\s*<', bloco('art-licenses'))))
        autor = sorted(set(html.unescape(x) for x in re.findall(r'href="/users/[^"]+"[^>]*>([^<]+)<', pg[:pg.find('field-name-field-art-files')] if 'field-name-field-art-files' in pg else pg)))[:3]
        arqs = sorted(set(re.findall(r'https://opengameart\.org/sites/default/files/[^"\'<> ]+', bloco('art-files'))))
        d = os.path.join(out, slug); os.makedirs(d, exist_ok=True)
        print(f"== {slug} | {titulo} | licença: {lic} | autor: {autor} | arquivos: {len(arqs)}")
        open(os.path.join(d, 'LICENCA.txt'), 'w').write(f"{titulo}\n{url}\nLicença: {', '.join(lic) or 'NÃO ENCONTRADA — conferir'}\nAutor (página): {', '.join(autor)}\n")
        for a in arqs:
            fn = os.path.join(d, re.sub(r'[^\w.\- ]', '_', urllib.request.unquote(a.rsplit('/', 1)[1])))
            if not os.path.exists(fn):
                with get(a) as r, open(fn, 'wb') as f: f.write(r.read())
            print(f"   ok {os.path.basename(fn)} ({os.path.getsize(fn) / 1e6:.1f} MB)")
            if fn.lower().endswith('.zip'):
                try: zipfile.ZipFile(fn).extractall(fn[:-4])
                except Exception as e: print('   zip ruim:', e)
    except Exception as e:
        print(f"-- {slug}: ERRO {type(e).__name__}: {str(e)[:150]}")
