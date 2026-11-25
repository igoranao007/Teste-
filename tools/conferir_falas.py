"""Confere as tomadas de voz: transcreve cada uma (Whisper local, nada sai da máquina) e compara com o texto do roteiro.
Mostra a nota de semelhança (0–1), a duração e o pico; sugere a melhor tomada de cada fala (texto certo, sem cortar, sem enrolar).
uso: <venv-com-whisper>/bin/python tools/conferir_falas.py [quem...]   →   imprime e grava audio/voz/ep1/CONFERENCIA.txt"""
import sys, os, glob, difflib, re, unicodedata
import whisper
sys.path.insert(0, os.path.dirname(__file__))
TXT = {}
for linha in open(os.path.join(os.path.dirname(__file__), 'falas_ep1.py')):
    m = re.match(r"\s*\('(\w+)', \"(.+?)\"", linha) or re.match(r".*\('(\w+)', \"(.+?)\"", linha)
    if m: TXT[m.group(1)] = m.group(2)
def norm(s): return ' '.join(re.sub(r'[^a-z0-9 ]', ' ', unicodedata.normalize('NFKD', s.lower()).encode('ascii', 'ignore').decode()).split())
SO = sys.argv[1:]
mod = whisper.load_model('small')
saida = []
for quem in sorted(os.listdir('audio/voz/ep1')):
    d = f'audio/voz/ep1/{quem}'
    if not os.path.isdir(d) or quem in ('mix', 'ref', 'amostras') or (SO and quem not in SO): continue
    por_fala = {}
    for f in sorted(glob.glob(d + '/*-[0-9].wav')):
        id_ = os.path.basename(f).rsplit('-', 1)[0]
        if id_ not in TXT: continue
        r = mod.transcribe(f, language='pt', fp16=False); ouvido = r['text'].strip()
        nota = difflib.SequenceMatcher(None, norm(ouvido), norm(TXT[id_])).ratio()
        dur = whisper.audio.load_audio(f).shape[0] / 16000
        por_fala.setdefault(id_, []).append((nota, dur, f, ouvido))
    for id_, ts in por_fala.items():
        ts.sort(key=lambda x: -x[0]); melhor = ts[0]
        saida.append(f'{quem} {id_}: "{TXT[id_]}"')
        for nota, dur, f, ouvido in ts: saida.append(f'   {"★" if f == melhor[2] else " "} {os.path.basename(f)}  {nota:.2f}  {dur:.2f}s  ouvido: "{ouvido}"')
print('\n'.join(saida)); open('audio/voz/ep1/CONFERENCIA.txt', 'w').write('\n'.join(saida) + '\n')
