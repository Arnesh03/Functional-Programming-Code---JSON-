#!/usr/bin/env python3
"""Convert CodeComplex into this project's dataset format.

CodeComplex (https://github.com/sybaik1/CodeComplex) is 4,900 Codeforces submissions labelled
with worst-case time complexity. It is used here as the **real-code counterpart** to the
generated set: the structures are genuine, written by people solving problems, not emitted by a
template.

Be clear about what it is and is not. Measured with `app.gold`, CodeComplex is **short and
shallow** — median 24 lines, mean 2.9 scopes, and only 22 of 4,900 files reach block depth 8,
against 1,000 of 1,000 in the generated set. It is not a deep-nesting corpus. Its value is that
it tests whether the pipeline survives contact with real code: ad-hoc names, tabs, `sys.setrecursionlimit`,
one-letter variables, no docstrings.

Output matches the generated dataset exactly — `<id>.py`, `manifest.jsonl`, `dataset.jsonl`,
`stats.json` — so every existing script runs against it unchanged:

    DATASET_DIR=data/codecomplex python3 scripts/run_code_pipeline.py --count 20
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import warnings
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.gold import record_from_source  # noqa: E402
from app.new_validators import normalize_document, validate_report  # noqa: E402

SRC = ROOT / "CodeComplex-main" / "data" / "python_data.jsonl"


def main() -> None:
    ap = argparse.ArgumentParser(description="Build a dataset from CodeComplex Python records")
    ap.add_argument("--src", default=str(SRC))
    ap.add_argument("--out", default=str(ROOT / "data" / "codecomplex"))
    ap.add_argument("--min-lines", type=int, default=0, help="skip files shorter than this")
    ap.add_argument("--min-depth", type=int, default=0, help="skip files shallower than this")
    ap.add_argument("--limit", type=int, default=0, help="stop after N kept files (0 = all)")
    ap.add_argument("--clean", action="store_true")
    args = ap.parse_args()

    src = Path(args.src)
    if not src.exists():
        sys.exit(f"not found: {src}\nDownload it:\n"
                 f"  curl -L -o python_data.jsonl "
                 f"https://raw.githubusercontent.com/sybaik1/CodeComplex/main/data/python_data.jsonl")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if args.clean:
        for stale in list(out.glob("*.py")) + list(out.glob("*.json*")):
            stale.unlink()

    records, seen, skipped, failed = [], set(), 0, 0
    manifest = (out / "manifest.jsonl").open("w", encoding="utf-8")
    dataset = (out / "dataset.jsonl").open("w", encoding="utf-8")

    # CodeComplex is real code: some of it raises SyntaxWarning on modern Python. That is a
    # property of the corpus, not a problem to fix, so the noise is silenced rather than printed
    # 4,900 times.
    warnings.simplefilter("ignore", SyntaxWarning)

    for i, line in enumerate(src.read_text(encoding="utf-8", errors="ignore").splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
            source = row["src"]
        except (json.JSONDecodeError, KeyError):
            failed += 1
            continue

        digest = hashlib.sha256(source.encode()).hexdigest()[:16]
        if digest in seen:          # the corpus contains repeated submissions
            skipped += 1
            continue

        file_id = f"cc_{len(records) + 1:05d}"
        try:
            gold = normalize_document(record_from_source(source, file_id))
        except (SyntaxError, ValueError, RecursionError):
            failed += 1
            continue

        depth = max((s["max_block_depth"] for s in gold["scopes"]), default=0)
        n_lines = source.count("\n") + 1
        if n_lines < args.min_lines or depth < args.min_depth:
            skipped += 1
            continue

        ok, errors, _warnings = validate_report(gold)
        if not ok:                  # a gold record that fails our own validator is unusable
            failed += 1
            continue

        seen.add(digest)
        sid = f"{file_id}_D{depth}"
        path = out / f"{sid}.py"
        path.write_text(source, encoding="utf-8")

        n = len(records) + 1
        split = "train" if n % 10 < 8 else ("val" if n % 10 == 8 else "test")
        metrics = {
            "n_lines": n_lines,
            "n_chars": len(source),
            "n_ast_nodes": len(gold["blocks"]) + len(gold["scopes"]),
            "block_depth": depth,
            "loop_depth": depth,     # CodeComplex has no separate per-kind measurement
            "branch_depth": depth,
            "n_functions": sum(1 for s in gold["scopes"] if "function" in s["kind"] or "method" in s["kind"]),
            "n_classes": sum(1 for s in gold["scopes"] if s["kind"] == "class"),
            "n_scopes": len(gold["scopes"]),
            "n_blocks": len(gold["blocks"]),
            "n_relations": len(gold["relations"]),
            "recursive_functions": [s["name"] for s in gold["scopes"] if s["is_recursive"]],
            "nested_recursion": False,
        }
        record = {
            "id": sid,
            "path": str(path.relative_to(ROOT)),
            "split": split,
            "sha256_16": digest,
            "source_dataset": "CodeComplex",
            "complexity": row.get("complexity"),
            "problem": row.get("problem"),
            "origin": row.get("from"),
            "tags": row.get("tags"),
            "metrics": metrics,
        }
        manifest.write(json.dumps(record) + "\n")
        dataset.write(json.dumps({**record, "source": source}) + "\n")
        records.append(record)

        if args.limit and len(records) >= args.limit:
            break

    manifest.close()
    dataset.close()

    depths = Counter(r["metrics"]["block_depth"] for r in records)
    lines = [r["metrics"]["n_lines"] for r in records]
    stats = {
        "source": "CodeComplex (Codeforces submissions, complexity-labelled)",
        "n_samples": len(records),
        "total_lines": sum(lines),
        "mean_lines": round(sum(lines) / max(1, len(lines)), 1),
        "min_lines": min(lines, default=0),
        "max_lines": max(lines, default=0),
        "block_depth": {str(k): depths[k] for k in sorted(depths)},
        "splits": dict(Counter(r["split"] for r in records)),
        "complexity_labels": dict(Counter(r["complexity"] for r in records).most_common()),
        "with_recursion": sum(1 for r in records if r["metrics"]["recursive_functions"]),
        "duplicates_skipped": skipped,
        "failed": failed,
    }
    (out / "stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")

    print(f"wrote {len(records)} files to {out}")
    print(f"  lines: mean {stats['mean_lines']} · max {stats['max_lines']}")
    print(f"  depth: {stats['block_depth']}")
    print(f"  splits: {stats['splits']}")
    print(f"  with recursion: {stats['with_recursion']} · skipped {skipped} · failed {failed}")


if __name__ == "__main__":
    main()
