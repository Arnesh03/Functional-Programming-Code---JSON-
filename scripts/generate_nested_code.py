#!/usr/bin/env python3
"""Generate a large dataset of long, deeply nested Python programs.

Scraped corpora give you whatever nesting happens to exist, which is a long tail of shallow
files. This generates nesting to order: every sample in the dataset is deeply nested, long,
and valid Python that actually runs.

Each program is assembled from unit templates, chosen and parameterised at random, that nest
the way working code nests:

    loop_pyramid     for/while chains with a branch ladder at the floor
    branch_pyramid   if/elif/else ladders nested inside one another
    try_pyramid      try/except/else/finally nested through loops
    with_pyramid     context managers nested through loops
    comprehension    comprehensions inside comprehensions, with conditions
    closure_tower    def inside def inside def, closing over every level
    class_tower      a class with an inner class and deeply nested methods
    recursion        self-recursion, recursion inside recursion, mutual recursion
    async_nested     async with / async for / await nested in loops
    match_nested     match/case inside match/case inside loops
    data_walk        recursive descent over a deeply nested literal
    generators       yield / yield from chains across nested loops
    state_machine    while + try + for/else + break/continue

Ground truth is never asserted by the templates. Every file is re-parsed with the stdlib `ast`
module and measured; the recorded depths are what a parser sees. A sample that comes out
shallower than the floor is thrown away and regenerated, so "nested" is a guarantee of the
dataset, not an intention.

Writes:
  <out>/<id>.py          the programs
  <out>/manifest.jsonl   one record per program: path, split, measured metrics
  <out>/stats.json       dataset-level distributions
  <out>/asts/<id>.json   flat py150-shape AST per program (only with --with-ast)
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import random
import subprocess
import sys
from collections import Counter
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IND = "    "


# --------------------------------------------------------------------------------------
# emitter
# --------------------------------------------------------------------------------------
class Emit:
    """Indentation-tracking line writer. Blocks are never left empty, so output always parses."""

    def __init__(self, level: int = 0) -> None:
        self.lines: list[str] = []
        self.level = level

    def __call__(self, line: str = "") -> None:
        self.lines.append(IND * self.level + line if line else "")

    @contextmanager
    def block(self, header: str):
        self(header)
        self.level += 1
        mark = len(self.lines)
        try:
            yield
        finally:
            if len(self.lines) == mark:
                self("pass")
            self.level -= 1

    def text(self) -> str:
        return "\n".join(self.lines)


# --------------------------------------------------------------------------------------
# naming and fragments
# --------------------------------------------------------------------------------------
VERBS = ["scan", "collect", "reduce", "merge", "fold", "sift", "weigh", "tally", "probe",
         "chart", "sweep", "rank", "distil", "gather", "trace", "resolve", "splice", "flatten"]
NOUNS = ["matrix", "ledger", "roster", "payload", "graph", "window", "buffer", "registry",
         "sector", "cohort", "lattice", "manifest", "channel", "segment", "bundle", "frame"]
TITLES = ["Ledger", "Roster", "Lattice", "Registry", "Cohort", "Manifest", "Channel",
          "Segment", "Bundle", "Frame", "Window", "Sector"]

GUARDS = [
    "value % {k} == 0",
    "value > threshold * {k}",
    "{k} < len(window) and window[{k}] is not None",
    "isinstance(value, int) and value not in seen",
    "depth_budget - {k} > 0",
    "abs(value) + {k} > score",
    "value & {k} == 0",
]

LEAVES = [
    "total += {v} * weights.get(({v}, value), 1)",
    "running = (running * 31 + value + {v}) % 1_000_003",
    "seen.add((row_index, {v}))",
    "buckets.setdefault(value % {m}, []).append({v})",
    "total ^= (value << ({v} % 5)) & 0xFFFF",
]


def namer(rng: random.Random, used: set[str]) -> str:
    while True:
        name = f"{rng.choice(VERBS)}_{rng.choice(NOUNS)}"
        if name not in used:
            used.add(name)
            return name


def title(rng: random.Random, used: set[str]) -> str:
    while True:
        name = f"{rng.choice(TITLES)}{rng.randint(10, 99)}"
        if name not in used:
            used.add(name)
            return name


def leaf_body(e: Emit, rng: random.Random, var: str, k: int = 3) -> None:
    for line in rng.sample(LEAVES, k=min(k, len(LEAVES))):
        e(line.format(v=var, m=rng.randint(3, 11)))
    with e.block("if len(trace) < 16:"):
        e(f"trace.append((row_index, {var}, value))")


@dataclass
class Unit:
    name: str
    source: str
    call: str
    kind: str
    needs_async: bool = False


# --------------------------------------------------------------------------------------
# unit templates
# --------------------------------------------------------------------------------------
def u_loop_pyramid(rng: random.Random, name: str, depth: int) -> Unit:
    e = Emit()
    with e.block(f"def {name}(matrix, weights=None, threshold=THRESHOLD):"):
        e(f'"""Loops nested {depth} deep; each floor carries a branch ladder."""')
        e("weights = weights or {}")
        e("total = running = score = 0")
        e("value = 0")
        e("seen, buckets, trace = set(), {}, []")
        with e.block("for row_index, row in enumerate(matrix):"):
            with e.block("if not row:"):
                e("continue")
            with e.block("try:"):
                with ExitStack() as stack:
                    last = "row_index"
                    for lvl in range(depth):
                        var = f"i{lvl}"
                        bound = max(2, 5 - lvl)
                        if lvl % 3 == 2:
                            e(f"{var} = 0")
                            stack.enter_context(e.block(f"while {var} < min(len(row), {bound}):"))
                            e(f"{var} += 1")
                        elif lvl % 3 == 1:
                            stack.enter_context(
                                e.block(f"for {var}, _slot in enumerate(row[:{bound}]):"))
                        else:
                            stack.enter_context(
                                e.block(f"for {var} in range(min(len(row), {bound})):"))
                        if lvl % 2 == 0:
                            e(f"value = row[{var}] if {var} < len(row) else {lvl}")
                        last = var
                    leaf_body(e, rng, last, k=rng.randint(2, 4))
                    with e.block(f"if value % 2 == 0 and {last} < 2:"):
                        with e.block("if value > threshold:"):
                            e("score += 2")
                        with e.block("elif value:"):
                            e("score -= 1")
                        with e.block("else:"):
                            e("score += 1")
                    with e.block("elif value % 3 == 0:"):
                        e("score += 3")
                    with e.block("else:"):
                        e("seen.discard((row_index, 0))")
            with e.block("except (IndexError, TypeError, ZeroDivisionError):"):
                e("continue")
        e('return {"total": total, "running": running, "score": score,')
        e('        "buckets": len(buckets), "trace": trace[:8], "seen": len(seen)}')
    return Unit(name, e.text(), f"{name}(DEMO_MATRIX)", "loop_pyramid")


def _ladder(e: Emit, rng: random.Random, lvl: int, depth: int) -> None:
    guard = rng.choice(GUARDS).format(k=lvl + 2)
    with e.block(f"if {guard}:"):
        e(f"score += {lvl + 1}")
        if lvl + 1 < depth:
            _ladder(e, rng, lvl + 1, depth)
        else:
            e("matched.append(('deep', value))")
    with e.block(f"elif value % {lvl + 3} == 0:"):
        e("score -= 1")
        if lvl + 1 < depth and lvl < 2:
            _ladder(e, rng, lvl + 1, depth)
        else:
            e(f"matched.append(('alt', {lvl}))")
    with e.block("else:"):
        e("skipped += 1")
        if lvl + 1 < depth and lvl < 1:
            _ladder(e, rng, lvl + 1, depth)


def u_branch_pyramid(rng: random.Random, name: str, depth: int) -> Unit:
    e = Emit()
    with e.block(f"def {name}(values, threshold=THRESHOLD):"):
        e(f'"""An if/elif/else ladder nested {depth} deep, inside a loop."""')
        e("score = skipped = 0")
        e("matched, seen = [], set()")
        e("window = list(values)[:24]")
        e(f"depth_budget = {depth + 4}")
        with e.block("for value in window:"):
            with e.block("if value is None:"):
                e("skipped += 1")
                e("continue")
            with e.block("if not isinstance(value, int):"):
                e("value = len(str(value))")
            _ladder(e, rng, 0, depth)
            e("seen.add(value)")
        e('return {"score": score, "skipped": skipped, "matched": matched[:8], "seen": len(seen)}')
    return Unit(name, e.text(), f"{name}(DEMO_FLAT)", "branch_pyramid")


def _try_nest(e: Emit, rng: random.Random, lvl: int, depth: int) -> None:
    with e.block("try:"):
        e(f"stage = {lvl}")
        if lvl + 1 < depth:
            with e.block(f"for probe in range(min(2, {lvl} + 2)):"):
                with e.block("if probe > 1:"):
                    e("break")
                _try_nest(e, rng, lvl + 1, depth)
        else:
            with e.block("if attempts % 3 == 0:"):
                e(f"raise ValueError(f'stage {lvl} rejected {{item!r}}')")
            with e.block("if attempts % 5 == 0:"):
                e("raise KeyError(attempts)")
            e(f"results.append((attempts, {lvl}))")
    with e.block(f"except ValueError as exc_{lvl}:"):
        e(f"errors.append(({lvl}, str(exc_{lvl})[:32]))")
    with e.block("except (KeyError, TypeError):"):
        e(f"errors.append(({lvl}, 'type'))")
    with e.block("else:"):
        e(f"clean += {lvl + 1}")
    with e.block("finally:"):
        e(f"touched.add({lvl})")


def u_try_pyramid(rng: random.Random, name: str, depth: int) -> Unit:
    e = Emit()
    with e.block(f"def {name}(payloads):"):
        e(f'"""try/except/else/finally nested {depth} deep through loops."""')
        e("errors, results = [], []")
        e("touched = set()")
        e("attempts = clean = 0")
        e("stage = -1")
        with e.block("for item in payloads:"):
            e("attempts += 1")
            _try_nest(e, rng, 0, depth)
        e('return {"errors": len(errors), "results": results[:8], "clean": clean,')
        e('        "touched": sorted(touched), "attempts": attempts}')
    return Unit(name, e.text(), f"{name}(DEMO_FLAT)", "try_pyramid")


def u_with_pyramid(rng: random.Random, name: str, depth: int) -> Unit:
    e = Emit()
    with e.block(f"def {name}(items):"):
        e(f'"""Context managers nested {depth} deep, with loops and branches inside."""')
        e("log, kept = [], []")
        e("total = 0")
        with e.block("for index, item in enumerate(items):"):
            with ExitStack() as stack:
                for lvl in range(depth):
                    stack.enter_context(
                        e.block(f"with tracked('lvl{lvl}', log) as ctx{lvl}:"))
                    if lvl % 2 == 0:
                        with e.block(f"if index % {lvl + 2} == 0:"):
                            e(f"total += {lvl}")
                with e.block("for step in range(2):"):
                    with e.block("if isinstance(item, int) and item % 2 == step:"):
                        e(f"kept.append((index, step, ctx{depth - 1}))")
                    with e.block("else:"):
                        e("total += 1")
        e('return {"log": len(log), "kept": kept[:8], "total": total}')
    return Unit(name, e.text(), f"{name}(DEMO_FLAT)", "with_pyramid")


def u_comprehension(rng: random.Random, name: str, depth: int) -> Unit:
    e = Emit()
    with e.block(f"def {name}(matrix):"):
        e('"""Comprehensions inside comprehensions, then a loop that consumes them."""')
        e("grid = [[cell for cell in row if cell % 2 == 0] for row in matrix if row]")
        e("folded = {r: {c: [v for v in row[:c + 1] if v]")
        e("              for c in range(min(3, len(row)))}")
        e("          for r, row in enumerate(matrix)}")
        e("chained = [v for row in grid for v in row if any(v > w for w in row[:2])]")
        e("paired = {(r, c): sum(v for v in vals if v)")
        e("          for r, cols in folded.items() for c, vals in cols.items()}")
        e("counted = sum(sum(1 for v in row if v) for row in matrix)")
        e("deep = [[[v + k for k in range(2) if (v + k) % 3]")
        e("         for v in row if v] for row in grid]")
        e("out = []")
        with e.block("for key, value in sorted(paired.items()):"):
            with e.block("if value:"):
                with e.block("for bucket in deep:"):
                    with e.block("if bucket:"):
                        with e.block("for inner in bucket:"):
                            with e.block("if any(x > value for x in inner):"):
                                e("out.append((key, value))")
                                e("break")
        e('return {"grid": len(grid), "chained": chained[:6], "counted": counted,')
        e('        "paired": len(paired), "out": out[:6]}')
    return Unit(name, e.text(), f"{name}(DEMO_MATRIX)", "comprehension")


def _closure(e: Emit, lvl: int, depth: int) -> None:
    """Inner defs are emitted before the `return`, so the name is bound when it is read."""
    with e.block(f"def level{lvl}(a{lvl}):"):
        with e.block(f"if a{lvl} % 2:"):
            e(f"a{lvl} += {lvl + 1}")
        if lvl == depth - 1:
            e("acc = 0")
            with e.block("for step in range(3):"):
                with e.block("if step % 2 == 0:"):
                    e("acc += " + " + ".join(f"a{k}" for k in range(depth)))
                with e.block("else:"):
                    e("acc -= step")
            e("return acc")
        else:
            _closure(e, lvl + 1, depth)
            e(f"return level{lvl + 1}")


def u_closure_tower(rng: random.Random, name: str, depth: int) -> Unit:
    e = Emit()
    with e.block(f"def {name}(seed=3):"):
        e(f'"""Functions nested {depth} deep, each closing over every level above it."""')
        _closure(e, 0, depth)
        e("chain = level0")
        e("return " + "level0" + "".join(f"(seed + {k})" for k in range(depth))
          + " + (0 if chain else 1)")
    return Unit(name, e.text(), f"{name}()", "closure_tower")


def u_class_tower(rng: random.Random, name: str, depth: int) -> Unit:
    e = Emit()
    with e.block(f"class {name}:"):
        e('"""A class with an inner class and deeply nested methods."""')
        e("LIMIT = 8")
        e("")
        with e.block("def __init__(self, matrix=None):"):
            e("self.matrix = matrix or []")
            e("self.cache = {}")
            e("self.log = []")
        e("")
        with e.block("class Inner:"):
            e('"""Nested class; its own methods nest again."""')
            e("")
            with e.block("def __init__(self, span=3):"):
                e("self.span = span")
            e("")
            with e.block("def expand(self, n):"):
                e("out = []")
                with e.block("for i in range(min(n, self.span)):"):
                    with e.block("for j in range(i + 1):"):
                        with e.block("if (i + j) % 2 == 0:"):
                            with e.block("for k in range(min(j + 1, 2)):"):
                                with e.block("if k <= j:"):
                                    e("out.append((i, j, k))")
                        with e.block("else:"):
                            e("out.append((i, j, -1))")
                e("return out")
        e("")
        with e.block("def tally(self, matrix=None):"):
            e('"""Nested loops over rows, memoised per row."""')
            e("matrix = matrix if matrix is not None else self.matrix")
            e("total = 0")
            with e.block("for row_index, row in enumerate(matrix):"):
                e("key = (row_index, len(row))")
                with e.block("if key in self.cache:"):
                    e("total += self.cache[key]")
                    e("continue")
                e("subtotal = 0")
                with ExitStack() as stack:
                    for lvl in range(max(2, depth - 1)):
                        bound = max(2, 4 - lvl)
                        stack.enter_context(
                            e.block(f"for c{lvl} in range(min(len(row), {bound})):"))
                    with e.block("if row[c0] % 2:"):
                        e("subtotal += row[c0]")
                    with e.block("else:"):
                        e("subtotal -= 1")
                e("self.cache[key] = subtotal")
                e("total += subtotal")
            e("return total")
        e("")
        e("@staticmethod")
        with e.block("def fold(rows):"):
            e("acc = []")
            with e.block("for row in rows:"):
                with e.block("try:"):
                    with e.block("for v in row:"):
                        with e.block("if v % 3 == 0:"):
                            with e.block("for w in range(2):"):
                                e("acc.append(v + w)")
                with e.block("except TypeError:"):
                    e("continue")
            e("return acc[:12]")
        e("")
        e("@property")
        with e.block("def summary(self):"):
            e('return {"rows": len(self.matrix), "cached": len(self.cache)}')
    return Unit(name, e.text(), f"{name}(DEMO_MATRIX).tally()", "class_tower")


def u_recursion(rng: random.Random, name: str, depth: int) -> Unit:
    e = Emit()
    ping, pong = f"{name}_ping", f"{name}_pong"
    with e.block(f"def {name}(node, budget={depth}):"):
        e('"""Self-recursion, and a self-call nested inside another self-call."""')
        with e.block("if budget <= 0 or not isinstance(node, dict):"):
            e("return 0")
        e('total = int(node.get("value") or 0)')
        with e.block('for k, child in enumerate(node.get("children") or []):'):
            with e.block("if k % 2 == 0:"):
                with e.block("try:"):
                    e(f"total += {name}({name}(child, budget - 1), budget - 2)")
                with e.block("except (TypeError, KeyError, RecursionError):"):
                    e("continue")
            with e.block("else:"):
                with e.block('for sub in (node.get("children") or [])[k:]:'):
                    with e.block("if isinstance(sub, dict):"):
                        e(f"total += {name}(sub, budget - 1)")
                    with e.block("elif isinstance(sub, int):"):
                        e("total += sub")
        e("return total")
    e("")
    e("")
    with e.block(f"def {ping}(node, budget={depth}):"):
        e('"""Mutual recursion: ping calls pong, pong calls ping."""')
        with e.block("if budget <= 0 or not isinstance(node, dict):"):
            e("return 0")
        e("acc = 0")
        with e.block('for child in node.get("children") or []:'):
            with e.block("if isinstance(child, dict):"):
                e(f"acc += {pong}(child, budget - 1)")
            with e.block("else:"):
                e("acc += 1")
        e('return acc + int(node.get("value") or 0)')
    e("")
    e("")
    with e.block(f"def {pong}(node, budget={depth}):"):
        with e.block("if budget <= 0:"):
            e("return 0")
        e("acc = 0")
        with e.block('for child in (node.get("children") or [])[:2]:'):
            with e.block("if isinstance(child, dict):"):
                with e.block("if budget % 2 == 0:"):
                    e(f"acc += {ping}(child, budget - 1)")
                with e.block("else:"):
                    e(f"acc += {pong}(child, budget - 1)")
        e("return acc + 1")
    return Unit(name, e.text(), f"{name}(DEMO_TREE) + {ping}(DEMO_TREE)", "recursion")


def u_async_nested(rng: random.Random, name: str, depth: int) -> Unit:
    e = Emit()
    with e.block(f"async def {name}(matrix):"):
        e('"""async with / async for / await, nested inside ordinary loops."""')
        e("seen, log = [], []")
        with e.block('async with async_tracked("outer", log):'):
            with e.block("for row in matrix:"):
                with e.block("if not row:"):
                    e("continue")
                with e.block("async for i in arange(min(len(row), 3)):"):
                    with e.block("if row[i] % 2 == 0:"):
                        with e.block(f'async with async_tracked(f"cell{{i}}", log):'):
                            with e.block("for j in range(i + 1):"):
                                with e.block("if row[j] > 0:"):
                                    e("seen.append((i, j, row[j]))")
                                with e.block("else:"):
                                    e("await asyncio.sleep(0)")
                    with e.block("else:"):
                        with e.block("try:"):
                            e("seen.append((i, row[i] // (i + 1)))")
                        with e.block("except ZeroDivisionError:"):
                            e("continue")
        e('return {"seen": seen[:8], "log": len(log)}')
    return Unit(name, e.text(), f"asyncio.run({name}(DEMO_MATRIX))", "async_nested", True)


def u_match_nested(rng: random.Random, name: str, depth: int) -> Unit:
    e = Emit()
    with e.block(f"def {name}(events):"):
        e('"""match/case inside match/case inside a loop."""')
        e("out = []")
        with e.block("for event in events:"):
            with e.block("match event:"):
                with e.block('case {"kind": "row", "cells": [first, *rest]}:'):
                    e('out.append(("first", first))')
                    with e.block("for cell in rest:"):
                        with e.block("match cell:"):
                            with e.block("case int() if cell > 5:"):
                                with e.block("for k in range(2):"):
                                    with e.block("if (cell + k) % 2:"):
                                        e('out.append(("big", cell, k))')
                            with e.block("case int():"):
                                e('out.append(("small", cell))')
                            with e.block("case _:"):
                                e('out.append(("other", str(cell)[:4]))')
                with e.block("case [a, b, *tail]:"):
                    with e.block("if a > b:"):
                        e('out.append(("desc", a, b, len(tail)))')
                    with e.block("else:"):
                        e('out.append(("asc", a, b, len(tail)))')
                with e.block("case int() | float() as num:"):
                    with e.block("if num > 0:"):
                        e('out.append(("num", num))')
                with e.block('case str() as text if text.startswith("s"):'):
                    e('out.append(("text", text[:4]))')
                with e.block("case _:"):
                    e('out.append(("unmatched",))')
        e("return out[:12]")
    return Unit(name, e.text(), f"{name}(DEMO_EVENTS)", "match_nested")


def u_data_walk(rng: random.Random, name: str, depth: int) -> Unit:
    e = Emit()
    with e.block(f"def {name}(blob=None, depth=0, budget={depth + 4}):"):
        e('"""Recursive descent over a deeply nested literal."""')
        e(f"blob = DEEP_{name.upper()} if blob is None else blob")
        with e.block("if budget <= 0:"):
            e('return {"depth": depth, "leaves": 0}')
        e("leaves = 0")
        e("deepest = depth")
        with e.block("if isinstance(blob, dict):"):
            with e.block("for key, child in blob.items():"):
                with e.block("if isinstance(child, (dict, list, tuple)):"):
                    e(f"inner = {name}(child, depth + 1, budget - 1)")
                    e('deepest = max(deepest, inner["depth"])')
                    e('leaves += inner["leaves"]')
                with e.block("elif isinstance(child, int):"):
                    with e.block("if child % 2 == 0:"):
                        e("leaves += 1")
                    with e.block("else:"):
                        e("leaves += 2")
        with e.block("elif isinstance(blob, (list, tuple)):"):
            with e.block("for item in blob:"):
                with e.block("if isinstance(item, (dict, list, tuple)):"):
                    e(f"inner = {name}(item, depth + 1, budget - 1)")
                    e('deepest = max(deepest, inner["depth"])')
                    e('leaves += inner["leaves"]')
                with e.block("else:"):
                    e("leaves += 1")
        with e.block("else:"):
            e("leaves += 1")
        e('return {"depth": deepest, "leaves": leaves}')
    return Unit(name, e.text(), f"{name}()", "data_walk")


def u_generators(rng: random.Random, name: str, depth: int) -> Unit:
    e = Emit()
    rows, cells = f"{name}_rows", f"{name}_cells"
    with e.block(f"def {cells}(row):"):
        e('"""Innermost generator: yields from nested loops and a genexp."""')
        with e.block("for i, v in enumerate(row):"):
            with e.block("if v % 2:"):
                e("yield from (v * k for k in range(1, 3) if v * k < 64)")
            with e.block("else:"):
                with e.block("for k in range(2):"):
                    with e.block("if v + k:"):
                        e("yield v + k")
    e("")
    e("")
    with e.block(f"def {rows}(matrix):"):
        with e.block("for row in matrix:"):
            with e.block("if row:"):
                e(f"yield from {cells}(row)")
    e("")
    e("")
    with e.block(f"def {name}(matrix):"):
        e("acc, runs = [], []")
        e("streak = 0")
        with e.block(f"for v in {rows}(matrix):"):
            with e.block("if v % 3 == 0:"):
                e("streak += 1")
                with e.block("if streak > 2:"):
                    e("runs.append(streak)")
                    e("streak = 0")
            with e.block("else:"):
                with e.block("if streak:"):
                    e("runs.append(-streak)")
                e("streak = 0")
                with e.block("if len(acc) < 32:"):
                    e("acc.append(v)")
        e('return {"acc": acc[:8], "runs": runs[:8], "streak": streak}')
    return Unit(name, e.text(), f"{name}(DEMO_MATRIX)", "generators")


def u_state_machine(rng: random.Random, name: str, depth: int) -> Unit:
    e = Emit()
    with e.block(f"def {name}(matrix, max_steps=48):"):
        e('"""while + try + for/else + break/continue, nested."""')
        e('state = "start"')
        e("steps = 0")
        e("log, found = [], []")
        with e.block("while steps < max_steps:"):
            e("steps += 1")
            with e.block("try:"):
                with e.block('if state == "start":'):
                    with e.block("for row in matrix:"):
                        with e.block("if not row:"):
                            e("continue")
                        with e.block("for v in row:"):
                            with e.block("if v % 3 == 0:"):
                                e('state = "collect"')
                                e("break")
                        with e.block("else:"):
                            e("continue")
                        e("break")
                    with e.block("else:"):
                        e('state = "done"')
                with e.block('elif state == "collect":'):
                    with e.block("for row_index, row in enumerate(matrix):"):
                        with e.block("for i, v in enumerate(row):"):
                            with e.block("if v and v % 2 == 0:"):
                                with e.block("if len(found) < 12:"):
                                    e("found.append((row_index, i, v))")
                                with e.block("else:"):
                                    e('state = "verify"')
                                    e("break")
                        with e.block('if state == "verify":'):
                            e("break")
                    with e.block("else:"):
                        e('state = "verify"')
                with e.block('elif state == "verify":'):
                    with e.block("for row_index, i, v in found:"):
                        with e.block("if v < 0:"):
                            e('raise RuntimeError("negative cell")')
                    e('state = "done"')
                with e.block("else:"):
                    e("break")
            with e.block("except RuntimeError:"):
                e('state = "done"')
            with e.block("finally:"):
                with e.block("if len(log) < 24:"):
                    e("log.append(state)")
            with e.block('if state == "done":'):
                e("break")
        e('return {"state": state, "steps": steps, "found": found[:6], "log": log[:6]}')
    return Unit(name, e.text(), f"{name}(DEMO_MATRIX)", "state_machine")


# CPython compiles at most 20 statically nested blocks into one code object. Templates that
# spend more than one block per level are capped so the output always compiles.
DEPTH_CAP = {
    "u_loop_pyramid": 13,
    "u_branch_pyramid": 14,
    "u_try_pyramid": 6,
    "u_with_pyramid": 12,
    "u_closure_tower": 12,
    "u_class_tower": 12,
}

TEMPLATES = [
    (u_loop_pyramid, 3),
    (u_branch_pyramid, 3),
    (u_try_pyramid, 2),
    (u_with_pyramid, 2),
    (u_comprehension, 2),
    (u_closure_tower, 2),
    (u_class_tower, 2),
    (u_recursion, 2),
    (u_async_nested, 1),
    (u_match_nested, 2),
    (u_data_walk, 2),
    (u_generators, 2),
    (u_state_machine, 2),
]
WEIGHTED = [fn for fn, w in TEMPLATES for _ in range(w)]


# --------------------------------------------------------------------------------------
# literals
# --------------------------------------------------------------------------------------
def nested_literal(rng: random.Random, depth: int) -> str:
    if depth <= 0:
        return str(rng.randint(0, 9))
    inner = nested_literal(rng, depth - 1)
    kind = depth % 3
    if kind == 0:
        return '{"level": %d, "items": [%s, %d]}' % (depth, inner, rng.randint(0, 9))
    if kind == 1:
        return "[%s, %d]" % (inner, rng.randint(0, 9))
    return "(%s, %d)" % (inner, rng.randint(0, 9))


def demo_tree(rng: random.Random, depth: int) -> str:
    if depth <= 0:
        return '{"value": %d, "children": []}' % rng.randint(1, 9)
    kids = ", ".join(demo_tree(rng, depth - 1) for _ in range(2 if depth > 3 else 1))
    return '{"value": %d, "children": [%s, %d]}' % (rng.randint(1, 9), kids, rng.randint(1, 9))


# --------------------------------------------------------------------------------------
# program assembly
# --------------------------------------------------------------------------------------
def make_program(idx: int, rng: random.Random, target_lines: int,
                 min_depth: int, max_depth: int) -> tuple[str, list[str]]:
    used: set[str] = set()
    units: list[Unit] = []
    lines = 0
    # always lead with the two densest templates, so every file has block nesting at the floor
    forced = [u_loop_pyramid, u_branch_pyramid]
    guard = 0
    while (lines < target_lines or len(units) < 4) and guard < 200:
        guard += 1
        fn = forced.pop(0) if forced else rng.choice(WEIGHTED)
        depth = min(rng.randint(min_depth, max_depth), DEPTH_CAP.get(fn.__name__, 10))
        name = title(rng, used) if fn is u_class_tower else namer(rng, used)
        unit = fn(rng, name, depth)
        units.append(unit)
        lines += unit.source.count("\n") + 3

    needs_async = any(u.needs_async for u in units)
    deep_names = [u.name for u in units if u.kind == "data_walk"]

    e = Emit()
    kinds = ", ".join(sorted({u.kind for u in units}))
    e(f'"""Generated sample {idx:05d}: {len(units)} deeply nested units ({kinds})."""')
    e("from __future__ import annotations")
    e("")
    if needs_async:
        e("import asyncio")
    e("from contextlib import contextmanager" + (", asynccontextmanager" if needs_async else ""))
    e("")
    e("THRESHOLD = 3")
    e(f"DEMO_MATRIX = [[(r * {rng.randint(3, 11)} + c) % {rng.randint(7, 17)} "
      f"for c in range(8)] for r in range(6)]")
    e("DEMO_FLAT = [c for row in DEMO_MATRIX for c in row]")
    e(f"DEMO_TREE = {demo_tree(rng, 5)}")
    e("DEMO_EVENTS = [")
    e('    {"kind": "row", "cells": [1, 7, 3]},')
    e('    {"kind": "row", "cells": [9, 8]},')
    e("    [4, 2, 1, 0],")
    e("    7,")
    e("    3.5,")
    e('    "sample",')
    e('    {"kind": "meta", "cells": []},')
    e("]")
    for dn in deep_names:
        e(f"DEEP_{dn.upper()} = {nested_literal(rng, rng.randint(6, 9))}")
    e("")
    e("")
    e("@contextmanager")
    with e.block("def tracked(label, log):"):
        e('"""Records entry and exit, so nested `with` blocks leave a trace."""')
        with e.block("if len(log) < 64:"):
            e('log.append(("enter", label))')
        with e.block("try:"):
            e("yield label")
        with e.block("finally:"):
            with e.block("if len(log) < 64:"):
                e('log.append(("exit", label))')
    if needs_async:
        e("")
        e("")
        e("@asynccontextmanager")
        with e.block("async def async_tracked(label, log):"):
            e('log.append(("enter", label))')
            with e.block("try:"):
                e("yield label")
            with e.block("finally:"):
                e('log.append(("exit", label))')
        e("")
        e("")
        with e.block("async def arange(n):"):
            with e.block("for i in range(n):"):
                with e.block("if i >= 0:"):
                    e("yield i")

    for unit in units:
        e("")
        e("")
        for line in unit.source.split("\n"):
            e(line) if line else e()

    e("")
    e("")
    with e.block(f"def pipeline_{idx:05d}():"):
        e('"""Drive every unit above, so nothing in this file is dead code."""')
        e("results = {}")
        for unit in units:
            e(f'results["{unit.name}"] = {unit.call}')
        e("digest = 0")
        with e.block("for key, value in sorted(results.items()):"):
            with e.block("if isinstance(value, dict):"):
                with e.block("for sub in value.values():"):
                    with e.block("if isinstance(sub, (list, tuple, set, dict, str)):"):
                        e("digest += len(sub)")
                    with e.block("elif isinstance(sub, int):"):
                        e("digest += sub % 97")
            with e.block("elif isinstance(value, (list, tuple, set)):"):
                e("digest += len(value)")
            with e.block("elif isinstance(value, int):"):
                e("digest += value % 97")
            with e.block("else:"):
                e("digest += 1")
        e('return {"units": len(results), "digest": digest % 100_003}')
    e("")
    e("")
    with e.block('if __name__ == "__main__":'):
        e(f"print(pipeline_{idx:05d}())")

    return e.text() + "\n", sorted({u.kind for u in units})


# --------------------------------------------------------------------------------------
# measurement — the parser is the authority, not the templates
# --------------------------------------------------------------------------------------
TRY_TYPES = tuple(t for t in (getattr(ast, "Try", None), getattr(ast, "TryStar", None)) if t)
MATCH_TYPES = tuple(t for t in (getattr(ast, "Match", None),) if t)
LOOP_NODES = (ast.For, ast.AsyncFor, ast.While, ast.comprehension)
BRANCH_NODES = (ast.If, ast.IfExp) + MATCH_TYPES
WITH_NODES = (ast.With, ast.AsyncWith)
FUNC_NODES = (ast.FunctionDef, ast.AsyncFunctionDef)
COMP_NODES = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
DATA_NODES = (ast.Dict, ast.List, ast.Tuple, ast.Set)
BLOCK_NODES = (LOOP_NODES[:3] + (ast.If,) + TRY_TYPES + WITH_NODES + FUNC_NODES
               + (ast.ClassDef,) + MATCH_TYPES)


def _chain_depth(node: ast.AST, types: tuple, running: int = 0) -> int:
    here = running + 1 if isinstance(node, types) else running
    best = here
    for child in ast.iter_child_nodes(node):
        best = max(best, _chain_depth(child, types, here))
    return best


def _call_graph(tree: ast.AST) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = {}
    for fn in (n for n in ast.walk(tree) if isinstance(n, FUNC_NODES)):
        calls = {c.func.id for c in ast.walk(fn)
                 if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)}
        graph.setdefault(fn.name, set()).update(calls)
    return graph


def _reaches(graph: dict[str, set[str]], start: str, target: str) -> bool:
    stack, seen = list(graph.get(start, ())), set()
    while stack:
        cur = stack.pop()
        if cur == target:
            return True
        if cur in seen:
            continue
        seen.add(cur)
        stack.extend(graph.get(cur, ()))
    return False


def measure(source: str) -> dict:
    tree = ast.parse(source)

    recursive, nested_recursion = set(), False
    for fn in (n for n in ast.walk(tree) if isinstance(n, FUNC_NODES)):
        self_calls = [c for c in ast.walk(fn) if isinstance(c, ast.Call)
                      and isinstance(c.func, ast.Name) and c.func.id == fn.name]
        if self_calls:
            recursive.add(fn.name)
            for call in self_calls:
                for arg in call.args:
                    if any(isinstance(s, ast.Call) and isinstance(s.func, ast.Name)
                           and s.func.id == fn.name for s in ast.walk(arg)):
                        nested_recursion = True

    graph = _call_graph(tree)
    mutual = sorted({a for a, outs in graph.items()
                     for b in outs if b != a and b in graph and _reaches(graph, b, a)})

    funcs = [n for n in ast.walk(tree) if isinstance(n, FUNC_NODES)]
    return {
        "n_lines": source.count("\n") + 1,
        "n_chars": len(source),
        "n_ast_nodes": sum(1 for _ in ast.walk(tree)),
        "n_functions": len(funcs),
        "n_async_functions": sum(1 for n in funcs if isinstance(n, ast.AsyncFunctionDef)),
        "n_classes": sum(1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef)),
        "block_depth": _chain_depth(tree, BLOCK_NODES),
        "loop_depth": _chain_depth(tree, LOOP_NODES),
        "branch_depth": _chain_depth(tree, BRANCH_NODES),
        "try_depth": _chain_depth(tree, TRY_TYPES) if TRY_TYPES else 0,
        "with_depth": _chain_depth(tree, WITH_NODES),
        "function_depth": _chain_depth(tree, FUNC_NODES),
        "comprehension_depth": _chain_depth(tree, COMP_NODES),
        "data_depth": _chain_depth(tree, DATA_NODES),
        "recursive_functions": sorted(recursive),
        "nested_recursion": nested_recursion,
        "mutual_recursion": mutual,
    }


def to_json_ast(source: str) -> list:
    """Flat node list in the py150 shape: {type, value?, children:[indices]}."""
    tree = ast.parse(source)
    nodes: list[dict] = []

    def visit(node: ast.AST) -> int:
        idx = len(nodes)
        rec: dict = {"type": type(node).__name__, "children": []}
        nodes.append(rec)
        value = getattr(node, "name", None) or getattr(node, "id", None) or getattr(node, "attr", None)
        if value is None and isinstance(node, ast.Constant) and isinstance(node.value, (str, int, float)):
            value = str(node.value)
        if value is not None:
            rec["value"] = str(value)
        for child in ast.iter_child_nodes(node):
            rec["children"].append(visit(child))
        return idx

    visit(tree)
    return nodes


def rel(path: Path) -> str:
    """Repo-relative when the output lives in the repo, absolute otherwise."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def qualifies(m: dict, floor: dict) -> bool:
    return (m["block_depth"] >= floor["block"]
            and m["loop_depth"] >= floor["loop"]
            and m["branch_depth"] >= floor["branch"]
            and m["n_lines"] >= floor["lines"])


