# PENDRIVE DO PROJETO — THE GREEN PATH — A SILENT WAR (minissérie)

> Documento de passagem: tudo o que foi feito, como foi feito, o que foi baixado, o que deu errado e o plano pra continuar.
> Escrito pra qualquer pessoa ou IA pegar o projeto e seguir. Repositório: `igoranao007/teste-`, branch
> `claude/mp4-animation-threejs-remotion-xyh5wp`. Idioma do projeto: **português (BR)**. Diretor: Igor Anão.

---

## 0. LEIA PRIMEIRO (regras do diretor — valem pra tudo)
1. **Nada é apagado nem sobrescrito.** Toda mudança gera arquivo NOVO com sufixo (`_v2`, `_v3`…). Os antigos ficam.
2. **A história não muda** sem o diretor autorizar. Referência da história: `MINISSERIE_NOTAS.md` (+ `ROTEIRO_v4.md` como base antiga).
3. **Phantom, Metalis, Zangão e Oliveira** estão **preservados** (modelos, texturas, esqueletos, animações) e a utilização deles
   é decisão do diretor (`PERSONAGENS_PRESERVADOS.md`, `DIRETRIZES_PRODUCAO.md`). Não mexer nos arquivos deles sem ordem.
4. Responder sempre em **português**. Mostrar resultado em imagem/folha antes de seguir; o diretor aprova por etapa.
5. Commits terminam com as linhas de atribuição da sessão; push na branch acima (`git push -u origin <branch>`).
6. Arquivos de licença restrita (modelos pagos, pacotes baixados) ficam **fora do git** (ver `.gitignore`) — documentar como regenerar.

---

## 1. O PROJETO
- Antes: um **trailer/filme curto** (v3 e v4, ~3 min, 16 planos, `ROTEIRO_v4.md`). **Última animação em MP4 (v4, 19/11):**
  `entrega/the-green-path-v4-720p.mp4` (720p, 92 MB; a versão em 1080p fica em `out/the-green-path-v4.mp4`, fora do git).
