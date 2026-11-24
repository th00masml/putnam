#!/usr/bin/env bash
# Score the formal-framing check on inconsistent premises (qwen2.5:7b first; the others are optional), then write report.md.
# Needs an Ollama server on 127.0.0.1:11434 (score.py). Re-runnable: finished models are skipped.
set -euo pipefail
cd "$(dirname "$0")"
PY=${PYTHON:-python}
N=$(wc -l < items.jsonl)

run() {
  local model=$1; shift
  local out="scores__${model//:/_}.jsonl"
  if [ -f "$out" ] && [ "$(wc -l < "$out")" -eq "$N" ]; then
    echo "skip $model (done)"; return
  fi
  echo "== $model $*"
  "$PY" ../../battery/score.py --model "$model" --items items.jsonl --out "$out" "$@"
}

run qwen2.5:7b-instruct
# optional, exploratory:
# run gemma3:12b
# run hermes3:8b
# run mistral:7b

"$PY" ../../battery/fit.py scores__*.jsonl --out report.md
