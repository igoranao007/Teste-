# AUDITORIA — EPISÓDIO 1, cenas 60–68 (pelo MANUAL DE DIREÇÃO do diretor, 25/11)

**Como foi verificado:** folhas de quadros a cada 0,75–1 s dos vídeos RENDERIZADOS (`entrega/ep1/*.mp4`), não do código; as falas novas
foram conferidas por transcrição local (`audio/voz/ep1/CONFERENCIA.txt`); a sirene foi medida segundo a segundo (abaixa 10 dB sob as falas).
**Não verificado:** a escuta humana do áudio (eu não ouço: conferi texto, tempo e volume, não a qualidade da atuação).

## Problemas achados e o que foi feito

| ID | Prio | Timecode | Esperado | Observado (v1) | Correção | Estado |
|---|---|---|---|---|---|---|
| 67-QUEDA-001 | P1 | 12,3–13,9 | queda em 3 tempos (susto · cedência · impacto/acomodação) | tombava rígido "como tábua", fora de quadro atrás da mesa | susto (mãos sobem, tranco pra trás) → braços pra frente procurando apoio enquanto a cadeira tomba → impacto com quique, mãos batem no chão, tremor de câmera só no impacto; câmera nova, do lado livre | **RESOLVIDO** (v2, 13,0 s e 13,8 s) |
| 67-CONT-002 | P1 | 15,4 | depois da queda ele continua de costas | reaparecia DE BRUÇOS (teletransporte de pose) | 15,4–16,4: ainda de costas na cadeira caída, força pra se erguer → corte NA AÇÃO pra ele de joelhos levantando | **RESOLVIDO** (v2, 16,0 s → 16,8 s) |
| 67-LUZ-003 | P1 | 15,4–20 | corpo legível sob a sirene | vermelho escuro: não se via o Igor | luz vermelha com preenchimento; câmera sem obstáculo | **RESOLVIDO** (v2) |
| 67-COR-004 | P2 | 15,2 | sirene vermelha contínua | a tela voltava pro amarelo | vermelho fixo na tela durante a sirene | **RESOLVIDO** (v2, 14,6 s) |
| 67-AUD-005 / 68-AUD-004 | P1 | 13,5–21 / 0–23 | diálogo sempre à frente | sirene não abaixava sob as falas | sirene com "ducking" automático (−10 dB em cada fala, rampas suaves) | **RESOLVIDO** (medido) |
| 68-POV-001 | P1 | 2,8–5,2 | POV do Adryan sem corte pra fora no meio do diálogo | plano de fora do Adryan no meio do POV | o protesto fica em POV (ouvimos o Adryan, o Igor reage); o corte pra 3ª pessoa só quando ele sai andando (ação nova) | **RESOLVIDO** (v2, 3,2–4,2 s) |
| 68-PORTA-002 | P1 | 15–17,5 | fechar a porta legível (contato, peso, batente) | porta escura, ação ilegível | luminária de grade sobre a porta (fonte de luz real) + câmera que mostra a folha e o vão | **RESOLVIDO** (v2, 16,2–17,2 s) |
| 68-ENQ-003 | P2 | 11–15 | rosto de quem fala (Gusta) | Gusta escondido atrás do Adryan | câmera reposicionada | **RESOLVIDO** (v2, 12,2 s) |
| 65-INT-001 | P2 | 11,2–12,9 | mão no mouse e clique visíveis | o clique acontece (movimento + som + a tela responde "ACESSANDO"), mas a mão no mouse não aparece em detalhe | tentei um insert em POV do Adryan: o corpo do Igor e a maleta tapam o mouse | **PENDENTE** |
| 67-ATU-006 | P2 | 0–3,2 | atuação no susto do "LOCAL DESCOBERTO" | rosto em close quase parado (as mãos sobem, mas ficam fora do quadro) | — | **PENDENTE** |
| GERAL-BOCA-001 | P2 | todas | boca acompanha a fala | Igor e Dom mexem a boca; Adryan, Gusta e Metalis só a cabeça (os modelos não têm osso de mandíbula) | — | **LIMITAÇÃO** (precisa de boca no modelo) |
| GERAL-GRITO-001 | P2 | 67 12,35 | grito de susto | o modelo de voz não grita: ficou um "Ah..." + o som da queda | — | **LIMITAÇÃO** |

## Resultado por cena
- **60, 61, 62** — aprovadas pelo diretor (25/11).
- **63 · entrega (POV)** — APROVADO COM PENDÊNCIAS (P3: o Gusta não aparece no POV, só no som dos passos).
- **64 · fita (POV)** — APROVADO.
- **65 · computador novo** — APROVADO COM PENDÊNCIAS (65-INT-001, P2).
- **66 · tela ARG-14** — APROVADO.
- **67 · Dom, queda e sirene (v2)** — APROVADO COM PENDÊNCIAS (67-ATU-006, P2; limitações de boca/grito).
- **68 · porta-bunker (v2)** — APROVADO COM PENDÊNCIAS (P2: o cone de luz da porta aparece como uma cunha clara em 2 planos).
Nenhum P0 em aberto. Aprovação final é do diretor.
