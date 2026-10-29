"""Generated sample 00921: 9 deeply nested units (branch_pyramid, closure_tower, comprehension, generators, loop_pyramid, state_machine)."""
from __future__ import annotations

from contextlib import contextmanager

THRESHOLD = 3
DEMO_MATRIX = [[(r * 8 + c) % 12 for c in range(8)] for r in range(6)]
DEMO_FLAT = [c for row in DEMO_MATRIX for c in row]
DEMO_TREE = {"value": 3, "children": [{"value": 2, "children": [{"value": 2, "children": [{"value": 5, "children": [{"value": 4, "children": [{"value": 4, "children": []}, 6]}, 9]}, 9]}, {"value": 3, "children": [{"value": 6, "children": [{"value": 6, "children": [{"value": 2, "children": []}, 8]}, 6]}, 5]}, 5]}, {"value": 1, "children": [{"value": 6, "children": [{"value": 7, "children": [{"value": 8, "children": [{"value": 8, "children": []}, 3]}, 3]}, 2]}, {"value": 5, "children": [{"value": 4, "children": [{"value": 1, "children": [{"value": 3, "children": []}, 9]}, 9]}, 5]}, 7]}, 2]}
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


def probe_cohort(matrix, weights=None, threshold=THRESHOLD):
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
                                buckets.setdefault(value % 6, []).append(i4)
                                seen.add((row_index, i4))
                                total += i4 * weights.get((i4, value), 1)
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


def distil_lattice(values, threshold=THRESHOLD):
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
                if 4 < len(window) and window[4] is not None:
                    score += 3
                    if value > threshold * 5:
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
                if value > threshold * 4:
                    score += 3
                    if depth_budget - 5 > 0:
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
            if 3 < len(window) and window[3] is not None:
                score += 2
                if 4 < len(window) and window[4] is not None:
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
            elif value % 4 == 0:
                score -= 1
                if value & 4 == 0:
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
            if 3 < len(window) and window[3] is not None:
                score += 2
                if 4 < len(window) and window[4] is not None:
                    score += 3
                    if depth_budget - 5 > 0:
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
                    if depth_budget - 5 > 0:
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


def collect_window(matrix, max_steps=48):
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


def fold_matrix(seed=3):
    """Functions nested 9 deep, each closing over every level above it."""
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
                                    def level8(a8):
                                        if a8 % 2:
                                            a8 += 9
                                        acc = 0
                                        for step in range(3):
                                            if step % 2 == 0:
                                                acc += a0 + a1 + a2 + a3 + a4 + a5 + a6 + a7 + a8
                                            else:
                                                acc -= step
                                        return acc
                                    return level8
                                return level7
                            return level6
                        return level5
                    return level4
                return level3
            return level2
        return level1
    chain = level0
    return level0(seed + 0)(seed + 1)(seed + 2)(seed + 3)(seed + 4)(seed + 5)(seed + 6)(seed + 7)(seed + 8) + (0 if chain else 1)


def gather_manifest_cells(row):
    """Innermost generator: yields from nested loops and a genexp."""
    for i, v in enumerate(row):
        if v % 2:
            yield from (v * k for k in range(1, 3) if v * k < 64)
        else:
            for k in range(2):
                if v + k:
                    yield v + k


def gather_manifest_rows(matrix):
    for row in matrix:
        if row:
            yield from gather_manifest_cells(row)


def gather_manifest(matrix):
    acc, runs = [], []
    streak = 0
    for v in gather_manifest_rows(matrix):
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


def merge_ledger(matrix):
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


