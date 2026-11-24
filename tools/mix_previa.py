"""Mixagem RÁPIDA pra prévia de uma cena (antes da mixagem final): cada som entra num instante, com ganho; um som pode ficar em loop.
uso: python3 tools/mix_previa.py saida.wav DURACAO "arquivo@inicio@dB" ["arquivo@inicio@dB@loop" ...]
     depois: ffmpeg -i video.mp4 -i saida.wav -c:v copy -c:a aac -shortest com_som.mp4"""
import sys, subprocess
out, dur, itens = sys.argv[1], float(sys.argv[2]), sys.argv[3:]
ins, fil = [], []
for i, it in enumerate(itens):
    p = it.split('@'); arq, t0, db = p[0], float(p[1]), float(p[2]); loop = len(p) > 3
    ins += (['-stream_loop', '-1'] if loop else []) + ['-i', arq]
    fil.append(f'[{i}:a]aresample=48000,aformat=channel_layouts=stereo,volume={db}dB,adelay={int(t0 * 1000)}|{int(t0 * 1000)},atrim=0:{dur}[a{i}]')
mix = ''.join(f'[a{i}]' for i in range(len(itens))) + f'amix=inputs={len(itens)}:normalize=0:duration=longest,atrim=0:{dur},alimiter=limit=0.95[o]'
subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fil) + ';' + mix, '-map', '[o]', '-ar', '48000', out], check=True)
print('mix', out, dur, 's', len(itens), 'sons')
