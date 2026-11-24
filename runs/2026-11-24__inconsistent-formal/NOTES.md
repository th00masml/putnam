# Formal-framing check on inconsistent premises (prepared 2026-11-24, not yet scored)

## Why

Review of the preprint draft: the relevance and formal-definition controls of
`../2026-11-24__explosion-pragmatics/` were run on explosion only. The paper's key anomaly is a "no" to
A, ¬A ⊢ A, which every candidate logic validates. That "no" may be pragmatic: with A and not-A both
given, "does A follow?" can be heard as "is A the case?". This run asks the inconsistent-premise schemata
again with the `formal` framing, which states that an argument is valid iff no possible situation makes
all premises true and the conclusion false.

Already in the data, before this run: qwen2.5:7b-instruct rejects A, ¬A ⊢ A in all three default framings
(follows 0.00, "Suppose the following are all true… must it be true" 0.00, valid 0.03), so the
suppositional framing did not rescue it either.

## Schemata

| Schema | Form | Gold (all six logics) | Role |
|---|---|:-:|---|
| identity_inconsistent | A, ¬A ⊢ A | valid | target |
| adjunction_inconsistent | A, ¬A ⊢ A∧¬A | valid | target |
| bystander_inconsistent | A, ¬A, C ⊢ C | valid | control: accepted so far by qwen2.5:7b |
| identity_consistent | A, C ⊢ C | valid | control: no contradiction |
| disjunct_from_disjunction | A∨B ⊢ A | invalid | yes-bias control under the formal framing |

`items.jsonl`: 584 items. `generate.py --schemata identity_inconsistent adjunction_inconsistent
bystander_inconsistent identity_consistent disjunct_from_disjunction --formal --per-cell 10
--symbolic-per-cell 10 --seed 54`. Everyday, nonsense and symbolic content, the three default framings
plus `formal` (the one-word wording fixed in the pragmatics run). Formal items: 28–30 per schema.

## Predictions for the formal framing (binarised at 0.5), written before scoring

| Account | A, ¬A ⊢ A | A, ¬A ⊢ A∧¬A | A, ¬A, C ⊢ C | A, C ⊢ C | A∨B ⊢ A |
|---|:-:|:-:|:-:|:-:|:-:|
| Pragmatic reading ("is A the case?"); formal definition removes it | yes | yes | yes | yes | no |
| Policy: discard the contradicted atom (survives the formal definition) | no | no | yes | yes | no |
| Formal framing only raises the yes-rate | yes | yes | yes | yes | **yes** |

## Decision rule

- Confirmatory model: qwen2.5:7b-instruct. Primary cell: A, ¬A ⊢ A under `formal`, all contents pooled.
  - Mean < 0.40 and A∨B ⊢ A under `formal` < 0.5: the "no" survives the formal definition; the policy
    reading stands and the pragmatic objection is answered for this schema.
  - Mean > 0.60 and A∨B ⊢ A under `formal` < 0.5: the "no" is pragmatic; the paper must say that the
    anomaly disappears under an explicit definition of validity.
  - 0.40–0.60, or A∨B ⊢ A under `formal` > 0.5: inconclusive.
- Adjunction is reported with the same bands as secondary. The two controls must stay above 0.5 under
  `formal`; if either does not, the run is reported as inconclusive.
- Other models (gemma3:12b, hermes3:8b, mistral:7b): optional, exploratory.
- Reliability: answer mass as frozen in `../../PREREGISTRATION.md` (no fallacy items in this run;
  A∨B ⊢ A is the yes-bias control instead).

## Running

`bash run.sh`, or the PowerShell loop with `$models = "qwen2.5:7b-instruct"` (add the other three models
if you want the exploratory rows). `fit.py` prints a schema × framing table because `formal` is present.

## Results (scored 2026-11-24, `report.md`)

qwen2.5:7b-instruct only. Reliability: 1 of 584 items with yes/no mass < 0.5; answer-order gap 0.015.

Mean P(yes) under `formal` (all contents): A, ¬A ⊢ A **0.00**; A, ¬A ⊢ A∧¬A 0.00; A, ¬A, C ⊢ C 0.89;
A, C ⊢ C 1.00; A∨B ⊢ A 0.01. The other framings give the same picture (A, ¬A ⊢ A: 0.00 / 0.00 / 0.04).

By the decision rule above: primary cell < 0.40, yes-bias control < 0.5, both controls > 0.5. The "no" to
A, ¬A ⊢ A survives an explicit definition of validity; the pragmatic objection is answered for this model
and schema. Adjunction (secondary) agrees.
