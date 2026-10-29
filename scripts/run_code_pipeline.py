#!/usr/bin/env python3
"""Run the extraction pipeline over a slice of the nested-code dataset and report the aggregate.

Mirrors the OPORD batch evaluator: every file goes through the same pipeline a single run uses,
results are stored per file, and the run ends with one table. What is new is that scoring needs
no gold annotation — `app.gold` reads the truth out of the AST — so accuracy is reported for
every file, not just validity.

    python3 scripts/run_code_pipeline.py --count 20 --strategy multicall
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import DATASET_DIR, MANIFEST_JSONL, METRICS_DIR  # noqa: E402
from app.evaluate import aggregate  # noqa: E402
from app.pipeline import run_pipeline_for_file  # noqa: E402


def load_manifest() -> list:
    if not MANIFEST_JSONL.exists():
        return []
    return [json.loads(line) for line in MANIFEST_JSONL.read_text().splitlines() if line.strip()]


def pick(rows: list, count: int, split: str, seed: int) -> list:
    if split != "all":
        rows = [r for r in rows if r.get("split") == split]
    rng = random.Random(seed)
    if count and count < len(rows):
        # Sampled, not the first N: the first N share a generation seed and would understate variety.
        rows = rng.sample(rows, count)
    return sorted(rows, key=lambda r: r["id"])


def main() -> None:
    ap = argparse.ArgumentParser(description="Batch-run the nested-code extraction pipeline")
    ap.add_argument("--count", type=int, default=20, help="files to run (0 = all)")
    ap.add_argument("--split", default="all", choices=["all", "train", "val", "test"])
    ap.add_argument("--strategy", default="multicall", choices=["single", "multicall", "gold"],
                    help="single: whole file per request; multicall: one request per definition")
    ap.add_argument("--seed", type=int, default=13)
    ap.add_argument("--no-save", action="store_true", help="skip the DB and prediction files")
    ap.add_argument("--tag", default="", help="label recorded with the metrics file")
    args = ap.parse_args()

    rows = load_manifest()
    if not rows:
        sys.exit(f"No manifest at {MANIFEST_JSONL}. Generate the dataset first:\n"
                 f"  python3 scripts/generate_nested_code.py --count 1000")

    chosen = pick(rows, args.count, args.split, args.seed)
    print(f"Running {len(chosen)} files | strategy={args.strategy} | split={args.split}")
    print(f"dataset: {DATASET_DIR}")

    scores, failures, rows_out = [], [], []
    t0 = time.time()

    for i, row in enumerate(chosen, 1):
        fid = row["id"]
        print(f"\n[{i}/{len(chosen)}] {fid}  ({row['metrics']['n_lines']} lines, "
              f"depth {row['metrics']['block_depth']})", flush=True)
        try:
            result = run_pipeline_for_file(fid, save=not args.no_save, strategy=args.strategy)
        except Exception as exc:                      # a bad file costs that file, not the run
            print(f"    FAILED: {type(exc).__name__}: {exc}")
            failures.append({"id": fid, "error": f"{type(exc).__name__}: {exc}"})
            continue

        s = result["score"]
        scores.append(s)
        rows_out.append({
            "id": fid,
            "split": row.get("split"),
            "valid": result["is_valid"],
            "n_errors": len(result["errors"]),
            "n_warnings": len(result["warnings"]),
            "scope_f1": s["scopes"]["f1"],
            "relation_f1": s["relations"]["f1"],
            "kind_accuracy": s["kind_accuracy"],
            "parent_accuracy": s["parent_accuracy"],
            "depth_mae": s["max_block_depth"]["mae"],
            "overall": s["overall"],
            "elapsed_s": result["elapsed_s"],
        })
        print(f"    valid={result['is_valid']}  scopes_f1={s['scopes']['f1']:.3f}  "
              f"rel_f1={s['relations']['f1']:.3f}  overall={s['overall']:.3f}  "
              f"{result['elapsed_s']:.1f}s")

    elapsed = time.time() - t0
    agg = aggregate(scores)

    print("\n" + "=" * 68)
    print(f"{len(scores)} files scored, {len(failures)} failed, {elapsed / 60:.1f} min total")
    if agg:
        print(f"  scope F1         {agg['scope_f1']:.3f}   "
              f"(precision {agg['scope_precision']:.3f} / recall {agg['scope_recall']:.3f})")
        print(f"  kind accuracy    {agg['kind_accuracy']:.3f}")
        print(f"  parent accuracy  {agg['parent_accuracy']:.3f}")
        print(f"  relation F1      {agg['relation_f1']:.3f}")
        print(f"  recursion F1     {agg['recursive_f1']:.3f}")
        print(f"  generator F1     {agg['generator_f1']:.3f}")
        print(f"  depth MAE        {agg['depth_mae']:.2f}  "
              f"(exact {agg['depth_exact_rate']:.3f})")
        print(f"  entrypoint F1    {agg['entrypoint_f1']:.3f}")
        print(f"  OVERALL          {agg['overall']:.3f}")
    valid = sum(1 for r in rows_out if r["valid"])
    print(f"  schema-valid     {valid}/{len(rows_out)}")
    print("=" * 68)

    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    out = METRICS_DIR / f"run_{stamp}_{args.strategy}{('_' + args.tag) if args.tag else ''}.json"
    out.write_text(json.dumps({
        "strategy": args.strategy,
        "split": args.split,
        "count": len(chosen),
        "seed": args.seed,
        "elapsed_s": round(elapsed, 1),
        "aggregate": agg,
        "per_file": rows_out,
        "failures": failures,
    }, indent=2), encoding="utf-8")
    print(f"metrics: {out}")


if __name__ == "__main__":
    main()
