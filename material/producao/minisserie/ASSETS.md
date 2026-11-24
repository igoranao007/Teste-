# Pacotes baixados pra minissérie (registro de licenças)

Arquivos ficam LOCAIS (fora do git): `material/modelos/itch/minisserie/` (itch.io, baixados com `tools/itch.py`) e `material/modelos/oga/`
(OpenGameArt). Rebaixar: os links abaixo. Créditos obrigatórios marcados com ★ (pôr nos créditos do episódio).

## Animações
| Pacote | Licença | Uso |
|---|---|---|
| Motifect Combat (40) e Locomotion (45) — motifect.io | uso em projetos, sem redistribuir os arquivos crus | luta, reações, andar, virar, agachar… (`m_*`) |
| Universal Animation Library — Quaternius | CC0 | idle, sentar, dirigir, pistola, empurrar, interagir… (`u_*`) |

## Modelos (itch.io)
| Pacote | Licença | Uso |
|---|---|---|
| PSX Weapons — ciprient | CC0 | taco, cano, faca, pá (entulho/base) |
| PSX Style Beretta 92 — sotn | (página sem licença explícita — conferir antes de publicar) | pistola do Nicolas |
| PSX Style Food Cans — sotn | (sem licença explícita — conferir) | enlatados do Zangão/Entrada |
| Drink Cans PSX — codyanka | CC0 | latas de refrigerante |
| Low Poly PSX Bunker Pack (63 assets soviéticos) — juggypuggy | CC0 | base de Kessinburgh, porta-bunker, rádio, prateleiras, cilindros |
| PSX Bookshelves & Food Shelves — munchkin-jonesy | uso comercial permitido (ver LICENSE.txt) | casa do Phantom, base |
| PS1-Style CRT TV, Leather Armchair — pepperonijabroni | CC0 (CRT) / sem licença explícita (poltrona) | telas, base do Dom |
| PS1/PSX retro PC — shayno | CC0 | computadores |
| PSX Doors Pack — iishazlyii | (sem licença explícita — conferir) | portas (alojamento) |
| Low Poly Rocks — itchga1 | (sem licença explícita — conferir) | pedrinha do Metalis |
| OFFICE_1 (enviado pelo diretor) | (licença não veio no zip) | computador do Igor com mouse, mesas, cadeiras, TV… |

## Som e música
| Pacote | Licença | Uso |
|---|---|---|
| 100 CC0 SFX — OpenGameArt | CC0 | efeitos gerais |
| 50 CC0 Sci-Fi SFX — OpenGameArt | CC0 | alarme, bips, telas, porta da sala secreta |
| Gunshot Sounds — OpenGameArt | CC0 | tiros |
| 25 CC0 Bang/Firework SFX — OpenGameArt | CC0 | estouros, explosão da parede |
| ★ 9 Explosion Sounds — OpenGameArt | CC BY-SA 3.0 (crédito) | explosão da parede do Phantom |
| ★ Old Locations — Horror Ambiences — canvas-coven | CC BY 4.0 (crédito) | ambiências (bunker, porão, fábrica) |
| PSX Horror Music Pack 1 — sxtempu | (sem licença explícita — conferir) | trilha |

## Animações aplicadas (24/11) — elenco v2
`material/producao/modelos-pagos/simple_character_psx/<personagem>_anim_v2.blend/.glb` (fora do git; os `_anim.glb` antigos ficam no disco)
para **Adryan, Gusta, Nicolas, Frentista, Dom, Luan**: as 10 antigas + 49 novas.
- UAL (u_): Idle_Loop, Idle_Talking_Loop, Walk_Loop, Walk_Formal_Loop, Jog_Fwd_Loop, Sprint_Loop, Sitting_Enter/Exit/Idle_Loop/Talking_Loop,
  Driving_Loop, Interact, PickUp_Table, Push_Loop, Hit_Chest, Hit_Head, Death01, Crouch_Idle_Loop, Crouch_Fwd_Loop, Pistol_Idle_Loop,
  Pistol_Aim_Neutral, Pistol_Shoot, Punch_Jab, Jump_Start/Loop/Land, Roll.
- Motifect (m_): idle_alert, idle_looking_around, idle_relaxed_weight_shift, idle_neutral, walk_cautious, walk_tired, walk_confident,
  turn_left_90, turn_right_90, turn_180, stumble_recover, stop_from_run, start_sprint, run_panic, back_to_wall, crouch_rise_up,
  sidestep_dodge, hit_react_face, stagger_backward, knockdown_fall, get_up, block_high.
- Pipeline: `animar_bvh.py` (UAL → locomoção → luta) → `aterrar.py` (pés no chão) → `qa_animacoes.py` → `exportar_glb.py`.
- QA: 57/59 OK em todos; u_Punch_Jab e u_Sprint_Loop marcados só por serem golpes/passos rápidos (conferido no visual: sem defeito).

## Animações aplicadas (24/11, 2ª rodada) — o RESTO do elenco
Mesmas 49 animações (27 `u_` + 22 `m_`) com `bash tools/animar_elenco_v2.sh <origem> <saida>` (retarget → aterrar → QA → GLB; nunca sobrescreve a origem):
| Personagem | Arquivo novo (fora do git) | No motor | QA |
|---|---|---|---|
| Igor (corpo; cabeça de caracal do motor) | `personagens/igor/igor_corpo_anim_v2.glb` | `T.igor({ anim: true })` → `I.corpo.clip(nome, t)` + `I.assentar()` | 47/49 |
| Dod (farda V4; cabeça do motor) | `personagens/dod/modelo/dod_farda_v4_anim_v2.glb` | `T.dod({ anim: true })` → `D.corpo.clip(nome, t)` + `D.assentar()` | 47/49 |
| Entrada | `personagens/entrada/entrada_militar_anim_v2.glb` | `E4.ator('entrada')` | 47/49 |
| Corsa | `personagens/corsa/corsa_militar_anim_v2.glb` | `E4.ator('corsa')` | 47/49 |
| Zangão original / militar | `personagens/zangao/zangao_{original,militar}_anim_v2.glb` | `E4.ator('zangao' / 'zangao_militar')` | 47/49 |
| Phantom clássico / amarelo | `personagens/phantom/phantom_{classica,amarela}_anim_v2.glb` (10 antigas + 49) | `E4.ator('phantom' / 'phantom_amarelo')` | 57/59 |
| Metalis (esqueleto Hips/LeftArm…: nomes traduzidos no script) | `personagens/metalis/metalis_final_anim_v2.glb` (10 + 49) | `E4.ator('metalis')` | 57/59 |
| Oliveira (halo/engrenagens girando de novo em todas) | `modelos-pagos/simple_character_psx/oliveira_anim_v2.glb` (10 + 49) | `E4.ator('oliveira')` | 57/59 |
Os 2 avisos em todos são `u_Punch_Jab` e `u_Sprint_Loop` (golpe/passada rápidos — sem defeito no visual). O QA agora ignora `halo`/`engr*` (giram de propósito).
Folha no motor do elenco inteiro: `material/producao/minisserie/folha_elenco_v2.jpg` (`PAGINA=88-folha-v2 node tools/folha_elenco.mjs …` + `tools/montar_folha_elenco.py`).
Bibliotecas: `material/modelos/ual/` (Quaternius, CC0) e `material/modelos/motifect/` (sem redistribuir) — fora do git.
