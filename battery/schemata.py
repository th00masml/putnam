"""Inference schemata from proposal-logic-revision.md, section 3.1, plus the explosion-chain follow-up."""

A, B, C = ("var", "A"), ("var", "B"), ("var", "C")


def neg(f):
    return ("not", f)


def conj(f, g):
    return ("and", f, g)


def disj(f, g):
    return ("or", f, g)


def imp(f, g):
    return ("imp", f, g)


# name -> (premises, conclusion)
SCHEMATA = {
    "modus_ponens": ([A, imp(A, B)], B),
    "modus_tollens": ([neg(B), imp(A, B)], neg(A)),
    "distribution": ([conj(A, disj(B, C))], disj(conj(A, B), conj(A, C))),
    "excluded_middle": ([], disj(A, neg(A))),
    "double_negation_elim": ([neg(neg(A))], A),
    "explosion": ([A, neg(A)], B),
    "disjunctive_syllogism": ([disj(A, B), neg(A)], B),
    "non_contradiction": ([], neg(conj(A, neg(A)))),
    "affirming_consequent": ([B, imp(A, B)], A),
    "denying_antecedent": ([neg(A), imp(A, B)], neg(B)),
}

# Decomposition of C. I. Lewis's derivation of explosion (A ⊢ A∨B; A∨B, ¬A ⊢ B; cut), with controls.
# Not part of the pilot battery; selected with generate.py --schemata.
CHAIN_SCHEMATA = {
    "disjunction_introduction": ([A], disj(A, B)),                 # step 1 of the Lewis argument
    "identity_inconsistent": ([A, neg(A)], A),                       # anything at all from inconsistent premises?
    "explosion_lemma": ([A, neg(A), disj(A, B)], B),                 # step 2 with the inconsistent premises present
    "double_ds": ([disj(A, B), neg(A), disj(neg(B), C)], C),         # two chained DS steps, no contradiction
}

# Follow-up to the explosion-chain run: is the "no" to A, ¬A ⊢ A about any inference from an inconsistent set,
# or only about conclusions on the contradicted atom? Selected with generate.py --schemata.
INCONSISTENCY_SCHEMATA = {
    "identity_consistent": ([A, C], C),                              # restating a premise, no contradiction
    "bystander_inconsistent": ([A, neg(A), C], C),                   # restating an unrelated premise next to a contradiction
    "adjunction_inconsistent": ([A, neg(A)], conj(A, neg(A))),       # restating the contradiction itself
}

# Second follow-up: which consequence relation for inconsistent premise sets (battery/mcs.py) fits?
# shared_conjunct separates free from universal MCS inference; clean_conjunct separates universal MCS inference
# from discarding only the contradicted atom; the ∨-intro item separates existential inference from the rest.
MCS_SCHEMATA = {
    "conjunction_elimination": ([conj(A, C)], C),                                  # control, consistent
    "shared_conjunct": ([conj(A, C), conj(C, neg(A))], C),          # C first: "both C and not-A" has no scope ambiguity
    "clean_conjunct": ([conj(A, C), neg(A)], C),
    "disjunction_introduction_inconsistent": ([A, neg(A)], disj(A, B)),
}

ALL_SCHEMATA = {**SCHEMATA, **CHAIN_SCHEMATA, **INCONSISTENCY_SCHEMATA, **MCS_SCHEMATA}
