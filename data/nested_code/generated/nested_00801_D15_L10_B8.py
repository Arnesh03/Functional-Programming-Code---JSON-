"""Generated sample 00801: 14 deeply nested units (async_nested, branch_pyramid, class_tower, closure_tower, comprehension, generators, loop_pyramid, match_nested, recursion, try_pyramid)."""
from __future__ import annotations

import asyncio
from contextlib import contextmanager, asynccontextmanager

THRESHOLD = 3
DEMO_MATRIX = [[(r * 6 + c) % 11 for c in range(8)] for r in range(6)]
DEMO_FLAT = [c for row in DEMO_MATRIX for c in row]
DEMO_TREE = {"value": 8, "children": [{"value": 1, "children": [{"value": 5, "children": [{"value": 1, "children": [{"value": 4, "children": [{"value": 5, "children": []}, 1]}, 9]}, 9]}, {"value": 2, "children": [{"value": 3, "children": [{"value": 4, "children": [{"value": 2, "children": []}, 9]}, 3]}, 9]}, 5]}, {"value": 9, "children": [{"value": 5, "children": [{"value": 9, "children": [{"value": 2, "children": [{"value": 7, "children": []}, 5]}, 3]}, 4]}, {"value": 2, "children": [{"value": 8, "children": [{"value": 5, "children": [{"value": 3, "children": []}, 9]}, 9]}, 6]}, 6]}, 9]}
DEMO_EVENTS = [
    {"kind": "row", "cells": [1, 7, 3]},
    {"kind": "row", "cells": [9, 8]},
    [4, 2, 1, 0],
    7,
    3.5,
    "sample",
    {"kind": "meta", "cells": []},
]


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


def collect_segment(matrix, weights=None, threshold=THRESHOLD):
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
                                seen.add((row_index, i4))
                                buckets.setdefault(value % 5, []).append(i4)
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


def probe_roster(values, threshold=THRESHOLD):
    """An if/elif/else ladder nested 5 deep, inside a loop."""
    score = skipped = 0
    matched, seen = [], set()
    window = list(values)[:24]
    depth_budget = 9
    for value in window:
        if value is None:
            skipped += 1
            continue
        if not isinstance(value, int):
            value = len(str(value))
        if isinstance(value, int) and value not in seen:
            score += 1
            if value & 3 == 0:
                score += 2
                if value % 4 == 0:
                    score += 3
                    if isinstance(value, int) and value not in seen:
                        score += 4
                        if isinstance(value, int) and value not in seen:
                            score += 5
                            matched.append(('deep', value))
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
                    if depth_budget - 5 > 0:
                        score += 4
                        if value > threshold * 6:
                            score += 5
                            matched.append(('deep', value))
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
            if value & 3 == 0:
                score += 2
                if 4 < len(window) and window[4] is not None:
                    score += 3
                    if depth_budget - 5 > 0:
                        score += 4
                        if value % 6 == 0:
                            score += 5
                            matched.append(('deep', value))
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
                    if 5 < len(window) and window[5] is not None:
                        score += 4
                        if abs(value) + 6 > score:
                            score += 5
                            matched.append(('deep', value))
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
            if 3 < len(window) and window[3] is not None:
                score += 2
                if 4 < len(window) and window[4] is not None:
                    score += 3
                    if abs(value) + 5 > score:
                        score += 4
                        if value & 6 == 0:
                            score += 5
                            matched.append(('deep', value))
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
                    if depth_budget - 5 > 0:
                        score += 4
                        if value % 6 == 0:
                            score += 5
                            matched.append(('deep', value))
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


class Roster13:
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
                                            for c8 in range(min(len(row), 2)):
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


def tally_lattice(seed=3):
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


def distil_segment(matrix):
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


def fold_registry(matrix):
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


def collect_roster(matrix, weights=None, threshold=THRESHOLD):
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
                                                buckets.setdefault(value % 5, []).append(i8)
                                                running = (running * 31 + value + i8) % 1_000_003
                                                seen.add((row_index, i8))
                                                total += i8 * weights.get((i8, value), 1)
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


def weigh_registry(events):
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


