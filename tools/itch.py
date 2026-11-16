"""Baixa assets GRATUITOS do itch.io (só páginas que permitem download por R$ 0).
uso: python3 tools/itch.py <pasta-saida> <url-da-pagina> [...]
Imprime preço, licença encontrada na página e os arquivos baixados. Não usa conta nem chave."""
import sys, re, os, json, html, requests
out, urls = sys.argv[1], sys.argv[2:]
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) asset-fetch"}
for url in urls:
    url = url.rstrip("/"); nome = url.split("//")[1].replace(".itch.io/", "__")
    s = requests.Session(); s.headers.update(UA)
    try:
        pg = s.get(url, timeout=60).text
        tok = re.search(r'name="csrf_token" value="([^"]+)"', pg)
        tok = tok.group(1) if tok else s.cookies.get("itchio_token", "")
        lic = re.findall(r'(CC0|CC[ -]BY[^<"]{0,20}|Creative Commons[^<"]{0,60}|public domain|commercial[^<."]{0,80})', pg, re.I)
        pago = re.search(r'"min_price":\s*(\d+)', pg)
        r = s.post(url + "/download_url", data={"csrf_token": tok}, timeout=60).json()
        if "url" not in r: print(f"-- {nome}: NÃO É GRÁTIS / sem download direto ({r})"); continue
        dp = s.get(r["url"], timeout=60).text
        ups = re.findall(r'data-upload_id="(\d+)"', dp)
        nomes = [html.unescape(n) for n in re.findall(r'<strong title="([^"]+)" class="name"', dp)]
        key = re.search(r'/download/([^/?"]+)', r["url"]).group(1)
        d = os.path.join(out, nome); os.makedirs(d, exist_ok=True)
        print(f"== {nome} | licença: {sorted(set(x.strip() for x in lic))[:4]} | arquivos: {nomes}")
        for i, uid in enumerate(dict.fromkeys(ups)):
            j = s.post(f"{url}/file/{uid}", params={"source": "game_download", "after_download_lightbox": "true"}, headers={"Referer": r["url"]}, data={"csrf_token": tok}, timeout=60).json()
            if "url" not in j: print("   sem url:", j); continue
            fn = nomes[i] if i < len(nomes) else ""
            if re.search(r"\.(pdf|rtf|txt|mtl|tar\.gz|exe|unitypackage)$", fn, re.I) or "godot" in fn.lower(): print("   pulei", fn); continue
            with s.get(j["url"], stream=True, timeout=300) as g:
                g.raise_for_status(); tam = 0
                cd = re.search(r'filename="?([^";]+)', g.headers.get("Content-Disposition", ""))
                if cd: fn = requests.utils.unquote(cd.group(1))
                fn = fn or f"{uid}.zip"
                if not re.search(r"\.(zip|rar|7z|fbx|glb|gltf|obj|blend|png|jpg)$", fn, re.I): print("   pulei", fn); continue
                with open(os.path.join(d, re.sub(r"[^\w.\- ]", "_", fn)), "wb") as f:
                    for ch in g.iter_content(1 << 16):
                        f.write(ch); tam += len(ch)
                        if tam > 300e6: raise RuntimeError("maior que 300 MB")
            print(f"   ok {fn} ({tam/1e6:.1f} MB)")
    except Exception as e:
        print(f"-- {nome}: ERRO {type(e).__name__}: {str(e)[:200]}")
