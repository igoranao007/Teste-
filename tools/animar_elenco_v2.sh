#!/usr/bin/env bash
# Aplica as 49 animações novas (27 u_ da Quaternius UAL + 22 m_ da Motifect) num personagem, igual ao elenco v2
# (Adryan, Gusta, Nicolas, Frentista, Dom, Luan). NUNCA sobrescreve a origem: gera <saida>_anim_v2.blend/.glb + QA.
# uso: bash tools/animar_elenco_v2.sh <origem.blend|.glb> <prefixo_saida>     (ex.: ... zangao_militar.blend material/.../zangao_militar)
#      GIROS/PULSO no ambiente = repassa pro girar_ossos.py (Oliveira: halo e engrenagens girando em todas as ações)
set -euo pipefail
ORIG=$1; OUT=$2; B="blender -b --disable-autoexec"; TB=tools/blender
UAL="${UAL:-material/modelos/ual/Universal Animation Library[Standard]/Unreal-Godot/UAL1_Standard.glb}"
BVH="${BVH:-material/modelos/motifect/BVH}"
U="Crouch_Fwd_Loop,Crouch_Idle_Loop,Death01,Driving_Loop,Hit_Chest,Hit_Head,Idle_Loop,Idle_Talking_Loop,Interact,Jog_Fwd_Loop,Jump_Land,Jump_Loop,Jump_Start,PickUp_Table,Pistol_Aim_Neutral,Pistol_Idle_Loop,Pistol_Shoot,Punch_Jab,Push_Loop,Roll,Sitting_Enter,Sitting_Exit,Sitting_Idle_Loop,Sitting_Talking_Loop,Sprint_Loop,Walk_Formal_Loop,Walk_Loop"
M="back_to_wall,block_high,crouch_rise_up,get_up,hit_react_face,idle_alert,idle_looking_around,idle_neutral,idle_relaxed_weight_shift,knockdown_fall,run_panic,sidestep_dodge,stagger_backward,start_sprint,stop_from_run,stumble_recover,turn_180,turn_left_90,turn_right_90,walk_cautious,walk_confident,walk_tired"
V="${OUT}_anim_v2.blend"; LOG="${OUT}_anim_v2.log"; : > "$LOG"
run(){ "$@" >> "$LOG" 2>&1 || { echo "ERRO em: $*  (ver $LOG)"; tail -20 "$LOG"; exit 1; }; }
if [[ "$ORIG" == *.glb ]]; then                       # modelo que só existe em GLB (Igor, Dod): vira .blend primeiro
  run $B --python-expr "import bpy,sys; bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=sys.argv[-2]); bpy.ops.wm.save_as_mainfile(filepath=sys.argv[-1])" -- "$ORIG" "$V"
  SRC="$V"
else SRC="$ORIG"; fi
CLIPES="$U" PREFIXO=u_ run $B "$SRC" --python $TB/animar_bvh.py -- "$UAL" "$V"
CLIPES="$M" PREFIXO=m_ run $B "$V" --python $TB/animar_bvh.py -- "$BVH" "$V"
run $B "$V" --python $TB/aterrar.py -- "$V"
[ -n "${GIROS:-}" ] && run $B "$V" --python $TB/girar_ossos.py -- "$V"
run $B "$V" --python $TB/qa_animacoes.py -- "${OUT}_anim_v2_qa.json"
run $B "$V" --python $TB/exportar_glb.py -- "${OUT}_anim_v2.glb"
rm -f "${V}1"
echo "OK $(basename "$OUT"): $(grep -c '^QA .* OK$' "$LOG") ações OK de $(grep '^QA ' "$LOG" | grep -vc '^QA FIM' | tr -d ' ') — $(grep '^QA ' "$LOG" | grep -v ' OK$' | grep -v '^QA FIM' | sed 's/^QA //' | tr '\n' '|')"
