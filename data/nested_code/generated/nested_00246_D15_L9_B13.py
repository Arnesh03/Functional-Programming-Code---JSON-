"""Generated sample 00246: 12 deeply nested units (async_nested, branch_pyramid, class_tower, comprehension, data_walk, loop_pyramid, match_nested, state_machine)."""
from __future__ import annotations

import asyncio
from contextlib import contextmanager, asynccontextmanager

THRESHOLD = 3
DEMO_MATRIX = [[(r * 3 + c) % 16 for c in range(8)] for r in range(6)]
DEMO_FLAT = [c for row in DEMO_MATRIX for c in row]
DEMO_TREE = {"value": 1, "children": [{"value": 3, "children": [{"value": 9, "children": [{"value": 1, "children": [{"value": 5, "children": [{"value": 8, "children": []}, 5]}, 1]}, 4]}, {"value": 3, "children": [{"value": 1, "children": [{"value": 5, "children": [{"value": 3, "children": []}, 4]}, 7]}, 3]}, 2]}, {"value": 5, "children": [{"value": 4, "children": [{"value": 7, "children": [{"value": 8, "children": [{"value": 6, "children": []}, 7]}, 7]}, 1]}, {"value": 7, "children": [{"value": 5, "children": [{"value": 8, "children": [{"value": 7, "children": []}, 6]}, 3]}, 7]}, 6]}, 2]}
DEMO_EVENTS = [
    {"kind": "row", "cells": [1, 7, 3]},
    {"kind": "row", "cells": [9, 8]},
    [4, 2, 1, 0],
    7,
    3.5,
    "sample",
    {"kind": "meta", "cells": []},
]
DEEP_TRACE_BUNDLE = [{"level": 6, "items": [([{"level": 3, "items": [([9, 1], 9), 6]}, 2], 8), 2]}, 8]


@contextmanager
def tracked(label, log):
    """Records entry and exit, so nested `with` blocks leave a trace."""
    if len(log) < 64:
        log.append(("enter", label))
    try:
        yield label
    finally:
        if len(log) < 64:
            log.append(("exit", label))


@asynccontextmanager
async def async_tracked(label, log):
    log.append(("enter", label))
    try:
        yield label
    finally:
        log.append(("exit", label))


async def arange(n):
    for i in range(n):
        if i >= 0:
            yield i


def merge_segment(matrix, weights=None, threshold=THRESHOLD):
    """Loops nested 8 deep; each floor carries a branch ladder."""
    weights = weights or {}
    total = running = score = 0
    value = 0
    seen, buckets, trace = set(), {}, []
    for row_index, row in enumerate(matrix):
        if not row:
            continue
        try:
            for i0 in range(min(len(row), 5)):
                value = row[i0] if i0 < len(row) else 0
                for i1, _slot in enumerate(row[:4]):
                    i2 = 0
                    while i2 < min(len(row), 3):
                        i2 += 1
                        value = row[i2] if i2 < len(row) else 2
                        for i3 in range(min(len(row), 2)):
                            for i4, _slot in enumerate(row[:2]):
                                value = row[i4] if i4 < len(row) else 4
                                i5 = 0
                                while i5 < min(len(row), 2):
                                    i5 += 1
                                    for i6 in range(min(len(row), 2)):
                                        value = row[i6] if i6 < len(row) else 6
                                        for i7, _slot in enumerate(row[:2]):
                                            seen.add((row_index, i7))
                                            buckets.setdefault(value % 8, []).append(i7)
                                            total += i7 * weights.get((i7, value), 1)
                                            running = (running * 31 + value + i7) % 1_000_003
                                            if len(trace) < 16:
                                                trace.append((row_index, i7, value))
                                            if value % 2 == 0 and i7 < 2:
                                                if value > threshold:
                                                    score += 2
                                                elif value:
                                                    score -= 1
                                                else:
                                                    score += 1
                                            elif value % 3 == 0:
                                                score += 3
                                            else:
                                                seen.discard((row_index, 0))
        except (IndexError, TypeError, ZeroDivisionError):
            continue
    return {"total": total, "running": running, "score": score,
            "buckets": len(buckets), "trace": trace[:8], "seen": len(seen)}


