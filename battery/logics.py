"""Gold-verdict model checkers for the six candidate logics.

Formulas are tuples: ("var", "A"), ("not", f), ("and", f, g), ("or", f, g), ("imp", f, g).

- CL, K3, LP, FDE: exhaustive many-valued truth tables (exact).
- IL: exhaustive Kripke-countermodel search over all posets with <= 3 worlds.
  A found countermodel proves invalidity; "valid" means no countermodel up to that size.
- QL: exhaustive search over valuations into MO2, the smallest non-distributive
  orthomodular lattice. A found countermodel proves invalidity; "valid" means valid in MO2.
  The conditional has no settled QL reading, so formulas containing "imp" return None.
"""

from itertools import combinations, product

LOGICS = ["CL", "IL", "K3", "LP", "FDE", "QL"]


def atoms(f):
    if f[0] == "var":
        return {f[1]}
    return set().union(*(atoms(g) for g in f[1:]))


def has_imp(f):
    return f[0] == "imp" or (f[0] != "var" and any(has_imp(g) for g in f[1:]))


# --- Many-valued logics (Dunn's four values as subsets of {t, f}) -------------

T, F = frozenset("t"), frozenset("f")
BOTH, NEITHER = frozenset("tf"), frozenset()
VALUES = {"CL": [T, F], "K3": [T, F, NEITHER], "LP": [T, F, BOTH], "FDE": [T, F, BOTH, NEITHER]}


def mv_eval(f, v):
    op = f[0]
    if op == "var":
        return v[f[1]]
    if op == "not":
        x = mv_eval(f[1], v)
        return frozenset({"t": "f", "f": "t"}[c] for c in x)
    if op == "imp":  # material conditional
        return mv_eval(("or", ("not", f[1]), f[2]), v)
    x, y = mv_eval(f[1], v), mv_eval(f[2], v)
    if op == "and":
        return frozenset(({"t"} if "t" in x and "t" in y else set()) | ({"f"} if "f" in x or "f" in y else set()))
    if op == "or":
        return frozenset(({"t"} if "t" in x or "t" in y else set()) | ({"f"} if "f" in x and "f" in y else set()))
    raise ValueError(op)


def mv_valid(logic, premises, conclusion):
    names = sorted(set().union(atoms(conclusion), *(atoms(p) for p in premises)))
    for vals in product(VALUES[logic], repeat=len(names)):
        v = dict(zip(names, vals))
        if all("t" in mv_eval(p, v) for p in premises) and "t" not in mv_eval(conclusion, v):
            return False
    return True


# --- Intuitionistic logic (Kripke models) ------------------------------------

def posets(n):
    """All partial orders on range(n), as sets of pairs (i, j) meaning i <= j."""
    pairs = [(i, j) for i in range(n) for j in range(n) if i != j]
    for k in range(len(pairs) + 1):
        for extra in combinations(pairs, k):
            le = {(i, i) for i in range(n)} | set(extra)
            antisym = all((j, i) not in le for i, j in extra)
            trans = all((a, d) in le for a, b in le for c, d in le if b == c)
            if antisym and trans:
                yield le


def up_sets(n, le):
    for k in range(n + 1):
        for s in combinations(range(n), k):
            s = set(s)
            if all(j in s for i in s for (a, j) in le if a == i):
                yield frozenset(s)


def forces(w, f, le, val):
    op = f[0]
    if op == "var":
        return w in val[f[1]]
    if op == "and":
        return forces(w, f[1], le, val) and forces(w, f[2], le, val)
    if op == "or":
        return forces(w, f[1], le, val) or forces(w, f[2], le, val)
    later = [u for (a, u) in le if a == w]
    if op == "not":
        return all(not forces(u, f[1], le, val) for u in later)
    if op == "imp":
        return all(not forces(u, f[1], le, val) or forces(u, f[2], le, val) for u in later)
    raise ValueError(op)


def il_valid(premises, conclusion, max_worlds=3):
    names = sorted(set().union(atoms(conclusion), *(atoms(p) for p in premises)))
    for n in range(1, max_worlds + 1):
        for le in posets(n):
            ups = list(up_sets(n, le))
            for sets in product(ups, repeat=len(names)):
                val = dict(zip(names, sets))
                for w in range(n):
                    if all(forces(w, p, le, val) for p in premises) and not forces(w, conclusion, le, val):
                        return False
    return True


# --- Quantum logic (MO2 orthomodular lattice) --------------------------------

MO2 = ["0", "a", "a'", "b", "b'", "1"]
COMP = {"0": "1", "1": "0", "a": "a'", "a'": "a", "b": "b'", "b'": "b"}


def mo2_le(x, y):
    return x == y or x == "0" or y == "1"


def mo2_meet(x, y):
    return x if mo2_le(x, y) else y if mo2_le(y, x) else "0"


def mo2_join(x, y):
    return y if mo2_le(x, y) else x if mo2_le(y, x) else "1"


def ql_eval(f, v):
    op = f[0]
    if op == "var":
        return v[f[1]]
    if op == "not":
        return COMP[ql_eval(f[1], v)]
    x, y = ql_eval(f[1], v), ql_eval(f[2], v)
    return mo2_meet(x, y) if op == "and" else mo2_join(x, y)


def ql_valid(premises, conclusion):
    if has_imp(conclusion) or any(has_imp(p) for p in premises):
        return None
    names = sorted(set().union(atoms(conclusion), *(atoms(p) for p in premises)))
    for vals in product(MO2, repeat=len(names)):
        v = dict(zip(names, vals))
        meet = "1"
        for p in premises:
            meet = mo2_meet(meet, ql_eval(p, v))
        if not mo2_le(meet, ql_eval(conclusion, v)):
            return False
    return True


def verdicts(premises, conclusion):
    """Gold verdict per logic: True (valid), False (invalid), None (undefined)."""
    out = {lg: mv_valid(lg, premises, conclusion) for lg in ("CL", "K3", "LP", "FDE")}
    out["IL"] = il_valid(premises, conclusion)
    out["QL"] = ql_valid(premises, conclusion)
    return {lg: out[lg] for lg in LOGICS}
