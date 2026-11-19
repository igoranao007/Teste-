#!/usr/bin/env bash
# roda o controle de qualidade em TODOS os planos (4 em paralelo) e junta o resultado em material/qa/RESUMO.txt
# uso: bash tools/qa_todos.sh            (antes de renderizar qualquer versão nova; ver material/qa/CHECKLIST.md)
set -uo pipefail; cd "$(dirname "$0")/.."
P="${PLANOS:-41-estrada 42-nicolas 43-posto 44-mendigo 45-titulo 57-maleta 46-casmiron 47-cabana 48-senha 49-olhos 50-elevador 51-sala-igor 52-arquivos 53-projeto-mogg 54-computador 55-tela-mogg 58-dom}"
python3 tools/sintaxe.py || exit 1
T=$(mktemp -d); i=0
for v in $P; do (timeout 1800 node tools/qa.mjs "$v" "${PASSO:-2}" > "$T/$v.txt" 2>&1) & i=$((i+1)); if [ $((i % 4)) -eq 0 ]; then wait; fi; done; wait
cat "$T"/*.txt | tee material/qa/RESUMO.txt; rm -r "${T:?}"
grep -q "problema" material/qa/RESUMO.txt && { echo "⚠ há problemas: corrigir antes de renderizar"; exit 1; } || echo "✓ todos os planos aprovados"
