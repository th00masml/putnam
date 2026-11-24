# Explosion pragmatic controls (prepared 2026-11-24, not yet scored)

## Why

The pilot "no" to explosion (A, ¬A ⊢ B) can come from at least two things that are not a
paraconsistent consequence relation:

1. **Relevance.** In the pilot, B is an unrelated sentence ("the oven is hot, it is not the case that
   the oven is hot, therefore the lights are off"). The model may be judging that the conclusion has
   nothing to do with the premises, which is a judgement about a good argument, not about validity.
2. **Task reading.** "Does it follow?" and "Must it be true?" invite an everyday reading of "follow".
   A model can know the formal answer and still give the conversational one.

This run varies both while holding the logical form fixed.

## Design

- **Content:** `everyday` (pilot pool: three unrelated sentences) vs `related` (one subject, three of its
  predicates: "the kettle is full, it is not the case that the kettle is full, therefore the kettle is hot").
- **Framing:** the three pilot framings plus `formal`, which states the classical definition of validity
  ("valid if and only if there is no possible situation in which all premises are true and the conclusion
  false") before asking.
- **Schemata:** explosion, DS, explosion_lemma (A, ¬A, A∨B ⊢ B), modus ponens as a valid anchor, and the
  two fallacies as yes-bias controls (the "no stable logic" check in `fit.py` needs them).

`items.jsonl`: 480 items, `generate.py --schemata explosion disjunctive_syllogism explosion_lemma
modus_ponens affirming_consequent denying_antecedent --content everyday related --related --formal
--per-cell 10 --seed 24`. 6 schemata × 2 contents × 10 instances × 4 framings.

## Predictions (binarised at 0.5), written before scoring

| Account of the explosion "no" | explosion, everyday | explosion, related | explosion, formal | fallacies, formal |
|---|:-:|:-:|:-:|:-:|
| Relevance filter on the conclusion | no | yes | (either) | no |
| Conversational reading of "follow" | no | (either) | yes | no |
| Contradiction aversion / non-transitive consequence | no | no | no | no |
| Formal instruction only raises yes-bias | no | – | yes | **yes** |

Reading:
- Explosion rises to yes with related content: the pilot anomaly is (at least partly) a relevance
  judgement. Report it as such; the DS-yes/explosion-no pattern then says nothing about consequence.
- Explosion rises under the formal framing and fallacies stay at no: the model has the classical
  answer and the default framings elicit a pragmatic one.
- If explosion rises under `formal` but fallacies rise with it, the instruction just shifts the yes
  threshold; it is not evidence about logic.
- Explosion stays at no in all four cells: the explosion-chain run (`../2026-10-14__explosion-chain/`)
  is needed to say which step is refused.

Thresholds, decoding and tie bands are the ones frozen in `../../PREREGISTRATION.md`.

## Running

`bash run.sh` (set `PYTHON=` if `python` is not on PATH). Same model list and skip logic as the
explosion-chain run. `fit.py` prints a by-framing table when the `formal` framing is present.
