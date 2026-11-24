"""Generate battery items as JSONL, each with a gold verdict per logic.

Usage: python generate.py [--per-cell N] [--seed S] [--out items.jsonl]

Items cross schema x content (everyday / nonsense / symbolic) x framing.
Gold verdicts come from logics.verdicts(), never from hand labels.

Pragmatic controls (off by default, so the pilot battery output is unchanged):
--related adds a "related" content type in which every atom is about the same subject, so the
conclusion of explosion is on topic rather than a non sequitur; --formal adds a "formal" framing
that states the classical definition of validity before asking.
"""

import argparse
import json
import random

from logics import verdicts
from schemata import ALL_SCHEMATA, SCHEMATA

CONTENT = {
    "everyday": [
        "the shop is open", "it is raining", "the train is late", "the kettle is on",
        "Anna is at home", "the door is locked", "the lights are off", "the bus has left",
        "the garden is wet", "the meeting was cancelled", "the dog is asleep", "the oven is hot",
        "the letter has arrived", "the road is closed", "the window is open",
    ],
    "nonsense": [
        "the blicket is wuggy", "the dax is florp", "every tove is mimsy", "the zorp has glimmed",
        "the fendle is brask", "the wug is tarvy", "the snarp is quallish", "the morb is plinty",
        "the gorp has drabbled", "the vint is skeely", "the plome is frabbic", "the yerk is dwindly",
        "the cronk has spaffled", "the lusk is tibbous", "the nib is grovish",
    ],
    "symbolic": ["P", "Q", "R"],
}
# "related" content: each instance draws one subject and three of its predicates, so A, B and C share a topic.
RELATED_TOPICS = {
    "the shop": ["is open", "is busy", "sells bread", "has a queue outside", "is lit up"],
    "the train": ["is late", "is crowded", "has left the station", "stops at Leeds", "is cancelled"],
    "the kettle": ["is on", "is full", "has boiled", "is hot", "is plugged in"],
    "the door": ["is locked", "is open", "is painted red", "has a bell", "is made of oak"],
    "the garden": ["is wet", "is in flower", "has been mown", "is fenced", "gets the morning sun"],
    "the dog": ["is asleep", "is hungry", "is in the garden", "has been walked", "is barking"],
    "the oven": ["is hot", "is switched off", "is clean", "has a cake in it", "is preheated"],
    "the road": ["is closed", "is icy", "is busy", "has been resurfaced", "leads to the coast"],
}
SYMBOL_POOL = list("PQRSTUVW")  # letters for extra symbolic instances (--symbolic-per-cell > 1)

# {clause}: conclusion embedded mid-sentence; {sentence}: conclusion as a standalone sentence.
FRAMINGS = {
    "follows": "Premises: {premises}\nDoes the following conclusion follow from the premises? {sentence}\nAnswer yes or no.",
    "must_be_true": "Suppose the following are all true: {premises}\nMust it then be true that {clause}? Answer yes or no.",
    "valid": "Consider this argument.\n{premises}\nTherefore, {clause}.\nIs this argument logically valid? Answer yes or no.",
}
FORMAL_FRAMING = {
    # Definition after the argument and "Reply with one word": with the definition first, qwen2.5:7b restated it
    # as a question instead of answering (yes/no first-token mass 0.01-0.09; see the explosion-pragmatics NOTES).
    "formal": "Premises: {premises}\nConclusion: {sentence}\nIn deductive logic, an argument is valid if and only if "
              "there is no possible situation in which all of its premises are true and its conclusion is false. "
              "By that definition, is this argument valid? Reply with one word. Answer yes or no.",
}
THEOREM_FRAMINGS = {
    "follows": "Does the following follow from no premises at all (is it a logical truth)? {sentence}\nAnswer yes or no.",
    "must_be_true": "Must it be true that {clause}? Answer yes or no.",
    "valid": "Is the following statement logically valid (true in virtue of logic alone)? {sentence}\nAnswer yes or no.",
}