def weigh_registry(values, threshold=THRESHOLD):
    """An if/elif/else ladder nested 6 deep, inside a loop."""
    score = skipped = 0
    matched, seen = [], set()
    window = list(values)[:24]
    depth_budget = 10
    for value in window:
        if value is None:
            skipped += 1
            continue
        if not isinstance(value, int):
            value = len(str(value))
        if depth_budget - 2 > 0:
            score += 1
            if 3 < len(window) and window[3] is not None:
                score += 2
                if value % 4 == 0:
                    score += 3
                    if value % 5 == 0:
                        score += 4
                        if 6 < len(window) and window[6] is not None:
                            score += 5
                            if value % 7 == 0:
                                score += 6
                                matched.append(('deep', value))
                            elif value % 8 == 0:
                                score -= 1
                                matched.append(('alt', 5))
                            else:
                                skipped += 1
                        elif value % 7 == 0:
                            score -= 1
                            matched.append(('alt', 4))
                        else:
                            skipped += 1
                    elif value % 6 == 0:
                        score -= 1
                        matched.append(('alt', 3))
                    else:
                        skipped += 1
                elif value % 5 == 0:
                    score -= 1
                    matched.append(('alt', 2))
                else:
                    skipped += 1
            elif value % 4 == 0:
                score -= 1
                if 4 < len(window) and window[4] is not None:
                    score += 3
                    if value & 5 == 0:
                        score += 4
                        if isinstance(value, int) and value not in seen:
                            score += 5
                            if depth_budget - 7 > 0:
                                score += 6
                                matched.append(('deep', value))
                            elif value % 8 == 0:
                                score -= 1
                                matched.append(('alt', 5))
                            else:
                                skipped += 1
                        elif value % 7 == 0:
                            score -= 1
                            matched.append(('alt', 4))
                        else:
                            skipped += 1
                    elif value % 6 == 0:
                        score -= 1
                        matched.append(('alt', 3))
                    else:
                        skipped += 1
                elif value % 5 == 0:
                    score -= 1
                    matched.append(('alt', 2))
                else:
                    skipped += 1
            else:
                skipped += 1
        elif value % 3 == 0:
            score -= 1
            if depth_budget - 3 > 0:
                score += 2
                if value & 4 == 0:
                    score += 3
                    if value > threshold * 5:
                        score += 4
                        if 6 < len(window) and window[6] is not None:
                            score += 5
                            if value % 7 == 0:
                                score += 6
                                matched.append(('deep', value))
                            elif value % 8 == 0:
                                score -= 1
                                matched.append(('alt', 5))
                            else:
                                skipped += 1
                        elif value % 7 == 0:
                            score -= 1
                            matched.append(('alt', 4))
                        else:
                            skipped += 1
                    elif value % 6 == 0:
                        score -= 1
                        matched.append(('alt', 3))
                    else:
                        skipped += 1
                elif value % 5 == 0:
                    score -= 1
                    matched.append(('alt', 2))
                else:
                    skipped += 1
            elif value % 4 == 0:
                score -= 1
                if value & 4 == 0:
                    score += 3
                    if abs(value) + 5 > score:
                        score += 4
                        if value % 6 == 0:
                            score += 5
                            if depth_budget - 7 > 0:
                                score += 6
                                matched.append(('deep', value))
                            elif value % 8 == 0:
                                score -= 1
                                matched.append(('alt', 5))
                            else:
                                skipped += 1
                        elif value % 7 == 0:
                            score -= 1
                            matched.append(('alt', 4))
                        else:
                            skipped += 1
                    elif value % 6 == 0:
                        score -= 1
                        matched.append(('alt', 3))
                    else:
                        skipped += 1
                elif value % 5 == 0:
                    score -= 1
                    matched.append(('alt', 2))
                else:
                    skipped += 1
            else:
                skipped += 1
        else:
            skipped += 1
            if value > threshold * 3:
                score += 2
                if abs(value) + 4 > score:
                    score += 3
                    if value > threshold * 5:
                        score += 4
                        if value & 6 == 0:
                            score += 5
                            if isinstance(value, int) and value not in seen:
                                score += 6
                                matched.append(('deep', value))
                            elif value % 8 == 0:
                                score -= 1
                                matched.append(('alt', 5))
                            else:
                                skipped += 1
                        elif value % 7 == 0:
                            score -= 1
                            matched.append(('alt', 4))
                        else:
                            skipped += 1
                    elif value % 6 == 0:
                        score -= 1
                        matched.append(('alt', 3))
                    else:
                        skipped += 1
                elif value % 5 == 0:
                    score -= 1
                    matched.append(('alt', 2))
                else:
                    skipped += 1
            elif value % 4 == 0:
                score -= 1
                if value & 4 == 0:
                    score += 3
                    if value > threshold * 5:
                        score += 4
                        if depth_budget - 6 > 0:
                            score += 5
                            if isinstance(value, int) and value not in seen:
                                score += 6
                                matched.append(('deep', value))
                            elif value % 8 == 0:
                                score -= 1
                                matched.append(('alt', 5))
                            else:
                                skipped += 1
                        elif value % 7 == 0:
                            score -= 1
                            matched.append(('alt', 4))
                        else:
                            skipped += 1
                    elif value % 6 == 0:
                        score -= 1
                        matched.append(('alt', 3))
                    else:
                        skipped += 1
                elif value % 5 == 0:
                    score -= 1
                    matched.append(('alt', 2))
                else:
                    skipped += 1
            else:
                skipped += 1
        seen.add(value)
    return {"score": score, "skipped": skipped, "matched": matched[:8], "seen": len(seen)}


