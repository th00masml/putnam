# Inconsistent-premises follow-up (prepared 2026-11-24, not yet scored)

## Why

In the explosion-chain run (`../2026-10-14__explosion-chain/report.md`) all four models reject
A, ¬A ⊢ A (mean P(yes): qwen2.5:7b 0.00, mistral:7b 0.03, hermes3:8b 0.07, gemma3:12b 0.24), which
every candidate logic validates. `fit.py` reads that as contradiction aversion (H_b). For qwen2.5:7b the
whole chain profile matches H_b. gemma3:12b does not: it also accepts A, ¬A, A∨B ⊢ B (0.97), which H_b
predicts it rejects.

A, ¬A ⊢ A has a second reading: asked "must A be true?" with ¬A in plain view, a model can treat the
premises as conflicting evidence about A and say no, without refusing inference from the inconsistent
set as such. This run separates the two readings.

## Schemata (all valid in all six logics; `battery/test_table.py`)

| Schema | Form | What a "no" means |
|---|---|---|
| identity_consistent | A, C ⊢ C | refuses to restate a premise at all (then A, ¬A ⊢ A is uninformative) |
| bystander_inconsistent | A, ¬A, C ⊢ C | refuses any conclusion once the premise set is inconsistent |
| adjunction_inconsistent | A, ¬A ⊢ A∧¬A | refuses to restate the contradiction itself |
| identity_inconsistent | A, ¬A ⊢ A | anchor from the explosion-chain run, new instances |

`items.jsonl`: 348 items. `generate.py --schemata identity_consistent bystander_inconsistent
adjunction_inconsistent identity_inconsistent --per-cell 10 --symbolic-per-cell 10 --seed 34`.
10 everyday + 10 nonsense + 10 symbolic instances × 3 framings = 90 per schema, except schemata with one
atom in symbolic notation (adjunction, identity_inconsistent): 8 instances, 24 items.

## Predictions (binarised at 0.5), written before scoring

| Account | A, C ⊢ C | A, ¬A, C ⊢ C | A, ¬A ⊢ A∧¬A | A, ¬A ⊢ A |
|---|:-:|:-:|:-:|:-:|
| Global contradiction aversion (H_b): no inference from an inconsistent set | yes | no | no | no |
| Conflicting-evidence reading: refuses only conclusions about the contradicted atom | yes | yes | no | no |
| Refuses to restate any premise | no | no | (either) | no |

Reading:
- Global aversion: the explosion-chain diagnosis stands as printed.
- Conflicting evidence: the model does reason from inconsistent sets; A, ¬A ⊢ A is a bad probe of H_b, and
  the explosion-chain diagnosis for that model is withdrawn. For gemma3:12b the remaining profile is the
  H_c one (every step of the Lewis argument accepted, explosion rejected), reported as exploratory.
- Refuses to restate: A, ¬A ⊢ A says nothing; no diagnosis.

Thresholds, decoding and the "no stable logic" rule are the ones frozen in `../../PREREGISTRATION.md`.
There are no fallacy items, so reliability is judged on answer mass only, as in the explosion-chain run.

## Running

`bash run.sh` (set `PYTHON=` if `python` is not on PATH), or the PowerShell loop with
`$models = "qwen2.5:7b-instruct","gemma3:12b","hermes3:8b","mistral:7b"`.