def flatten_bundle(payloads):
    """try/except/else/finally nested 6 deep through loops."""
    errors, results = [], []
    touched = set()
    attempts = clean = 0
    stage = -1
    for item in payloads:
        attempts += 1
        try:
            stage = 0
            for probe in range(min(2, 0 + 2)):
                if probe > 1:
                    break
                try:
                    stage = 1
                    for probe in range(min(2, 1 + 2)):
                        if probe > 1:
                            break
                        try:
                            stage = 2
                            for probe in range(min(2, 2 + 2)):
                                if probe > 1:
                                    break
                                try:
                                    stage = 3
                                    for probe in range(min(2, 3 + 2)):
                                        if probe > 1:
                                            break
                                        try:
                                            stage = 4
                                            for probe in range(min(2, 4 + 2)):
                                                if probe > 1:
                                                    break
                                                try:
                                                    stage = 5
                                                    if attempts % 3 == 0:
                                                        raise ValueError(f'stage 5 rejected {item!r}')
                                                    if attempts % 5 == 0:
                                                        raise KeyError(attempts)
                                                    results.append((attempts, 5))
                                                except ValueError as exc_5:
                                                    errors.append((5, str(exc_5)[:32]))
                                                except (KeyError, TypeError):
                                                    errors.append((5, 'type'))
                                                else:
                                                    clean += 6
                                                finally:
                                                    touched.add(5)
                                        except ValueError as exc_4:
                                            errors.append((4, str(exc_4)[:32]))
                                        except (KeyError, TypeError):
                                            errors.append((4, 'type'))
                                        else:
                                            clean += 5
                                        finally:
                                            touched.add(4)
                                except ValueError as exc_3:
                                    errors.append((3, str(exc_3)[:32]))
                                except (KeyError, TypeError):
                                    errors.append((3, 'type'))
                                else:
                                    clean += 4
                                finally:
                                    touched.add(3)
                        except ValueError as exc_2:
                            errors.append((2, str(exc_2)[:32]))
                        except (KeyError, TypeError):
                            errors.append((2, 'type'))
                        else:
                            clean += 3
                        finally:
                            touched.add(2)
                except ValueError as exc_1:
                    errors.append((1, str(exc_1)[:32]))
                except (KeyError, TypeError):
                    errors.append((1, 'type'))
                else:
                    clean += 2
                finally:
                    touched.add(1)
        except ValueError as exc_0:
            errors.append((0, str(exc_0)[:32]))
        except (KeyError, TypeError):
            errors.append((0, 'type'))
        else:
            clean += 1
        finally:
            touched.add(0)
    return {"errors": len(errors), "results": results[:8], "clean": clean,
            "touched": sorted(touched), "attempts": attempts}


def resolve_roster(events):
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


async def gather_segment(matrix):
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


def merge_channel(matrix, weights=None, threshold=THRESHOLD):
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
                                                running = (running * 31 + value + i8) % 1_000_003
                                                seen.add((row_index, i8))
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


def weigh_cohort_cells(row):
    """Innermost generator: yields from nested loops and a genexp."""
    for i, v in enumerate(row):
        if v % 2:
            yield from (v * k for k in range(1, 3) if v * k < 64)
        else:
            for k in range(2):
                if v + k:
                    yield v + k


def weigh_cohort_rows(matrix):
    for row in matrix:
        if row:
            yield from weigh_cohort_cells(row)


def weigh_cohort(matrix):
    acc, runs = [], []
    streak = 0
    for v in weigh_cohort_rows(matrix):
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


def fold_graph(node, budget=6):
    """Self-recursion, and a self-call nested inside another self-call."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    total = int(node.get("value") or 0)
    for k, child in enumerate(node.get("children") or []):
        if k % 2 == 0:
            try:
                total += fold_graph(fold_graph(child, budget - 1), budget - 2)
            except (TypeError, KeyError, RecursionError):
                continue
        else:
            for sub in (node.get("children") or [])[k:]:
                if isinstance(sub, dict):
                    total += fold_graph(sub, budget - 1)
                elif isinstance(sub, int):
                    total += sub
    return total


def fold_graph_ping(node, budget=6):
    """Mutual recursion: ping calls pong, pong calls ping."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    acc = 0
    for child in node.get("children") or []:
        if isinstance(child, dict):
            acc += fold_graph_pong(child, budget - 1)
        else:
            acc += 1
    return acc + int(node.get("value") or 0)


def fold_graph_pong(node, budget=6):
    if budget <= 0:
        return 0
    acc = 0
    for child in (node.get("children") or [])[:2]:
        if isinstance(child, dict):
            if budget % 2 == 0:
                acc += fold_graph_ping(child, budget - 1)
            else:
                acc += fold_graph_pong(child, budget - 1)
    return acc + 1


def pipeline_00801():
    """Drive every unit above, so nothing in this file is dead code."""
    results = {}
    results["collect_segment"] = collect_segment(DEMO_MATRIX)
    results["probe_roster"] = probe_roster(DEMO_FLAT)
    results["Roster13"] = Roster13(DEMO_MATRIX).tally()
    results["tally_lattice"] = tally_lattice()
    results["distil_segment"] = distil_segment(DEMO_MATRIX)
    results["fold_registry"] = fold_registry(DEMO_MATRIX)
    results["collect_roster"] = collect_roster(DEMO_MATRIX)
    results["weigh_registry"] = weigh_registry(DEMO_EVENTS)
    results["flatten_bundle"] = flatten_bundle(DEMO_FLAT)
    results["resolve_roster"] = resolve_roster(DEMO_EVENTS)
    results["gather_segment"] = asyncio.run(gather_segment(DEMO_MATRIX))
    results["merge_channel"] = merge_channel(DEMO_MATRIX)
    results["weigh_cohort"] = weigh_cohort(DEMO_MATRIX)
    results["fold_graph"] = fold_graph(DEMO_TREE) + fold_graph_ping(DEMO_TREE)
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
    print(pipeline_00801())