def merge_roster(matrix, weights=None, threshold=THRESHOLD):
    """Loops nested 5 deep; each floor carries a branch ladder."""
    weights = weights or {}
    total = running = score = 0
    value = 0
    seen, buckets, trace = set(), {}, []
    for row_index, row in enumerate(matrix):
        if not row:
            continue
        try:
            for i0 in range(min(len(row), 5)):
                value = row[i0] if i0 < len(row) else 0
                for i1, _slot in enumerate(row[:4]):
                    i2 = 0
                    while i2 < min(len(row), 3):
                        i2 += 1
                        value = row[i2] if i2 < len(row) else 2
                        for i3 in range(min(len(row), 2)):
                            for i4, _slot in enumerate(row[:2]):
                                value = row[i4] if i4 < len(row) else 4
                                total += i4 * weights.get((i4, value), 1)
                                seen.add((row_index, i4))
                                total ^= (value << (i4 % 5)) & 0xFFFF
                                if len(trace) < 16:
                                    trace.append((row_index, i4, value))
                                if value % 2 == 0 and i4 < 2:
                                    if value > threshold:
                                        score += 2
                                    elif value:
                                        score -= 1
                                    else:
                                        score += 1
                                elif value % 3 == 0:
                                    score += 3
                                else:
                                    seen.discard((row_index, 0))
        except (IndexError, TypeError, ZeroDivisionError):
            continue
    return {"total": total, "running": running, "score": score,
            "buckets": len(buckets), "trace": trace[:8], "seen": len(seen)}


def flatten_channel(events):
    """match/case inside match/case inside a loop."""
    out = []
    for event in events:
        match event:
            case {"kind": "row", "cells": [first, *rest]}:
                out.append(("first", first))
                for cell in rest:
                    match cell:
                        case int() if cell > 5:
                            for k in range(2):
                                if (cell + k) % 2:
                                    out.append(("big", cell, k))
                        case int():
                            out.append(("small", cell))
                        case _:
                            out.append(("other", str(cell)[:4]))
            case [a, b, *tail]:
                if a > b:
                    out.append(("desc", a, b, len(tail)))
                else:
                    out.append(("asc", a, b, len(tail)))
            case int() | float() as num:
                if num > 0:
                    out.append(("num", num))
            case str() as text if text.startswith("s"):
                out.append(("text", text[:4]))
            case _:
                out.append(("unmatched",))
    return out[:12]


