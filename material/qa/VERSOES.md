# THE GREEN PATH v4 — histórico de versões

Regra: a versão anterior aprovada fica guardada (tag git `vX-estavel` + cópia do vídeo em `out/historico/`, fora do git
por causa do tamanho). Pra voltar: `git checkout v4.3-estavel -- lib videos tools` e re-renderizar, ou usar o mp4 guardado.

## v4.3 (estável) — tag `v4.3-estavel` (commit fdd8ad9) · `out/historico/v4.3-720p.mp4`
- Base desta rodada. Problemas que o diretor achou nela: BUG 01–04 abaixo.

## v4.4 (estável) — tag `v4.4-estavel`
**Mudanças**
- Metalis (44): caminhada única com passada medida; virada suave; gestos com alvos relativos ao corpo (ombro), cotovelo pra fora;
  mão no peitoril viva (respira, ergue nas falas); câmeras de 3/4 por fora.
- Frentista (43): caminhadas com tempo natural (antes 2,9 m em 0,85–1,1 s = 3–4 m/s, corria com a animação de andar);
  plano 43 de 22 → 24 s; pagamento reposicionado (bolso DIREITO), câmera lateral na troca da grana.
- Mangueira (43): rota que desce primeiro e é empurrada pra fora das cápsulas do corpo do frentista.
- Elevador (50): andam quando a porta abre (1,7 s) e chegam em 11 s (antes 0–2,4 s parados + 15,4 s pra 10 m); viram um pro
  outro; plano/contraplano por cima do ombro.
- Motor: trava do pé (foot locking) em toda caminhada; mistura parado↔andando .15 s; passada medida por personagem.
- QA: braço atravessando o corpo, braço congelado, pé deslizando (métrica corrigida: os DOIS pés fora do chão), objeto flexível × corpo.

**Problemas encontrados → corrigidos**: ver `REGISTRO.md` #21–#28.

**Testes**: `bash tools/qa_todos.sh` (resultado em `RESUMO.txt`), `quadros_vazios.py`, folha 1 qps do filme inteiro,
quadro a quadro de 43 (bico/mangueira/grana), 44 (Metalis), 50 (elevador), `NAO_REGREDIR.md`.

**Resultado**: QA quadro a quadro (PASSO=1) aprovado em todos os planos com personagem; `quadros_vazios.py` = 0;
folha 1 qps dos 232 s revisada; 720p 63 MB. Tag `v4.4-estavel` · `out/historico/v4.4-720p.mp4`.
Pendências documentadas em `AUDITORIA_v4.4.md` (o que não dá pra medir automaticamente).
