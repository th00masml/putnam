# Preregistration: analysis choices frozen before scoring the explosion-chain run

Frozen 2026-11-24, before any model has scored `runs/2026-10-14__explosion-chain/items.jsonl`.
The pilot (`runs/2026-10-11__pilot-ollama/`) was analysed with these same values, but post hoc;
it is exploratory and its numbers are not confirmatory evidence.

The values live in `battery/fit.py` and must not change for this run. Any later change goes in a
new dated section here with the reason, and the explosion-chain report is then labelled exploratory.

| Choice | Value | Where |
|---|---|---|
| Binarisation of P(yes) | yes iff P(yes) > 0.5 | `YES_CUT` |
| "No stable logic" if fallacy yes-rate exceeds | 0.25 | `MAX_FALLACY_YES` |
| "No stable logic" if share of items with yes/no first-token mass < 0.5 exceeds | 25% | `MAX_LOW_MASS` |
| Tie band for logic ranking | 1 nat | `TIE_NATS` |
| Primary logic comparison | held-out-schema log-likelihood | `held_out_loglik` |
| Secondary comparison | schema-level marginal likelihood (one observation per schema) | `schema_level` |
| Item-level Bayes factors | not reported as evidence | |
| Decoding | temperature 0, first token, top-20 logprobs, both answer orders averaged | `battery/score.py` |

Hypotheses H_a to H_d and their predicted response patterns for the explosion-chain schemata are
the ones in `runs/2026-10-14__explosion-chain/NOTES.md` (written 2026-10-14). The diagnosis is the
one `chain_section` in `battery/fit.py` prints; a model flagged "no stable logic" gets no diagnosis
in the paper.
