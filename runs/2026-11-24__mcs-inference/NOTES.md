# MCS-inference follow-up (prepared 2026-11-24, not yet scored)

## Why

After the inconsistent-premises run, qwen2.5:7b-instruct's binarised profile over eight schemata
(∨-intro yes, DS yes, double DS yes, A,¬A,A∨B ⊢ B no, explosion no, A,¬A,C ⊢ C yes, A,¬A ⊢ A no,
A,¬A ⊢ A∧¬A no) matched inference from maximal consistent subsets (MCS) of the premises (Rescher &
Manor 1970, *Theory and Decision* 1(2): 179–217, doi:10.1007/BF00154005). That hypothesis was formed
after seeing the data. This run tests it on items chosen to separate it from its neighbours.

## Candidate relations

Computed by `battery/mcs.py` (classical logic on subsets of the premises), checked by hand in
`battery/test_table.py`:
- **MCS free**: classical consequence of the premises that are in no minimal inconsistent subset.
- **MCS universal**: classical consequence of every maximal consistent subset (the hypothesis).
- **MCS existential**: classical consequence of at least one maximal consistent subset.

Written by hand, no formal definition:
- **Discard the contradicted atom**: drop what the premises say about an atom they both assert and deny,
  keep everything else they say (including the other conjunct of a conjunction).
- **Global contradiction aversion** (H_b): accept nothing from an inconsistent premise set.

## Schemata and predictions (binarised at 0.5), written before scoring

All seven are valid in all six candidate logics, so any "no" is a departure from all of them.

| Schema | Form | free | universal | existential | discard atom | global aversion |
|---|---|:-:|:-:|:-:|:-:|:-:|
| conjunction_elimination | A∧C ⊢ C | yes | yes | yes | yes | yes |
| shared_conjunct | A∧C, C∧¬A ⊢ C | no | **yes** | yes | yes | no |
| clean_conjunct | A∧C, ¬A ⊢ C | no | **no** | yes | yes | no |
| disjunction_introduction_inconsistent | A, ¬A ⊢ A∨B | no | no | yes | no | no |
| identity_inconsistent | A, ¬A ⊢ A | no | no | yes | no | no |
| bystander_inconsistent | A, ¬A, C ⊢ C | yes | yes | yes | yes | no |
| explosion_lemma | A, ¬A, A∨B ⊢ B | no | no | yes | no | no |

The hypothesis (MCS universal) differs from its nearest rivals in one item each: from MCS free on
`shared_conjunct`, from "discard the contradicted atom" on `clean_conjunct`. The last three rows are
anchors from earlier runs, with new instances.

