#!/usr/bin/env python3
"""CLI for the nested-code structure pipeline.

    python3 main.py extract nested_00002            # one file through the model
    python3 main.py extract nested_00002 --gold     # ground truth, no model
    python3 main.py hierarchy nested_00002          # print the scope outline
    python3 main.py batch --count 20                # batch run with scoring
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from app.hierarchy import render_text, render_tree_text, to_nested_tree  # noqa: E402
from app.pipeline import run_gold_hierarchy, run_pipeline_for_file  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description="Nested-code structure extraction")
    sub = ap.add_subparsers(dest="command", required=True)

    ex = sub.add_parser("extract", help="run one file through the pipeline")
    ex.add_argument("target")
    ex.add_argument("--strategy", default="multicall", choices=["single", "multicall", "gold"])
    ex.add_argument("--gold", action="store_true", help="shorthand for --strategy gold")
    ex.add_argument("--show", action="store_true", help="print the hierarchy outline")

    hi = sub.add_parser("hierarchy", help="print the ground-truth outline for a file")
    hi.add_argument("target")

    tr = sub.add_parser("tree", help="print the nested tree for a file")
    tr.add_argument("target")
    tr.add_argument("--json", action="store_true", help="emit the tree as JSON")

    ba = sub.add_parser("batch", help="run many files and report the aggregate")
    ba.add_argument("--count", type=int, default=20)
    ba.add_argument("--strategy", default="multicall", choices=["single", "multicall", "gold"])
    ba.add_argument("--split", default="all", choices=["all", "train", "val", "test"])

    args = ap.parse_args()

    if args.command == "extract":
        strategy = "gold" if args.gold else args.strategy
        result = run_pipeline_for_file(args.target, strategy=strategy, print_hierarchy=args.show)
        print(json.dumps({"file_id": result["file_id"], "valid": result["is_valid"],
                          "errors": result["errors"][:5], "score": result["score"]}, indent=2))
    elif args.command == "hierarchy":
        print(render_text(run_gold_hierarchy(args.target)))
    elif args.command == "tree":
        from app.gold import record_from_source
        from app.new_validators import normalize_document
        from app.pipeline import _load_source
        file_id, source = _load_source(args.target)
        tree = to_nested_tree(normalize_document(record_from_source(source, file_id)))
        print(json.dumps(tree, indent=2) if args.json else render_tree_text(tree))
    elif args.command == "batch":
        import subprocess
        subprocess.run([sys.executable, str(ROOT / "scripts" / "run_code_pipeline.py"),
                        "--count", str(args.count), "--strategy", args.strategy,
                        "--split", args.split], check=False)


if __name__ == "__main__":
    main()
