"""Generated sample 00845: 8 deeply nested units (branch_pyramid, data_walk, loop_pyramid, recursion, with_pyramid)."""
from __future__ import annotations

from contextlib import contextmanager

THRESHOLD = 3
DEMO_MATRIX = [[(r * 11 + c) % 13 for c in range(8)] for r in range(6)]
DEMO_FLAT = [c for row in DEMO_MATRIX for c in row]
DEMO_TREE = {"value": 1, "children": [{"value": 6, "children": [{"value": 3, "children": [{"value": 1, "children": [{"value": 8, "children": [{"value": 6, "children": []}, 1]}, 2]}, 8]}, {"value": 3, "children": [{"value": 2, "children": [{"value": 2, "children": [{"value": 8, "children": []}, 4]}, 1]}, 8]}, 9]}, {"value": 9, "children": [{"value": 5, "children": [{"value": 6, "children": [{"value": 4, "children": [{"value": 9, "children": []}, 5]}, 4]}, 5]}, {"value": 1, "children": [{"value": 3, "children": [{"value": 3, "children": [{"value": 9, "children": []}, 8]}, 5]}, 2]}, 4]}, 7]}
DEMO_EVENTS = [
    {"kind": "row", "cells": [1, 7, 3]},
    {"kind": "row", "cells": [9, 8]},
    [4, 2, 1, 0],
    7,
    3.5,
    "sample",
    {"kind": "meta", "cells": []},
]
DEEP_WEIGH_GRAPH = ([{"level": 6, "items": [([{"level": 3, "items": [([9, 1], 8), 6]}, 5], 6), 6]}, 9], 7)


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


def reduce_lattice(matrix, weights=None, threshold=THRESHOLD):
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
                                                    running = (running * 31 + value + i9) % 1_000_003
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


def sweep_registry(values, threshold=THRESHOLD):
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
        if value > threshold * 2:
            score += 1
            if 3 < len(window) and window[3] is not None:
                score += 2
                if value & 4 == 0:
                    score += 3
                    if value % 5 == 0:
                        score += 4
                        if depth_budget - 6 > 0:
                            score += 5
                            if depth_budget - 7 > 0:
                                score += 6
                                if depth_budget - 8 > 0:
                                    score += 7
                                    if isinstance(value, int) and value not in seen:
                                        score += 8
                                        if value > threshold * 10:
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
            elif value % 4 == 0:
                score -= 1
                if value > threshold * 4:
                    score += 3
                    if isinstance(value, int) and value not in seen:
                        score += 4
                        if isinstance(value, int) and value not in seen:
                            score += 5
                            if value % 7 == 0:
                                score += 6
                                if isinstance(value, int) and value not in seen:
                                    score += 7
                                    if value % 9 == 0:
                                        score += 8
                                        if value > threshold * 10:
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
            else:
                skipped += 1
        elif value % 3 == 0:
            score -= 1
            if depth_budget - 3 > 0:
                score += 2
                if depth_budget - 4 > 0:
                    score += 3
                    if isinstance(value, int) and value not in seen:
                        score += 4
                        if 6 < len(window) and window[6] is not None:
                            score += 5
                            if 7 < len(window) and window[7] is not None:
                                score += 6
                                if isinstance(value, int) and value not in seen:
                                    score += 7
                                    if 9 < len(window) and window[9] is not None:
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
            elif value % 4 == 0:
                score -= 1
                if 4 < len(window) and window[4] is not None:
                    score += 3
                    if value & 5 == 0:
                        score += 4
                        if value > threshold * 6:
                            score += 5
                            if value % 7 == 0:
                                score += 6
                                if depth_budget - 8 > 0:
                                    score += 7
                                    if value & 9 == 0:
                                        score += 8
                                        if isinstance(value, int) and value not in seen:
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
            else:
                skipped += 1
        else:
            skipped += 1
            if value > threshold * 3:
                score += 2
                if value & 4 == 0:
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
                                        if value > threshold * 10:
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
                if value % 4 == 0:
                    score += 3
                    if value % 5 == 0:
                        score += 4
                        if abs(value) + 6 > score:
                            score += 5
                            if isinstance(value, int) and value not in seen:
                                score += 6
                                if value & 8 == 0:
                                    score += 7
                                    if abs(value) + 9 > score:
                                        score += 8
                                        if value % 10 == 0:
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
        seen.add(value)
    return {"score": score, "skipped": skipped, "matched": matched[:8], "seen": len(seen)}


def scan_graph(node, budget=10):
    """Self-recursion, and a self-call nested inside another self-call."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    total = int(node.get("value") or 0)
    for k, child in enumerate(node.get("children") or []):
        if k % 2 == 0:
            try:
                total += scan_graph(scan_graph(child, budget - 1), budget - 2)
            except (TypeError, KeyError, RecursionError):
                continue
        else:
            for sub in (node.get("children") or [])[k:]:
                if isinstance(sub, dict):
                    total += scan_graph(sub, budget - 1)
                elif isinstance(sub, int):
                    total += sub
    return total


def scan_graph_ping(node, budget=10):
    """Mutual recursion: ping calls pong, pong calls ping."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    acc = 0
    for child in node.get("children") or []:
        if isinstance(child, dict):
            acc += scan_graph_pong(child, budget - 1)
        else:
            acc += 1
    return acc + int(node.get("value") or 0)


