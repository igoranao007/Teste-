# MANUAL DE DIREÇÃO, CONTINUIDADE E QA — TOCA DO ANÃO (regras do diretor, 25/11)

> Original completo: `material/producao/minisserie/MANUAL_DIRECAO_TOCA_DO_ANAO.pdf`. **Usar ANTES de produzir, ao revisar cenas existentes
> e DEPOIS de cada renderização.** Vale pra todas as cenas, passadas e futuras. Resumo operacional abaixo (o PDF manda em caso de dúvida).

## Regra de honestidade técnica
Nunca dizer "corrigido" sem ver a versão renderizada. Se não deu pra verificar, dizer exatamente o que foi e o que não foi verificado.
Prioridades: **P0** quebra a compreensão/lógica (POV errado, teletransporte, queda sem causa) · **P1** prejudica forte a imersão (colisão
ausente, atuação congelada, fala inaudível, corte confuso) · **P2** reduz qualidade (enquadramento, timing, luz pouco legível) · **P3** polimento.

## 12 regras inegociáveis
1. **POV**: câmera = olhos do personagem; ele não aparece de fora na mesma ação. Mãos/braços podem aparecer se coerentes. Mudar pra 3ª pessoa = corte claro.
2. **Continuidade**: posição, orientação, distância, estado e direção de personagens e objetos se mantêm; nada de teletransporte ou troca de lado.
3. **Causa e efeito**: ninguém cai, grita, reage ou muda de posição sem motivo estabelecido.
4. **Interação**: computador, mouse, teclado, portas, maçanetas exigem contato visível e sincronizado; a interface responde; objeto não se move sozinho.
5. **Física**: gravidade, colisão, peso, inércia, resistência, pés apoiados, mãos em contato; sem atravessar, flutuar ou penetrar malha.
6. **Animação**: antecipação → ação → acomodação; respiração, ajustes de equilíbrio, olhar; nada de pose congelada ou movimento mecânico.
7. **Quedas em 3 tempos**: (1) susto/desequilíbrio — ombros contraem, centro de gravidade desloca; (2) cedência — joelhos flexionam, tronco
   recua, braços procuram proteção; (3) impacto/acomodação — mãos, antebraço, quadril tocam o chão em sequência, o corpo absorve e estabiliza.
   **Evitar**: aparecer já deitado no quadro seguinte · cair reto como tábua · parar instantâneo sem reação secundária.
8. **Atuação**: falas curtas e naturais com intenção (alerta, dúvida, susto, ordem, medo); boca, voz, expressão e respiração sincronizadas; gritar ≠ atuar.
9. **Áudio**: diálogo inteligível SEMPRE à frente; sirene/efeitos sustentam a tensão sem cobrir a fala; impactos no quadro do contato.
10. **Legibilidade**: silhuetas, roupas, camisas (Vasco) e identidade legíveis; luz, sombra e efeito não escondem a ação.
11. **Câmera**: todo plano tem função; nada de corte aleatório nem tremor constante (tremor só em impacto/susto); movimento respeita corpo e ação.
12. **Fidelidade**: não alterar personagens, história, figurino, identidade visual ou o que deve ficar oculto sem autorização.

## Testes de aprovação
- **Pausa em qualquer corte**: dá pra dizer onde está a câmera, pra onde olham e onde estão os objetos importantes?
- **Sem áudio**: entende-se a ação? **Sem olhar**: entende-se quem fala e o que aconteceu?

## Processo (por cena)
1 ENTENDER (o que a cena comunica, o que fica oculto) · 2 AUDITAR (tabela: problema, P0–P3, evidência com timecode, causa provável, correção)
· 3 PLANEJAR (beats + plano de tomadas: enquadramento/POV, posições, ação, reação, causa, consequência, animação, som, critério)
· 4 IMPLEMENTAR (mudanças pequenas e rastreáveis, sem sobrescrever originais) · 5 VALIDAR (renderizar e revisar cortes, contatos, colisões,
sincronia, áudio e posições finais) · 6 RELATAR (o que foi analisado/alterado/testado, resolvido com evidência, pendente, limitações reais)
→ **APROVADO · APROVADO COM PENDÊNCIAS · REPROVADO · NÃO VALIDADO** (não aprovar com P0; não esconder P1).

## Formato de bug report
`ID [CENA-AREA-NNN] · Prioridade · Timecode · Esperado · Observado · Impacto · Causa provável (hipótese) · Correção · Teste de aceite`

**Princípio final: a cena não está pronta quando parece pronta no código. Está pronta quando o resultado renderizado comunica exatamente
a intenção, sem quebrar a lógica, a física, a atuação ou a continuidade.**