def chart_window(matrix):
    """Comprehensions inside comprehensions, then a loop that consumes them."""
    grid = [[cell for cell in row if cell % 2 == 0] for row in matrix if row]
    folded = {r: {c: [v for v in row[:c + 1] if v]
                  for c in range(min(3, len(row)))}
              for r, row in enumerate(matrix)}
    chained = [v for row in grid for v in row if any(v > w for w in row[:2])]
    paired = {(r, c): sum(v for v in vals if v)
              for r, cols in folded.items() for c, vals in cols.items()}
    counted = sum(sum(1 for v in row if v) for row in matrix)
    deep = [[[v + k for k in range(2) if (v + k) % 3]
             for v in row if v] for row in grid]
    out = []
    for key, value in sorted(paired.items()):
        if value:
            for bucket in deep:
                if bucket:
                    for inner in bucket:
                        if any(x > value for x in inner):
                            out.append((key, value))
                            break
    return {"grid": len(grid), "chained": chained[:6], "counted": counted,
            "paired": len(paired), "out": out[:6]}


def trace_bundle(blob=None, depth=0, budget=8):
    """Recursive descent over a deeply nested literal."""
    blob = DEEP_TRACE_BUNDLE if blob is None else blob
    if budget <= 0:
        return {"depth": depth, "leaves": 0}
    leaves = 0
    deepest = depth
    if isinstance(blob, dict):
        for key, child in blob.items():
            if isinstance(child, (dict, list, tuple)):
                inner = trace_bundle(child, depth + 1, budget - 1)
                deepest = max(deepest, inner["depth"])
                leaves += inner["leaves"]
            elif isinstance(child, int):
                if child % 2 == 0:
                    leaves += 1
                else:
                    leaves += 2
    elif isinstance(blob, (list, tuple)):
        for item in blob:
            if isinstance(item, (dict, list, tuple)):
                inner = trace_bundle(item, depth + 1, budget - 1)
                deepest = max(deepest, inner["depth"])
                leaves += inner["leaves"]
            else:
                leaves += 1
    else:
        leaves += 1
    return {"depth": deepest, "leaves": leaves}


class Lattice46:
    """A class with an inner class and deeply nested methods."""
    LIMIT = 8

    def __init__(self, matrix=None):
        self.matrix = matrix or []
        self.cache = {}
        self.log = []

    class Inner:
        """Nested class; its own methods nest again."""

        def __init__(self, span=3):
            self.span = span

        def expand(self, n):
            out = []
            for i in range(min(n, self.span)):
                for j in range(i + 1):
                    if (i + j) % 2 == 0:
                        for k in range(min(j + 1, 2)):
                            if k <= j:
                                out.append((i, j, k))
                    else:
                        out.append((i, j, -1))
            return out

    def tally(self, matrix=None):
        """Nested loops over rows, memoised per row."""
        matrix = matrix if matrix is not None else self.matrix
        total = 0
        for row_index, row in enumerate(matrix):
            key = (row_index, len(row))
            if key in self.cache:
                total += self.cache[key]
                continue
            subtotal = 0
            for c0 in range(min(len(row), 4)):
                for c1 in range(min(len(row), 3)):
                    for c2 in range(min(len(row), 2)):
                        for c3 in range(min(len(row), 2)):
                            for c4 in range(min(len(row), 2)):
                                for c5 in range(min(len(row), 2)):
                                    for c6 in range(min(len(row), 2)):
                                        for c7 in range(min(len(row), 2)):
                                            if row[c0] % 2:
                                                subtotal += row[c0]
                                            else:
                                                subtotal -= 1
            self.cache[key] = subtotal
            total += subtotal
        return total

    @staticmethod
    def fold(rows):
        acc = []
        for row in rows:
            try:
                for v in row:
                    if v % 3 == 0:
                        for w in range(2):
                            acc.append(v + w)
            except TypeError:
                continue
        return acc[:12]

    @property
    def summary(self):
        return {"rows": len(self.matrix), "cached": len(self.cache)}