- Agora: **minissérie** "THE GREEN PATH — A SILENT WAR" (logo: `material/producao/minisserie/titulo_the_green_path_a_silent_war.png`).
- Estética: **PS1/PSX low-poly** — render em 1/4 da resolução ampliado sem filtro, vértices que tremem, textura afim, cor 15 bits
  com pontilhado, texturas 64–512 px com filtro "closest", neblina; verde (#39ff6a) predominante, amarelo nos faróis/energia.
- Lore: ilha de **BARLOTH** (mapa `material/producao/minisserie/referencia/mapa_ilha_barloth.png`), capital **Casmiron City**,
  cidade **Kessinburgh**. Grupos: **Toca do Anão** (Igor, Gusta, Adryan, Nicolas), **renegados anti-caos** (Dod, Corsa, Zangão,
  Entrada — base em Kessinburgh), **grupo do Dom** (Dom, Oliveira, Luan; chama o Phantom), **máfia casmirenha**.
  O antigo "Projeto Mogg" agora se chama **ARG-14** (continua sendo uma fita VHS). Nome novo na lore: **Wallen**.

## 2. COMO RODAR
```bash
npm install                                   # three.js, playwright, remotion
python3 -m venv audio/.venv && audio/.venv/bin/pip install numpy scipy pillow
node render.mjs 43 --at=1,4,7                 # preview de um plano → previews/
node tools/foto.mjs <pasta-video> <t> "<query>" saida.jpg   # um quadro de qualquer página (ex.: 91-luan 1 "p=dom&v=tres")
bash tools/filme4.sh                          # som + render dos 16 planos + edição Remotion → out/the-green-path-v4.mp4
```
- Blender 5.x em linha de comando (`blender -b arquivo.blend --python script.py -- args`).
- Chromium/Playwright já instalados no ambiente; `render.mjs` sobe um servidor local e captura quadro a quadro.

## 3. ONDE ESTÁ CADA COISA
| Pasta/arquivo | O que é |
|---|---|
| `videos/NN-nome/index.html` | um plano/cena por pasta; tudo é função do tempo `t` (`S.update = t => …`). 41–56 = filme v4; 90–99 = folhas/testes |
| `lib/ps1.js` | motor PS1 (palco, materiais `P.mat`, tremor, pontilhado, neblina, caixa/cilindro/esfera) |
| `lib/modelo.js` | carrega GLB/FBX e troca materiais por `P.mat`; material com nome `*brilho*` = luz própria; `*aura*` = brilho aditivo |
| `lib/elenco4.js` | **elenco com esqueleto**: `E4.ator('nome')` → `{obj, pose(clip,t), osso(n), …}`; tabela `ELENCO` (arquivo, altura, passada) |
| `lib/tgp.js` | Igor, Dod, Dom (`acessoriosDom`: capa, chapéu, véu, bastão, círculo), maleta, fita VHS, mesa, celular |
| `lib/filme.js`, `lib/v4.js` | carro, estrada, placa, casa/cabana, corredor, computador; utilidades dos planos v4 |
| `lib/terminal.js` | telas verdes, digitação, perda de sinal |
| `tools/blender/` | todos os scripts de modelagem/rig/animação/render (ver §5 e §6) |
| `tools/*.py` | pintura de texturas, vozes (`clonar_voz.py`, `falas_v5.py`), som (`som4.py`), folhas |
| `material/producao/personagens/<nome>/` | cada personagem: `LEIA.md` (como refazer), texturas, folhas, exports |
| `material/producao/modelos-pagos/simple_character_psx/` | base paga **Simple PSX Character (JashiPSX)** + todos os `*_anim*.blend/.glb` (fora do git) |
| `material/producao/minisserie/` | logo, referências, `ASSETS.md` (licenças de tudo que foi baixado) |
| `material/modelos/itch/`, `material/modelos/oga/`, `material/modelos/office/` | pacotes baixados / enviados (fora do git) |
| `audio/` | trilhas, vozes (`audio/voz/v4`, `v5`), `synth.py` |
| `MINISSERIE_NOTAS.md` | **TODA a história nova e as cenas** (episódio 1) — a fonte da verdade |

## 4. PERSONAGENS (estado atual)
Base comum dos humanos: **Simple PSX Character (JashiPSX)** — esqueleto `spine…spine.005`, `shoulder/upper_arm/forearm/hand.L/R`,
dedos `f_index.01…`, `thigh/shin/foot/toe.L/R`. Licença: usar e modificar no projeto, **não redistribuir** (fora do git).

| Personagem | Arquivo no jogo (`lib/elenco4.js`) | Como foi feito | Animações |
|---|---|---|---|
| **Adryan** (17, Agente TDA, camisa do Vasco nº 99) | `vegetti_vasco_final_anim_v2.glb` | `pintar_jashi_vasco.py ROUPA=vasco` + `montar_jashi.py` | 59 (v2) |
| **Gusta** (terno preto, gravata verde) | `gusta_anim_v2.glb` | `ROUPA=terno` | 59 (v2) |
| **Nicolas** (14, camisa 10 do Flamengo) | `nicolas_anim_v2.glb` | `realinhar_rosto.py` + montar | 59 (v2) |
| **Frentista** (camisa azul de posto) | `frentista_anim_v2.glb` | `ROUPA=frentista` | 59 (v2) |
| **Dom** (líder; rosto = FOTO do ator; capa branca de chamas, chapéu cônico com 火) | `dom_anim_v2.glb` + `T.acessoriosDom(A)` | `ROUPA=dom`, `rosto_foto.py`, `dom_lider.py` (medalhão-reator, linhas, braçadeiras, emblema) | 59 (v2) |
| **Luan** (gordo, 15, camisa do Atlético-MG, máscara de gás, óculos) | `luan_anim_v2.glb` | `ROUPA=luan` (foto da camisa projetada), `luan_jashi.py` | 59 (v2) |
| **Igor Anão** (cabeça de caracal, moletom azul) | `T.igor()` (lib/tgp.js) | corpo próprio + cabeça | antigas (precisa mapear ossos pras novas) |
| **Entrada** (militar) | `exports/entrada_militar.glb` | `vestir_personagem.py PERSONAGEM=entrada` (cabeça 3D + uniforme v2, luvas pretas) | antigas |
| **Corsa** (cabeça de pardal, militar) | `exports/corsa_militar.glb` | `vestir_corsa_v2.py` | antigas |
| **Dod** (gato preto com cérebro exposto, uniforme verde) | `T.dod()` / `videos/95-dod` | `vestir_dod_v3.py` | poses próprias |
| **Phantom** (versões vermelha e amarela; 2 pistolas Malorian) | `phantom` / `phantom_amarelo` | `phantom.py` (modelo do diretor convertido pra PSX) | 10 antigas — **preservado** |
| **Metalis** (mendigo de Casmiron) | `metalis_final.glb` | `montar_metalis.py`, `mendigar_metalis.py` | próprias — **preservado** |
| **Zangão** (original e militar; águia → escudo do Universitário pendente) | `exports/zangao_*.glb` | `zangao.py` | — **preservado** |
| **Oliveira** (cabeça de lagarto, armadura do Dom, halo girando) | `oliveira_anim.glb` | `oliveira_jashi.py`, `girar_ossos.py` | 10 + giros — **preservado** |

Folhas de todos os ângulos: `material/producao/personagens/*/folha_*.jpg`. Folha no motor: `videos/91-luan/?p=<nome>&v=frente|tres|lado|costas|rosto&clip=<animação>`; Dom: `videos/98-dom/?v=...&bastao=0|1&comando=1`.

## 5. PIPELINES (passo a passo, comandos reais)
### 5.1 Personagem humano novo na base JashiPSX (o que deu a qualidade aprovada)
1. `tris.json`: `blender -b base.blend --python tools/blender/dump_tris.py -- <obj> out.json` (todos os triângulos com UV/posição/normal).
2. Textura 1024 pintada **sobre as dobras originais**: `ROUPA=<nome> PELE_RGB=r,g,b CAB=r,g,b RES=1024 python3 tools/pintar_jashi_vasco.py tris.json character_256.png foto.jpg saida.png`
   (ramos ROUPA: vasco, terno, dom, frentista, luan, oliveira; `dobra()` mantém a sombra pintada; foto de camisa pode ser projetada no tronco).
3. `blender -b --disable-autoexec simple-character-psx.blend --python tools/blender/montar_jashi.py -- textura.png saida.blend`
   (env: `CALCA=1`, `OCULOS=1`, `CABELO_CURTO=0/1`, `AFRO=<tex>` + `AFRO_*`, `ROSTO_PLANO`).
4. Extras por personagem (rosto em foto `rosto_foto.py`, acessórios `luan_jashi.py`, `dom_lider.py`…).
5. `blender -b p.blend --python tools/blender/animar_jashi.py -- p_anim.blend` (10 animações base; `BRACO_ABRE=graus` pra corpo gordo).
6. `blender -b p_anim.blend --python tools/blender/exportar_glb.py -- p_anim.glb` → entrada em `lib/elenco4.js`.
7. Inspeção em resolução cheia: `tools/blender/render_jashi.py -- pasta [acao] [quadro]` (`BELO=1` = Cycles bonito; `VISTAS=frente,tres`).

### 5.2 Animações novas (o que foi feito por último)
```bash
UAL=".../Universal Animation Library[Standard]/Unreal-Godot/UAL1_Standard.glb"
CLIPES="Idle_Loop,Walk_Loop,..." PREFIXO=u_ blender -b X_anim.blend --python tools/blender/animar_bvh.py -- "$UAL" X_anim_v2.blend
CLIPES="walk_cautious,..."       PREFIXO=m_ blender -b X_anim_v2.blend --python tools/blender/animar_bvh.py -- <Motifect>/BVH X_anim_v2.blend
blender -b X_anim_v2.blend --python tools/blender/aterrar.py -- X_anim_v2.blend          # pés no chão
blender -b X_anim_v2.blend --python tools/blender/qa_animacoes.py -- qa.json             # verificação automática
blender -b X_anim_v2.blend --python tools/blender/folha_animacoes.py -- quadros/         # folha visual
python3 tools/montar_folha_animacoes.py quadros/ qa.json folha.jpg "TÍTULO"
blender -b X_anim_v2.blend --python tools/blender/exportar_glb.py -- X_anim_v2.glb
```
- `animar_bvh.py`: retarget em espaço de mundo; lê **BVH** (esqueleto Hips/Spine1/LeftArm…) e **GLB da Quaternius** (pelvis/spine_01/upperarm_l…);
  escala pela perna; quadril em altura absoluta; `SEM_DESLOC=1` trava no lugar; mantém as ações que já existem.
- `aterrar.py`: desce/sobe o quadril de cada ação até o pé encostar (cuidado: o objeto do esqueleto tem escala — usar a matriz sem normalizar).
- `qa_animacoes.py`: pé afundando/flutuando (em relação à pose de descanso), estalo > 60°/quadro, NaN.
- Resultado: Adryan, Gusta, Nicolas, Frentista, Dom, Luan com 59 animações (10 antigas + 27 `u_` + 22 `m_`), 57/59 OK
  (Punch_Jab e Sprint_Loop marcados só por serem rápidos; conferidos no visual). Lista em `material/producao/minisserie/ASSETS.md`.

### 5.3 Converter um 3D "normal" pra PSX (ex.: `tools/blender/phantom.py`)
Soldar vértices (`remove_doubles 0.0004`) → reduzir (DECIMATE ~7 mil tri) → UV novo (smart_project) → **bake Cycles** (difuso + AO) em 512 →
cor 15 bits → esqueleto do elenco nas articulações medidas → pesos automáticos → limpar pesos errados → pose A→T aplicada → tirar faces que
esticaram > 2,2× → acessórios presos no osso.

### 5.4 Outras técnicas que funcionaram
- **Bake de malha alta → baixa** pra textura com detalhe de escamas/rugas (Cycles DIFFUSE + AO, `use_selected_to_active`).
- **Placas de armadura curvas** medidas por raios do eixo do osso até a pele (`oliveira_jashi.py: placa()`), com chanfro, rebites, sulcos acesos.
- **Linhas de energia** em relevo coladas na superfície por raio, com pesos copiados da malha (`linhas_energia.py`).
- **Aura aditiva** (cópia inflada das partes acesas, material `*aura*`) = brilho forte no motor.
- **Ossos extras girando** em todas as ações, loop sem emenda (`girar_ossos.py`: `GIROS="halo:0.25"`).
- **Pano no motor** (capa/véu do Dom): malha em grade recalculada por quadro (`pano()` em lib/tgp.js) + debrum aceso (`fita()`).
- **IK de 2 ossos no motor** pra mão segurar objeto apoiado no chão (bastão do Dom, `segurar()` em `acessoriosDom`).
- **Folhas de inspeção**: sempre renderizar frente/3/4/lado/costas/rosto + closes, em resolução cheia, antes de mostrar.

## 6. ANIMAÇÕES DISPONÍVEIS (nomes no GLB v2)
- Antigas (10): `idle walk run talk wave sit cower attack hit death`.
- `u_` (Quaternius UAL, CC0): Idle_Loop, Idle_Talking_Loop, Walk_Loop, Walk_Formal_Loop, Jog_Fwd_Loop, Sprint_Loop, Sitting_Enter/Exit/
  Idle_Loop/Talking_Loop, Driving_Loop, Interact, PickUp_Table, Push_Loop, Hit_Chest, Hit_Head, Death01, Crouch_Idle_Loop, Crouch_Fwd_Loop,
  Pistol_Idle_Loop, Pistol_Aim_Neutral, Pistol_Shoot, Punch_Jab, Jump_Start/Loop/Land, Roll. (Na biblioteca ainda há: Dance_Loop,
  Fixing_Kneeling, Pistol_Aim_Up/Down, Pistol_Reload, Punch_Cross, Spell_Simple_*, Sword_*, Swim_*, Idle_Torch_Loop.)
- `m_` (Motifect): idle_alert, idle_looking_around, idle_relaxed_weight_shift, idle_neutral, walk_cautious, walk_tired, walk_confident,
  turn_left_90, turn_right_90, turn_180, stumble_recover, stop_from_run, start_sprint, run_panic, back_to_wall, crouch_rise_up,
  sidestep_dodge, hit_react_face, stagger_backward, knockdown_fall, get_up, block_high. (Pacotes têm 85 clipes no total: luta + locomoção.)
- No motor: `A.pose('u_Walk_Loop', t)`; `passada` em `ELENCO` = metros por ciclo de `walk` (pra não deslizar o pé).

## 7. O QUE FOI BAIXADO / RECEBIDO (licenças em `material/producao/minisserie/ASSETS.md`)
- Animações: Motifect Combat (40) e Locomotion (45) — uso no projeto, sem redistribuir; Quaternius Universal Animation Library — CC0.
- Modelos itch.io (`tools/itch.py <pasta> <url>`): armas corpo a corpo (CC0), pistola Beretta, latas de comida e refrigerante (CC0),
  **bunker soviético com 63 peças (CC0)**, estantes/livros, TV de tubo (CC0), PC antigo (CC0), portas, pedras, poltrona.
- OpenGameArt: 100 CC0 SFX, 50 CC0 sci-fi SFX (alarmes/bips), tiros (CC0), 25 estouros (CC0), 9 explosões (**CC BY-SA 3.0 — crédito**),
  ambiências de terror (canvas-coven, **CC BY 4.0 — crédito**), música de terror PSX.
- Do diretor: pacote **OFFICE_1** (computador com mouse, mesas, cadeiras, TV, estantes, sofás…) em `material/modelos/office/`;
  referências: mapa de Barloth, capas Star Comics (Catman, Omnis, Spaceman), logo Star Comics, porta-retrato, pose do Dom, escudo do
  Universitário, 3 vídeos pra tela do computador do Corsa (fora do git).
- Sites que funcionam deste ambiente: itch.io, opengameart.org, freesound.org. Bloqueados: kenney.nl, pixabay.com.
- Itens marcados "sem licença explícita" no ASSETS.md: **conferir antes de publicar**.

## 8. ÁUDIO E VOZES
- Vozes clonadas **localmente** com Chatterbox multilíngue (`tools/clonar_voz.py`, `tools/falas_v5.py`): Igor (referência `audio/voz/igor-ref.wav`),
  Adryan (falas dele do v4), Dom (voz pública do modelo, engrossada com `tools/vilao.sh`).
- Pendentes: **Gusta** (sem voz gravada), **Oliveira** (voz livre, grave/"grossa"), **Luan** (voz livre de adolescente).
- **Crítica do público**: as falas pareciam lidas. Agora precisa de **atuação**: emoção, ritmo, pausas, gritos (susto do Igor, "Fecha essa
  porta imediatamente!", "Mas é o Nicolas, ele tá só!", Gusta segurando o Adryan). Chatterbox: subir `exaggeration` (0,7–0,9), várias
  tomadas por fala, escolher a melhor; pós: compressão, EQ, reverb da sala.
- **Boca**: quem fala mexe a boca/mandíbula e fecha quando para (Oliveira explicitamente).
- Som do filme: `tools/som4.py` (cues + vozes) → `audio/synth.py`.

## 9. ERROS COMETIDOS E LIÇÕES (pra não repetir)
1. **Texturas procedurais de 64 px** pareciam feias e de baixa qualidade → usar a base JashiPSX e pintar em 1024 sobre as dobras originais.
2. **Folhas em 1/4 da resolução** escondiam defeitos → inspecionar em resolução cheia (`render_jashi.py`) e com closes.
3. **Pescoço/cabeça desencaixados** (Luan v1, Oliveira v1) → aplicar a MESMA escala por altura no pescoço e na cabeça; encaixar a base do pescoço no centro da gola.
4. **Coisas tortas por posição estimada** (bigode do Zangão, armas no coldre) → **medir** no modelo (vistas ortográficas com grade, centros por cor/material) antes de posicionar.
5. **Diminuir o que não era pra diminuir** (bigode) → ler o pedido com atenção; o diretor disse "o problema NÃO é o tamanho".
6. **Mão que some/fica estranha** (Entrada com luva da cor da manga; Dom com punho modelado) → usar a mão do PRÓPRIO modelo, posicionada; contraste de cor.
7. **Bastão "flutuando"** preso só na mão → objeto apoiado no chão + IK do braço até ele.
8. **Redução estilhaçando a malha** (modelo com vértices soltos nas costuras de UV) → soldar antes de decimar.
9. **Retarget**: o quadril do BVH fica na origem no descanso → escalar pela perna; ações com o mesmo nome do BVH eram apagadas → renomear a origem.
10. **Aterrar**: o objeto do esqueleto tem escala → converter o deslocamento com a matriz SEM normalizar.
11. **Seleção no Blender** (smart_project empacotando ilhas de todos os objetos) → desselecionar tudo antes.
12. **Nunca apagar arquivo rastreado sem querer** (`.blend1`) e nunca `git stash` acidental — conferir `git status`.
13. Pedidos do diretor chegam em várias mensagens: **anotar tudo** em `MINISSERIE_NOTAS.md` antes de produzir; confirmar dúvidas.

## 10. PLANO PRA CONTINUAR (ordem combinada)
**Etapa A — terminar as animações**
1. Mapear os ossos de **Igor, Entrada, Corsa e Dod** (esqueletos diferentes) e acrescentar o mapa no `animar_bvh.py` (`MAP_*`), aplicar o mesmo
   conjunto `u_`/`m_`, `aterrar.py`, `qa_animacoes.py`, folha visual, exportar `_v2` e ligar no motor sem apagar os antigos.
2. Clipes extras que as cenas pedem: Igor caindo com a cadeira (knockdown + get_up), apertar botão (Interact), Corsa clicando no mouse
   (Sitting_Idle + mão), Zangão/Entrada comendo sentados (Sitting_Idle + braço), Dod digitando/escrevendo, todos virando pro telão (turn_*).

**Etapa B — cenas do episódio 1 (detalhe em `MINISSERIE_NOTAS.md` §3–4b)**
1. **Posto**: alojamento reformulado (interior, porta, itens, janela de verdade — pacotes bunker/office/portas); frentista entra; pedra no carro
   (pedra do pacote de rochas); Adryan sai, verifica, volta; diálogo de sempre; Adryan entra, liga o carro e vai.
2. **Nicolas no carro**: vira com o braço pra trás das costas (sugere arma — pistola do pacote).
3. **Sala do Igor em POV do Adryan** (Adryan entrega a maleta; o Nicolas NUNCA esteve na sala). Computador do Igor novo (OFFICE, com mouse).
   Fala trocada: "Preciso apagar imediatamente os experimentos que o Wallen fez." Menu da fita: **ARG-14**.
4. **Dom na tela**: modelo novo SEM bastão, pouco visível (contraluz/ruído), parado.
5. **Cenas novas**: Igor cai com a cadeira → Dom de sirene → "Malditos, eles me acharam!" → Igor levanta → POV Adryan: "Fecha essa porta
   imediatamente!" (porta-bunker) → "Mas é o Nicolas, ele tá só!" → procedimentos de sobrevivência → Gusta segura o Adryan pelos ombros
   ("Ele vai ficar bem. Mas se ficar na rebeldia, iremos morrer.") → fecham e trancam → Igor aperta o botão vermelho, alerta, sala secreta verde.
6. **Kessinburgh — Casmiron**: dezoom da roupa verde do Dod; base bunker/militar; quarteto **sem falas**: Corsa vendo vídeos no PC (pula 2, deixa
   o 3º até o fim), Zangão e Entrada comendo enlatado sentados, Dod na estação meteorológica escrevendo; telão "ALERTA — MISSÃO DE RESGATE —
   CASMIRON (CAPITAL)" (resgate do Igor); todos olham; preto.
7. **Base do Dom — Local: ????**: Dom sentado, só os braços (mãos entrelaçadas), mexe o braço ao falar; telão com o mapa de Barloth em
   Casmiron; Oliveira e Luan (diálogo completo nas notas); "Já chamei certas pessoas para esta operação." "Quem?"
8. **4 horas antes**: casa do Phantom cheia de quadrinhos (capas Star Comics na parede), ele quase caindo da cadeira com o porta-retrato,
   parede explode, sombra do Dom: "Phantom, podemos conversar?" → **fim do episódio 1**.

**Etapa C — áudio e acabamento**: vozes com atuação (incl. Oliveira grave e Luan adolescente), boca sincronizada, sons dos pacotes,
música, mixagem, créditos (incluir os créditos CC BY dos sons e o aviso de produção independente de `DIRETRIZES_PRODUCAO.md`), render final.

**Pendências abertas com o diretor**: título novo da minissérie (se mudar de novo), falas antigas que mudam por causa do grupo Dom,
decisão sobre Phantom/Metalis/Zangão/Oliveira, licenças dos pacotes "sem licença explícita".