# --------------------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="Generate long, deeply nested Python programs")
    ap.add_argument("--count", type=int, default=1000, help="programs to generate")
    ap.add_argument("--target-lines", type=int, default=700, help="minimum lines per program")
    ap.add_argument("--min-depth", type=int, default=4, help="per-unit nesting depth, low end")
    ap.add_argument("--max-depth", type=int, default=10, help="per-unit nesting depth, high end")
    ap.add_argument("--min-block-depth", type=int, default=8,
                    help="reject a file whose measured block nesting is shallower")
    ap.add_argument("--min-loop-depth", type=int, default=4)
    ap.add_argument("--min-branch-depth", type=int, default=4)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", default=str(ROOT / "data" / "nested_code" / "generated"))
    ap.add_argument("--with-ast", action="store_true", help="also write asts/<id>.json per file")
    ap.add_argument("--run-check", type=int, default=5,
                    help="execute this many random samples to prove they run (0 to skip)")
    ap.add_argument("--clean", action="store_true", help="delete previous output in --out first")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if args.clean:
        for stale in list(out.glob("*.py")) + list(out.glob("*.jsonl")) + list(out.glob("*.json")):
            stale.unlink()
        for stale in out.glob("asts/*.json"):
            stale.unlink()
    if args.with_ast:
        (out / "asts").mkdir(exist_ok=True)

    floor = {"block": args.min_block_depth, "loop": args.min_loop_depth,
             "branch": args.min_branch_depth, "lines": args.target_lines}

    manifest_path = out / "manifest.jsonl"
    dataset_path = out / "dataset.jsonl"
    seen_hashes: set[str] = set()
    records: list[dict] = []
    rejected = dupes = 0

    with manifest_path.open("w", encoding="utf-8") as mf, \
            dataset_path.open("w", encoding="utf-8") as df:
        for idx in range(1, args.count + 1):
            source = metrics = None
            kinds: list[str] = []
            for _ in range(8):  # retry until the measurement clears the floor
                candidate, kinds = make_program(
                    idx, rng, args.target_lines, args.min_depth, args.max_depth)
                try:
                    metrics_c = measure(candidate)
                    compile(candidate, f"<sample {idx}>", "exec")
                except SyntaxError as exc:
                    rejected += 1
                    print(f"  sample {idx}: invalid Python ({exc}) — retrying", file=sys.stderr)
                    continue
                digest = hashlib.sha256(candidate.encode()).hexdigest()[:16]
                if digest in seen_hashes:
                    dupes += 1
                    continue
                if not qualifies(metrics_c, floor):
                    rejected += 1
                    continue
                seen_hashes.add(digest)
                source, metrics, unit_kinds = candidate, metrics_c, kinds
                break
            if source is None or metrics is None:
                print(f"  sample {idx}: gave up after 8 attempts", file=sys.stderr)
                continue

            sid = (f"nested_{idx:05d}_D{metrics['block_depth']}"
                   f"_L{metrics['loop_depth']}_B{metrics['branch_depth']}")
            path = out / f"{sid}.py"
            path.write_text(source, encoding="utf-8")

            split = "train" if idx % 10 < 8 else ("val" if idx % 10 == 8 else "test")
            record = {
                "id": sid,
                "path": rel(path),
                "split": split,
                "unit_kinds": unit_kinds,
                "sha256_16": hashlib.sha256(source.encode()).hexdigest()[:16],
                "metrics": metrics,
            }
            if args.with_ast:
                ast_path = out / "asts" / f"{sid}.json"
                ast_path.write_text(json.dumps(to_json_ast(source)), encoding="utf-8")
                record["ast_path"] = rel(ast_path)
            mf.write(json.dumps(record) + "\n")
            df.write(json.dumps({**record, "source": source}) + "\n")
            records.append(record)

            if idx % 100 == 0:
                print(f"  {idx}/{args.count} ...")

    # ---- run-check: prove the programs actually execute -------------------------------
    failures: list[str] = []
    if args.run_check and records:
        sample = rng.sample(records, k=min(args.run_check, len(records)))
        for rec in sample:
            target = Path(rec["path"])
            target = target if target.is_absolute() else ROOT / target
            proc = subprocess.run([sys.executable, "-I", str(target)],
                                  capture_output=True, text=True, timeout=180)
            if proc.returncode != 0:
                failures.append(f"{rec['id']}: {proc.stderr.strip().splitlines()[-1:]}")

    # ---- stats ------------------------------------------------------------------------
    def dist(key: str) -> dict:
        c = Counter(r["metrics"][key] for r in records)
        return {str(k): c[k] for k in sorted(c)}

    total_lines = sum(r["metrics"]["n_lines"] for r in records)
    stats = {
        "n_samples": len(records),
        "total_lines": total_lines,
        "mean_lines": round(total_lines / max(1, len(records)), 1),
        "min_lines": min((r["metrics"]["n_lines"] for r in records), default=0),
        "max_lines": max((r["metrics"]["n_lines"] for r in records), default=0),
        "total_ast_nodes": sum(r["metrics"]["n_ast_nodes"] for r in records),
        "splits": dict(Counter(r["split"] for r in records)),
        "unit_kinds": dict(Counter(k for r in records for k in r["unit_kinds"]).most_common()),
        "block_depth": dist("block_depth"),
        "loop_depth": dist("loop_depth"),
        "branch_depth": dist("branch_depth"),
        "try_depth": dist("try_depth"),
        "with_depth": dist("with_depth"),
        "function_depth": dist("function_depth"),
        "comprehension_depth": dist("comprehension_depth"),
        "data_depth": dist("data_depth"),
        "with_nested_recursion": sum(1 for r in records if r["metrics"]["nested_recursion"]),
        "with_mutual_recursion": sum(1 for r in records if r["metrics"]["mutual_recursion"]),
        "floor": floor,
        "rejected_below_floor_or_invalid": rejected,
        "duplicates_discarded": dupes,
        "run_checked": min(args.run_check, len(records)) if args.run_check else 0,
        "run_check_failures": failures,
    }
    (out / "stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")

    print(f"\nwrote {len(records)} programs to {out}")
    print(f"  {total_lines:,} lines total, mean {stats['mean_lines']} per file, "
          f"longest {stats['max_lines']}")
    print(f"  block-depth distribution: {stats['block_depth']}")
    print(f"  loop-depth distribution:  {stats['loop_depth']}")
    print(f"  splits: {stats['splits']}")
    print(f"  rejected below floor/invalid: {rejected}, duplicates: {dupes}")
    if args.run_check:
        print(f"  run-checked {stats['run_checked']} samples: "
              f"{'all passed' if not failures else failures}")
    print(f"manifest: {manifest_path}")
    print(f"dataset:  {dataset_path}  (same records plus the source text)")
    print(f"stats:    {out / 'stats.json'}")
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