def distil_payload(events):
    """match/case inside match/case inside a loop."""
    out = []
    for event in events:
        match event:
            case {"kind": "row", "cells": [first, *rest]}:
                out.append(("first", first))
                for cell in rest:
                    match cell:
                        case int() if cell > 5:
                            for k in range(2):
                                if (cell + k) % 2:
                                    out.append(("big", cell, k))
                        case int():
                            out.append(("small", cell))
                        case _:
                            out.append(("other", str(cell)[:4]))
            case [a, b, *tail]:
                if a > b:
                    out.append(("desc", a, b, len(tail)))
                else:
                    out.append(("asc", a, b, len(tail)))
            case int() | float() as num:
                if num > 0:
                    out.append(("num", num))
            case str() as text if text.startswith("s"):
                out.append(("text", text[:4]))
            case _:
                out.append(("unmatched",))
    return out[:12]


def probe_lattice(matrix, max_steps=48):
    """while + try + for/else + break/continue, nested."""
    state = "start"
    steps = 0
    log, found = [], []
    while steps < max_steps:
        steps += 1
        try:
            if state == "start":
                for row in matrix:
                    if not row:
                        continue
                    for v in row:
                        if v % 3 == 0:
                            state = "collect"
                            break
                    else:
                        continue
                    break
                else:
                    state = "done"
            elif state == "collect":
                for row_index, row in enumerate(matrix):
                    for i, v in enumerate(row):
                        if v and v % 2 == 0:
                            if len(found) < 12:
                                found.append((row_index, i, v))
                            else:
                                state = "verify"
                                break
                    if state == "verify":
                        break
                else:
                    state = "verify"
            elif state == "verify":
                for row_index, i, v in found:
                    if v < 0:
                        raise RuntimeError("negative cell")
                state = "done"
            else:
                break
        except RuntimeError:
            state = "done"
        finally:
            if len(log) < 24:
                log.append(state)
        if state == "done":
            break
    return {"state": state, "steps": steps, "found": found[:6], "log": log[:6]}


def merge_ledger(events):
    """match/case inside match/case inside a loop."""
    out = []
    for event in events:
        match event:
            case {"kind": "row", "cells": [first, *rest]}:
                out.append(("first", first))
                for cell in rest:
                    match cell:
                        case int() if cell > 5:
                            for k in range(2):
                                if (cell + k) % 2:
                                    out.append(("big", cell, k))
                        case int():
                            out.append(("small", cell))
                        case _:
                            out.append(("other", str(cell)[:4]))
            case [a, b, *tail]:
                if a > b:
                    out.append(("desc", a, b, len(tail)))
                else:
                    out.append(("asc", a, b, len(tail)))
            case int() | float() as num:
                if num > 0:
                    out.append(("num", num))
            case str() as text if text.startswith("s"):
                out.append(("text", text[:4]))
            case _:
                out.append(("unmatched",))
    return out[:12]


