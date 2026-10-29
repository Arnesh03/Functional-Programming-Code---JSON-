#!/usr/bin/env python3
"""Build a dataset of deeply nested code from the py150 ASTs.

py150 ships 150k Python files already parsed into JSON ASTs, which is why it is the source here:
the tree *is* the ground truth, so nothing has to be annotated. What it does not ship is a notion
of "nested" — that is computed below, and the filtering is the whole point of this script.

"Nested" is measured three ways, because they are different phenomena and a dataset that conflates
them cannot answer which one a model struggles with:

  loop_depth      loops inside loops (for/while inside for/while)
  branch_depth    conditionals inside conditionals
  recursion       a function whose body calls its own name, and whether that call sits inside
                  another call to itself (recursion within recursion)

Output is one JSON object per line, carrying the AST, the measured depths, and the reconstructed
source where available — so it can be scored the same way the OPORD records are.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "nested_code"

# py150 node types. Its parser emits Python 2 era names; both spellings are accepted so the
# script does not silently measure zero on one of them.
LOOP_TYPES = {"For", "While", "ForStatement", "WhileStatement", "comprehension"}
BRANCH_TYPES = {"If", "IfExp", "IfStatement", "TryExcept", "TryFinally", "Try"}
FUNC_TYPES = {"FunctionDef", "AsyncFunctionDef"}
CALL_TYPES = {"Call"}
NAME_TYPES = {"Name", "NameLoad", "NameStore", "attr", "Attribute"}


def children_of(node: dict, ast: list) -> list:
    """py150 stores children as indices into the file's flat node list."""
    return [ast[i] for i in node.get("children", []) if 0 <= i < len(ast)]


def max_depth_of(ast: list, types: set) -> int:
    """Deepest chain of `types` nested inside one another, over the whole file."""
    best = 0

    def walk(idx: int, depth: int, seen: frozenset) -> None:
        nonlocal best
        if idx in seen or not (0 <= idx < len(ast)):
            return
        node = ast[idx]
        here = depth + 1 if node.get("type") in types else depth
        best = max(best, here)
        for child in node.get("children", []):
            walk(child, here, seen | {idx})

    walk(0, 0, frozenset())
    return best


def function_names(ast: list) -> list[str]:
    return [n.get("value") for n in ast if n.get("type") in FUNC_TYPES and n.get("value")]


def recursion_report(ast: list) -> dict:
    """Functions that call themselves, and whether such a call is itself inside another."""
    names = set(function_names(ast))
    if not names:
        return {"recursive_functions": [], "nested_recursion": False}

    recursive, nested = [], False

    for i, node in enumerate(ast):
        if node.get("type") not in FUNC_TYPES:
            continue
        fname = node.get("value")
        if fname not in names:
            continue

        self_calls: list[int] = []

        def walk(idx: int, depth: int, seen: frozenset) -> None:
            nonlocal nested
            if idx in seen or not (0 <= idx < len(ast)):
                return
            n = ast[idx]
            if n.get("type") in CALL_TYPES:
                # The callee name sits in the call's own subtree; a match on the enclosing
                # function's name is a self-call.
                for c in n.get("children", []):
                    if 0 <= c < len(ast) and ast[c].get("value") == fname:
                        self_calls.append(idx)
                        if depth > 0:
                            nested = True
                        depth += 1
                        break
            for c in n.get("children", []):
                walk(c, depth, seen | {idx})

        walk(i, 0, frozenset())
        if self_calls:
            recursive.append(fname)

    return {"recursive_functions": sorted(set(recursive)), "nested_recursion": nested}


def classify(ast: list) -> dict:
    loop = max_depth_of(ast, LOOP_TYPES)
    branch = max_depth_of(ast, BRANCH_TYPES)
    rec = recursion_report(ast)
    return {
        "n_nodes": len(ast),
        "loop_depth": loop,
        "branch_depth": branch,
        "max_nesting": max(loop, branch),
        **rec,
        "n_functions": len(function_names(ast)),
    }


def qualifies(m: dict, min_depth: int) -> bool:
    """Deep block nesting, or recursion — either is 'nested code' for our purposes."""
    return (m["loop_depth"] >= min_depth
            or m["branch_depth"] >= min_depth
            or m["nested_recursion"]
            or len(m["recursive_functions"]) > 0)


def main() -> None:
    ap = argparse.ArgumentParser(description="Filter py150 down to deeply nested code")
    ap.add_argument("--src", default=str(DATA / "python50k_eval.json"),
                    help="py150 AST file (one JSON AST per line)")
    ap.add_argument("--out", default=str(DATA / "nested_code.jsonl"))
    ap.add_argument("--min-depth", type=int, default=3, help="loops/branches nested this deep")
    ap.add_argument("--limit", type=int, default=0, help="stop after N qualifying files (0 = all)")
    ap.add_argument("--scan", type=int, default=0, help="read at most N input lines (0 = all)")
    args = ap.parse_args()

    src, out = Path(args.src), Path(args.out)
    if not src.exists():
        sys.exit(f"Not found: {src}\nDownload py150.tar.gz from https://www.sri.inf.ethz.ch/py150 "
                 f"and extract it into {DATA}")

    out.parent.mkdir(parents=True, exist_ok=True)
    kept = scanned = 0
    hist: Counter = Counter()

    with src.open(encoding="utf-8", errors="ignore") as fh, out.open("w", encoding="utf-8") as fo:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            scanned += 1
            if args.scan and scanned > args.scan:
                break
            try:
                ast = json.loads(line)
            except json.JSONDecodeError:
                continue  # a malformed line costs that file, not the run
            if not isinstance(ast, list) or not ast:
                continue

            m = classify(ast)
            hist[m["max_nesting"]] += 1
            if not qualifies(m, args.min_depth):
                continue

            fo.write(json.dumps({"id": f"py150_{scanned}", "metrics": m, "ast": ast}) + "\n")
            kept += 1
            if args.limit and kept >= args.limit:
                break

    print(f"scanned {scanned} files, kept {kept}")
    print("nesting-depth distribution (max of loop/branch):")
    for depth in sorted(hist):
        print(f"  depth {depth}: {hist[depth]}")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
