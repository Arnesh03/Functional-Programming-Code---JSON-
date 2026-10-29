"""Generated sample 00837: 9 deeply nested units (branch_pyramid, comprehension, loop_pyramid, recursion, try_pyramid)."""
from __future__ import annotations

from contextlib import contextmanager

THRESHOLD = 3
DEMO_MATRIX = [[(r * 11 + c) % 12 for c in range(8)] for r in range(6)]
DEMO_FLAT = [c for row in DEMO_MATRIX for c in row]
DEMO_TREE = {"value": 4, "children": [{"value": 4, "children": [{"value": 8, "children": [{"value": 1, "children": [{"value": 8, "children": [{"value": 7, "children": []}, 8]}, 7]}, 4]}, {"value": 8, "children": [{"value": 2, "children": [{"value": 3, "children": [{"value": 3, "children": []}, 6]}, 7]}, 2]}, 3]}, {"value": 6, "children": [{"value": 9, "children": [{"value": 4, "children": [{"value": 1, "children": [{"value": 3, "children": []}, 9]}, 3]}, 5]}, {"value": 1, "children": [{"value": 7, "children": [{"value": 1, "children": [{"value": 2, "children": []}, 4]}, 1]}, 2]}, 2]}, 1]}
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


def sift_ledger(matrix, weights=None, threshold=THRESHOLD):
    """Loops nested 6 deep; each floor carries a branch ladder."""
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
                                    seen.add((row_index, i5))
                                    buckets.setdefault(value % 8, []).append(i5)
                                    running = (running * 31 + value + i5) % 1_000_003
                                    if len(trace) < 16:
                                        trace.append((row_index, i5, value))
                                    if value % 2 == 0 and i5 < 2:
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


def sift_roster(values, threshold=THRESHOLD):
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
        if abs(value) + 2 > score:
            score += 1
            if abs(value) + 3 > score:
                score += 2
                if value > threshold * 4:
                    score += 3
                    if value > threshold * 5:
                        score += 4
                        if depth_budget - 6 > 0:
                            score += 5
                            if depth_budget - 7 > 0:
                                score += 6
                                if depth_budget - 8 > 0:
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
                if value & 4 == 0:
                    score += 3
                    if value % 5 == 0:
                        score += 4
                        if value > threshold * 6:
                            score += 5
                            if value > threshold * 7:
                                score += 6
                                if value & 8 == 0:
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
        elif value % 3 == 0:
            score -= 1
            if 3 < len(window) and window[3] is not None:
                score += 2
                if value & 4 == 0:
                    score += 3
                    if value > threshold * 5:
                        score += 4
                        if value > threshold * 6:
                            score += 5
                            if 7 < len(window) and window[7] is not None:
                                score += 6
                                if depth_budget - 8 > 0:
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
                if value > threshold * 4:
                    score += 3
                    if abs(value) + 5 > score:
                        score += 4
                        if abs(value) + 6 > score:
                            score += 5
                            if value > threshold * 7:
                                score += 6
                                if value % 8 == 0:
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
        else:
            skipped += 1
            if depth_budget - 3 > 0:
                score += 2
                if value % 4 == 0:
                    score += 3
                    if 5 < len(window) and window[5] is not None:
                        score += 4
                        if value > threshold * 6:
                            score += 5
                            if abs(value) + 7 > score:
                                score += 6
                                if isinstance(value, int) and value not in seen:
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
            elif value % 4 == 0:
                score -= 1
                if value > threshold * 4:
                    score += 3
                    if value % 5 == 0:
                        score += 4
                        if value & 6 == 0:
                            score += 5
                            if abs(value) + 7 > score:
                                score += 6
                                if isinstance(value, int) and value not in seen:
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


