# THE GREEN PATH — pacote de conhecimento (pra próxima sessão do Claude)

> Se você é o Claude e recebeu este zip: **leia tudo antes de mexer em qualquer coisa**. Isto é o que uma sessão inteira
> aprendeu fazendo o filme THE GREEN PATH com o diretor (Igor Anão): o que funcionou, o que deu errado, por quê, e como
> não repetir. Trate como um professor falando com você. O diretor fala **português do Brasil**: responda sempre em PT-BR.

## Ordem de leitura
| # | Arquivo | O que tem |
|---|---|---|
| 1 | `01_projeto_e_pipeline.md` | o que é o filme, como o código está organizado, como renderizar, comandos |
| 2 | `02_apps_e_ferramentas.md` | todos os apps/bibliotecas usados, versões, pra que serve cada um, armadilhas de instalação |
| 3 | `03_personagens_e_modelos.md` | **as 3 formas de fazer personagem**: modelo em código, modelo pronto (pago/grátis), "Frankenstein" — passo a passo |
| 4 | `04_animacao_e_motor.md` | o motor de animação: avaliador próprio, IK com rotação, trava do pé, caminhar, pegar objetos, portas, carro |
| 5 | `05_qa_erros_e_licoes.md` | **os erros que eu cometi** e a regra que nasceu de cada um; o sistema de QA; checklist |
| 6 | `06_audio_e_vozes.md` | som sintetizado, passos por superfície, clonagem de voz local, voz de vilão, conferência com Whisper |
| 7 | `07_cameras_cenas_e_direcao.md` | enquadramento, câmeras que dão errado, POV, como cada cena foi resolvida |
| 8 | `08_preferencias_do_diretor.md` | como o diretor trabalha, o que ele gosta/odeia, regras de entrega e de git |
| 9 | `09_historico_de_pedidos.md` | linha do tempo dos pedidos e versões (v3 → v5) |
| — | `conversa_completa.md` | a conversa inteira em texto (sem saídas de ferramenta; e-mail removido) |
| — | `referencia/` | cópias dos arquivos-chave de QA (registro de bugs, checklist, não-regredir, versões, auditoria) |
| — | `codigo/` | cópias dos arquivos de código mais importantes (pra consulta; a fonte da verdade é o repositório) |
| — | `imagens/` | folhas de personagem (o que o diretor aprovou) |

## As 10 regras de ouro (se só der tempo de ler isto)
1. **Medição não substitui olhar.** Toda correção: medir (QA) **e** tirar fotos de perto, de 2 ângulos, nos quadros de início/meio/fim.
2. **Revise o filme INTEIRO depois de renderizar** (folha 1 quadro/s + `tools/quadros_vazios.py`), não só o trecho mexido.
3. **Nunca insira `// comentário` no meio de uma linha** com edição automática — quebrou planos inteiros 3 vezes. Use `/* */`. Rode `python3 tools/sintaxe.py`.
4. **Ache a causa raiz** antes de remendar: ex. o `AnimationMixer` do Three.js não reescreve ossos parados → tudo acumulava (girava/tremia).
5. **Velocidade realista:** distância ÷ tempo sempre conferida (andar 1,1–1,4 m/s). Personagem "correndo" com animação de andar = pé patinando.
6. **O personagem tem que ALCANÇAR o que segura**: confira ombro, comprimento do braço e altura do alvo (o Metalis de 1,10 m não alcançava a janela).
7. **Mão nunca cruza o corpo** pra pegar algo do outro lado: use a mão do lado certo (o Igor folheava com a mão errada; o frentista guardava a grana no bolso errado).
8. **Câmera:** o que está entre a câmera e o rosto (monitor, moldura da porta, vidro) estraga o plano. Rosto feito de foto só funciona de FRENTE.
9. **Nada liga/desliga de um quadro pro outro**: tudo com rampa (pesos, pegadas, gestos, direção da mão) — senão "salto de mão".
10. **Peça desculpa e assuma o erro** quando o diretor achar um bug que você deveria ter achado; depois crie um teste pra ele nunca voltar.
