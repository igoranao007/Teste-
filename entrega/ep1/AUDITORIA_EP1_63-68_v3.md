# AUDITORIA — EPISÓDIO 1, sequência do bunker 63–68 (versão 3, 25/11) — pelo MANUAL DE DIREÇÃO

**Pedido do diretor:** "vi que tem objetos flutuando ou objetos sem sentido. Tipo um copo d'água no Japão" + a sequência inteira no POV do
Adryan, com continuidade, e a KATANA AMARELA (aprovada) logo depois de trancarem a porta.

**Como foi verificado:** (1) QA automático de física em cada cena (`node tools/qa_flutuando.mjs <cena> <t>`: raio pra baixo da base de cada
objeto + objetos do tampo da mesa que se atravessam); (2) câmeras de inspeção de fora (mesa, estantes, arquivo); (3) folhas de quadros dos
vídeos RENDERIZADOS (1 quadro/s, e 10 quadros/s no beat da katana). **Não verificado:** escuta humana do áudio.

## Problemas achados e o que foi feito

| ID | Prio | Onde | Observado | Correção | Estado |
|---|---|---|---|---|---|
| SALA-FIS-001 | P1 | 63–68 | o COPO d'água ficava no ar, fora da mesa nova (era da mesa antiga, maior) | copo no tampo, canto direito da frente | **RESOLVIDO** (QA: 0 cm) |
| SALA-FIS-002 | P1 | 63–68 | porta-retrato, pilha de pastas e luminária de mesa ficavam DENTRO da maleta aberta | retrato → frente-centro; luminária → canto frente-direito; pastas → em cima do arquivo de metal | **RESOLVIDO** (QA: nenhum objeto se atravessando) |
| SALA-FIS-003 | P1 | 63–68 | blocos de livros no meio do vão da estante, apoiados na ponta de um fichário | cada item vai pra tábua da sua fileira (tábuas achadas por raio) | **RESOLVIDO** |
| SALA-FIS-004 | P1 | 63, 64 | o computador ANTIGO boiava 21–24 cm acima da mesa (e a 65 já usava o novo: erro de continuidade) | 63 e 64 usam a mesma sala arrumada (`lib/bunker.js` → `arrumarSala`) e o computador novo | **RESOLVIDO** |
| SALA-FIS-005 | P2 | 63–68 | celular no lugar da pasta das fichas; gabinete a 80 cm do chão | celular ao lado do copo; gabinete no chão; a pasta das fichas tem lugar fixo (GEO.FICHAS) e aparece fechada da 64 à 68 | **RESOLVIDO** |
| 63/64-INS-003 | P2 | 63 6–11 s · 64 3,2–8,6 s | fichas e fita filmadas "de cima" (fora do olhar do Adryan) | POV: o Adryan baixa o olhar pras fichas / se inclina sobre a maleta | **RESOLVIDO** |
| 68-POV-001 | P0 | 68 inteira | metade da cena era de fora do Adryan | 68 v3 toda em POV, mãos dele no puxador e no volante | **RESOLVIDO** |
| 68-CONT-002 | P1 | 67→68 | posições "pulavam" de uma cena pra outra | começa onde a 67 termina (Adryan em GEO.RECUO, Igor em GEO.IG_PE, Gusta perto da porta, cadeira caída, maleta aberta); o Igor contorna a cadeira até o botão | **RESOLVIDO** |
| 68-KAT-005 | — | 68 23,7–30 s | (beat novo, aprovado) | pancada → a lâmina amarela atravessa a ~40 cm da cabeça (faíscas, vibração) → esquiva em 3 tempos → no chão respirando, sirene abafada | **FEITO** (24,3 s) |
| 68-LUZ-006 | P1 | 68 18–20,6 s | fechar a porta ficou escuro (v3 primeiro render) | luz da luminária de grade sobre a porta na folha enquanto ele está nela | **CORRIGIDO** (re-render) |
| 68-ENQ-007 | P2 | 68 25,4–30 s | no chão a lâmina ficava pequena | o olhar fixa e aproxima na lâmina | **CORRIGIDO** (re-render) |
| 68-GIRO-008 | P1 | 68 1,4–3,1 · 22,6–24,1 s | (achado no teste) virar o olhar entre dois alvos opostos passava pela própria cabeça / pelo Gusta | o olhar gira pelo ÂNGULO, pela direita, longe do Gusta | **RESOLVIDO** |

## Falsos positivos do QA (conferidos à mão)
fechos e tampa da maleta aberta (presos na dobradiça), partes do Igor e da cadeira, a água dentro do copo, a tela de dentro do monitor,
relógio de parede e lâmpada pendurada (presos), telas da sala secreta (penduradas na parede).

## Resultado por cena
- **63 · entrega (POV)** — APROVADO.
- **64 · fita (POV)** — APROVADO.
- **65 · computador** — APROVADO COM PENDÊNCIAS (65-INT-001 da auditoria anterior: o mouse aparece pouco).
- **66 · tela ARG-14** — APROVADO.
- **67 · Dom, queda e sirene** — APROVADO COM PENDÊNCIAS (67-ATU-006, P2).
- **68 · porta, botão, katana (v3)** — APROVADO COM PENDÊNCIAS (P2: no plano do chão, 25,4–30 s, a lâmina ainda é fina na tela —
  lê como lâmina amarela cravada, mas pequena; P3: o rosto do Igor fica pequeno no fundo nos primeiros 11 s).
  Re-render conferido: porta legível (18–21 s), katana com faíscas e vibração (24,3–24,7 s), esquiva em 3 tempos (24,3–25,35 s).

## Entregas (versões novas; as antigas ficam)
`63-sala_v2.mp4` · `64-fita_v2.mp4` · `65-computador_v2.mp4` · `66-tela_v2.mp4` · `67-dom_v3.mp4` · `68-porta_v3.mp4` ·
`sequencia_sala_do_igor_v2.mp4` (63→68 emendadas, 1 min 42 s).
Aprovação final é do diretor.
