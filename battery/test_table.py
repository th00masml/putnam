"""Check computed verdicts against the hand-written table in proposal-logic-revision.md (section 3.1)
and the hand-derived verdicts for the explosion-chain schemata."""

from logics import LOGICS, verdicts
from schemata import ALL_SCHEMATA

Y, N, X = True, False, None  # X = undefined (QL conditional)

#                            CL IL K3 LP FDE QL
EXPECTED = {
    "modus_ponens":             [Y, Y, Y, N, N, X],
    "modus_tollens":            [Y, Y, Y, N, N, X],
    "distribution":             [Y, Y, Y, Y, Y, N],
    "excluded_middle":          [Y, N, N, Y, N, Y],
    "double_negation_elim":     [Y, N, Y, Y, Y, Y],
    "explosion":                [Y, Y, Y, N, N, Y],
    "disjunctive_syllogism":    [Y, Y, Y, N, N, N],
    "non_contradiction":        [Y, Y, N, Y, N, Y],
    "affirming_consequent":     [N, N, N, N, N, X],
    "denying_antecedent":       [N, N, N, N, N, X],
    # explosion-chain follow-up
    "disjunction_introduction": [Y, Y, Y, Y, Y, Y],
    "identity_inconsistent":    [Y, Y, Y, Y, Y, Y],
    "explosion_lemma":          [Y, Y, Y, N, N, Y],
    "double_ds":                [Y, Y, Y, N, N, N],
}


def main():
    failures = 0
    for name, (premises, conclusion) in ALL_SCHEMATA.items():
        got = verdicts(premises, conclusion)
        for logic, want in zip(LOGICS, EXPECTED[name]):
            if got[logic] != want:
                failures += 1
                print(f"MISMATCH {name} {logic}: table={want} computed={got[logic]}")
    columns = {lg: tuple(EXPECTED[s][i] for s in ALL_SCHEMATA) for i, lg in enumerate(LOGICS)}
    if len(set(columns.values())) != len(LOGICS):
        failures += 1
        print("MISMATCH: two logics share a verdict column")
    print("OK" if failures == 0 else f"{failures} failure(s)")
    return failures


if __name__ == "__main__":
    raise SystemExit(main())