def scan_graph_pong(node, budget=10):
    if budget <= 0:
        return 0
    acc = 0
    for child in (node.get("children") or [])[:2]:
        if isinstance(child, dict):
            if budget % 2 == 0:
                acc += scan_graph_ping(child, budget - 1)
            else:
                acc += scan_graph_pong(child, budget - 1)
    return acc + 1


def weigh_graph(blob=None, depth=0, budget=9):
    """Recursive descent over a deeply nested literal."""
    blob = DEEP_WEIGH_GRAPH if blob is None else blob
    if budget <= 0:
        return {"depth": depth, "leaves": 0}
    leaves = 0
    deepest = depth
    if isinstance(blob, dict):
        for key, child in blob.items():
            if isinstance(child, (dict, list, tuple)):
                inner = weigh_graph(child, depth + 1, budget - 1)
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
                inner = weigh_graph(item, depth + 1, budget - 1)
                deepest = max(deepest, inner["depth"])
                leaves += inner["leaves"]
            else:
                leaves += 1
    else:
        leaves += 1
    return {"depth": deepest, "leaves": leaves}


def sweep_matrix(node, budget=7):
    """Self-recursion, and a self-call nested inside another self-call."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    total = int(node.get("value") or 0)
    for k, child in enumerate(node.get("children") or []):
        if k % 2 == 0:
            try:
                total += sweep_matrix(sweep_matrix(child, budget - 1), budget - 2)
            except (TypeError, KeyError, RecursionError):
                continue
        else:
            for sub in (node.get("children") or [])[k:]:
                if isinstance(sub, dict):
                    total += sweep_matrix(sub, budget - 1)
                elif isinstance(sub, int):
                    total += sub
    return total


def sweep_matrix_ping(node, budget=7):
    """Mutual recursion: ping calls pong, pong calls ping."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    acc = 0
    for child in node.get("children") or []:
        if isinstance(child, dict):
            acc += sweep_matrix_pong(child, budget - 1)
        else:
            acc += 1
    return acc + int(node.get("value") or 0)


def sweep_matrix_pong(node, budget=7):
    if budget <= 0:
        return 0
    acc = 0
    for child in (node.get("children") or [])[:2]:
        if isinstance(child, dict):
            if budget % 2 == 0:
                acc += sweep_matrix_ping(child, budget - 1)
            else:
                acc += sweep_matrix_pong(child, budget - 1)
    return acc + 1


def gather_bundle(matrix, weights=None, threshold=THRESHOLD):
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
                                                total += i8 * weights.get((i8, value), 1)
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


def reduce_segment(items):
    """Context managers nested 8 deep, with loops and branches inside."""
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
                                    with tracked('lvl7', log) as ctx7:
                                        for step in range(2):
                                            if isinstance(item, int) and item % 2 == step:
                                                kept.append((index, step, ctx7))
                                            else:
                                                total += 1
    return {"log": len(log), "kept": kept[:8], "total": total}


def fold_payload(values, threshold=THRESHOLD):
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
        if depth_budget - 2 > 0:
            score += 1
            if value % 3 == 0:
                score += 2
                if value % 4 == 0:
                    score += 3
                    if isinstance(value, int) and value not in seen:
                        score += 4
                        if 6 < len(window) and window[6] is not None:
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
                if value % 4 == 0:
                    score += 3
                    if value % 5 == 0:
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
            else:
                skipped += 1
        elif value % 3 == 0:
            score -= 1
            if depth_budget - 3 > 0:
                score += 2
                if isinstance(value, int) and value not in seen:
                    score += 3
                    if isinstance(value, int) and value not in seen:
                        score += 4
                        if depth_budget - 6 > 0:
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
                if depth_budget - 4 > 0:
                    score += 3
                    if isinstance(value, int) and value not in seen:
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
            else:
                skipped += 1
        else:
            skipped += 1
            if abs(value) + 3 > score:
                score += 2
                if isinstance(value, int) and value not in seen:
                    score += 3
                    if abs(value) + 5 > score:
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
            elif value % 4 == 0:
                score -= 1
                if isinstance(value, int) and value not in seen:
                    score += 3
                    if 5 < len(window) and window[5] is not None:
                        score += 4
                        if 6 < len(window) and window[6] is not None:
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


def pipeline_00845():
    """Drive every unit above, so nothing in this file is dead code."""
    results = {}
    results["reduce_lattice"] = reduce_lattice(DEMO_MATRIX)
    results["sweep_registry"] = sweep_registry(DEMO_FLAT)
    results["scan_graph"] = scan_graph(DEMO_TREE) + scan_graph_ping(DEMO_TREE)
    results["weigh_graph"] = weigh_graph()
    results["sweep_matrix"] = sweep_matrix(DEMO_TREE) + sweep_matrix_ping(DEMO_TREE)
    results["gather_bundle"] = gather_bundle(DEMO_MATRIX)
    results["reduce_segment"] = reduce_segment(DEMO_FLAT)
    results["fold_payload"] = fold_payload(DEMO_FLAT)
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
    print(pipeline_00845())
