"""Score battery items with a local Ollama model: P(yes) from first-token log-probabilities (section 3.2).

Usage: python score.py --model qwen2.5:7b-instruct --items items.jsonl --out scores.jsonl [--limit N]

Each item is scored twice, with the answer order "yes or no" and "no or yes", and averaged.
P(yes) = mass on yes-tokens / (mass on yes-tokens + mass on no-tokens) among the top-20 first tokens.
Requires an Ollama server with logprobs support on localhost:11434.
"""

import argparse
import hashlib
import json
import math
import time
import urllib.request

URL = "http://127.0.0.1:11434/api/chat"
OPTIONS = {"num_predict": 1, "temperature": 0}
TOP_LOGPROBS = 20


def model_digest(model):
    """Digest of the exact weights Ollama serves under this tag (tags like llama3.1:latest move)."""
    req = urllib.request.Request(URL.replace("/api/chat", "/api/tags"))
    with urllib.request.urlopen(req, timeout=60) as r:
        for m in json.load(r)["models"]:
            if m["name"] == model or m["model"] == model:
                return m["digest"]
    return None


def p_yes(model, prompt, think, num_thread=None):
    body = {"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False,
            "logprobs": True, "top_logprobs": TOP_LOGPROBS, "options": dict(OPTIONS)}
    if num_thread:
        body["options"]["num_thread"] = num_thread
    if think is not None:
        body["think"] = think
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        top = json.load(r)["logprobs"][0]["top_logprobs"]
    y = sum(math.exp(t["logprob"]) for t in top if t["token"].strip().lower() == "yes")
    n = sum(math.exp(t["logprob"]) for t in top if t["token"].strip().lower() == "no")
    return (y / (y + n) if y + n > 0 else None), y + n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--items", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--no-think", action="store_true", help="send think=false (for reasoning models)")
    ap.add_argument("--num-thread", type=int, default=None, help="llama.cpp CPU threads (set low on CPU-limited pods)")
    args = ap.parse_args()
    think = False if args.no_think else None

    items = [json.loads(line) for line in open(args.items, encoding="utf-8")][: args.limit]
    meta = {"model": args.model, "digest": model_digest(args.model), "options": OPTIONS, "top_logprobs": TOP_LOGPROBS,
            "think": think, "num_thread": args.num_thread, "items": args.items,
            "items_sha256": hashlib.sha256(open(args.items, "rb").read()).hexdigest(), "n_items": len(items),
            "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "prompt_template": "item['prompt'], and again with 'Answer yes or no.' -> 'Answer no or yes.'"}
    with open(args.out.removesuffix(".jsonl") + ".meta.json", "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
    start = time.time()
    with open(args.out, "w", encoding="utf-8") as fh:
        for i, it in enumerate(items):
            p1, m1 = p_yes(args.model, it["prompt"], think, args.num_thread)
            p2, m2 = p_yes(args.model, it["prompt"].replace("Answer yes or no.", "Answer no or yes."), think, args.num_thread)
            ps = [p for p in (p1, p2) if p is not None]
            rec = {k: it[k] for k in ("id", "schema", "content", "framing", "gold")}
            rec.update(p_yes=sum(ps) / len(ps) if ps else None, p_yes_order=[p1, p2], answer_mass=[m1, m2])
            fh.write(json.dumps(rec) + "\n")
            if (i + 1) % 100 == 0:
                el = time.time() - start
                print(f"{i + 1}/{len(items)} items, {el:.0f}s elapsed, ~{el / (i + 1) * (len(items) - i - 1):.0f}s left", flush=True)
    print(f"done: {len(items)} items -> {args.out}")


if __name__ == "__main__":
    main()