def render(f, names, symbolic):
    op = f[0]
    if op == "var":
        return names[f[1]]
    r = lambda g: render(g, names, symbolic)  # noqa: E731
    if symbolic:
        sym = {"and": "∧", "or": "∨", "imp": "→"}
        return f"¬{r(f[1])}" if op == "not" else f"({r(f[1])} {sym[op]} {r(f[2])})"
    if op == "not":
        return f"it is not the case that {r(f[1])}"
    if op == "and":
        return f"both {r(f[1])} and {r(f[2])}"
    if op == "or":
        return f"either {r(f[1])} or {r(f[2])}"
    if op == "imp":
        return f"if {r(f[1])}, then {r(f[2])}"
    raise ValueError(op)


def clause(f, names, symbolic):
    s = render(f, names, symbolic)
    return s[1:-1] if symbolic and s.startswith("(") and s.endswith(")") else s


def sentence(f, names, symbolic):
    s = clause(f, names, symbolic)
    return s if symbolic else s[0].upper() + s[1:] + "."


def related_letters(rng):
    subject = rng.choice(sorted(RELATED_TOPICS))
    return [f"{subject} {pred}" for pred in rng.sample(RELATED_TOPICS[subject], 3)]


def make_items(per_cell, seed, symbolic_per_cell=1, schemata=None, related=False, formal=False):
    rng = random.Random(seed)
    sym_rng = random.Random(seed + 1)  # separate stream so default output is unchanged
    rel_rng = random.Random(seed + 2)
    content_types = dict(CONTENT, related=None) if related else CONTENT
    items = []
    for schema in (schemata or SCHEMATA):
        premises, conclusion = ALL_SCHEMATA[schema]
        gold = verdicts(premises, conclusion)
        for content, pool in content_types.items():
            symbolic = content == "symbolic"
            n = symbolic_per_cell if symbolic else per_cell
            seen = set()
            for _ in range(50 * n):  # bounded retries; schemata with few atoms have few distinct instances
                if len(seen) == n:
                    break
                if symbolic:
                    letters = pool if not seen else sym_rng.sample(SYMBOL_POOL, 3)
                elif content == "related":
                    letters = related_letters(rel_rng)
                else:
                    letters = rng.sample(pool, 3)
                names = dict(zip("ABC", letters))
                prem = (", " if symbolic else " ").join(sentence(p, names, symbolic) for p in premises)
                fields = {"premises": prem, "clause": clause(conclusion, names, symbolic),
                          "sentence": sentence(conclusion, names, symbolic)}
                key = (prem, fields["clause"])
                if key in seen:
                    continue
                k = len(seen)
                seen.add(key)
                templates = (dict(FRAMINGS, **FORMAL_FRAMING) if formal else FRAMINGS) if premises else THEOREM_FRAMINGS
                for framing, tpl in templates.items():
                    items.append({
                        "id": f"{schema}/{content}/{k}/{framing}",
                        "schema": schema,
                        "content": content,
                        "framing": framing,
                        "prompt": tpl.format(**fields),
                        "gold": gold,
                    })
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-cell", type=int, default=20, help="instances per schema x non-symbolic content")
    ap.add_argument("--symbolic-per-cell", type=int, default=1, help="instances per schema in symbolic notation")
    ap.add_argument("--schemata", nargs="+", choices=list(ALL_SCHEMATA), help="only these schemata (default: the pilot battery)")
    ap.add_argument("--content", nargs="+", choices=[*CONTENT, "related"], help="only these content types (default: all)")
    ap.add_argument("--related", action="store_true", help="add the topically related content type (pragmatic control)")
    ap.add_argument("--formal", action="store_true", help="add the framing with an explicit definition of validity")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="items.jsonl")
    args = ap.parse_args()
    items = make_items(args.per_cell, args.seed, args.symbolic_per_cell, args.schemata,
                       args.related, args.formal)
    if args.content:
        items = [it for it in items if it["content"] in args.content]
    with open(args.out, "w", encoding="utf-8") as fh:
        for it in items:
            fh.write(json.dumps(it, ensure_ascii=False) + "\n")
    print(f"wrote {len(items)} items to {args.out}")


if __name__ == "__main__":
    main()
