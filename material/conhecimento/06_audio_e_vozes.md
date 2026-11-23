# 6. Áudio e vozes

## Som sintetizado (`audio/synth.py`)
- Tudo é gerado por código a partir de "cues" (`tools/som4.py` → `videos/00-filme4/cues.json`): motor, pneus, grilos, lâmpada, chiado de fita,
  drones, impactos, cliques, e os da v4.5: **porta do carro abrindo/batendo, batida de nós dos dedos, portinhola, rangido, trinco**.
- Mix final em −14 LUFS. Stingers estavam ~12 dB acima da mediana (o diretor achou alto) → −5…−9 dB.
- Som novo = função `fx_nome()` + entrada em `SFX.update({...})` com (função, ganho dB, estéreo?). Cue: `cue('nome', P('57') + t, gain=..., param=...)`.

## Passos (`passos()` no som4.py)
- Um som por **contato do pé**, nas fases medidas do clipe (`material/qa/pes.json`), com a mesma aceleração do `caminhar`.
- Superfície por cena (concreto, mato, madeira, corredor, carpete, arrasto) × peso do personagem × variação; volume igualado entre superfícies.
- `re=True` (de ré), `ate=` (corta passos depois do fim do plano).

## Vozes (clonagem LOCAL com Chatterbox)
- `tools/falas_v4.py` / `tools/falas_v5.py`: referência de cada personagem (amostra do dono da voz ou as próprias falas já usadas), 2–3 tomadas por fala.
- **Sempre conferir com faster-whisper** (texto ouvido = texto pedido) e escolher a tomada; cortar silêncio das pontas (`silenceremove` + `areverse`).
- Problemas vistos: tomada alucinando (15 s pra uma frase de 3 s); "Dom" lido como "Então" → grafia "D'om".
- **Voz de vilão do Dom:** "voz pública" = a voz padrão do modelo aberto (não é de pessoa real identificável), tratada com `tools/vilao.sh`:
  −4 semitons sem mudar a velocidade + camada uma oitava abaixo + graves + compressor + saturação leve + eco grande.
- Personagem sem voz (Nicolas): só legenda — `FALAS` com arquivo `None` (o som4 calcula a duração pelo tamanho do texto).
- Boca/cabeça seguem o volume da fala por quadro (`material/voz-v4.json`); gesto de fala usa `fala.peso()` (peso suave pela fala inteira), nunca o volume quadro a quadro (tremia).
