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

## 2026-11-24: explosion pragmatic-control run

Added before any model has scored `runs/2026-11-24__explosion-pragmatics/items.jsonl`. No analysis
value above changes. The predicted patterns and their readings are the ones in that run's `NOTES.md`.
A difference between conditions counts only if it crosses the 0.5 cut for the mean P(yes) of the
cell; smaller shifts are reported but not interpreted.

## 2026-11-24: results, reporting change, inconsistent-premises follow-up

Scored: explosion-pragmatics (5 models) and explosion-chain (4 models); results in each run's `NOTES.md`.
No frozen value changed. Models that failed the reliability rule in a run are reported as exploratory for
that run, even where the failure is driven by one conditional schema (denying the antecedent).

Reporting only: `fit.py` now prints a warning under a logic-fit table that rests on fewer than three
schemata. The diagnosis text in `chain_section` is unchanged, even though it mislabels gemma3:12b (see the
explosion-chain `NOTES.md`); the paper reports the full profile, not the label.

Added before scoring: `runs/2026-11-24__inconsistent-premises/` (predictions in its `NOTES.md`), on the
four explosion-chain models.

## 2026-11-24: MCS-inference follow-up

Added before any model has scored `runs/2026-11-24__mcs-inference/items.jsonl`. Hypothesis (formed post
hoc from qwen2.5:7b's profile): inference from inconsistent premises follows universal maximal-consistent-
subset consequence. Candidates, predictions, the confirmatory model and the decision rule (including the
0.40–0.60 inconclusive band for the deciding schema) are in that run's `NOTES.md`; the candidate
relations are computed by `battery/mcs.py` and printed by `fit.py` (`mcs_section`). No earlier frozen
value changes.

## 2026-11-24: MCS-inference result

The preregistered hypothesis (qwen2.5:7b follows universal MCS consequence) is refuted: qwen2.5:7b accepts
A∧C, ¬A ⊢ C (mean 0.94). Its profile matches the pre-specified "discard the contradicted atom" row
exactly. Its formalisation (`split_universal` in `battery/mcs.py`) was written after this result and is
exploratory until tested in a new preregistered run. Details in the run's `NOTES.md`.

## 2026-11-24: formal-framing check on inconsistent premises

Added before any model has scored `runs/2026-11-24__inconsistent-formal/items.jsonl`, in response to a
review of the preprint draft. Primary cell, bands and controls are in that run's `NOTES.md`. No earlier
frozen value changes.

## 2026-11-24: Claude API condition (before any API scoring)

Scorer: `battery/score_api.py` (Message Batches API). The API gives no log-probabilities and current models
take neither a temperature nor disabled thinking, so P(yes) is the share of "yes" among k = 5 samples per
answer order (10 per item), after the model's own adaptive thinking at effort `medium`; replies that do not
start with yes/no, refusals and errors are non-answers and lower `answer_mass`. No refusal fallbacks (they
would mix models). This is a different measure from the local first-token P(yes) and is reported as a
separate condition, never pooled with local models.

Rules applied unchanged: each run's predictions and decision rules in its `NOTES.md`, the 0.5 cut, and the
reliability rule (answer_mass < 0.5 plays the role of low yes/no mass). The Claude model counts as a second
confirmatory model only if it passes the reliability rule in the explosion-pragmatics run (the only run with
fallacy items); otherwise its results are exploratory.