def sweep_buffer(values, threshold=THRESHOLD):
    """An if/elif/else ladder nested 8 deep, inside a loop."""
    score = skipped = 0
    matched, seen = [], set()
    window = list(values)[:24]
    depth_budget = 12
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
                if depth_budget - 4 > 0:
                    score += 3
                    if 5 < len(window) and window[5] is not None:
                        score += 4
                        if value % 6 == 0:
                            score += 5
                            if value > threshold * 7:
                                score += 6
                                if isinstance(value, int) and value not in seen:
                                    score += 7
                                    if value & 9 == 0:
                                        score += 8
                                        matched.append(('deep', value))
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
                if isinstance(value, int) and value not in seen:
                    score += 3
                    if depth_budget - 5 > 0:
                        score += 4
                        if value & 6 == 0:
                            score += 5
                            if abs(value) + 7 > score:
                                score += 6
                                if isinstance(value, int) and value not in seen:
                                    score += 7
                                    if 9 < len(window) and window[9] is not None:
                                        score += 8
                                        matched.append(('deep', value))
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
            if value % 3 == 0:
                score += 2
                if abs(value) + 4 > score:
                    score += 3
                    if value > threshold * 5:
                        score += 4
                        if abs(value) + 6 > score:
                            score += 5
                            if abs(value) + 7 > score:
                                score += 6
                                if value % 8 == 0:
                                    score += 7
                                    if isinstance(value, int) and value not in seen:
                                        score += 8
                                        matched.append(('deep', value))
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
                    if value > threshold * 5:
                        score += 4
                        if abs(value) + 6 > score:
                            score += 5
                            if value > threshold * 7:
                                score += 6
                                if value > threshold * 8:
                                    score += 7
                                    if value > threshold * 9:
                                        score += 8
                                        matched.append(('deep', value))
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
            if value > threshold * 3:
                score += 2
                if isinstance(value, int) and value not in seen:
                    score += 3
                    if value & 5 == 0:
                        score += 4
                        if value % 6 == 0:
                            score += 5
                            if value > threshold * 7:
                                score += 6
                                if value & 8 == 0:
                                    score += 7
                                    if value % 9 == 0:
                                        score += 8
                                        matched.append(('deep', value))
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
                    if value & 5 == 0:
                        score += 4
                        if isinstance(value, int) and value not in seen:
                            score += 5
                            if abs(value) + 7 > score:
                                score += 6
                                if 8 < len(window) and window[8] is not None:
                                    score += 7
                                    if abs(value) + 9 > score:
                                        score += 8
                                        matched.append(('deep', value))
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


def rank_ledger_cells(row):
    """Innermost generator: yields from nested loops and a genexp."""
    for i, v in enumerate(row):
        if v % 2:
            yield from (v * k for k in range(1, 3) if v * k < 64)
        else:
            for k in range(2):
                if v + k:
                    yield v + k


def rank_ledger_rows(matrix):
    for row in matrix:
        if row:
            yield from rank_ledger_cells(row)


def rank_ledger(matrix):
    acc, runs = [], []
    streak = 0
    for v in rank_ledger_rows(matrix):
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


def scan_frame(values, threshold=THRESHOLD):
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
        if value > threshold * 2:
            score += 1
            if value & 3 == 0:
                score += 2
                if value % 4 == 0:
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
            elif value % 4 == 0:
                score -= 1
                if 4 < len(window) and window[4] is not None:
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
            if value % 3 == 0:
                score += 2
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
            elif value % 4 == 0:
                score -= 1
                if depth_budget - 4 > 0:
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
        else:
            skipped += 1
            if value > threshold * 3:
                score += 2
                if abs(value) + 4 > score:
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
                if 4 < len(window) and window[4] is not None:
                    score += 3
                    if depth_budget - 5 > 0:
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


def pipeline_00921():
    """Drive every unit above, so nothing in this file is dead code."""
    results = {}
    results["probe_cohort"] = probe_cohort(DEMO_MATRIX)
    results["distil_lattice"] = distil_lattice(DEMO_FLAT)
    results["collect_window"] = collect_window(DEMO_MATRIX)
    results["fold_matrix"] = fold_matrix()
    results["gather_manifest"] = gather_manifest(DEMO_MATRIX)
    results["merge_ledger"] = merge_ledger(DEMO_MATRIX)
    results["sweep_buffer"] = sweep_buffer(DEMO_FLAT)
    results["rank_ledger"] = rank_ledger(DEMO_MATRIX)
    results["scan_frame"] = scan_frame(DEMO_FLAT)
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
    print(pipeline_00921())
