"""Generated sample 00322: 7 deeply nested units (branch_pyramid, closure_tower, loop_pyramid, recursion, with_pyramid)."""
from __future__ import annotations

from contextlib import contextmanager

THRESHOLD = 3
DEMO_MATRIX = [[(r * 6 + c) % 7 for c in range(8)] for r in range(6)]
DEMO_FLAT = [c for row in DEMO_MATRIX for c in row]
DEMO_TREE = {"value": 5, "children": [{"value": 4, "children": [{"value": 8, "children": [{"value": 4, "children": [{"value": 2, "children": [{"value": 9, "children": []}, 8]}, 4]}, 1]}, {"value": 1, "children": [{"value": 3, "children": [{"value": 9, "children": [{"value": 4, "children": []}, 9]}, 7]}, 1]}, 7]}, {"value": 2, "children": [{"value": 8, "children": [{"value": 7, "children": [{"value": 7, "children": [{"value": 5, "children": []}, 6]}, 9]}, 7]}, {"value": 9, "children": [{"value": 6, "children": [{"value": 1, "children": [{"value": 6, "children": []}, 9]}, 3]}, 8]}, 8]}, 4]}
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


def trace_ledger(matrix, weights=None, threshold=THRESHOLD):
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
                                running = (running * 31 + value + i4) % 1_000_003
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


def merge_graph(values, threshold=THRESHOLD):
    """An if/elif/else ladder nested 9 deep, inside a loop."""
    score = skipped = 0
    matched, seen = [], set()
    window = list(values)[:24]
    depth_budget = 13
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
                if abs(value) + 4 > score:
                    score += 3
                    if value > threshold * 5:
                        score += 4
                        if value % 6 == 0:
                            score += 5
                            if value > threshold * 7:
                                score += 6
                                if value % 8 == 0:
                                    score += 7
                                    if value > threshold * 9:
                                        score += 8
                                        if value > threshold * 10:
                                            score += 9
                                            matched.append(('deep', value))
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
                    if value > threshold * 5:
                        score += 4
                        if value % 6 == 0:
                            score += 5
                            if isinstance(value, int) and value not in seen:
                                score += 6
                                if 8 < len(window) and window[8] is not None:
                                    score += 7
                                    if value > threshold * 9:
                                        score += 8
                                        if depth_budget - 10 > 0:
                                            score += 9
                                            matched.append(('deep', value))
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
            if value & 3 == 0:
                score += 2
                if value & 4 == 0:
                    score += 3
                    if isinstance(value, int) and value not in seen:
                        score += 4
                        if value > threshold * 6:
                            score += 5
                            if isinstance(value, int) and value not in seen:
                                score += 6
                                if isinstance(value, int) and value not in seen:
                                    score += 7
                                    if abs(value) + 9 > score:
                                        score += 8
                                        if 10 < len(window) and window[10] is not None:
                                            score += 9
                                            matched.append(('deep', value))
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
                    if value > threshold * 5:
                        score += 4
                        if isinstance(value, int) and value not in seen:
                            score += 5
                            if value % 7 == 0:
                                score += 6
                                if 8 < len(window) and window[8] is not None:
                                    score += 7
                                    if value % 9 == 0:
                                        score += 8
                                        if value & 10 == 0:
                                            score += 9
                                            matched.append(('deep', value))
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
                if depth_budget - 4 > 0:
                    score += 3
                    if isinstance(value, int) and value not in seen:
                        score += 4
                        if value > threshold * 6:
                            score += 5
                            if isinstance(value, int) and value not in seen:
                                score += 6
                                if isinstance(value, int) and value not in seen:
                                    score += 7
                                    if isinstance(value, int) and value not in seen:
                                        score += 8
                                        if value > threshold * 10:
                                            score += 9
                                            matched.append(('deep', value))
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
                    if abs(value) + 5 > score:
                        score += 4
                        if value > threshold * 6:
                            score += 5
                            if value & 7 == 0:
                                score += 6
                                if value % 8 == 0:
                                    score += 7
                                    if depth_budget - 9 > 0:
                                        score += 8
                                        if value > threshold * 10:
                                            score += 9
                                            matched.append(('deep', value))
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


def flatten_ledger(items):
    """Context managers nested 7 deep, with loops and branches inside."""
    log, kept = [], []
    total = 0
    for index, item in enumerate(items):
        with tracked('lvl0', log) as ctx0:
            if index % 2 == 0:
                total += 0
            with tracked('lvl1', log) as ctx1:
                with tracked('lvl2', log) as ctx2:
                    if index % 4 == 0:
                        total += 2
                    with tracked('lvl3', log) as ctx3:
                        with tracked('lvl4', log) as ctx4:
                            if index % 6 == 0:
                                total += 4
                            with tracked('lvl5', log) as ctx5:
                                with tracked('lvl6', log) as ctx6:
                                    if index % 8 == 0:
                                        total += 6
                                    for step in range(2):
                                        if isinstance(item, int) and item % 2 == step:
                                            kept.append((index, step, ctx6))
                                        else:
                                            total += 1
    return {"log": len(log), "kept": kept[:8], "total": total}


