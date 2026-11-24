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

## Results (scored 2026-11-24, `report.md`)

All four models pass the reliability rule (answer mass only). Mean P(yes), everyday / nonsense / symbolic:

| Model | A, C ⊢ C | A, ¬A, C ⊢ C | A, ¬A ⊢ A∧¬A | A, ¬A ⊢ A | matching row |
|---|---|---|---|---|---|
| qwen2.5:7b-instruct | 0.92 / 0.96 / 0.61 | 0.88 / 0.92 / 0.47 | 0.00 / 0.00 / 0.01 | 0.03 / 0.00 / 0.00 | conflicting evidence |
| gemma3:12b | 1.00 / 1.00 / 0.99 | 1.00 / 1.00 / 1.00 | 0.31 / 0.34 / 0.55 | 0.23 / 0.28 / 0.17 | conflicting evidence |
| hermes3:8b | 0.81 / 0.85 / 0.43 | 0.56 / 0.78 / 0.08 | 0.03 / 0.20 / 0.09 | 0.06 / 0.15 / 0.00 | global aversion, marginal (bystander mean 0.47) |
| mistral:7b | 0.91 / 0.84 / 0.33 | 0.54 / 0.38 / 0.40 | 0.04 / 0.07 / 0.30 | 0.03 / 0.02 / 0.03 | global aversion, marginal (bystander mean 0.44) |

Against the predictions above:
- qwen2.5:7b and gemma3:12b draw conclusions from an inconsistent premise set when the conclusion is an
  untouched premise, and refuse conclusions about the contradicted atom. By the reading written before
  scoring, A, ¬A ⊢ A is a bad probe of H_b for them, and the explosion-chain H_b diagnosis is withdrawn
  for both. For gemma3:12b the remaining profile is H_c (every step of the Lewis argument accepted,
  explosion rejected), exploratory because it failed the fallacy check in the pragmatics run.
- hermes3:8b and mistral:7b fall on the global-aversion side, but only just, both are weak on restating a
  premise in symbolic notation even without a contradiction, and both failed the fallacy check in the
  pragmatics run. Exploratory.

Post hoc, not preregistered: qwen2.5:7b's whole profile across the three explosion runs (∨-intro yes,
DS yes, double DS yes, A,¬A,A∨B ⊢ B no, explosion no, A,¬A,C ⊢ C yes, A,¬A ⊢ A no, A,¬A ⊢ A∧¬A no) is
what inference from maximal consistent subsets predicts, with a conclusion accepted only if it follows
from every maximal consistent subset of the premises (Rescher & Manor 1970, from memory, verify before
citing). That consequence relation is not reflexive (A, ¬A ⊬ A), so it is none of the six candidate
logics. It needs its own preregistered run before it goes in the paper. A discriminating item:
A∧C, ¬A ⊢ C, which universal maximal-consistent-subset inference rejects and "ignore the contradicted
atom" accepts.
