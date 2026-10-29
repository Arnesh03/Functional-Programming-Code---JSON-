"""Generated sample 00110: 8 deeply nested units (async_nested, branch_pyramid, data_walk, loop_pyramid, state_machine)."""
from __future__ import annotations

import asyncio
from contextlib import contextmanager, asynccontextmanager

THRESHOLD = 3
DEMO_MATRIX = [[(r * 11 + c) % 12 for c in range(8)] for r in range(6)]
DEMO_FLAT = [c for row in DEMO_MATRIX for c in row]
DEMO_TREE = {"value": 3, "children": [{"value": 6, "children": [{"value": 3, "children": [{"value": 1, "children": [{"value": 5, "children": [{"value": 4, "children": []}, 5]}, 5]}, 2]}, {"value": 5, "children": [{"value": 9, "children": [{"value": 4, "children": [{"value": 6, "children": []}, 2]}, 1]}, 2]}, 6]}, {"value": 4, "children": [{"value": 6, "children": [{"value": 6, "children": [{"value": 8, "children": [{"value": 4, "children": []}, 8]}, 3]}, 5]}, {"value": 2, "children": [{"value": 1, "children": [{"value": 2, "children": [{"value": 1, "children": []}, 8]}, 9]}, 8]}, 3]}, 2]}
DEMO_EVENTS = [
    {"kind": "row", "cells": [1, 7, 3]},
    {"kind": "row", "cells": [9, 8]},
    [4, 2, 1, 0],
    7,
    3.5,
    "sample",
    {"kind": "meta", "cells": []},
]
DEEP_TRACE_CHANNEL = [{"level": 6, "items": [([{"level": 3, "items": [([1, 8], 3), 8]}, 0], 4), 3]}, 2]
DEEP_WEIGH_PAYLOAD = [{"level": 6, "items": [([{"level": 3, "items": [([1, 2], 7), 1]}, 8], 2), 9]}, 7]


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


def rank_registry(matrix, weights=None, threshold=THRESHOLD):
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
                                                    buckets.setdefault(value % 4, []).append(i9)
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


def probe_manifest(values, threshold=THRESHOLD):
    """An if/elif/else ladder nested 7 deep, inside a loop."""
    score = skipped = 0
    matched, seen = [], set()
    window = list(values)[:24]
    depth_budget = 11
    for value in window:
        if value is None:
            skipped += 1
            continue
        if not isinstance(value, int):
            value = len(str(value))
        if 2 < len(window) and window[2] is not None:
            score += 1
            if value > threshold * 3:
                score += 2
                if abs(value) + 4 > score:
                    score += 3
                    if value & 5 == 0:
                        score += 4
                        if abs(value) + 6 > score:
                            score += 5
                            if isinstance(value, int) and value not in seen:
                                score += 6
                                if isinstance(value, int) and value not in seen:
                                    score += 7
                                    matched.append(('deep', value))
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
                    if depth_budget - 5 > 0:
                        score += 4
                        if depth_budget - 6 > 0:
                            score += 5
                            if value > threshold * 7:
                                score += 6
                                if 8 < len(window) and window[8] is not None:
                                    score += 7
                                    matched.append(('deep', value))
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
                    if value % 5 == 0:
                        score += 4
                        if value & 6 == 0:
                            score += 5
                            if isinstance(value, int) and value not in seen:
                                score += 6
                                if depth_budget - 8 > 0:
                                    score += 7
                                    matched.append(('deep', value))
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
                        if 6 < len(window) and window[6] is not None:
                            score += 5
                            if 7 < len(window) and window[7] is not None:
                                score += 6
                                if value % 8 == 0:
                                    score += 7
                                    matched.append(('deep', value))
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
                if value > threshold * 4:
                    score += 3
                    if value % 5 == 0:
                        score += 4
                        if isinstance(value, int) and value not in seen:
                            score += 5
                            if abs(value) + 7 > score:
                                score += 6
                                if isinstance(value, int) and value not in seen:
                                    score += 7
                                    matched.append(('deep', value))
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
                        if value > threshold * 6:
                            score += 5
                            if isinstance(value, int) and value not in seen:
                                score += 6
                                if value & 8 == 0:
                                    score += 7
                                    matched.append(('deep', value))
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


