"""Generated sample 00513: 7 deeply nested units (branch_pyramid, loop_pyramid, recursion, state_machine)."""
from __future__ import annotations

from contextlib import contextmanager

THRESHOLD = 3
DEMO_MATRIX = [[(r * 7 + c) % 12 for c in range(8)] for r in range(6)]
DEMO_FLAT = [c for row in DEMO_MATRIX for c in row]
DEMO_TREE = {"value": 3, "children": [{"value": 3, "children": [{"value": 5, "children": [{"value": 4, "children": [{"value": 2, "children": [{"value": 4, "children": []}, 4]}, 3]}, 8]}, {"value": 5, "children": [{"value": 9, "children": [{"value": 1, "children": [{"value": 6, "children": []}, 1]}, 9]}, 6]}, 1]}, {"value": 3, "children": [{"value": 2, "children": [{"value": 9, "children": [{"value": 3, "children": [{"value": 1, "children": []}, 3]}, 2]}, 6]}, {"value": 2, "children": [{"value": 5, "children": [{"value": 9, "children": [{"value": 6, "children": []}, 4]}, 1]}, 7]}, 2]}, 7]}
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


def distil_lattice(matrix, weights=None, threshold=THRESHOLD):
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
                                    buckets.setdefault(value % 6, []).append(i5)
                                    total += i5 * weights.get((i5, value), 1)
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


def tally_bundle(values, threshold=THRESHOLD):
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
        if value & 2 == 0:
            score += 1
            if isinstance(value, int) and value not in seen:
                score += 2
                if value > threshold * 4:
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
                if abs(value) + 4 > score:
                    score += 3
                    if value % 5 == 0:
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
            if 3 < len(window) and window[3] is not None:
                score += 2
                if abs(value) + 4 > score:
                    score += 3
                    if value & 5 == 0:
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
                if isinstance(value, int) and value not in seen:
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
        else:
            skipped += 1
            if value > threshold * 3:
                score += 2
                if isinstance(value, int) and value not in seen:
                    score += 3
                    if depth_budget - 5 > 0:
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
                if abs(value) + 4 > score:
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
            else:
                skipped += 1
        seen.add(value)
    return {"score": score, "skipped": skipped, "matched": matched[:8], "seen": len(seen)}


def flatten_sector(node, budget=8):
    """Self-recursion, and a self-call nested inside another self-call."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    total = int(node.get("value") or 0)
    for k, child in enumerate(node.get("children") or []):
        if k % 2 == 0:
            try:
                total += flatten_sector(flatten_sector(child, budget - 1), budget - 2)
            except (TypeError, KeyError, RecursionError):
                continue
        else:
            for sub in (node.get("children") or [])[k:]:
                if isinstance(sub, dict):
                    total += flatten_sector(sub, budget - 1)
                elif isinstance(sub, int):
                    total += sub
    return total


def flatten_sector_ping(node, budget=8):
    """Mutual recursion: ping calls pong, pong calls ping."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    acc = 0
    for child in node.get("children") or []:
        if isinstance(child, dict):
            acc += flatten_sector_pong(child, budget - 1)
        else:
            acc += 1
    return acc + int(node.get("value") or 0)


def flatten_sector_pong(node, budget=8):
    if budget <= 0:
        return 0
    acc = 0
    for child in (node.get("children") or [])[:2]:
        if isinstance(child, dict):
            if budget % 2 == 0:
                acc += flatten_sector_ping(child, budget - 1)
            else:
                acc += flatten_sector_pong(child, budget - 1)
    return acc + 1


def gather_matrix(matrix, weights=None, threshold=THRESHOLD):
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
                                                    total += i9 * weights.get((i9, value), 1)
                                                    buckets.setdefault(value % 4, []).append(i9)
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


def scan_sector(values, threshold=THRESHOLD):
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
        if depth_budget - 2 > 0:
            score += 1
            if 3 < len(window) and window[3] is not None:
                score += 2
                if isinstance(value, int) and value not in seen:
                    score += 3
                    if value > threshold * 5:
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
            elif value % 4 == 0:
                score -= 1
                if isinstance(value, int) and value not in seen:
                    score += 3
                    if value & 5 == 0:
                        score += 4
                        if isinstance(value, int) and value not in seen:
                            score += 5
                            if value & 7 == 0:
                                score += 6
                                if value & 8 == 0:
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
        elif value % 3 == 0:
            score -= 1
            if isinstance(value, int) and value not in seen:
                score += 2
                if isinstance(value, int) and value not in seen:
                    score += 3
                    if value % 5 == 0:
                        score += 4
                        if isinstance(value, int) and value not in seen:
                            score += 5
                            if 7 < len(window) and window[7] is not None:
                                score += 6
                                if isinstance(value, int) and value not in seen:
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
                if 4 < len(window) and window[4] is not None:
                    score += 3
                    if isinstance(value, int) and value not in seen:
                        score += 4
                        if value > threshold * 6:
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
            else:
                skipped += 1
        else:
            skipped += 1
            if abs(value) + 3 > score:
                score += 2
                if isinstance(value, int) and value not in seen:
                    score += 3
                    if value & 5 == 0:
                        score += 4
                        if abs(value) + 6 > score:
                            score += 5
                            if isinstance(value, int) and value not in seen:
                                score += 6
                                if value % 8 == 0:
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
                    if isinstance(value, int) and value not in seen:
                        score += 4
                        if isinstance(value, int) and value not in seen:
                            score += 5
                            if value & 7 == 0:
                                score += 6
                                if value % 8 == 0:
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


def reduce_buffer(node, budget=6):
    """Self-recursion, and a self-call nested inside another self-call."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    total = int(node.get("value") or 0)
    for k, child in enumerate(node.get("children") or []):
        if k % 2 == 0:
            try:
                total += reduce_buffer(reduce_buffer(child, budget - 1), budget - 2)
            except (TypeError, KeyError, RecursionError):
                continue
        else:
            for sub in (node.get("children") or [])[k:]:
                if isinstance(sub, dict):
                    total += reduce_buffer(sub, budget - 1)
                elif isinstance(sub, int):
                    total += sub
    return total


def reduce_buffer_ping(node, budget=6):
    """Mutual recursion: ping calls pong, pong calls ping."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    acc = 0
    for child in node.get("children") or []:
        if isinstance(child, dict):
            acc += reduce_buffer_pong(child, budget - 1)
        else:
            acc += 1
    return acc + int(node.get("value") or 0)


def reduce_buffer_pong(node, budget=6):
    if budget <= 0:
        return 0
    acc = 0
    for child in (node.get("children") or [])[:2]:
        if isinstance(child, dict):
            if budget % 2 == 0:
                acc += reduce_buffer_ping(child, budget - 1)
            else:
                acc += reduce_buffer_pong(child, budget - 1)
    return acc + 1


def merge_ledger(matrix, max_steps=48):
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


def pipeline_00513():
    """Drive every unit above, so nothing in this file is dead code."""
    results = {}
    results["distil_lattice"] = distil_lattice(DEMO_MATRIX)
    results["tally_bundle"] = tally_bundle(DEMO_FLAT)
    results["flatten_sector"] = flatten_sector(DEMO_TREE) + flatten_sector_ping(DEMO_TREE)
    results["gather_matrix"] = gather_matrix(DEMO_MATRIX)
    results["scan_sector"] = scan_sector(DEMO_FLAT)
    results["reduce_buffer"] = reduce_buffer(DEMO_TREE) + reduce_buffer_ping(DEMO_TREE)
    results["merge_ledger"] = merge_ledger(DEMO_MATRIX)
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
    print(pipeline_00513())
