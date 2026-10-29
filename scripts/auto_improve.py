#!/usr/bin/env python3
"""Self-improvement loop for the code-extraction lane.

Each round: measure on the dev split → mine the failures into corrected examples and rules →
re-measure with them → keep the new working memory ONLY if it scores better on a test split that
is never used for tuning. A gain on dev alone is memorisation of the mined examples, so a tie on
the held-out split is a rejection. Accepted versions are written to
`assets/eval/learned_hints.json`, which the prompts read on the next run: no retraining involved.

    python3 scripts/auto_improve.py --rounds 2 --dev 10 --test 10
    python3 scripts/auto_improve.py --report-only

Ported from the OPORD build's `scripts/auto_improve.py`. What is mined differs, because what a
code extraction gets wrong differs: scope, kind and parent are already perfect, so the loop goes
after nesting depth, the generator flag, and invented or missed call edges.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import learned_hints  # noqa: E402
from app.config import DATASET_DIR, MANIFEST_JSONL, METRICS_DIR  # noqa: E402
from app.evaluate import aggregate  # noqa: E402
from app.pipeline import run_pipeline_for_file  # noqa: E402

HISTORY_PATH = ROOT / "assets" / "eval" / "improve_history.jsonl"
MAX_MINED_EXAMPLES = 3


def log(msg: str) -> None:
    print(msg, flush=True)


# ──────────────────────────────────────────────────────────── splits
def make_splits(dev_size: int, test_size: int, seed: int) -> dict:
    """Disjoint dev and test slices. Asking for different sizes invalidates earlier baselines."""
    rows = [json.loads(l) for l in MANIFEST_JSONL.read_text().splitlines() if l.strip()]
    pool = [r for r in rows if r.get("split") in ("train", "val")]
    held = [r for r in rows if r.get("split") == "test"]
    rng = random.Random(seed)
    dev = rng.sample(pool, min(dev_size, len(pool)))
    test = rng.sample(held, min(test_size, len(held)))
    return {"dev": dev, "test": test}


# ──────────────────────────────────────────────────────────── measure
def measure(rows: list, label: str, strategy: str) -> dict:
    """Run the pipeline over a split and return the aggregate plus the raw results for mining."""
    log(f"   measuring {label} ({len(rows)} files)…")
    scores, results = [], []
    for i, row in enumerate(rows, 1):
        try:
            res = run_pipeline_for_file(row["id"], save=False, strategy=strategy)
        except Exception as exc:
            log(f"      {row['id']}: FAILED {type(exc).__name__}: {exc}")
            continue
        scores.append(res["score"])
        results.append(res)
        log(f"      [{i}/{len(rows)}] {row['id']}  depth_exact="
            f"{res['score']['max_block_depth']['exact_rate']:.2f}  "
            f"overall={res['score']['overall']:.3f}")
    agg = aggregate(scores)
    return {"aggregate": agg, "results": results}


# ──────────────────────────────────────────────────────────── mine
def _source_slice(file_id: str, start: int, end: int) -> str:
    hits = sorted(DATASET_DIR.glob(f"{file_id}*.py"))
    if not hits:
        return ""
    lines = hits[0].read_text(encoding="utf-8", errors="ignore").split("\n")
    span = lines[max(0, start - 1):end]
    if len(span) > learned_hints.MAX_EXAMPLE_LINES:
        head = span[: learned_hints.MAX_EXAMPLE_LINES - 6]
        span = head + ["    # … body continues …"] + span[-5:]
    return "\n".join(span)


def mine(measured: dict, hints: dict, families: set | None = None) -> tuple:
    """Turn this round's failures into rules and corrected examples.

    `families` selects which rule kinds to write — {"depth"}, {"depth", "relation"}, etc.
    Isolating them matters: on the CodeComplex run the depth rule improved the held-out split
    while the relation rule cost more than depth gained, and a combined candidate hides that.
    """
    families = families or {"depth", "flag", "relation"}
    depth_errs, gen_errs, rel_spurious, rel_missed = [], [], 0, 0

    for res in measured["results"]:
        pred = {s["name"]: s for s in res["record"].get("scopes", [])}
        gold = {s["name"]: s for s in res["gold"].get("scopes", [])}
        for name in sorted(set(pred) & set(gold)):
            p, g = pred[name], gold[name]
            claimed, truth = int(p.get("max_block_depth") or 0), int(g.get("max_block_depth") or 0)
            if claimed != truth and truth > 0:
                depth_errs.append({
                    "file_id": res["file_id"], "name": name,
                    "claimed": claimed, "truth": truth, "delta": claimed - truth,
                    "start": int(g.get("start_line") or 0), "end": int(g.get("end_line") or 0),
                    "block_kinds": list(g.get("block_kinds") or []),
                })
            if bool(p.get("is_generator")) != bool(g.get("is_generator")):
                gen_errs.append({"name": name, "claimed": bool(p.get("is_generator")),
                                 "truth": bool(g.get("is_generator"))})

        def triples(rec):
            by_id = {s["scope_id"]: s["name"] for s in rec.get("scopes", [])}
            return {(r.get("relation_type"), by_id.get(r.get("from_scope"), r.get("from_scope")),
                     by_id.get(r.get("to_scope"), r.get("to_scope")))
                    for r in rec.get("relations", [])}
        tp, tg = triples(res["record"]), triples(res["gold"])
        rel_spurious += len(tp - tg)
        rel_missed += len(tg - tp)

    notes, candidate = [], {**hints}
    depth_rules, flag_rules, relation_rules, examples = [], [], [], []

    if depth_errs and "depth" in families:
        deltas = [e["delta"] for e in depth_errs]
        mean_delta = statistics.mean(deltas)
        direction = "under" if mean_delta < 0 else "over"
        depth_rules.append(
            f"You are {direction}counting max_block_depth by {abs(mean_delta):.1f} levels on "
            f"average ({len(depth_errs)} scopes wrong this round). Count the longest chain of "
            f"nested for / while / if / try / with / match by following the indentation down to "
            f"the deepest statement, not by counting distinct constructs.")
        depth_rules.append(
            "An `elif` is nested one level deeper than the `if` it follows, and an `except`, "
            "`else` or `finally` is one level deeper than its `try`. Deep branch ladders are "
            "where the count is most often missed.")
        notes.append(f"{len(depth_errs)} depth errors, mean delta {mean_delta:+.2f}")

        worst = sorted(depth_errs, key=lambda e: -abs(e["delta"]))[:MAX_MINED_EXAMPLES]
        for e in worst:
            src = _source_slice(e["file_id"], e["start"], e["end"])
            if not src:
                continue
            examples.append({
                "source": src,
                "correct": {"name": e["name"], "max_block_depth": e["truth"],
                            "block_kinds": e["block_kinds"]},
                "note": f"you said depth {e['claimed']}, the parser says {e['truth']}",
            })

    if gen_errs and "flag" in families:
        missed = sum(1 for e in gen_errs if e["truth"] and not e["claimed"])
        flag_rules.append(
            f"is_generator was wrong on {len(gen_errs)} scopes this round"
            f"{f' ({missed} were generators you missed)' if missed else ''}. It is true whenever "
            f"the body contains `yield` or `yield from` anywhere, however deeply nested — "
            f"including inside a `try`, a `with`, or a loop.")
        notes.append(f"{len(gen_errs)} generator-flag errors")

    if (rel_spurious or rel_missed) and "relation" in families:
        relation_rules.append(
            f"Relations this round: {rel_spurious} invented, {rel_missed} missed. Record a call "
            f"only when the target is a function or class defined in this same file; ignore "
            f"len, range, print, int, isinstance, enumerate, sorted and anything imported. "
            f"Do not omit a call just because it appears inside a nested block.")
        notes.append(f"relations: {rel_spurious} invented, {rel_missed} missed")

    candidate["depth_rules"] = depth_rules or hints.get("depth_rules") or []
    candidate["flag_rules"] = flag_rules or hints.get("flag_rules") or []
    candidate["relation_rules"] = relation_rules or hints.get("relation_rules") or []
    if examples:
        candidate["examples"] = examples
    return candidate, notes


# ──────────────────────────────────────────────────────────── history
def append_history(entry: dict) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with HISTORY_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def report() -> None:
    if not HISTORY_PATH.exists():
        log("No rounds recorded yet.")
        return
    log(f"{'round':>6}  {'dev':>7}  {'test':>7}  decision")
    for line in HISTORY_PATH.read_text().splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        log(f"{str(e.get('round', '-')):>6}  {e.get('dev_score', 0):>7.4f}  "
            f"{e.get('test_score', 0):>7.4f}  {e.get('decision', '')}")


# ──────────────────────────────────────────────────────────── driver
def main() -> None:
    ap = argparse.ArgumentParser(description="Mine failures into prompt hints, keep only what generalises")
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--dev", type=int, default=10, help="files used to measure and to mine failures")
    ap.add_argument("--test", type=int, default=10, help="held out; only used to confirm an improvement")
    ap.add_argument("--strategy", default="multicall", choices=["single", "multicall"])
    ap.add_argument("--seed", type=int, default=21)
    ap.add_argument("--rules", default="depth,flag,relation",
                    help="which rule families to mine: any of depth,flag,relation")
    ap.add_argument("--report-only", action="store_true")
    args = ap.parse_args()

    if args.report_only:
        return report()

    families = {f.strip() for f in args.rules.split(",") if f.strip()}
    t0 = time.time()
    splits = make_splits(args.dev, args.test, args.seed)
    log(f"dev {len(splits['dev'])} files · test {len(splits['test'])} files (held out) "
        f"· strategy {args.strategy} · rules {sorted(families)}")

    champion = learned_hints.load()
    log(f"\n=== baseline (learned hints v{champion.get('version', 0)}) ===")
    dev0 = measure(splits["dev"], "baseline on dev", args.strategy)
    test0 = measure(splits["test"], "baseline on test (held out)", args.strategy)
    dev_score = dev0["aggregate"].get("learning_score", 0.0)
    test_score = test0["aggregate"].get("learning_score", 0.0)
    log(f"   baseline: dev {dev_score:.4f} · test {test_score:.4f}")
    append_history({"round": 0, "dev_score": dev_score, "test_score": test_score,
                    "decision": "baseline"})

    last_dev = dev0
    for rnd in range(1, args.rounds + 1):
        log(f"\n=== round {rnd} ===")
        candidate, notes = mine(last_dev, champion, families)
        if not notes:
            log("   nothing left to mine — every scope matched. Stopping.")
            break
        for n in notes:
            log(f"   mined: {n}")

        learned_hints.write_candidate(candidate)
        cand_dev = measure(splits["dev"], f"round {rnd} candidate on dev", args.strategy)
        cand_dev_score = cand_dev["aggregate"].get("learning_score", 0.0)
        log(f"   candidate dev {cand_dev_score:.4f} (was {dev_score:.4f})")

        cand_test = measure(splits["test"], f"round {rnd} candidate on test (held out)", args.strategy)
        cand_test_score = cand_test["aggregate"].get("learning_score", 0.0)

        # A gain on dev alone is memorisation of the mined examples, so a tie on the held-out
        # split is a rejection, not an acceptance.
        if cand_test_score > test_score:
            champion = learned_hints.save({**candidate, "scores": {
                "dev": cand_dev_score, "test": cand_test_score}})
            log(f"   ACCEPTED as hints v{champion['version']}: "
                f"held-out {test_score:.4f} → {cand_test_score:.4f}")
            dev_score, test_score, last_dev = cand_dev_score, cand_test_score, cand_dev
            append_history({"round": rnd, "dev_score": cand_dev_score, "test_score": cand_test_score,
                            "decision": f"accepted as hints v{champion['version']}"})
        else:
            learned_hints.write_candidate(champion)   # roll back
            log(f"   rejected: held-out {cand_test_score:.4f} is not better than "
                f"{test_score:.4f} — rolled back to v{champion.get('version', 0)}")
            append_history({"round": rnd, "dev_score": cand_dev_score, "test_score": cand_test_score,
                            "decision": "rejected on held-out test"})
            break

    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    log(f"\nfinished in {(time.time() - t0) / 60:.1f} min · "
        f"hints v{learned_hints.version()} · history: {HISTORY_PATH}")


if __name__ == "__main__":
    main()