`shared_conjunct` puts C first in the second premise ("both the shop is open and it is not the case that
the kettle is on"). The first draft had "both it is not the case that the kettle is on and the shop is
open", which can be read as ¬(A∧C); on that reading MCS universal predicts no. Fixed before any scoring.

## Decision rule

- `fit.py` prints the binarised profile and the number of mismatches with each row, and assigns a
  relation only on a unique exact match.
- Confirmatory model: qwen2.5:7b-instruct (the only model that passed every reliability check so far).
  The hypothesis is supported if it matches MCS universal exactly, and refuted otherwise. If the
  deciding schema (`shared_conjunct` or `clean_conjunct`) has a mean P(yes) within 0.40–0.60, report the
  result as inconclusive rather than as a match or a refutation.
- gemma3:12b, hermes3:8b, mistral:7b: exploratory, reported with the same rule.
- Thresholds, decoding and the answer-mass rule are the ones frozen in `../../PREREGISTRATION.md`.
  No fallacy items, so reliability is judged on answer mass only.

## Items

`items.jsonl`: 624 items. `generate.py --schemata conjunction_elimination shared_conjunct clean_conjunct
disjunction_introduction_inconsistent identity_inconsistent bystander_inconsistent explosion_lemma
--per-cell 10 --symbolic-per-cell 10 --seed 44`. 90 items per schema (identity_inconsistent: 84).

## Running

`bash run.sh` (set `PYTHON=` if `python` is not on PATH), or the PowerShell loop with
`$models = "qwen2.5:7b-instruct","gemma3:12b","hermes3:8b","mistral:7b"`.

## Results (scored 2026-11-24, `report.md`)

All four models pass the answer-mass rule. Mean P(yes), everyday / nonsense / symbolic, and `fit.py`'s match:

| Schema | qwen2.5:7b | gemma3:12b | hermes3:8b | mistral:7b |
|---|---|---|---|---|
| A∧C ⊢ C | 0.97 / 0.99 / 1.00 | 1.00 / 0.98 / 1.00 | 0.79 / 0.83 / 0.78 | 0.78 / 0.83 / 0.42 |
| A∧C, C∧¬A ⊢ C | 0.95 / 1.00 / 0.65 | 0.99 / 0.95 / 1.00 | 0.84 / 0.86 / 0.38 | 0.58 / 0.57 / 0.70 |
| **A∧C, ¬A ⊢ C** | **0.94 / 0.88 / 1.00** | 0.78 / 0.74 / 0.90 | 0.39 / 0.62 / 0.15 | 0.35 / 0.44 / 0.49 |
| A, ¬A ⊢ A∨B | 0.01 / 0.02 / 0.53 | 0.23 / 0.30 / 0.13 | 0.07 / 0.26 / 0.16 | 0.02 / 0.04 / 0.33 |
| A, ¬A ⊢ A | 0.03 / 0.01 / 0.00 | 0.25 / 0.32 / 0.17 | 0.04 / 0.20 / 0.00 | 0.05 / 0.02 / 0.03 |
| A, ¬A, C ⊢ C | 0.90 / 0.98 / 0.39 | 0.99 / 0.99 / 1.00 | 0.68 / 0.76 / 0.09 | 0.53 / 0.48 / 0.41 |
| A, ¬A, A∨B ⊢ B | 0.35 / 0.10 / 0.56 | 0.99 / 1.00 / 0.90 | 0.12 / 0.58 / 0.34 | 0.09 / 0.05 / 0.10 |
| `fit.py` | discard the contradicted atom, exact | none (closest: discard atom, 1 off) | MCS universal, exact | none (MCS universal and global aversion, 1 off each) |

**Preregistered test: the hypothesis is refuted for the confirmatory model.** qwen2.5:7b accepts
A∧C, ¬A ⊢ C (mean 0.94, well outside the 0.40–0.60 inconclusive band), which MCS universal rejects.
Its profile matches, exactly and uniquely, the "discard the contradicted atom" row written before the run.

hermes3:8b (exploratory) matches MCS universal exactly, but its deciding item is weak (0.39 mean, 0.62 on
nonsense content) and it failed the fallacy check in the pragmatics run. gemma3:12b again accepts DS run
on inconsistent premises (0.96), which no candidate here predicts; its other six items match "discard the
contradicted atom". mistral:7b matches nothing.

Post hoc, not preregistered: "discard the contradicted atom" can be formalised as universal MCS
consequence after splitting every conjunctive premise into its conjuncts (`split_universal` in
`battery/mcs.py`, added after this run). Checked against all of qwen2.5:7b's data from the three
explosion runs and this one (14 schemata, fallacies excluded), it disagrees on none; plain MCS universal
disagrees on one (A∧C, ¬A ⊢ C). For the other models split-universal disagrees on 1 (gemma: the DS lemma),
3 (hermes) and 4 (mistral) schemata. The relation is syntax-sensitive: it treats A∧C differently from
the pair A, C only before splitting, so it is not a consequence relation on propositions. A new
preregistered run would have to test it on items where splitting matters and where it doesn't
(e.g. ¬(A∨C)-style premises that split only after De Morgan).