async def reduce_payload(matrix):
    """async with / async for / await, nested inside ordinary loops."""
    seen, log = [], []
    async with async_tracked("outer", log):
        for row in matrix:
            if not row:
                continue
            async for i in arange(min(len(row), 3)):
                if row[i] % 2 == 0:
                    async with async_tracked(f"cell{i}", log):
                        for j in range(i + 1):
                            if row[j] > 0:
                                seen.append((i, j, row[j]))
                            else:
                                await asyncio.sleep(0)
                else:
                    try:
                        seen.append((i, row[i] // (i + 1)))
                    except ZeroDivisionError:
                        continue
    return {"seen": seen[:8], "log": len(log)}


def trace_matrix(values, threshold=THRESHOLD):
    """An if/elif/else ladder nested 10 deep, inside a loop."""
    score = skipped = 0
    matched, seen = [], set()
    window = list(values)[:24]
    depth_budget = 14
    for value in window:
        if value is None:
            skipped += 1
            continue
        if not isinstance(value, int):
            value = len(str(value))
        if isinstance(value, int) and value not in seen:
            score += 1
            if abs(value) + 3 > score:
                score += 2
                if isinstance(value, int) and value not in seen:
                    score += 3
                    if value & 5 == 0:
                        score += 4
                        if 6 < len(window) and window[6] is not None:
                            score += 5
                            if depth_budget - 7 > 0:
                                score += 6
                                if 8 < len(window) and window[8] is not None:
                                    score += 7
                                    if isinstance(value, int) and value not in seen:
                                        score += 8
                                        if depth_budget - 10 > 0:
                                            score += 9
                                            if value > threshold * 11:
                                                score += 10
                                                matched.append(('deep', value))
                                            elif value % 12 == 0:
                                                score -= 1
                                                matched.append(('alt', 9))
                                            else:
                                                skipped += 1
                                        elif value % 11 == 0:
                                            score -= 1
                                            matched.append(('alt', 8))
                                        else:
                                            skipped += 1
                                    elif value % 10 == 0:
                                        score -= 1
                                        matched.append(('alt', 7))
                                    else:
                                        skipped += 1
                                elif value % 9 == 0:
                                    score -= 1
                                    matched.append(('alt', 6))
                                else:
                                    skipped += 1
                            elif value % 8 == 0:
                                score -= 1
                                matched.append(('alt', 5))
                            else:
                                skipped += 1
                        elif value % 7 == 0:
                            score -= 1
                            matched.append(('alt', 4))
                        else:
                            skipped += 1
                    elif value % 6 == 0:
                        score -= 1
                        matched.append(('alt', 3))
                    else:
                        skipped += 1
                elif value % 5 == 0:
                    score -= 1
                    matched.append(('alt', 2))
                else:
                    skipped += 1
            elif value % 4 == 0:
                score -= 1
                if value > threshold * 4:
                    score += 3
                    if value & 5 == 0:
                        score += 4
                        if isinstance(value, int) and value not in seen:
                            score += 5
                            if value & 7 == 0:
                                score += 6
                                if depth_budget - 8 > 0:
                                    score += 7
                                    if depth_budget - 9 > 0:
                                        score += 8
                                        if value > threshold * 10:
                                            score += 9
                                            if 11 < len(window) and window[11] is not None:
                                                score += 10
                                                matched.append(('deep', value))
                                            elif value % 12 == 0:
                                                score -= 1
                                                matched.append(('alt', 9))
                                            else:
                                                skipped += 1
                                        elif value % 11 == 0:
                                            score -= 1
                                            matched.append(('alt', 8))
                                        else:
                                            skipped += 1
                                    elif value % 10 == 0:
                                        score -= 1
                                        matched.append(('alt', 7))
                                    else:
                                        skipped += 1
                                elif value % 9 == 0:
                                    score -= 1
                                    matched.append(('alt', 6))
                                else:
                                    skipped += 1
                            elif value % 8 == 0:
                                score -= 1
                                matched.append(('alt', 5))
                            else:
                                skipped += 1
                        elif value % 7 == 0:
                            score -= 1
                            matched.append(('alt', 4))
                        else:
                            skipped += 1
                    elif value % 6 == 0:
                        score -= 1
                        matched.append(('alt', 3))
                    else:
                        skipped += 1
                elif value % 5 == 0:
                    score -= 1
                    matched.append(('alt', 2))
                else:
                    skipped += 1
            else:
                skipped += 1
        elif value % 3 == 0:
            score -= 1
            if 3 < len(window) and window[3] is not None:
                score += 2
                if abs(value) + 4 > score:
                    score += 3
                    if abs(value) + 5 > score:
                        score += 4
                        if value & 6 == 0:
                            score += 5
                            if value > threshold * 7:
                                score += 6
                                if abs(value) + 8 > score:
                                    score += 7
                                    if isinstance(value, int) and value not in seen:
                                        score += 8
                                        if 10 < len(window) and window[10] is not None:
                                            score += 9
                                            if abs(value) + 11 > score:
                                                score += 10
                                                matched.append(('deep', value))
                                            elif value % 12 == 0:
                                                score -= 1
                                                matched.append(('alt', 9))
                                            else:
                                                skipped += 1
                                        elif value % 11 == 0:
                                            score -= 1
                                            matched.append(('alt', 8))
                                        else:
                                            skipped += 1
                                    elif value % 10 == 0:
                                        score -= 1
                                        matched.append(('alt', 7))
                                    else:
                                        skipped += 1
                                elif value % 9 == 0:
                                    score -= 1
                                    matched.append(('alt', 6))
                                else:
                                    skipped += 1
                            elif value % 8 == 0:
                                score -= 1
                                matched.append(('alt', 5))
                            else:
                                skipped += 1
                        elif value % 7 == 0:
                            score -= 1
                            matched.append(('alt', 4))
                        else:
                            skipped += 1
                    elif value % 6 == 0:
                        score -= 1
                        matched.append(('alt', 3))
                    else:
                        skipped += 1
                elif value % 5 == 0:
                    score -= 1
                    matched.append(('alt', 2))
                else:
                    skipped += 1
            elif value % 4 == 0:
                score -= 1
                if depth_budget - 4 > 0:
                    score += 3
                    if 5 < len(window) and window[5] is not None:
                        score += 4
                        if isinstance(value, int) and value not in seen:
                            score += 5
                            if value % 7 == 0:
                                score += 6
                                if value > threshold * 8:
                                    score += 7
                                    if isinstance(value, int) and value not in seen:
                                        score += 8
                                        if abs(value) + 10 > score:
                                            score += 9
                                            if value > threshold * 11:
                                                score += 10
                                                matched.append(('deep', value))
                                            elif value % 12 == 0:
                                                score -= 1
                                                matched.append(('alt', 9))
                                            else:
                                                skipped += 1
                                        elif value % 11 == 0:
                                            score -= 1
                                            matched.append(('alt', 8))
                                        else:
                                            skipped += 1
                                    elif value % 10 == 0:
                                        score -= 1
                                        matched.append(('alt', 7))
                                    else:
                                        skipped += 1
                                elif value % 9 == 0:
                                    score -= 1
                                    matched.append(('alt', 6))
                                else:
                                    skipped += 1
                            elif value % 8 == 0:
                                score -= 1
                                matched.append(('alt', 5))
                            else:
                                skipped += 1
                        elif value % 7 == 0:
                            score -= 1
                            matched.append(('alt', 4))
                        else:
                            skipped += 1
                    elif value % 6 == 0:
                        score -= 1
                        matched.append(('alt', 3))
                    else:
                        skipped += 1
                elif value % 5 == 0:
                    score -= 1
                    matched.append(('alt', 2))
                else:
                    skipped += 1
            else:
                skipped += 1
        else:
            skipped += 1
            if value & 3 == 0:
                score += 2
                if isinstance(value, int) and value not in seen:
                    score += 3
                    if isinstance(value, int) and value not in seen:
                        score += 4
                        if value % 6 == 0:
                            score += 5
                            if value % 7 == 0:
                                score += 6
                                if abs(value) + 8 > score:
                                    score += 7
                                    if value > threshold * 9:
                                        score += 8
                                        if depth_budget - 10 > 0:
                                            score += 9
                                            if 11 < len(window) and window[11] is not None:
                                                score += 10
                                                matched.append(('deep', value))
                                            elif value % 12 == 0:
                                                score -= 1
                                                matched.append(('alt', 9))
                                            else:
                                                skipped += 1
                                        elif value % 11 == 0:
                                            score -= 1
                                            matched.append(('alt', 8))
                                        else:
                                            skipped += 1
                                    elif value % 10 == 0:
                                        score -= 1
                                        matched.append(('alt', 7))
                                    else:
                                        skipped += 1
                                elif value % 9 == 0:
                                    score -= 1
                                    matched.append(('alt', 6))
                                else:
                                    skipped += 1
                            elif value % 8 == 0:
                                score -= 1
                                matched.append(('alt', 5))
                            else:
                                skipped += 1
                        elif value % 7 == 0:
                            score -= 1
                            matched.append(('alt', 4))
                        else:
                            skipped += 1
                    elif value % 6 == 0:
                        score -= 1
                        matched.append(('alt', 3))
                    else:
                        skipped += 1
                elif value % 5 == 0:
                    score -= 1
                    matched.append(('alt', 2))
                else:
                    skipped += 1
            elif value % 4 == 0:
                score -= 1
                if value % 4 == 0:
                    score += 3
                    if isinstance(value, int) and value not in seen:
                        score += 4
                        if depth_budget - 6 > 0:
                            score += 5
                            if abs(value) + 7 > score:
                                score += 6
                                if abs(value) + 8 > score:
                                    score += 7
                                    if value > threshold * 9:
                                        score += 8
                                        if depth_budget - 10 > 0:
                                            score += 9
                                            if depth_budget - 11 > 0:
                                                score += 10
                                                matched.append(('deep', value))
                                            elif value % 12 == 0:
                                                score -= 1
                                                matched.append(('alt', 9))
                                            else:
                                                skipped += 1
                                        elif value % 11 == 0:
                                            score -= 1
                                            matched.append(('alt', 8))
                                        else:
                                            skipped += 1
                                    elif value % 10 == 0:
                                        score -= 1
                                        matched.append(('alt', 7))
                                    else:
                                        skipped += 1
                                elif value % 9 == 0:
                                    score -= 1
                                    matched.append(('alt', 6))
                                else:
                                    skipped += 1
                            elif value % 8 == 0:
                                score -= 1
                                matched.append(('alt', 5))
                            else:
                                skipped += 1
                        elif value % 7 == 0:
                            score -= 1
                            matched.append(('alt', 4))
                        else:
                            skipped += 1
                    elif value % 6 == 0:
                        score -= 1
                        matched.append(('alt', 3))
                    else:
                        skipped += 1
                elif value % 5 == 0:
                    score -= 1
                    matched.append(('alt', 2))
                else:
                    skipped += 1
            else:
                skipped += 1
        seen.add(value)
    return {"score": score, "skipped": skipped, "matched": matched[:8], "seen": len(seen)}


def pipeline_00246():
    """Drive every unit above, so nothing in this file is dead code."""
    results = {}
    results["merge_segment"] = merge_segment(DEMO_MATRIX)
    results["weigh_registry"] = weigh_registry(DEMO_FLAT)
    results["merge_roster"] = merge_roster(DEMO_MATRIX)
    results["flatten_channel"] = flatten_channel(DEMO_EVENTS)
    results["chart_window"] = chart_window(DEMO_MATRIX)
    results["trace_bundle"] = trace_bundle()
    results["Lattice46"] = Lattice46(DEMO_MATRIX).tally()
    results["distil_payload"] = distil_payload(DEMO_EVENTS)
    results["probe_lattice"] = probe_lattice(DEMO_MATRIX)
    results["merge_ledger"] = merge_ledger(DEMO_EVENTS)
    results["reduce_payload"] = asyncio.run(reduce_payload(DEMO_MATRIX))
    results["trace_matrix"] = trace_matrix(DEMO_FLAT)
    digest = 0
    for key, value in sorted(results.items()):
        if isinstance(value, dict):
            for sub in value.values():
                if isinstance(sub, (list, tuple, set, dict, str)):
                    digest += len(sub)
                elif isinstance(sub, int):
                    digest += sub % 97
        elif isinstance(value, (list, tuple, set)):
            digest += len(value)
        elif isinstance(value, int):
            digest += value % 97
        else:
            digest += 1
    return {"units": len(results), "digest": digest % 100_003}


if __name__ == "__main__":
    print(pipeline_00246())
