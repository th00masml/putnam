"""Consequence relations for inconsistent premise sets, built on classical logic (post hoc follow-up, 2026-11-24).

Maximal consistent subsets (MCS) of the premises, after Rescher & Manor (1970):
- free:        classical consequence of the premises that lie in no minimal inconsistent subset.
- universal:   classical consequence of every MCS (the "skeptical" relation).
- existential: classical consequence of at least one MCS (the "credulous" relation).
free ⊆ universal ⊆ existential. On a consistent premise set all three coincide with classical logic.

split_universal (added after the MCS-inference run, post hoc): universal consequence after splitting every
conjunctive premise into its conjuncts. It formalises the hand-written "discard the contradicted atom" row.
"""

from itertools import combinations

from logics import mv_valid


def consistent(fs):
    return not mv_valid("CL", list(fs), ("and", ("var", "A"), ("not", ("var", "A"))))


def maximal_consistent_subsets(premises):
    idx = range(len(premises))
    found = []
    for k in range(len(premises), -1, -1):
        for sub in combinations(idx, k):
            if consistent([premises[i] for i in sub]) and not any(set(sub) <= s for s in found):
                found.append(set(sub))
    return [[premises[i] for i in sorted(s)] for s in found]


def minimal_inconsistent_subsets(premises):
    idx = range(len(premises))
    found = []
    for k in range(1, len(premises) + 1):
        for sub in combinations(idx, k):
            if not consistent([premises[i] for i in sub]) and not any(s <= set(sub) for s in found):
                found.append(set(sub))
    return found


def mcs_verdicts(premises, conclusion):
    mcs = maximal_consistent_subsets(premises)
    in_mis = set().union(*minimal_inconsistent_subsets(premises))
    free = [p for i, p in enumerate(premises) if i not in in_mis]
    follows = [mv_valid("CL", m, conclusion) for m in mcs]
    return {"free": mv_valid("CL", free, conclusion), "universal": all(follows), "existential": any(follows)}


def split_conjunctions(premises):
    out = []
    for f in premises:
        out += split_conjunctions([f[1], f[2]]) if f[0] == "and" else [f]
    return out


def split_universal(premises, conclusion):
    """Post hoc (2026-11-24): universal MCS consequence over the conjuncts of the premises."""
    return mcs_verdicts(split_conjunctions(premises), conclusion)["universal"]
