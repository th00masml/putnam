"""Fit candidate logics to scored items (section 3.3) and write a Markdown report.

Usage: python fit.py scores__A.jsonl [scores__B.jsonl ...] --out report.md

Each logic L predicts "yes" on items L validates and "no" otherwise, up to an error rate eps.
- Marginal likelihood: eps ~ Uniform(0, 0.5), responses binarised at P(yes) = 0.5.
- Held-out-schema check: eps fitted on the other schemata, log-likelihood on the held-out one.
Primary analysis uses only conditional-free schemata (all six logics defined);
the secondary uses all schemata (QL excluded, since its conditional is undefined).
"""

import argparse
import json
import math
import os
from collections import defaultdict

from scipy.special import betainc, betaln

from logics import LOGICS
from schemata import ALL_SCHEMATA, SCHEMATA

COND_FREE = ["distribution", "excluded_middle", "double_negation_elim", "explosion", "disjunctive_syllogism", "non_contradiction"]
ANALYSES = {"conditional-free (primary)": (COND_FREE, LOGICS),
            "all schemata (QL excluded)": (list(SCHEMATA), [lg for lg in LOGICS if lg != "QL"])}
FALLACIES = ["affirming_consequent", "denying_antecedent"]
TIE_NATS = 1.0          # logics within this many nats of the best log ML are reported as tied
MAX_FALLACY_YES = 0.25  # provisional reliability thresholds (not preregistered)
MAX_LOW_MASS = 0.25


def log_marginal(k, n):
    """log of 2 * integral_0^0.5 eps^(n-k) (1-eps)^k d eps: k agreements out of n."""
    a, b = n - k + 1, k + 1
    return math.log(2) + betaln(a, b) + math.log(max(betainc(a, b, 0.5), 1e-300))


def agreements(recs, logic):
    k = sum((r["p_yes"] > 0.5) == r["gold"][logic] for r in recs)
    return k, len(recs)


def held_out_loglik(recs, schemata, logic):
    total = 0.0
    for s in schemata:
        train = [r for r in recs if r["schema"] != s and r["schema"] in schemata]
        test = [r for r in recs if r["schema"] == s]
        k, n = agreements(train, logic)
        eps = min((n - k + 0.5) / (n + 1), 0.5)
        kt, nt = agreements(test, logic)
        total += kt * math.log(1 - eps) + (nt - kt) * math.log(eps)
    return total


def chain_section(mean):
    """Explosion-chain follow-up: which step of the Lewis argument does the model refuse?"""
    names = {"disjunction_introduction": "∨-introduction (A ⊢ A∨B)",
             "identity_inconsistent": "identity from inconsistent premises (A, ¬A ⊢ A)",
             "explosion_lemma": "DS with the inconsistent premises present (A, ¬A, A∨B ⊢ B)",
             "double_ds": "two chained DS steps", "disjunctive_syllogism": "DS", "explosion": "explosion"}
    out = ["**Chain decomposition.** Mean P(yes): " + "; ".join(f"{names[s]} {mean[s]:.2f}" for s in names if s in mean) + "."]
    m = lambda s: mean.get(s, 0.5)  # noqa: E731
    if m("identity_inconsistent") < 0.5:
        out.append("Rejects even A, ¬A ⊢ A: the model refuses to reason from inconsistent premises at all, so its \"no\" to "
                   "explosion says nothing about its consequence relation (contradiction aversion, H_b).")
    elif m("disjunction_introduction") < 0.5:
        out.append("Rejects ∨-introduction: a relevance-style filter on atoms that appear only in the conclusion. This blocks the "
                   "Lewis argument at step 1 (H_a); it fits a relevance logic only if DS is rejected too.")
    elif m("explosion_lemma") > 0.5 > m("explosion"):
        out.append("Accepts both steps of the Lewis argument, including DS run on the very same inconsistent premises, yet rejects "
                   "its conclusion: consequence is not closed under cut (H_c). No Tarskian consequence relation fits; a "
                   "non-transitive one does.")
    elif m("explosion_lemma") < 0.5 < m("disjunctive_syllogism"):
        out.append("Accepts DS but rejects it once an inconsistent pair is added to the premises: the trigger is the contradiction "
                   "in the premise set, not the missing ∨-introduction step. Premise-set filtering rather than a logic.")
    if "double_ds" in mean:
        out.append(f"Two chained DS steps without a contradiction: {mean['double_ds']:.2f} "
                   + ("(chaining itself works; the failure is specific to inconsistent premises)." if mean["double_ds"] > 0.5
                      else "(chaining fails even without a contradiction)."))
    return [" ".join(out) + "\n"]


