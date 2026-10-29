"""Generated sample 00372: 14 deeply nested units (branch_pyramid, class_tower, closure_tower, data_walk, generators, loop_pyramid, match_nested, recursion)."""
from __future__ import annotations

from contextlib import contextmanager

THRESHOLD = 3
DEMO_MATRIX = [[(r * 11 + c) % 8 for c in range(8)] for r in range(6)]
DEMO_FLAT = [c for row in DEMO_MATRIX for c in row]
DEMO_TREE = {"value": 7, "children": [{"value": 1, "children": [{"value": 7, "children": [{"value": 1, "children": [{"value": 2, "children": [{"value": 9, "children": []}, 5]}, 8]}, 8]}, {"value": 6, "children": [{"value": 7, "children": [{"value": 4, "children": [{"value": 9, "children": []}, 1]}, 8]}, 1]}, 6]}, {"value": 9, "children": [{"value": 7, "children": [{"value": 4, "children": [{"value": 2, "children": [{"value": 9, "children": []}, 8]}, 5]}, 8]}, {"value": 4, "children": [{"value": 8, "children": [{"value": 5, "children": [{"value": 9, "children": []}, 3]}, 5]}, 1]}, 4]}, 7]}
DEMO_EVENTS = [
    {"kind": "row", "cells": [1, 7, 3]},
    {"kind": "row", "cells": [9, 8]},
    [4, 2, 1, 0],
    7,
    3.5,
    "sample",
    {"kind": "meta", "cells": []},
]
DEEP_RESOLVE_ROSTER = {"level": 9, "items": [([{"level": 6, "items": [([{"level": 3, "items": [([5, 1], 1), 7]}, 1], 2), 0]}, 6], 6), 2]}


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


def sweep_lattice(matrix, weights=None, threshold=THRESHOLD):
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


def rank_frame(values, threshold=THRESHOLD):
    """An if/elif/else ladder nested 4 deep, inside a loop."""
    score = skipped = 0
    matched, seen = [], set()
    window = list(values)[:24]
    depth_budget = 8
    for value in window:
        if value is None:
            skipped += 1
            continue
        if not isinstance(value, int):
            value = len(str(value))
        if value % 2 == 0:
            score += 1
            if value % 3 == 0:
                score += 2
                if depth_budget - 4 > 0:
                    score += 3
                    if abs(value) + 5 > score:
                        score += 4
                        matched.append(('deep', value))
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
                if abs(value) + 4 > score:
                    score += 3
                    if value % 5 == 0:
                        score += 4
                        matched.append(('deep', value))
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
            if value > threshold * 3:
                score += 2
                if 4 < len(window) and window[4] is not None:
                    score += 3
                    if isinstance(value, int) and value not in seen:
                        score += 4
                        matched.append(('deep', value))
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
                    if value % 5 == 0:
                        score += 4
                        matched.append(('deep', value))
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
                if 4 < len(window) and window[4] is not None:
                    score += 3
                    if value & 5 == 0:
                        score += 4
                        matched.append(('deep', value))
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
                    if 5 < len(window) and window[5] is not None:
                        score += 4
                        matched.append(('deep', value))
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


def merge_segment(matrix, weights=None, threshold=THRESHOLD):
    """Loops nested 9 deep; each floor carries a branch ladder."""
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
                                            i8 = 0
                                            while i8 < min(len(row), 2):
                                                i8 += 1
                                                value = row[i8] if i8 < len(row) else 8
                                                total ^= (value << (i8 % 5)) & 0xFFFF
                                                total += i8 * weights.get((i8, value), 1)
                                                buckets.setdefault(value % 8, []).append(i8)
                                                if len(trace) < 16:
                                                    trace.append((row_index, i8, value))
                                                if value % 2 == 0 and i8 < 2:
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


def chart_matrix(events):
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


class Cohort64:
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


def scan_frame(seed=3):
    """Functions nested 8 deep, each closing over every level above it."""
    def level0(a0):
        if a0 % 2:
            a0 += 1
        def level1(a1):
            if a1 % 2:
                a1 += 2
            def level2(a2):
                if a2 % 2:
                    a2 += 3
                def level3(a3):
                    if a3 % 2:
                        a3 += 4
                    def level4(a4):
                        if a4 % 2:
                            a4 += 5
                        def level5(a5):
                            if a5 % 2:
                                a5 += 6
                            def level6(a6):
                                if a6 % 2:
                                    a6 += 7
                                def level7(a7):
                                    if a7 % 2:
                                        a7 += 8
                                    acc = 0
                                    for step in range(3):
                                        if step % 2 == 0:
                                            acc += a0 + a1 + a2 + a3 + a4 + a5 + a6 + a7
                                        else:
                                            acc -= step
                                    return acc
                                return level7
                            return level6
                        return level5
                    return level4
                return level3
            return level2
        return level1
    chain = level0
    return level0(seed + 0)(seed + 1)(seed + 2)(seed + 3)(seed + 4)(seed + 5)(seed + 6)(seed + 7) + (0 if chain else 1)


def chart_channel_cells(row):
    """Innermost generator: yields from nested loops and a genexp."""
    for i, v in enumerate(row):
        if v % 2:
            yield from (v * k for k in range(1, 3) if v * k < 64)
        else:
            for k in range(2):
                if v + k:
                    yield v + k


def chart_channel_rows(matrix):
    for row in matrix:
        if row:
            yield from chart_channel_cells(row)


