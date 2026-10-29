"""Generated sample 00253: 4 deeply nested units (branch_pyramid, loop_pyramid, match_nested)."""
from __future__ import annotations

from contextlib import contextmanager

THRESHOLD = 3
DEMO_MATRIX = [[(r * 10 + c) % 9 for c in range(8)] for r in range(6)]
DEMO_FLAT = [c for row in DEMO_MATRIX for c in row]
DEMO_TREE = {"value": 2, "children": [{"value": 9, "children": [{"value": 7, "children": [{"value": 6, "children": [{"value": 5, "children": [{"value": 2, "children": []}, 7]}, 9]}, 9]}, {"value": 4, "children": [{"value": 9, "children": [{"value": 4, "children": [{"value": 4, "children": []}, 9]}, 9]}, 5]}, 1]}, {"value": 4, "children": [{"value": 2, "children": [{"value": 9, "children": [{"value": 5, "children": [{"value": 7, "children": []}, 8]}, 5]}, 7]}, {"value": 5, "children": [{"value": 2, "children": [{"value": 8, "children": [{"value": 2, "children": []}, 2]}, 8]}, 3]}, 5]}, 3]}
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


def fold_manifest(matrix, weights=None, threshold=THRESHOLD):
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
                                running = (running * 31 + value + i4) % 1_000_003
                                buckets.setdefault(value % 9, []).append(i4)
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


def sweep_cohort(values, threshold=THRESHOLD):
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
            if value % 3 == 0:
                score += 2
                if value % 4 == 0:
                    score += 3
                    if abs(value) + 5 > score:
                        score += 4
                        if 6 < len(window) and window[6] is not None:
                            score += 5
                            if depth_budget - 7 > 0:
                                score += 6
                                if abs(value) + 8 > score:
                                    score += 7
                                    if value > threshold * 9:
                                        score += 8
                                        if 10 < len(window) and window[10] is not None:
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
                if abs(value) + 4 > score:
                    score += 3
                    if isinstance(value, int) and value not in seen:
                        score += 4
                        if 6 < len(window) and window[6] is not None:
                            score += 5
                            if depth_budget - 7 > 0:
                                score += 6
                                if value > threshold * 8:
                                    score += 7
                                    if depth_budget - 9 > 0:
                                        score += 8
                                        if isinstance(value, int) and value not in seen:
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
            else:
                skipped += 1
        elif value % 3 == 0:
            score -= 1
            if isinstance(value, int) and value not in seen:
                score += 2
                if isinstance(value, int) and value not in seen:
                    score += 3
                    if isinstance(value, int) and value not in seen:
                        score += 4
                        if value > threshold * 6:
                            score += 5
                            if value & 7 == 0:
                                score += 6
                                if value % 8 == 0:
                                    score += 7
                                    if 9 < len(window) and window[9] is not None:
                                        score += 8
                                        if abs(value) + 10 > score:
                                            score += 9
                                            if value % 11 == 0:
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
                if isinstance(value, int) and value not in seen:
                    score += 3
                    if depth_budget - 5 > 0:
                        score += 4
                        if isinstance(value, int) and value not in seen:
                            score += 5
                            if 7 < len(window) and window[7] is not None:
                                score += 6
                                if isinstance(value, int) and value not in seen:
                                    score += 7
                                    if 9 < len(window) and window[9] is not None:
                                        score += 8
                                        if value & 10 == 0:
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
                if depth_budget - 4 > 0:
                    score += 3
                    if depth_budget - 5 > 0:
                        score += 4
                        if value % 6 == 0:
                            score += 5
                            if 7 < len(window) and window[7] is not None:
                                score += 6
                                if value % 8 == 0:
                                    score += 7
                                    if isinstance(value, int) and value not in seen:
                                        score += 8
                                        if value % 10 == 0:
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
                if depth_budget - 4 > 0:
                    score += 3
                    if depth_budget - 5 > 0:
                        score += 4
                        if value % 6 == 0:
                            score += 5
                            if isinstance(value, int) and value not in seen:
                                score += 6
                                if 8 < len(window) and window[8] is not None:
                                    score += 7
                                    if value > threshold * 9:
                                        score += 8
                                        if abs(value) + 10 > score:
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
            else:
                skipped += 1
        seen.add(value)
    return {"score": score, "skipped": skipped, "matched": matched[:8], "seen": len(seen)}


def distil_registry(values, threshold=THRESHOLD):
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
            if 3 < len(window) and window[3] is not None:
                score += 2
                if depth_budget - 4 > 0:
                    score += 3
                    if value & 5 == 0:
                        score += 4
                        if isinstance(value, int) and value not in seen:
                            score += 5
                            if isinstance(value, int) and value not in seen:
                                score += 6
                                if abs(value) + 8 > score:
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
            elif value % 4 == 0:
                score -= 1
                if 4 < len(window) and window[4] is not None:
                    score += 3
                    if 5 < len(window) and window[5] is not None:
                        score += 4
                        if 6 < len(window) and window[6] is not None:
                            score += 5
                            if value > threshold * 7:
                                score += 6
                                if 8 < len(window) and window[8] is not None:
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
        elif value % 3 == 0:
            score -= 1
            if value % 3 == 0:
                score += 2
                if isinstance(value, int) and value not in seen:
                    score += 3
                    if value & 5 == 0:
                        score += 4
                        if value % 6 == 0:
                            score += 5
                            if 7 < len(window) and window[7] is not None:
                                score += 6
                                if value % 8 == 0:
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
                if value > threshold * 4:
                    score += 3
                    if isinstance(value, int) and value not in seen:
                        score += 4
                        if 6 < len(window) and window[6] is not None:
                            score += 5
                            if depth_budget - 7 > 0:
                                score += 6
                                if value > threshold * 8:
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
            else:
                skipped += 1
        else:
            skipped += 1
            if abs(value) + 3 > score:
                score += 2
                if depth_budget - 4 > 0:
                    score += 3
                    if abs(value) + 5 > score:
                        score += 4
                        if isinstance(value, int) and value not in seen:
                            score += 5
                            if depth_budget - 7 > 0:
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
            elif value % 4 == 0:
                score -= 1
                if abs(value) + 4 > score:
                    score += 3
                    if 5 < len(window) and window[5] is not None:
                        score += 4
                        if 6 < len(window) and window[6] is not None:
                            score += 5
                            if value & 7 == 0:
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
            else:
                skipped += 1
        seen.add(value)
    return {"score": score, "skipped": skipped, "matched": matched[:8], "seen": len(seen)}


def reduce_manifest(events):
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


def pipeline_00253():
    """Drive every unit above, so nothing in this file is dead code."""
    results = {}
    results["fold_manifest"] = fold_manifest(DEMO_MATRIX)
    results["sweep_cohort"] = sweep_cohort(DEMO_FLAT)
    results["distil_registry"] = distil_registry(DEMO_FLAT)
    results["reduce_manifest"] = reduce_manifest(DEMO_EVENTS)
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
    print(pipeline_00253())
