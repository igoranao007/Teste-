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

## Pacotes baixados — 2ª leva (24/11, pra deixar o episódio vivo)
Tudo LOCAL (fora do git). ★ = crédito obrigatório. Rebaixar: `python3 tools/oga.py material/modelos/oga <slug>` ·
`python3 tools/itch.py material/modelos/itch/minisserie <url>` · `python3 tools/polyhaven.py material/modelos/polyhaven <id>`.

### Sons e músicas — OpenGameArt (`material/modelos/oga/<slug>/LICENCA.txt` em cada pasta)
| Pacote — autor | Licença |
|---|---|
| 100 CC0 metal and wood SFX — rubberduck (`oga/100-cc0-metal-and-wood-sfx`) | CC0 |
| 100 CC0 SFX #2 — rubberduck (`oga/100-cc0-sfx-2`) | CC0 |
| 100 CC0 SFX — rubberduck (`oga/100-cc0-sfx`) | CC0 |
| 25 CC0 bang / firework SFX — rubberduck (`oga/25-cc0-bang-firework-sfx`) | CC0 |
| 50 CC0 Sci-Fi SFX — rubberduck (`oga/50-cc0-sci-fi-sfx`) | CC0 |
| 7 Eating Crunches — StarNinjas (`oga/7-eating-crunches`) | CC0 |
| 75 CC0 breaking / falling / hit sfx — rubberduck (`oga/75-cc0-breaking-falling-hit-sfx`) | CC0 |
| ★ 9 explosion sounds — Unnamed (`oga/9-explosion-sounds`) | CC-BY-SA 3.0 |
| ★ 9 sci-fi computer sounds and beeps — qubodup (`oga/9-sci-fi-computer-sounds-and-beeps`) | CC-BY 3.0 |
| Car engine start 01 — looneybits (`oga/car-engine-start-01`) | CC0 |
| Cave In — StarNinjas (`oga/cave-in`) | CC0 |
| Crickets Ambient Noise - loopable — Wolfgang_ (`oga/crickets-ambient-noise-loopable`) | CC0 |
| cutlery sounds — TinyWorlds (`oga/cutlery-sounds`) | CC0 |
| Door Lock Sounds — Cough-E (`oga/door-lock-sounds`) | CC0 |
| Door Open, Door Close Set — qubodup (`oga/door-open-door-close-set`) | CC0 |
| ★ Double Click Mouse Sfx Sound Effect —  (`oga/double-click-mouse-sfx-sound-effect`) | CC-BY 4.0 |
| ★ Facility Alert Siren — FiveBrosStopMosYT (`oga/facility-alert-siren`) | CC-BY 3.0, CC-BY 4.0, OGA-BY 3.0 |
| Factory ambiance — yd (`oga/factory-ambiance`) | CC0 |
| Gunshot Sounds — Tabasco (`oga/gunshot-sounds`) | CC0 |
| Heartbeat sounds — bart (`oga/heartbeat-sounds`) | CC0 |
| Horror Atmosphere — SubspaceAudio (`oga/horror-atmosphere`) | CC0 |
| ★ Imminent Threat — Matthew Pablo (`oga/imminent-threat`) | CC-BY-SA 3.0 |
| Keyboard Soundpack #1 [Typing and Single Keystrokes] — unicaegames (`oga/keyboard-soundpack-1-typing-and-single-keystrokes`) | CC0 |
| Metal Interactions — qubodup (`oga/metal-interactions`) | CC0 |
| mouse click — LFA (`oga/mouse-click`) | CC0 |
| Night of the Streets [Horror/Suspense] — nene (`oga/night-of-the-streets-horrorsuspense`) | CC0 |
| ★ Office Chair Roll Sfx Sound Effect —  (`oga/office-chair-roll-sfx-sound-effect`) | CC-BY 4.0 |
| ★ Perpetual Tension — Zander Noriega (`oga/perpetual-tension`) | CC-BY 3.0 |
| ★ Sci-Fi Drone Loop — jdagenet (`oga/sci-fi-drone-loop`) | CC-BY 3.0 |
| Short alarm — yd (`oga/short-alarm`) | CC0 |
| Sirens and Alarm Noise — aquinn (`oga/sirens-and-alarm-noise`) | CC0 |
| Sirens in Darkness — cynicmusic (`oga/sirens-in-darkness`) | CC0 |
| ★ static noise similar to an untuned tv (also known as white noise) — thebardofblasphemy (`oga/static-noise-similar-untuned-tv-also-known-white-noise`) | GPL 2.0 |
| ★ Super Foley Pack — dklon (`oga/super-foley-pack`) | CC-BY 3.0 |
| ★ Wooden Debris — spookymodem (`oga/wooden-debris`) | CC-BY 3.0 |

