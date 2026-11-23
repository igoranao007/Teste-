# 8. Como o diretor trabalha (preferências e regras)

## Comunicação
- Escreve em **português do Brasil**, informal, rápido, às vezes com erros de digitação ("fraquetain" = Frankenstein, "din" = fim, "precher" = preencher).
  Interprete pela intenção; se ambíguo, mostre opções lado a lado (fotos) e pergunte o mínimo.
- Manda **capturas de tela com o tempo do vídeo** (ex. 00:54, 03:18): investigue exatamente aquele quadro, ache a causa, e confira o resto.
- Quer ser avisado do que você está fazendo; respostas diretas, com o que mudou, onde ver no vídeo (tempo) e o que não deu pra verificar.
- Gosta de ser tratado como diretor: análise "quadro a quadro", "como mestre animador". Odeia ter que achar bugs que você deveria ter achado.

## Gosto / estética
- Identidade **PS1/PSX**: low-poly, pixel duro, cor de 15 bits, vértice tremendo, neblina, noite verde. Não "modernizar".
- Realismo de comportamento: gente sai do carro como gente, porta secreta tem portinhola, frentista segue o procedimento real de abastecer.
- Rostos de foto **chapados/planos** (referência: freira de terror PS1), não "bolha".
- Personagens consistentes com o elenco (mesmo modelo base), mas aceita "Frankenstein" (corpo de um, cara de outro).
- Cores do Dom: claro + amarelo; texto em japonês nas costas ("小人の隠れ家" = Toca do Anão).

## Regras de entrega e git (do ambiente)
- Branch: `claude/mp4-animation-threejs-remotion-xyh5wp`; nunca outra sem permissão; **não abrir PR** sem pedido.
- Commits em PT-BR terminando com as linhas de autoria (Co-Authored-By/Claude-Session). Sem ID de modelo em commit.
- **Nunca** commitar o pacote pago (JashiPSX) nem modelos/pacotes de terceiros que não podem ser redistribuídos.
- Não modificar o vídeo antigo v3. Entrega 720p < 100 MB. Guardar a versão anterior (tag + histórico) antes de cada nova.
- Privacidade: não enviar dados do diretor pra serviços externos; clonagem de voz só local.
- Hook do ambiente pede commit+push quando há mudanças não salvas: faça.
