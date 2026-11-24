"""Score battery items with a Claude model through the Message Batches API (proposal section 3.2, API models).

Usage:
  python score_api.py --items items.jsonl --out scores__claude-opus-5-5.jsonl --dry-run
  python score_api.py --items items.jsonl --out scores__claude-opus-5-5.jsonl

The Claude API returns no token log-probabilities and current models accept neither a temperature nor
disabled thinking, so the local first-token measure cannot be reproduced. Instead each item is sent k times
in each answer order ("Answer yes or no." / "Answer no or yes."), and:
  p_yes_order[o] = share of "yes" among the samples in order o whose reply starts with yes or no
  p_yes          = mean of the two orders
  answer_mass[o] = share of samples in order o whose reply starts with yes or no (refusals, errors and
                   other replies count against it)
so the output has the fields fit.py reads. The measure is the model's answer after its own (adaptive)
thinking, not its first-token inclination: treat API rows as a separate condition, not as another local model.

Requests run as one batch (50% price; usually under an hour, at most 24 h). The batch id is saved next to
--out, so a rerun after an interruption resumes polling instead of resubmitting.
No refusal fallbacks: a fallback would answer with a different model and mix models within one score file.
Refusals are recorded and count as non-answers.
Credentials: ANTHROPIC_API_KEY or an `ant auth login` profile.
"""

import argparse
import hashlib
import json
import os
import re
import time

YES_NO = re.compile(r"^\W*(yes|no)\b", re.IGNORECASE)
ORDERS = ("Answer yes or no.", "Answer no or yes.")


def parse(text):
    m = YES_NO.match(text or "")
    return m.group(1).lower() if m else None


def build_requests(items, model, k, effort, max_tokens):
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    reqs = []
    for i, it in enumerate(items):
        if ORDERS[0] not in it["prompt"]:
            raise SystemExit(f"item {it['id']} lacks '{ORDERS[0]}', cannot flip the answer order")
        for o, phrase in enumerate(ORDERS):
            prompt = it["prompt"].replace(ORDERS[0], phrase)
            for s in range(k):
                params = {"model": model, "max_tokens": max_tokens,
                          "messages": [{"role": "user", "content": prompt}]}
                if effort:
                    params["output_config"] = {"effort": effort}
                reqs.append(Request(custom_id=f"i{i}_o{o}_s{s}", params=MessageCreateParamsNonStreaming(**params)))
    return reqs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="claude-opus-5-5")
    ap.add_argument("--k", type=int, default=5, help="samples per item per answer order")
    ap.add_argument("--effort", default="medium", help="output_config.effort (the model's default on Opus 5.5 is medium)")
    ap.add_argument("--max-tokens", type=int, default=4000, help="thinking counts toward this")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--poll", type=int, default=60, help="seconds between status checks")
    ap.add_argument("--dry-run", action="store_true", help="print the request count and one prompt, send nothing")
    args = ap.parse_args()

    items = [json.loads(line) for line in open(args.items, encoding="utf-8")][: args.limit]
    n_req = len(items) * 2 * args.k
    state_path = args.out.removesuffix(".jsonl") + ".batch.json"
    print(f"{len(items)} items x 2 orders x k={args.k} = {n_req} requests to {args.model} (effort {args.effort})")
    if args.dry_run:
        print("--- first prompt, order 2 ---\n" + items[0]["prompt"].replace(ORDERS[0], ORDERS[1]))
        return

    import anthropic
    client = anthropic.Anthropic()

    if os.path.exists(state_path):
        state = json.load(open(state_path, encoding="utf-8"))
        print(f"resuming batch {state['batch_id']}")
    else:
        if n_req > 100_000:
            raise SystemExit("more than 100,000 requests: split the item file or lower --k")
        batch = client.messages.batches.create(requests=build_requests(items, args.model, args.k, args.effort, args.max_tokens))
        state = {"batch_id": batch.id, "model": args.model, "k": args.k, "effort": args.effort,
                 "max_tokens": args.max_tokens, "items": args.items, "n_items": len(items),
                 "items_sha256": hashlib.sha256(open(args.items, "rb").read()).hexdigest(),
                 "submitted": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "anthropic_sdk": anthropic.__version__,
                 "fallbacks": None, "temperature": "API default (not settable on this model)"}
        json.dump(state, open(state_path, "w", encoding="utf-8"), indent=2)
        print(f"submitted batch {batch.id}")

    while True:
        batch = client.messages.batches.retrieve(state["batch_id"])
        c = batch.request_counts
        print(f"{batch.processing_status}: processing {c.processing}, succeeded {c.succeeded}, errored {c.errored}, "
              f"canceled {c.canceled}, expired {c.expired}", flush=True)
        if batch.processing_status == "ended":
            break
        time.sleep(args.poll)

    answers = {}  # (item, order) -> list of "yes" / "no" / None
    outcomes = {"succeeded": 0, "refusal": 0, "errored": 0, "canceled": 0, "expired": 0, "unparsed": 0}
    usage = {"input_tokens": 0, "output_tokens": 0}
    models_served = set()
    for res in client.messages.batches.results(state["batch_id"]):
        i, o, _ = (int(x[1:]) for x in res.custom_id.split("_"))
        ans = None
        if res.result.type == "succeeded":
            msg = res.result.message
            models_served.add(msg.model)
            usage["input_tokens"] += msg.usage.input_tokens
            usage["output_tokens"] += msg.usage.output_tokens
            if msg.stop_reason == "refusal":
                outcomes["refusal"] += 1
            else:
                outcomes["succeeded"] += 1
                ans = parse(next((b.text for b in msg.content if b.type == "text"), ""))
                outcomes["unparsed"] += ans is None
        else:
            outcomes[res.result.type] += 1
        answers.setdefault((i, o), []).append(ans)

    with open(args.out, "w", encoding="utf-8") as fh:
        for i, it in enumerate(items):
            p_order, mass = [], []
            for o in range(2):
                got = answers.get((i, o), [])
                valid = [a for a in got if a is not None]
                p_order.append(sum(a == "yes" for a in valid) / len(valid) if valid else None)
                mass.append(len(valid) / args.k)
            ps = [p for p in p_order if p is not None]
            rec = {k: it[k] for k in ("id", "schema", "content", "framing", "gold")}
            rec.update(p_yes=sum(ps) / len(ps) if ps else None, p_yes_order=p_order, answer_mass=mass,
                       n_samples=args.k)
            fh.write(json.dumps(rec) + "\n")

    state.update(finished=time.strftime("%Y-%m-%dT%H:%M:%S%z"), outcomes=outcomes, usage=usage,
                 models_served=sorted(models_served))
    json.dump(state, open(args.out.removesuffix(".jsonl") + ".meta.json", "w", encoding="utf-8"), indent=2)
    print(f"done: {len(items)} items -> {args.out}; outcomes {outcomes}; tokens {usage}")


if __name__ == "__main__":
    main()