def collect_window(values, threshold=THRESHOLD):
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
        if abs(value) + 2 > score:
            score += 1
            if 3 < len(window) and window[3] is not None:
                score += 2
                if abs(value) + 4 > score:
                    score += 3
                    if value & 5 == 0:
                        score += 4
                        if abs(value) + 6 > score:
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
            elif value % 4 == 0:
                score -= 1
                if isinstance(value, int) and value not in seen:
                    score += 3
                    if 5 < len(window) and window[5] is not None:
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
            else:
                skipped += 1
        elif value % 3 == 0:
            score -= 1
            if value & 3 == 0:
                score += 2
                if 4 < len(window) and window[4] is not None:
                    score += 3
                    if value % 5 == 0:
                        score += 4
                        if 6 < len(window) and window[6] is not None:
                            score += 5
                            if abs(value) + 7 > score:
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
                    if abs(value) + 5 > score:
                        score += 4
                        if value > threshold * 6:
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
            else:
                skipped += 1
        else:
            skipped += 1
            if abs(value) + 3 > score:
                score += 2
                if value % 4 == 0:
                    score += 3
                    if abs(value) + 5 > score:
                        score += 4
                        if value & 6 == 0:
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
                if value > threshold * 4:
                    score += 3
                    if isinstance(value, int) and value not in seen:
                        score += 4
                        if depth_budget - 6 > 0:
                            score += 5
                            if abs(value) + 7 > score:
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


def probe_cohort(matrix, max_steps=48):
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


def trace_channel(blob=None, depth=0, budget=11):
    """Recursive descent over a deeply nested literal."""
    blob = DEEP_TRACE_CHANNEL if blob is None else blob
    if budget <= 0:
        return {"depth": depth, "leaves": 0}
    leaves = 0
    deepest = depth
    if isinstance(blob, dict):
        for key, child in blob.items():
            if isinstance(child, (dict, list, tuple)):
                inner = trace_channel(child, depth + 1, budget - 1)
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
                inner = trace_channel(item, depth + 1, budget - 1)
                deepest = max(deepest, inner["depth"])
                leaves += inner["leaves"]
            else:
                leaves += 1
    else:
        leaves += 1
    return {"depth": deepest, "leaves": leaves}


async def flatten_window(matrix):
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


def probe_registry(matrix, max_steps=48):
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


def weigh_payload(blob=None, depth=0, budget=8):
    """Recursive descent over a deeply nested literal."""
    blob = DEEP_WEIGH_PAYLOAD if blob is None else blob
    if budget <= 0:
        return {"depth": depth, "leaves": 0}
    leaves = 0
    deepest = depth
    if isinstance(blob, dict):
        for key, child in blob.items():
            if isinstance(child, (dict, list, tuple)):
                inner = weigh_payload(child, depth + 1, budget - 1)
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
                inner = weigh_payload(item, depth + 1, budget - 1)
                deepest = max(deepest, inner["depth"])
                leaves += inner["leaves"]
            else:
                leaves += 1
    else:
        leaves += 1
    return {"depth": deepest, "leaves": leaves}


def pipeline_00110():
    """Drive every unit above, so nothing in this file is dead code."""
    results = {}
    results["rank_registry"] = rank_registry(DEMO_MATRIX)
    results["probe_manifest"] = probe_manifest(DEMO_FLAT)
    results["collect_window"] = collect_window(DEMO_FLAT)
    results["probe_cohort"] = probe_cohort(DEMO_MATRIX)
    results["trace_channel"] = trace_channel()
    results["flatten_window"] = asyncio.run(flatten_window(DEMO_MATRIX))
    results["probe_registry"] = probe_registry(DEMO_MATRIX)
    results["weigh_payload"] = weigh_payload()
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
    print(pipeline_00110())
