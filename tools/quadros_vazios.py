"""QA de enquadramento: acha trechos do filme em que o quadro está 'vazio' (quase uniforme: só névoa, só preto)
— câmera apontando pro nada. uso: python3 tools/quadros_vazios.py out/the-green-path-v4.mp4 [lim=9]
Compara com a lista de trechos vazios DE PROPÓSITO (tela preta do começo, transições)."""
import subprocess, sys, numpy as np
v = sys.argv[1]; lim = float(sys.argv[2]) if len(sys.argv) > 2 else .8
W, H = 160, 90
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', v, '-vf', f'fps=4,scale={W}:{H},format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
f = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(float)
# desvio padrão do quadro sem as legendas/ficha (faixa de baixo e canto direito podem ter texto)
core = f[:, int(H * .08):int(H * .72), int(W * .05):int(W * .62)]
gx = np.abs(np.diff(core, axis=2)).mean(axis=(1, 2)); gy = np.abs(np.diff(core, axis=1)).mean(axis=(1, 2))
sd = gx + gy; t = np.arange(len(sd)) / 4          # energia de bordas: névoa lisa ~0; cena escura com objetos tem bordas
vazio = sd < lim; trechos = []; i = 0
while i < len(vazio):
    if vazio[i]:
        j = i
        while j < len(vazio) and vazio[j]: j += 1
        if (j - i) / 4 >= .75: trechos.append((t[i], t[j - 1], round(float(sd[i:j].mean()), 1)))
        i = j
    else: i += 1
PROPOSITAL = [(0, 2.2), (266.5, 269.8)]   # preto + ruído do começo · v5: preto seco depois do "Dom?! É você?" e antes do EM BREVE
ruins = [x for x in trechos if not any(a <= x[0] and x[1] <= b for a, b in PROPOSITAL)]
for a, b, m in trechos: print(f"{'OK (proposital)' if (a, b, m) not in ruins else 'VAZIO':16s} {int(a//60)}:{a%60:05.2f}–{int(b//60)}:{b%60:05.2f}  bordas {m}")
print('✓ nenhum quadro vazio fora do previsto' if not ruins else f'⚠ {len(ruins)} trecho(s) com câmera no vazio'); sys.exit(1 if ruins else 0)
