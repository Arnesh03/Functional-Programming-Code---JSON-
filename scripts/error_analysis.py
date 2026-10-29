#!/usr/bin/env python3
"""Break the aggregate scores down into the errors they are made of.

An aggregate says *how much* is wrong. This says *what* is wrong: whether depth errors are
over- or under-counts, how the error grows with true depth, which block kinds show up in
mis-counted scopes, and whether relation and generator failures are recall or precision.

    python3 scripts/error_analysis.py
    python3 scripts/error_analysis.py --model qwen3     # a different run's predictions
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import PREDS_DIR  # noqa: E402


def load_pairs(model: str):
    pairs = []
    for d in sorted(glob.glob(str(PREDS_DIR / "*"))):
        gold_p = os.path.join(d, "gold.json")
        preds = sorted(glob.glob(os.path.join(d, f"*{model}*pred.json")))
        if os.path.exists(gold_p) and preds:
            pairs.append((json.load(open(preds[-1])), json.load(open(gold_p))))
    return pairs


def triples(record):
    by = {s["scope_id"]: s["name"] for s in record.get("scopes", [])}
    return {(r.get("relation_type"), by.get(r.get("from_scope")), by.get(r.get("to_scope")))
            for r in record.get("relations", [])}


def main() -> None:
    ap = argparse.ArgumentParser(description="Error breakdown over stored predictions")
    ap.add_argument("--model", default="gpt-oss", help="substring of the prediction filename")
    args = ap.parse_args()

    pairs = load_pairs(args.model)
    if not pairs:
        sys.exit(f"no prediction/gold pairs matching {args.model!r} under {PREDS_DIR}")
    print(f"{len(pairs)} prediction/gold pairs matching {args.model!r}\n")

    signed, by_truth = [], collections.defaultdict(list)
    kinds_wrong, kinds_right = collections.Counter(), collections.Counter()
    gen_missed, gen_invented = [], []
    rel_missed, rel_invented = collections.Counter(), collections.Counter()

    for pred, gold in pairs:
        P = {s["name"]: s for s in pred.get("scopes", [])}
        G = {s["name"]: s for s in gold.get("scopes", [])}
        for n in set(P) & set(G):
            c = int(P[n].get("max_block_depth") or 0)
            t = int(G[n].get("max_block_depth") or 0)
            if c or t:
                signed.append(c - t)
                by_truth[t].append(c - t)
                for k in G[n].get("block_kinds") or []:
                    (kinds_wrong if c != t else kinds_right)[k] += 1
            if bool(P[n].get("is_generator")) != bool(G[n].get("is_generator")):
                (gen_missed if G[n].get("is_generator") else gen_invented).append(n)
        tp_, tg = triples(pred), triples(gold)
        for t in tg - tp_:
            rel_missed[t[0]] += 1
        for t in tp_ - tg:
            rel_invented[t[0]] += 1

    hist = collections.Counter(signed)
    print(f"=== DEPTH · {len(signed)} scopes ===")
    for d in sorted(hist):
        print(f"  {d:+3d} levels : {hist[d]:4d}  {'#' * min(60, hist[d] // 2)}")
    under = sum(v for k, v in hist.items() if k < 0)
    over = sum(v for k, v in hist.items() if k > 0)
    print(f"  exact {hist[0]}/{len(signed)} = {hist[0]/len(signed):.4f} · "
          f"under {under} · over {over}")
    print(f"  mean signed {statistics.mean(signed):+.3f} · "
          f"mean |error| {statistics.mean(abs(x) for x in signed):.3f}")

    print("\n=== DEPTH ERROR vs TRUE DEPTH ===")
    for t in sorted(by_truth):
        v = by_truth[t]
        if len(v) >= 4:
            print(f"  true depth {t:2d}: n={len(v):3d}  exact={sum(1 for x in v if x == 0)/len(v):.2f}"
                  f"  mean signed={statistics.mean(v):+.2f}")

    print("\n=== BLOCK KINDS in mis-counted vs correct scopes ===")
    for k in sorted(set(kinds_wrong) | set(kinds_right),
                    key=lambda x: -(kinds_wrong[x] + kinds_right[x])):
        w, r = kinds_wrong[k], kinds_right[k]
        if w + r >= 10:
            print(f"  {k:10s} wrong={w:4d} right={r:4d}  error rate={w/(w+r):.2f}")

    print(f"\n=== GENERATORS ===  missed {len(gen_missed)} · invented {len(gen_invented)}")
    print(f"  most-missed names: {[n for n, _ in collections.Counter(gen_missed).most_common(6)]}")

    print("\n=== RELATIONS by type ===")
    for t in sorted(set(rel_missed) | set(rel_invented)):
        print(f"  {str(t):20s} missed={rel_missed[t]:3d} invented={rel_invented[t]:3d}")


if __name__ == "__main__":
    main()
