# putnam

Does an LLM's yes/no judgement of argument validity match any standard logic (CL, IL, K3, LP, FDE, QL)?
Proposals: `proposal.md`, `proposal-logic-revision.md`. Analysis choices: `PREREGISTRATION.md`.

## Setup

Python 3.10+ and an [Ollama](https://ollama.com) server with logprobs support on 127.0.0.1:11434.

```bash
pip install -r requirements.txt
```

## Pipeline (`battery/`)

1. `generate.py` writes items (schema × content × framing) with gold verdicts from `logics.py`.
   `python generate.py --per-cell 10 --seed 14 --out items.jsonl`; `--schemata ...` picks a subset.
2. `score.py` gets P(yes) from first-token logprobs, both answer orders.
   `python score.py --model qwen2.5:7b-instruct --items items.jsonl --out scores__qwen2.5_7b-instruct.jsonl`
   Also writes `scores__*.meta.json` with the model digest, decoding options and item-file hash.
3. `fit.py` ranks logics and writes a Markdown report.
   `python fit.py scores__*.jsonl --out report.md`

`python test_table.py` checks the gold verdicts against hand-computed truth tables.

## Runs (`runs/`)

- `2026-10-11__pilot-ollama/`: seven local models, full battery (exploratory).
- `2026-10-11__explosion-symbolic/`: symbolic-only explosion/DS check (scores only).
- `2026-10-14__explosion-chain/`: prepared, not yet scored. `bash run.sh` (see `NOTES.md`).

Pilot score files predate `score.py` writing metadata, so their model digests are not recorded.