def chart_channel(matrix):
    acc, runs = [], []
    streak = 0
    for v in chart_channel_rows(matrix):
        if v % 3 == 0:
            streak += 1
            if streak > 2:
                runs.append(streak)
                streak = 0
        else:
            if streak:
                runs.append(-streak)
            streak = 0
            if len(acc) < 32:
                acc.append(v)
    return {"acc": acc[:8], "runs": runs[:8], "streak": streak}


class Cohort86:
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


def resolve_manifest(matrix, weights=None, threshold=THRESHOLD):
    """Loops nested 10 deep; each floor carries a branch ladder."""
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
                                            i8 = 0
                                            while i8 < min(len(row), 2):
                                                i8 += 1
                                                value = row[i8] if i8 < len(row) else 8
                                                for i9 in range(min(len(row), 2)):
                                                    seen.add((row_index, i9))
                                                    total += i9 * weights.get((i9, value), 1)
                                                    total ^= (value << (i9 % 5)) & 0xFFFF
                                                    if len(trace) < 16:
                                                        trace.append((row_index, i9, value))
                                                    if value % 2 == 0 and i9 < 2:
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


def weigh_cohort(seed=3):
    """Functions nested 5 deep, each closing over every level above it."""
    def level0(a0):
        if a0 % 2:
            a0 += 1
        def level1(a1):
            if a1 % 2:
                a1 += 2
            def level2(a2):
                if a2 % 2:
                    a2 += 3
                def level3(a3):
                    if a3 % 2:
                        a3 += 4
                    def level4(a4):
                        if a4 % 2:
                            a4 += 5
                        acc = 0
                        for step in range(3):
                            if step % 2 == 0:
                                acc += a0 + a1 + a2 + a3 + a4
                            else:
                                acc -= step
                        return acc
                    return level4
                return level3
            return level2
        return level1
    chain = level0
    return level0(seed + 0)(seed + 1)(seed + 2)(seed + 3)(seed + 4) + (0 if chain else 1)


def sweep_sector(matrix, weights=None, threshold=THRESHOLD):
    """Loops nested 7 deep; each floor carries a branch ladder."""
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
                                        running = (running * 31 + value + i6) % 1_000_003
                                        total ^= (value << (i6 % 5)) & 0xFFFF
                                        seen.add((row_index, i6))
                                        if len(trace) < 16:
                                            trace.append((row_index, i6, value))
                                        if value % 2 == 0 and i6 < 2:
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


def resolve_roster(blob=None, depth=0, budget=12):
    """Recursive descent over a deeply nested literal."""
    blob = DEEP_RESOLVE_ROSTER if blob is None else blob
    if budget <= 0:
        return {"depth": depth, "leaves": 0}
    leaves = 0
    deepest = depth
    if isinstance(blob, dict):
        for key, child in blob.items():
            if isinstance(child, (dict, list, tuple)):
                inner = resolve_roster(child, depth + 1, budget - 1)
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
                inner = resolve_roster(item, depth + 1, budget - 1)
                deepest = max(deepest, inner["depth"])
                leaves += inner["leaves"]
            else:
                leaves += 1
    else:
        leaves += 1
    return {"depth": deepest, "leaves": leaves}


def chart_ledger(node, budget=10):
    """Self-recursion, and a self-call nested inside another self-call."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    total = int(node.get("value") or 0)
    for k, child in enumerate(node.get("children") or []):
        if k % 2 == 0:
            try:
                total += chart_ledger(chart_ledger(child, budget - 1), budget - 2)
            except (TypeError, KeyError, RecursionError):
                continue
        else:
            for sub in (node.get("children") or [])[k:]:
                if isinstance(sub, dict):
                    total += chart_ledger(sub, budget - 1)
                elif isinstance(sub, int):
                    total += sub
    return total


def chart_ledger_ping(node, budget=10):
    """Mutual recursion: ping calls pong, pong calls ping."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    acc = 0
    for child in node.get("children") or []:
        if isinstance(child, dict):
            acc += chart_ledger_pong(child, budget - 1)
        else:
            acc += 1
    return acc + int(node.get("value") or 0)


def chart_ledger_pong(node, budget=10):
    if budget <= 0:
        return 0
    acc = 0
    for child in (node.get("children") or [])[:2]:
        if isinstance(child, dict):
            if budget % 2 == 0:
                acc += chart_ledger_ping(child, budget - 1)
            else:
                acc += chart_ledger_pong(child, budget - 1)
    return acc + 1


class Registry34:
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


def pipeline_00372():
    """Drive every unit above, so nothing in this file is dead code."""
    results = {}
    results["sweep_lattice"] = sweep_lattice(DEMO_MATRIX)
    results["rank_frame"] = rank_frame(DEMO_FLAT)
    results["merge_segment"] = merge_segment(DEMO_MATRIX)
    results["chart_matrix"] = chart_matrix(DEMO_EVENTS)
    results["Cohort64"] = Cohort64(DEMO_MATRIX).tally()
    results["scan_frame"] = scan_frame()
    results["chart_channel"] = chart_channel(DEMO_MATRIX)
    results["Cohort86"] = Cohort86(DEMO_MATRIX).tally()
    results["resolve_manifest"] = resolve_manifest(DEMO_MATRIX)
    results["weigh_cohort"] = weigh_cohort()
    results["sweep_sector"] = sweep_sector(DEMO_MATRIX)
    results["resolve_roster"] = resolve_roster()
    results["chart_ledger"] = chart_ledger(DEMO_TREE) + chart_ledger_ping(DEMO_TREE)
    results["Registry34"] = Registry34(DEMO_MATRIX).tally()
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
    print(pipeline_00372())
