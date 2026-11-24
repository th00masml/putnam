"""Compute every number in the preprint from the score files and write paper/tables.tex.

Usage (from the repo root): python paper/make_tables.py
Means are over items (P(yes) averaged over both answer orders). 95% intervals are percentile bootstrap
intervals over instances (one instance = one schema x content x sentence choice, all its framings together),
2000 resamples, seed 0.
"""

import glob
import json
import os
import random
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "battery"))
from fit import FALLACIES, MAX_FALLACY_YES, MAX_LOW_MASS, YES_CUT  # noqa: E402
from logics import verdicts  # noqa: E402
from mcs import mcs_verdicts, split_universal  # noqa: E402
from schemata import ALL_SCHEMATA  # noqa: E402

RUNS = os.path.join(ROOT, "runs")
FOLLOWUPS = ["2026-11-24__explosion-pragmatics", "2026-10-14__explosion-chain",
             "2026-11-24__inconsistent-premises", "2026-11-24__mcs-inference"]
MODELS = ["qwen2.5_7b-instruct", "gemma3_12b", "hermes3_8b", "mistral_7b"]
NAMES = {"qwen2.5_7b-instruct": "qwen2.5:7b-instruct", "gemma3_12b": "gemma3:12b", "hermes3_8b": "hermes3:8b",
         "mistral_7b": "mistral:7b", "llama3.1_latest": "llama3.1:latest", "qwen2.5_14b": "qwen2.5:14b",
         "qwen3-coder_30b": "qwen3-coder:30b", "qwen3.5_9b": "qwen3.5:9b", "qwen3.8_27b": "qwen3.8:27b"}
PROFILE = [  # schema, LaTeX form
    ("modus_ponens", r"$A, A\to B \vdash B$"),
    ("disjunctive_syllogism", r"$A\lor B, \neg A \vdash B$"),
    ("double_ds", r"$A\lor B, \neg A, \neg B\lor C \vdash C$"),
    ("disjunction_introduction", r"$A \vdash A\lor B$"),
    ("conjunction_elimination", r"$A\land C \vdash C$"),
    ("identity_consistent", r"$A, C \vdash C$"),
    ("explosion", r"$A, \neg A \vdash B$"),
    ("identity_inconsistent", r"$A, \neg A \vdash A$"),
    ("adjunction_inconsistent", r"$A, \neg A \vdash A\land\neg A$"),
    ("disjunction_introduction_inconsistent", r"$A, \neg A \vdash A\lor B$"),
    ("explosion_lemma", r"$A, \neg A, A\lor B \vdash B$"),
    ("bystander_inconsistent", r"$A, \neg A, C \vdash C$"),
    ("shared_conjunct", r"$A\land C, C\land\neg A \vdash C$"),
    ("clean_conjunct", r"$A\land C, \neg A \vdash C$"),
]


def load(run, model):
    path = os.path.join(RUNS, run, f"scores__{model}.jsonl")
    if not os.path.exists(path):
        return []
    recs = [json.loads(line) for line in open(path, encoding="utf-8")]
    for r in recs:
        r["run"] = run
    return [r for r in recs if r["p_yes"] is not None]


def mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def boot_ci(recs, n=2000, seed=0):
    units = defaultdict(list)
    for r in recs:
        schema, content, k, _ = r["id"].split("/")
        units[(r["run"], schema, content, k)].append(r["p_yes"])
    keys = list(units)
    rng = random.Random(seed)
    stats = []
    for _ in range(n):
        sample = [x for key in rng.choices(keys, k=len(keys)) for x in units[key]]
        stats.append(mean(sample))
    stats.sort()
    return stats[int(0.025 * n)], stats[int(0.975 * n) - 1]


def reliability(recs):
    fal = [r["p_yes"] for r in recs if r["schema"] in FALLACIES]
    fal_yes = mean(fal) if fal else None
    low = sum(min(r["answer_mass"]) < 0.5 for r in recs) / len(recs)
    ok = (fal_yes is None or fal_yes <= MAX_FALLACY_YES) and low <= MAX_LOW_MASS
    return fal_yes, low, ok


def yn(b):
    return r"\checkmark" if b else r"$\times$"


def fmt(x):
    return f"{x:.2f}"


def table_pilot():
    run = "2026-10-11__pilot-ollama"
    models = sorted(os.path.basename(p)[8:-6] for p in glob.glob(os.path.join(RUNS, run, "scores__*.jsonl")))
    rows = []
    for m in models:
        recs = load(run, m)
        ds = mean([r["p_yes"] for r in recs if r["schema"] == "disjunctive_syllogism"])
        ex = mean([r["p_yes"] for r in recs if r["schema"] == "explosion"])
        fal, low, ok = reliability(recs)
        rows.append(f"{NAMES.get(m, m)} & {fmt(ds)} & {fmt(ex)} & {fmt(fal)} & {low:.0%} & {'ok' if ok else 'unstable'} \\\\")
    return "\n".join([
        r"\begin{table}[t]\centering\small",
        r"\caption{Pilot (exploratory): mean $P(\text{yes})$ on disjunctive syllogism (DS) and explosion over all content types and framings, "
        r"yes-rate on the two fallacies, share of items with yes/no first-token mass $<0.5$, and the reliability verdict.}",
        r"\label{tab:pilot}",
        r"\begin{tabular}{lrrrrl}\toprule",
        r"Model & DS & Explosion & Fallacy yes & Low mass & Reliability \\\midrule",
        *[x.replace("%", r"\%") for x in rows],
        r"\bottomrule\end{tabular}\end{table}"])