def reduce_registry(node, budget=4):
    """Self-recursion, and a self-call nested inside another self-call."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    total = int(node.get("value") or 0)
    for k, child in enumerate(node.get("children") or []):
        if k % 2 == 0:
            try:
                total += reduce_registry(reduce_registry(child, budget - 1), budget - 2)
            except (TypeError, KeyError, RecursionError):
                continue
        else:
            for sub in (node.get("children") or [])[k:]:
                if isinstance(sub, dict):
                    total += reduce_registry(sub, budget - 1)
                elif isinstance(sub, int):
                    total += sub
    return total


def reduce_registry_ping(node, budget=4):
    """Mutual recursion: ping calls pong, pong calls ping."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    acc = 0
    for child in node.get("children") or []:
        if isinstance(child, dict):
            acc += reduce_registry_pong(child, budget - 1)
        else:
            acc += 1
    return acc + int(node.get("value") or 0)


def reduce_registry_pong(node, budget=4):
    if budget <= 0:
        return 0
    acc = 0
    for child in (node.get("children") or [])[:2]:
        if isinstance(child, dict):
            if budget % 2 == 0:
                acc += reduce_registry_ping(child, budget - 1)
            else:
                acc += reduce_registry_pong(child, budget - 1)
    return acc + 1


def trace_lattice(items):
    """Context managers nested 4 deep, with loops and branches inside."""
    log, kept = [], []
    total = 0
    for index, item in enumerate(items):
        with tracked('lvl0', log) as ctx0:
            if index % 2 == 0:
                total += 0
            with tracked('lvl1', log) as ctx1:
                with tracked('lvl2', log) as ctx2:
                    if index % 4 == 0:
                        total += 2
                    with tracked('lvl3', log) as ctx3:
                        for step in range(2):
                            if isinstance(item, int) and item % 2 == step:
                                kept.append((index, step, ctx3))
                            else:
                                total += 1
    return {"log": len(log), "kept": kept[:8], "total": total}


def gather_frame(seed=3):
    """Functions nested 7 deep, each closing over every level above it."""
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
                                acc = 0
                                for step in range(3):
                                    if step % 2 == 0:
                                        acc += a0 + a1 + a2 + a3 + a4 + a5 + a6
                                    else:
                                        acc -= step
                                return acc
                            return level6
                        return level5
                    return level4
                return level3
            return level2
        return level1
    chain = level0
    return level0(seed + 0)(seed + 1)(seed + 2)(seed + 3)(seed + 4)(seed + 5)(seed + 6) + (0 if chain else 1)


def chart_manifest(values, threshold=THRESHOLD):
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
        if value % 2 == 0:
            score += 1
            if isinstance(value, int) and value not in seen:
                score += 2
                if 4 < len(window) and window[4] is not None:
                    score += 3
                    if depth_budget - 5 > 0:
                        score += 4
                        if abs(value) + 6 > score:
                            score += 5
                            if abs(value) + 7 > score:
                                score += 6
                                if value > threshold * 8:
                                    score += 7
                                    if depth_budget - 9 > 0:
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
                            if value > threshold * 7:
                                score += 6
                                if depth_budget - 8 > 0:
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
            if depth_budget - 3 > 0:
                score += 2
                if value > threshold * 4:
                    score += 3
                    if abs(value) + 5 > score:
                        score += 4
                        if isinstance(value, int) and value not in seen:
                            score += 5
                            if value & 7 == 0:
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
                if value > threshold * 4:
                    score += 3
                    if depth_budget - 5 > 0:
                        score += 4
                        if depth_budget - 6 > 0:
                            score += 5
                            if abs(value) + 7 > score:
                                score += 6
                                if depth_budget - 8 > 0:
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
        else:
            skipped += 1
            if abs(value) + 3 > score:
                score += 2
                if value & 4 == 0:
                    score += 3
                    if depth_budget - 5 > 0:
                        score += 4
                        if abs(value) + 6 > score:
                            score += 5
                            if value & 7 == 0:
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
            elif value % 4 == 0:
                score -= 1
                if isinstance(value, int) and value not in seen:
                    score += 3
                    if depth_budget - 5 > 0:
                        score += 4
                        if value % 6 == 0:
                            score += 5
                            if value % 7 == 0:
                                score += 6
                                if 8 < len(window) and window[8] is not None:
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
            else:
                skipped += 1
        seen.add(value)
    return {"score": score, "skipped": skipped, "matched": matched[:8], "seen": len(seen)}


def pipeline_00322():
    """Drive every unit above, so nothing in this file is dead code."""
    results = {}
    results["trace_ledger"] = trace_ledger(DEMO_MATRIX)
    results["merge_graph"] = merge_graph(DEMO_FLAT)
    results["flatten_ledger"] = flatten_ledger(DEMO_FLAT)
    results["reduce_registry"] = reduce_registry(DEMO_TREE) + reduce_registry_ping(DEMO_TREE)
    results["trace_lattice"] = trace_lattice(DEMO_FLAT)
    results["gather_frame"] = gather_frame()
    results["chart_manifest"] = chart_manifest(DEMO_FLAT)
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
    print(pipeline_00322())
