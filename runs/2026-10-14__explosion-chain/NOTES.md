# Explosion-chain follow-up (prepared 2026-10-14, not yet scored)

## Why

All seven pilot models (`../2026-10-11__pilot-ollama/report.md`) accept disjunctive syllogism (DS,
mean P(yes) 0.61–1.00) and reject explosion (0.00–0.28), in every content type including symbolic
notation (`../2026-10-11__explosion-symbolic/`). No candidate logic gives that pair. C. I. Lewis's
derivation gets explosion from two steps plus cut:

1. A ⊢ A ∨ B (∨-introduction)
2. A ∨ B, ¬A ⊢ B (DS)
3. cut: A, ¬A ⊢ B

This run asks which step the models refuse.

## Schemata (gold verdicts computed by `battery/logics.py`, checked in `battery/test_table.py`)

| Schema | Form | CL | IL | K3 | LP | FDE | QL | Role |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|---|
| disjunction_introduction | A ⊢ A∨B | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | step 1 |
| identity_inconsistent | A, ¬A ⊢ A | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | does *anything* follow from inconsistent premises? |
| explosion_lemma | A, ¬A, A∨B ⊢ B | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | step 2 with the inconsistent pair present |
| double_ds | A∨B, ¬A, ¬B∨C ⊢ C | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | two chained steps, no contradiction |
| explosion | A, ¬A ⊢ B | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | anchor (re-scored in the same run) |
| disjunctive_syllogism | A∨B, ¬A ⊢ B | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | anchor |

## Hypotheses and predicted pattern (binarised at 0.5), written before scoring

| Hypothesis | ∨-intro | A,¬A ⊢ A | A,¬A,A∨B ⊢ B | double DS | DS | explosion |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| H_a relevance filter (conclusion must not introduce a new atom) | no | yes | yes | yes | yes | no |
| H_b contradiction aversion (nothing follows from an inconsistent set) | yes | no | no | yes | yes | no |
| H_c non-transitive consequence (every step accepted, cut refused) | yes | yes | yes | yes | yes | no |
| H_d premise-set filter (DS fails only when a contradiction is present) | yes | yes | no | yes | yes | no |
| Classical competence | yes | yes | yes | yes | yes | yes |
| LP / FDE | yes | yes | no | no | no | no |

Reading:
- H_b: the explosion "no" is not about consequence at all; drop the "structural anomaly" claim.
- H_a: rejection sits at ∨-introduction. Relevance logics (e.g. R) accept ∨-introduction and reject DS,
  so this is not a relevance logic either; it is a surface filter on conclusion vocabulary.
- H_c: the model's acceptance relation is not closed under cut, so no Tarskian consequence relation
  fits. Candidate label, from memory and to be verified before use in writing: Tennant's Core Logic
  (∨-introduction and DS valid, explosion invalid, unrestricted cut rejected). Strict–tolerant ST is
  not a fit: it validates every classically valid inference, explosion included.
- H_d: same conclusion as H_b for the paper (filtering, not a logic), but the filter is narrower.
- `double_ds` separates "cut fails in general" from "cut fails only across a contradiction".

`battery/fit.py` prints a **Chain decomposition** paragraph with this diagnosis when
`disjunction_introduction` is among the scored schemata. The logic-fit tables in that report are
secondary here (only explosion and DS are in its conditional-free list).

## Items

`items.jsonl`: 534 items. `generate.py --schemata disjunction_introduction identity_inconsistent
explosion_lemma double_ds explosion disjunctive_syllogism --per-cell 10 --symbolic-per-cell 10 --seed 14`.
Per schema: 10 everyday + 10 nonsense + 10 symbolic instances × 3 framings = 90, except
`identity_inconsistent` symbolic = 24 (one atom, eight letters in the pool, so eight distinct instances).
The pilot battery output of `generate.py` (no `--schemata`) is byte-identical to before the change.

## Running

`bash run.sh` (set `PYTHON=` if `python` is not on PATH) scores the seven pilot models sequentially (needs Ollama on 127.0.0.1:11434, one model
on the GPU at a time) and writes `report.md`. Skips models whose score file already has 534 lines.

## Results (scored 2026-11-24, `report.md`)

Four models: qwen2.5:7b-instruct, gemma3:12b, hermes3:8b, mistral:7b (llama3.1 dropped after the
explosion-pragmatics run; the larger Qwen models were not run). All four pass the reliability rule; there
are no fallacy items here, so it is judged on answer mass only (worst: qwen2.5:7b, 102/534 = 19% < 25%).

Mean P(yes), binarised reading against the hypothesis table above:

| Model | ∨-intro | A,¬A ⊢ A | A,¬A,A∨B ⊢ B | double DS | DS | explosion | closest hypothesis |
|---|---:|---:|---:|---:|---:|---:|---|
| qwen2.5:7b-instruct | 0.84 | 0.00 | 0.38 | 0.85 | 1.00 | 0.00 | H_b, all six columns match |
| gemma3:12b | 0.94 | 0.24 | 0.97 | 1.00 | 1.00 | 0.13 | none: H_c except A,¬A ⊢ A |
| hermes3:8b | 0.41 | 0.07 | 0.35 | 0.54 | 0.83 | 0.02 | H_b-like, but ∨-intro below 0.5 |
| mistral:7b | 0.40 | 0.03 | 0.10 | 0.38 | 0.60 | 0.13 | H_b-like, chaining fails without contradiction too |

`fit.py` prints H_b for all four, because its decision rule checks A, ¬A ⊢ A first. That label is right for
qwen2.5:7b (the only model that also passed the fallacy check in the pragmatics run). For gemma3:12b it is
not: H_b predicts a "no" to A, ¬A, A∨B ⊢ B, and gemma says yes (0.97). hermes3:8b and mistral:7b are weak
on ∨-introduction and chained DS even without a contradiction, and failed the fallacy check in the
pragmatics run, so their profiles are exploratory.

Consequence for the paper: the "structural anomaly" / non-transitive-consequence reading (H_c) is not
supported for qwen2.5:7b. Its explosion "no" is a refusal to infer anything from an inconsistent premise
set, not a consequence relation. gemma3:12b is the open case; `../2026-11-24__inconsistent-premises/`
tests whether its "no" to A, ¬A ⊢ A is about the contradicted atom only.

**Correction (2026-11-24, after review of the preprint draft).** The H_c label ("not closed under cut")
needs care. Lewis's argument uses the form of Cut that combines premise sets. With a shared premise set
Γ = {A, ¬A}, Cut would need Γ ⊢ A∨B accepted, and both qwen2.5:7b (0.19) and gemma3:12b (0.22) reject it
(`../2026-11-24__mcs-inference/`). The data show failures of reflexivity (A, ¬A ⊬ A) and monotonicity
(DS accepted, DS with A added rejected), not of shared-premise Cut. "gemma3:12b = H_c" above should be
read as "accepts every step of Lewis's argument as posed and rejects its conclusion", nothing more.