def table_pragmatics():
    run = "2026-11-24__explosion-pragmatics"
    rows = []
    for m in MODELS + ["llama3.1_latest"]:
        recs = load(run, m)
        ex = [r for r in recs if r["schema"] == "explosion"]
        cells = [mean([r["p_yes"] for r in ex if r["content"] == "everyday" and r["framing"] != "formal"]),
                 mean([r["p_yes"] for r in ex if r["content"] == "related" and r["framing"] != "formal"]),
                 mean([r["p_yes"] for r in ex if r["framing"] == "formal"])]
        fal, low, ok = reliability(recs)
        rows.append(f"{NAMES[m]} & " + " & ".join(fmt(c) for c in cells)
                    + f" & {fmt(fal)} & {low:.0%} & {'ok' if ok else 'unstable'} \\\\")
    return "\n".join([
        r"\begin{table}[t]\centering\small",
        r"\caption{Pragmatic controls: mean $P(\text{yes})$ on explosion with unrelated (everyday) and topically related atoms "
        r"under the three default framings, and under the framing that states the classical definition of validity (both contents). "
        r"Fallacy yes-rate, low-mass share and reliability are over the whole run.}",
        r"\label{tab:pragmatics}",
        r"\begin{tabular}{lrrrrrl}\toprule",
        r"Model & Unrelated & Related & Formal & Fallacy yes & Low mass & Reliability \\\midrule",
        *[x.replace("%", r"\%") for x in rows],
        r"\bottomrule\end{tabular}\end{table}"])


def table_profile():
    data = {m: [r for run in FOLLOWUPS for r in load(run, m)] for m in MODELS}
    cands = {
        "CL": lambda p, c: verdicts(p, c)["CL"],
        "LP": lambda p, c: verdicts(p, c)["LP"],
        "MCS-U": lambda p, c: mcs_verdicts(p, c)["universal"],
        "Split": split_universal,
    }
    lines, mism = [], {m: defaultdict(int) for m in MODELS}
    for s, form in PROFILE:
        p, c = ALL_SCHEMATA[s]
        preds = {k: f(p, c) for k, f in cands.items()}
        cells = []
        for m in MODELS:
            recs = [r for r in data[m] if r["schema"] == s]
            mu = mean([r["p_yes"] for r in recs])
            for k, v in preds.items():
                mism[m][k] += (mu > YES_CUT) != v
            if m == MODELS[0]:
                lo, hi = boot_ci(recs)
                cells.append(f"{fmt(mu)} [{fmt(lo)}, {fmt(hi)}]")
            else:
                cells.append(fmt(mu))
        lines.append(f"{form} & " + " & ".join(yn(v) for v in preds.values()) + " & " + " & ".join(cells) + r" \\")
        if s == "identity_consistent":
            lines.append(r"\midrule")
    lines.append(r"\midrule")
    for k in cands:
        lines.append(f"\\multicolumn{{5}}{{r}}{{mismatches with {k}}} & " + " & ".join(str(mism[m][k]) for m in MODELS) + r" \\")
    return "\n".join([
        r"\begin{table*}[t]\centering\small",
        r"\caption{Profile over the follow-up runs (pooled across runs where a schema recurs). Left: verdicts of classical logic, "
        r"LP, universal maximal-consistent-subset consequence (MCS-U) and MCS-U after splitting conjunctive premises (Split, "
        r"formalised post hoc). Right: mean $P(\text{yes})$; for the confirmatory model qwen2.5:7b, with a 95\% instance-bootstrap "
        r"interval. Upper block: consistent premises; lower block: inconsistent premises. Every form is classically valid; forms marked $\times$ under LP are invalid in LP and FDE, "
        r"and all others are valid in all six candidate logics. Bottom: number of schemata whose binarised mean disagrees "
        r"with each candidate.}",
        r"\label{tab:profile}",
        r"\begin{tabular}{lcccc" + "r" * len(MODELS) + r"}\toprule",
        r"Form & CL & LP & MCS-U & Split & qwen2.5:7b & gemma3 & hermes3 & mistral \\\midrule",
        *lines,
        r"\bottomrule\end{tabular}\end{table*}"])


def table_digests():
    rows = []
    for m in MODELS:
        metas = [json.load(open(p)) for run in FOLLOWUPS for p in glob.glob(os.path.join(RUNS, run, f"scores__{m}.meta.json"))]
        digests = sorted({x["digest"][:12] for x in metas if x.get("digest")})
        rows.append(f"{NAMES[m]} & \\texttt{{{', '.join(digests)}}} \\\\")
    return "\n".join([
        r"\begin{table}[h]\centering\small",
        r"\caption{Ollama model digests (first 12 hex digits) recorded for the follow-up runs.}",
        r"\label{tab:digests}",
        r"\begin{tabular}{ll}\toprule Model & Digest \\\midrule",
        *rows,
        r"\bottomrule\end{tabular}\end{table}"])


def counts():
    out = {}
    for run in FOLLOWUPS + ["2026-10-11__pilot-ollama"]:
        out[run] = sum(1 for _ in open(os.path.join(RUNS, run, "items.jsonl"), encoding="utf-8"))
    return out


if __name__ == "__main__":
    tex = "\n\n".join([table_pilot(), table_pragmatics(), table_profile()])
    head = "% Generated by paper/make_tables.py; do not edit by hand.\n"
    with open(os.path.join(ROOT, "paper", "tables.tex"), "w", encoding="utf-8") as fh:
        fh.write(head + tex + "\n")
    with open(os.path.join(ROOT, "paper", "digests.tex"), "w", encoding="utf-8") as fh:
        fh.write(head + table_digests() + "\n")
    print(tex)
    print(counts())
