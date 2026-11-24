#!/usr/bin/env bash
# PRÉVIA do EPISÓDIO 1 (antes das vozes novas com atuação): junta os planos renderizados (out/NN-*.mp4) com uma trilha PROVISÓRIA por cena:
#  · cenas que continuam iguais ao v4/v5: o som recortado do vídeo v4 entregue (vozes + sons originais);
#  · cenas que mudaram: o som antigo SÓ até onde a fala não mudou (sai "Projeto Mogg", "Toca do Anão", "Dom?! É você?") + sons dos pacotes;
#  · falas novas: aparecem como LEGENDA na própria cena (E.legendas) até a etapa de vozes.
# uso: bash tools/ep1_previa.sh [video_v4_720p.mp4]  →  entrega/ep1/the-green-path-ep1_previa.mp4 (720p)
set -euo pipefail
V4="${1:-_baixados/video_v4_720p.mp4}"; T=$(mktemp -d); O=material/modelos/oga; MX="python3 tools/mix_previa.py"
corta() { ffmpeg -v error -y -ss "$2" -t "$3" -i "$V4" -vn -ac 2 -ar 48000 "$T/$1.wav"; }          # nome, início no v4, duração
SIR="$O/sirens-and-alarm-noise/siren_0.mp3"; ALA="$O/short-alarm/alarm_0.ogg"; EXP="$O/9-explosion-sounds/explosions_1/explosion03.wav"
AMB="$O/horror-atmosphere/Juhani Junkala - Post Apocalyptic Wastelands _Loop Ready_.ogg"; FAB="$O/factory-ambiance/Factory.ogg"; DRO="$O/sirens-in-darkness/012_Sirens_in_Darkness_0.mp3"
TEC="$O/keyboard-soundpack-1-typing-and-single-keystrokes/unicae_games_keyboard_soundpack_1_0/Generated Typing/generated-004_medium.wav"; CLI="$O/mouse-click/mouseclick.wav"
CRU="$O/7-eating-crunches/crunch_-_tito"; BEEP="$O/50-cc0-sci-fi-sfx/sci-fi-sfx/retro_beep_02.ogg"; HB="$O/heartbeat-sounds/heartbeat_fast_reverb.wav"
D="$O/door-open-door-close-set/qubodup-DoorSet/qubodup-DoorSet/ogg"; H="$O/75-cc0-breaking-falling-hit-sfx/sfx_breaking_and_falling"
# som original (v4/v5) das cenas que continuam
corta 41 0 17; corta 42 17 9; corta 57 94 14; corta 46 108 12; corta 47 120 19.5; corta 48 139.5 10; corta 50 157.5 24
corta 63 181.5 14; corta 67 236.5 9; corta 68 245.5 7
corta 52a 195.5 10.6; corta 53a 208.5 6.0; corta 54a 220.5 8.9; corta 58a 252.5 12.4
# posto/metalis/nicolas: mixes próprios (vozes do v4 + sons novos) — refaz se não existirem
[ -f "${A60:-x}" ] || true
$MX "$T/64.wav" 13 "$T/52a.wav@0@0"
$MX "$T/65.wav" 12 "$T/53a.wav@0@0" "$AMB@5.8@-16@loop"
$MX "$T/66.wav" 16 "$T/54a.wav@0@0" "$TEC@9@-8" "$AMB@8.8@-18@loop"
$MX "$T/69.wav" 18 "$T/58a.wav@0@0" "$H/bfh1_wood_breaking_01.ogg@13.25@0" "$H/bfh1_metal_falling_01.ogg@13.35@-4" "$SIR@14.2@-4@loop"
$MX "$T/70.wav" 8 "$SIR@0@-6@loop" "$HB@0@-6"
$MX "$T/71.wav" 24 "$SIR@0@-8@loop" "$D/qubodup-DoorClose04.ogg@17.2@2" "$H/bfh1_metal_hit_02.ogg@19.4@-2" "$CLI@17.75@0" "$ALA@17.85@-3@loop" "$BEEP@19.6@-4" "$AMB@19.6@-10@loop"
$MX "$T/72.wav" 28 "$FAB@0@-14@loop" "$CLI@9.35@-2" "$CLI@10.75@-2" "$CRU/crunch.1.ogg@14.6@-6" "$CRU/crunch.3.ogg@16.2@-6" "$CRU/crunch.4.ogg@17.5@-6" "$ALA@19.3@-2@loop"
$MX "$T/73.wav" 63 "$DRO@0@-10@loop"
$MX "$T/74.wav" 25 "$AMB@0@-12@loop" "$EXP@11.45@3" "$H/bfh1_rock_falling_03.ogg@11.9@-2" "$H/bfh1_wood_breaking_04.ogg@12.2@-3" "$DRO@19.4@-6"
$MX "$T/75.wav" 7 "$BEEP@.4@-6" "$DRO@0@-14"
S=/tmp/claude-0/-home-user/6c5cacc2-dc59-5109-814b-bca4e4f94049/scratchpad
for n in 60 61 62; do cp "$S/a$n.wav" "$T/$n.wav"; done
ORDEM="41-estrada 42-nicolas 60-ep1-posto 61-ep1-metalis 75-ep1-titulo 57-maleta 46-casmiron 47-cabana 48-senha 62-ep1-nicolas 50-elevador 63-ep1-sala 64-ep1-entrega 65-ep1-fita 66-ep1-computador 67-ep1-tela 68-ep1-chiado 69-ep1-dom 70-ep1-malditos 71-ep1-porta 72-ep1-kessinburgh 73-ep1-base-dom 74-ep1-phantom"
: > "$T/lista.txt"
for p in $ORDEM; do n=${p%%-*}; ffmpeg -v error -y -i "out/$p.mp4" -i "$T/$n.wav" -map 0:v -map 1:a -vf "scale=1280:720,fps=30" -c:v libx264 -crf 24 -preset fast -c:a aac -b:a 160k -ar 48000 -ac 2 -shortest "$T/$p.mp4"; echo "file '$T/$p.mp4'" >> "$T/lista.txt"; done
mkdir -p entrega/ep1; ffmpeg -v error -y -f concat -safe 0 -i "$T/lista.txt" -c copy entrega/ep1/the-green-path-ep1_previa.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 entrega/ep1/the-green-path-ep1_previa.mp4; rm -rf "$T"