### Modelos 3D — Poly Haven (CC0, `material/modelos/polyhaven/`) — 50 modelos, precisam virar PSX (reduzir + textura 128–256)
- **Base de Kessinburgh**: old_military_crate, wooden_military_crate, ammo_box, vintage_radio_transceiver (estação do Dod), metal_office_desk,
  steel_frame_shelves_01/02, worn_metal_rack, portable_generator, metal_tool_chest, metal_jerrycan_green, russian_food_cans_01, can_rusted,
  power_box_01, hanging_industrial_lamp, industrial_wall_lamp, plastic_monobloc_chair_01, metal_stool_01, service_pistol, portable_searchlight,
  Megaphone_01, concrete_road_barrier
- **Alojamento do posto**: old_bed_frame, drawer_cabinet, WoodenChair_01, wall_clock, metal_trash_can, desk_lamp_arm_01, cardboard_box_01,
  rollershutter_door, utility_box_01
- **Casa do Phantom**: wooden_bookshelf_worn, book_encyclopedia_set_01, hanging_picture_frame_01/02/03 (capas Star Comics),
  standing_picture_frame_01/02 (porta-retrato), ArmChair_01, Sofa_01, side_table_01, binder_notebook, Rockingchair_01 (cadeira quase caindo),
  ceiling_fan, boombox, portable_cassette_player
- **Base do Dom**: modern_arm_chair_01, industrial_coffee_table · **Pedrinha do Metalis**: rock_07, rock_09

### Modelos 3D — itch.io (`material/modelos/itch/minisserie/`)
| Pacote | Licença | Uso |
|---|---|---|
| PSX Weapons & Ammo Free Sampler + Aftermath sampler — the-atr0city | CC0 | armas/munição na base |
| Low Poly PSX Weapons Pack — juggypuggy | CC0 | armas na base |
| PSX Style Low Poly Couch — duhgless | CC0 | sofá (casa do Phantom / base do Dom) |
| PSX 90s Home Interior Props (amostra) — gmingassets | uso comercial, crédito apreciado | casa do Phantom, alojamento |
| PSX Books — geouug | página cita CC-BY e domínio público — **conferir** | livros da casa do Phantom |
| PSX Bed — sakepella · PSX Household Items — rubber-ducky-games · PSX Monitor — itsmonss | **sem licença explícita — conferir** | alojamento, base |
| PSX Barrel, Jerry Can, Wooden Box, VHS, TV, Air Conditioner, Vending Machine — iishazlyii | **sem licença explícita — conferir** | posto, base |
| ★ Old Locations — Horror Ambiences — canvas-coven (`itch/minisserie_som/`) | CC BY 4.0 | ambiências |
Pagos (não baixados): bunkers militares (lowbitlab, harning, retroassetslibrary), armários (tillion, pomarf), móveis (vertexvandal, gravyassets,
hutski3d), entulho (aquicor), PSX Mega Pack 1/2 (pizzadoggy), ambiências de terror (cyberleaf, lowbitlab, chuckyassets, gravity-sound…).
Sketchfab: o token salvo no ambiente está **inválido** (401) — trocar em Configurações do ambiente se quiser usar.