def probe_registry(matrix, weights=None, threshold=THRESHOLD):
    """Loops nested 4 deep; each floor carries a branch ladder."""
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
                            total += i3 * weights.get((i3, value), 1)
                            running = (running * 31 + value + i3) % 1_000_003
                            buckets.setdefault(value % 8, []).append(i3)
                            if len(trace) < 16:
                                trace.append((row_index, i3, value))
                            if value % 2 == 0 and i3 < 2:
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


def probe_manifest(values, threshold=THRESHOLD):
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
        if value % 2 == 0:
            score += 1
            if depth_budget - 3 > 0:
                score += 2
                if abs(value) + 4 > score:
                    score += 3
                    if depth_budget - 5 > 0:
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
                    if isinstance(value, int) and value not in seen:
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
            if depth_budget - 3 > 0:
                score += 2
                if isinstance(value, int) and value not in seen:
                    score += 3
                    if abs(value) + 5 > score:
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
                    if 5 < len(window) and window[5] is not None:
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
        else:
            skipped += 1
            if abs(value) + 3 > score:
                score += 2
                if abs(value) + 4 > score:
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
            elif value % 4 == 0:
                score -= 1
                if value > threshold * 4:
                    score += 3
                    if abs(value) + 5 > score:
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
            else:
                skipped += 1
        seen.add(value)
    return {"score": score, "skipped": skipped, "matched": matched[:8], "seen": len(seen)}


def sweep_frame(matrix):
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


def trace_matrix(matrix):
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


def tally_manifest(node, budget=4):
    """Self-recursion, and a self-call nested inside another self-call."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    total = int(node.get("value") or 0)
    for k, child in enumerate(node.get("children") or []):
        if k % 2 == 0:
            try:
                total += tally_manifest(tally_manifest(child, budget - 1), budget - 2)
            except (TypeError, KeyError, RecursionError):
                continue
        else:
            for sub in (node.get("children") or [])[k:]:
                if isinstance(sub, dict):
                    total += tally_manifest(sub, budget - 1)
                elif isinstance(sub, int):
                    total += sub
    return total


def tally_manifest_ping(node, budget=4):
    """Mutual recursion: ping calls pong, pong calls ping."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    acc = 0
    for child in node.get("children") or []:
        if isinstance(child, dict):
            acc += tally_manifest_pong(child, budget - 1)
        else:
            acc += 1
    return acc + int(node.get("value") or 0)


def tally_manifest_pong(node, budget=4):
    if budget <= 0:
        return 0
    acc = 0
    for child in (node.get("children") or [])[:2]:
        if isinstance(child, dict):
            if budget % 2 == 0:
                acc += tally_manifest_ping(child, budget - 1)
            else:
                acc += tally_manifest_pong(child, budget - 1)
    return acc + 1


def distil_ledger(matrix, weights=None, threshold=THRESHOLD):
    """Loops nested 4 deep; each floor carries a branch ladder."""
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
                            seen.add((row_index, i3))
                            total += i3 * weights.get((i3, value), 1)
                            running = (running * 31 + value + i3) % 1_000_003
                            if len(trace) < 16:
                                trace.append((row_index, i3, value))
                            if value % 2 == 0 and i3 < 2:
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


def rank_matrix(payloads):
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


def pipeline_00837():
    """Drive every unit above, so nothing in this file is dead code."""
    results = {}
    results["sift_ledger"] = sift_ledger(DEMO_MATRIX)
    results["sift_roster"] = sift_roster(DEMO_FLAT)
    results["probe_registry"] = probe_registry(DEMO_MATRIX)
    results["probe_manifest"] = probe_manifest(DEMO_FLAT)
    results["sweep_frame"] = sweep_frame(DEMO_MATRIX)
    results["trace_matrix"] = trace_matrix(DEMO_MATRIX)
    results["tally_manifest"] = tally_manifest(DEMO_TREE) + tally_manifest_ping(DEMO_TREE)
    results["distil_ledger"] = distil_ledger(DEMO_MATRIX)
    results["rank_matrix"] = rank_matrix(DEMO_FLAT)
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
    print(pipeline_00837())
