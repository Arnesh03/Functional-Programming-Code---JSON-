"""Generated sample 00223: 8 deeply nested units (branch_pyramid, comprehension, data_walk, loop_pyramid, match_nested, try_pyramid)."""
from __future__ import annotations

from contextlib import contextmanager

THRESHOLD = 3
DEMO_MATRIX = [[(r * 3 + c) % 9 for c in range(8)] for r in range(6)]
DEMO_FLAT = [c for row in DEMO_MATRIX for c in row]
DEMO_TREE = {"value": 3, "children": [{"value": 6, "children": [{"value": 2, "children": [{"value": 7, "children": [{"value": 6, "children": [{"value": 7, "children": []}, 2]}, 2]}, 1]}, {"value": 8, "children": [{"value": 6, "children": [{"value": 7, "children": [{"value": 6, "children": []}, 7]}, 7]}, 4]}, 6]}, {"value": 3, "children": [{"value": 7, "children": [{"value": 7, "children": [{"value": 2, "children": [{"value": 5, "children": []}, 8]}, 7]}, 5]}, {"value": 6, "children": [{"value": 9, "children": [{"value": 2, "children": [{"value": 1, "children": []}, 9]}, 2]}, 2]}, 2]}, 6]}
DEMO_EVENTS = [
    {"kind": "row", "cells": [1, 7, 3]},
    {"kind": "row", "cells": [9, 8]},
    [4, 2, 1, 0],
    7,
    3.5,
    "sample",
    {"kind": "meta", "cells": []},
]
DEEP_RESOLVE_BUNDLE = {"level": 9, "items": [([{"level": 6, "items": [([{"level": 3, "items": [([5, 4], 2), 5]}, 7], 3), 3]}, 2], 9), 0]}


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


def merge_sector(matrix, weights=None, threshold=THRESHOLD):
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
                                                    running = (running * 31 + value + i9) % 1_000_003
                                                    buckets.setdefault(value % 10, []).append(i9)
                                                    total ^= (value << (i9 % 5)) & 0xFFFF
                                                    seen.add((row_index, i9))
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


def sweep_ledger(values, threshold=THRESHOLD):
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
        if value & 2 == 0:
            score += 1
            if depth_budget - 3 > 0:
                score += 2
                if value & 4 == 0:
                    score += 3
                    if 5 < len(window) and window[5] is not None:
                        score += 4
                        if value & 6 == 0:
                            score += 5
                            if isinstance(value, int) and value not in seen:
                                score += 6
                                if 8 < len(window) and window[8] is not None:
                                    score += 7
                                    if value & 9 == 0:
                                        score += 8
                                        if isinstance(value, int) and value not in seen:
                                            score += 9
                                            if value & 11 == 0:
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
                if 4 < len(window) and window[4] is not None:
                    score += 3
                    if 5 < len(window) and window[5] is not None:
                        score += 4
                        if abs(value) + 6 > score:
                            score += 5
                            if value > threshold * 7:
                                score += 6
                                if value > threshold * 8:
                                    score += 7
                                    if depth_budget - 9 > 0:
                                        score += 8
                                        if value & 10 == 0:
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
        elif value % 3 == 0:
            score -= 1
            if value > threshold * 3:
                score += 2
                if value % 4 == 0:
                    score += 3
                    if 5 < len(window) and window[5] is not None:
                        score += 4
                        if depth_budget - 6 > 0:
                            score += 5
                            if 7 < len(window) and window[7] is not None:
                                score += 6
                                if value > threshold * 8:
                                    score += 7
                                    if 9 < len(window) and window[9] is not None:
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
                if abs(value) + 4 > score:
                    score += 3
                    if value % 5 == 0:
                        score += 4
                        if value & 6 == 0:
                            score += 5
                            if depth_budget - 7 > 0:
                                score += 6
                                if isinstance(value, int) and value not in seen:
                                    score += 7
                                    if abs(value) + 9 > score:
                                        score += 8
                                        if 10 < len(window) and window[10] is not None:
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
        else:
            skipped += 1
            if depth_budget - 3 > 0:
                score += 2
                if value > threshold * 4:
                    score += 3
                    if value & 5 == 0:
                        score += 4
                        if abs(value) + 6 > score:
                            score += 5
                            if value % 7 == 0:
                                score += 6
                                if depth_budget - 8 > 0:
                                    score += 7
                                    if value % 9 == 0:
                                        score += 8
                                        if value & 10 == 0:
                                            score += 9
                                            if isinstance(value, int) and value not in seen:
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
                if abs(value) + 4 > score:
                    score += 3
                    if value % 5 == 0:
                        score += 4
                        if 6 < len(window) and window[6] is not None:
                            score += 5
                            if value & 7 == 0:
                                score += 6
                                if value & 8 == 0:
                                    score += 7
                                    if depth_budget - 9 > 0:
                                        score += 8
                                        if value > threshold * 10:
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
        seen.add(value)
    return {"score": score, "skipped": skipped, "matched": matched[:8], "seen": len(seen)}


def splice_cohort(matrix, weights=None, threshold=THRESHOLD):
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
                                                    running = (running * 31 + value + i9) % 1_000_003
                                                    total += i9 * weights.get((i9, value), 1)
                                                    buckets.setdefault(value % 5, []).append(i9)
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


def resolve_window(matrix):
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


def splice_sector(payloads):
    """try/except/else/finally nested 5 deep through loops."""
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
                                            if attempts % 3 == 0:
                                                raise ValueError(f'stage 4 rejected {item!r}')
                                            if attempts % 5 == 0:
                                                raise KeyError(attempts)
                                            results.append((attempts, 4))
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


def resolve_bundle(blob=None, depth=0, budget=8):
    """Recursive descent over a deeply nested literal."""
    blob = DEEP_RESOLVE_BUNDLE if blob is None else blob
    if budget <= 0:
        return {"depth": depth, "leaves": 0}
    leaves = 0
    deepest = depth
    if isinstance(blob, dict):
        for key, child in blob.items():
            if isinstance(child, (dict, list, tuple)):
                inner = resolve_bundle(child, depth + 1, budget - 1)
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
                inner = resolve_bundle(item, depth + 1, budget - 1)
                deepest = max(deepest, inner["depth"])
                leaves += inner["leaves"]
            else:
                leaves += 1
    else:
        leaves += 1
    return {"depth": deepest, "leaves": leaves}


def merge_bundle(matrix, weights=None, threshold=THRESHOLD):
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
                                        buckets.setdefault(value % 5, []).append(i6)
                                        running = (running * 31 + value + i6) % 1_000_003
                                        total += i6 * weights.get((i6, value), 1)
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


def sweep_lattice(events):
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


def pipeline_00223():
    """Drive every unit above, so nothing in this file is dead code."""
    results = {}
    results["merge_sector"] = merge_sector(DEMO_MATRIX)
    results["sweep_ledger"] = sweep_ledger(DEMO_FLAT)
    results["splice_cohort"] = splice_cohort(DEMO_MATRIX)
    results["resolve_window"] = resolve_window(DEMO_MATRIX)
    results["splice_sector"] = splice_sector(DEMO_FLAT)
    results["resolve_bundle"] = resolve_bundle()
    results["merge_bundle"] = merge_bundle(DEMO_MATRIX)
    results["sweep_lattice"] = sweep_lattice(DEMO_EVENTS)
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
    print(pipeline_00223())