def model_section(name, recs):
    recs = [r for r in recs if r["p_yes"] is not None]
    out = [f"## {name}\n", f"{len(recs)} scored items.\n"]
    best = {}

    for title, (schemata, logics) in ANALYSES.items():
        sub = [r for r in recs if r["schema"] in schemata]
        if not sub:
            continue
        rows = []
        for lg in logics:
            k, n = agreements(sub, lg)
            rows.append((lg, k / n, log_marginal(k, n), held_out_loglik(sub, schemata, lg)))
        top_ml = max(r[2] for r in rows)
        rows.sort(key=lambda r: -r[2])
        tied = [r[0] for r in rows if r[2] >= top_ml - TIE_NATS]
        best[title] = (" = ".join(tied) + (" (tie)" if len(tied) > 1 else ""), max(rows, key=lambda r: r[3])[0])
        out.append(f"### Logic fit: {title}\n")
        out.append("| Logic | Agreement | log ML | log BF vs best | Held-out-schema log-lik |")
        out.append("|---|---:|---:|---:|---:|")
        for lg, acc, ml, ho in rows:
            out.append(f"| {lg} | {acc:.3f} | {ml:.1f} | {ml - top_ml:.1f} | {ho:.1f} |")
        out.append("")

    cell = defaultdict(list)
    for r in recs:
        cell[(r["schema"], r["content"])].append(r["p_yes"])
    contents = ["everyday", "nonsense", "symbolic"]
    out.append("### Mean P(yes) by schema and content\n")
    out.append("| Schema | " + " | ".join(contents) + " | " + " | ".join(LOGICS) + " |")
    out.append("|---|" + "---:|" * len(contents) + ":-:|" * len(LOGICS))
    for s in [s for s in ALL_SCHEMATA if any(cell[(s, c)] for c in contents)]:
        gold = recs[[r["schema"] for r in recs].index(s)]["gold"]
        marks = ["–" if gold[lg] is None else "✓" if gold[lg] else "✗" for lg in LOGICS]
        vals = [f"{sum(cell[(s, c)]) / len(cell[(s, c)]):.2f}" if cell[(s, c)] else "" for c in contents]
        out.append(f"| {s} | " + " | ".join(vals) + " | " + " | ".join(marks) + " |")
    out.append("")

    fallacy = [r["p_yes"] for r in recs if r["schema"] in FALLACIES]
    order_gap = [abs(r["p_yes_order"][0] - r["p_yes_order"][1]) for r in recs if None not in r["p_yes_order"]]
    low_mass = sum(min(r["answer_mass"]) < 0.5 for r in recs)
    fallacy_yes = sum(fallacy) / len(fallacy) if fallacy else None
    if fallacy_yes is not None:
        out.append(f"- Yes-bias on invalid controls (mean P(yes) on fallacies): **{fallacy_yes:.2f}**")
    out.append(f"- Answer-order sensitivity (mean |P(yes | yes-first) − P(yes | no-first)|): **{sum(order_gap) / len(order_gap):.3f}**")
    out.append(f"- Items where yes/no tokens got < 50% of first-token mass in either order: **{low_mass}**\n")

    problems = []
    if fallacy_yes is not None and fallacy_yes > MAX_FALLACY_YES:
        problems.append(f"fallacy yes-rate {fallacy_yes:.2f} > {MAX_FALLACY_YES}")
    if low_mass / len(recs) > MAX_LOW_MASS:
        problems.append(f"{low_mass / len(recs):.0%} of items have yes/no mass < 0.5 (limit {MAX_LOW_MASS:.0%})")
    best["reliability"] = "no stable logic" if problems else "ok"
    if problems:
        out.append(f"**No stable logic.** {'; '.join(problems).capitalize()}. The model barely separates valid from "
                   "invalid items, so the logic rankings above mostly track noise and do not show that the model "
                   "has any of these consequence relations.\n")

    mean = {s: sum(r["p_yes"] for r in recs if r["schema"] == s) / max(1, sum(r["schema"] == s for r in recs))
            for s in ALL_SCHEMATA if any(r["schema"] == s for r in recs)}
    if "disjunction_introduction" in mean:
        out += chain_section(mean)
    elif mean.get("disjunctive_syllogism", 0) > 0.5 > mean.get("explosion", 1):
        out.append(f"**Structural anomaly.** Accepts disjunctive syllogism (mean P(yes) {mean['disjunctive_syllogism']:.2f}) "
                   f"but rejects explosion ({mean['explosion']:.2f}). No candidate logic gives this pattern. Explosion "
                   "follows from ∨-introduction, disjunctive syllogism and chaining, so if the model also accepts "
                   "∨-introduction its inferences are not transitive, and no Tarskian consequence relation fits.\n")
    return out, best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scores", nargs="+")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    sections, summary = [], []
    for path in args.scores:
        name = os.path.basename(path).removeprefix("scores__").removesuffix(".jsonl")
        recs = [json.loads(line) for line in open(path, encoding="utf-8")]
        sec, best = model_section(name, recs)
        sections += sec
        cf, al = best["conditional-free (primary)"], best["all schemata (QL excluded)"]
        summary.append(f"| {name} | {cf[0]} | {cf[1]} | {al[0]} | {al[1]} | {best['reliability']} |")

    report = ["# Pilot results: logic profiles of local LLMs\n",
              "Generated by `battery/fit.py`. Responses binarised at P(yes) = 0.5. Bayes factors treat items as",
              "independent, but items within a schema share one gold verdict, so they overstate confidence;",
              "the held-out-schema column is the more conservative comparison.\n",
              "**Explosion caveat.** Among conditional-free schemata, only explosion and disjunctive syllogism",
              "separate CL from LP: CL validates both, LP neither. A model that answers \"no\" to explosion gains",
              "on LP (and FDE) relative to CL, but that \"no\" more likely reflects a relevance or pragmatic",
              "judgement (the conclusion is unrelated to the premises) or reluctance to reason from contradictory",
              "premises than a paraconsistent consequence relation. A model that rejects explosion but accepts",
              "disjunctive syllogism fits neither CL nor LP, and CL and LP then tie. Do not read an LP win or a",
              "CL/LP tie as paraconsistency unless disjunctive syllogism is rejected too.\n",
              "## Summary: best-fitting logic\n",
              f"Logics within {TIE_NATS:g} nat of the best log ML are listed as a tie. \"Held-out\" is the best logic by",
              "held-out-schema log-likelihood; where it differs from the ML winner, neither should be reported as the",
              f"model's logic. Reliability is \"no stable logic\" when fallacy yes-rate > {MAX_FALLACY_YES} or more than",
              f"{MAX_LOW_MASS:.0%} of items have yes/no mass < 0.5 (provisional thresholds, not preregistered).\n",
              "| Model | Cond.-free: ML | Cond.-free: held-out | All (no QL): ML | All: held-out | Reliability |",
              "|---|---|---|---|---|---|", *summary, "", *sections]
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(report) + "\n")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
