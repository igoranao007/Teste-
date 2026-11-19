#!/usr/bin/env python3
"""Checagem de sintaxe OBRIGATÓRIA antes de qualquer QA/render: lib/*.js, tools/*.mjs e o <script type="module"> de cada plano.
(registro #29: um comentário // inserido no meio de uma linha derrubou um plano inteiro — duas vezes)"""
import glob, re, subprocess, sys, tempfile, os
ruins = 0
alvos = sorted(glob.glob('lib/*.js') + glob.glob('tools/*.mjs'))
for f in alvos:
    r = subprocess.run(['node', '--check', f], capture_output=True, text=True)
    if r.returncode: ruins += 1; print('✗', f, r.stderr.strip().splitlines()[:3])
with tempfile.TemporaryDirectory() as d:
    for f in sorted(glob.glob('videos/*/index.html')):
        m = re.search(r'<script type="module">(.*?)</script>', open(f).read(), re.S)
        if not m: continue
        p = os.path.join(d, 'x.mjs'); open(p, 'w').write(m.group(1))
        r = subprocess.run(['node', '--check', p], capture_output=True, text=True)
        if r.returncode: ruins += 1; print('✗', f, r.stderr.strip().splitlines()[:3])
print('✓ sintaxe ok' if not ruins else f'⚠ {ruins} arquivo(s) com erro de sintaxe'); sys.exit(1 if ruins else 0)
