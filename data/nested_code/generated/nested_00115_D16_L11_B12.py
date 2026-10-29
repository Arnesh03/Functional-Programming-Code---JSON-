"""Generated sample 00115: 9 deeply nested units (async_nested, branch_pyramid, data_walk, loop_pyramid, recursion, try_pyramid)."""
from __future__ import annotations

import asyncio
from contextlib import contextmanager, asynccontextmanager

THRESHOLD = 3
DEMO_MATRIX = [[(r * 4 + c) % 8 for c in range(8)] for r in range(6)]
DEMO_FLAT = [c for row in DEMO_MATRIX for c in row]
DEMO_TREE = {"value": 4, "children": [{"value": 3, "children": [{"value": 8, "children": [{"value": 4, "children": [{"value": 6, "children": [{"value": 7, "children": []}, 4]}, 4]}, 9]}, {"value": 6, "children": [{"value": 6, "children": [{"value": 5, "children": [{"value": 3, "children": []}, 8]}, 4]}, 5]}, 7]}, {"value": 8, "children": [{"value": 1, "children": [{"value": 2, "children": [{"value": 6, "children": [{"value": 3, "children": []}, 4]}, 9]}, 5]}, {"value": 8, "children": [{"value": 3, "children": [{"value": 6, "children": [{"value": 2, "children": []}, 9]}, 5]}, 7]}, 1]}, 9]}
DEMO_EVENTS = [
    {"kind": "row", "cells": [1, 7, 3]},
    {"kind": "row", "cells": [9, 8]},
    [4, 2, 1, 0],
    7,
    3.5,
    "sample",
    {"kind": "meta", "cells": []},
]
DEEP_RANK_WINDOW = [{"level": 6, "items": [([{"level": 3, "items": [([3, 5], 2), 9]}, 9], 2), 5]}, 5]


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


def splice_buffer(matrix, weights=None, threshold=THRESHOLD):
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
                                                    buckets.setdefault(value % 7, []).append(i9)
                                                    running = (running * 31 + value + i9) % 1_000_003
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


def splice_sector(values, threshold=THRESHOLD):
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
            if abs(value) + 3 > score:
                score += 2
                if value & 4 == 0:
                    score += 3
                    if value & 5 == 0:
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
                if abs(value) + 4 > score:
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
            else:
                skipped += 1
        else:
            skipped += 1
            if depth_budget - 3 > 0:
                score += 2
                if value & 4 == 0:
                    score += 3
                    if value % 5 == 0:
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
                if isinstance(value, int) and value not in seen:
                    score += 3
                    if value & 5 == 0:
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


def tally_frame(payloads):
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


async def trace_sector(matrix):
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


def probe_sector(values, threshold=THRESHOLD):
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
        if depth_budget - 2 > 0:
            score += 1
            if value % 3 == 0:
                score += 2
                if value > threshold * 4:
                    score += 3
                    if depth_budget - 5 > 0:
                        score += 4
                        if isinstance(value, int) and value not in seen:
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
                if value % 4 == 0:
                    score += 3
                    if 5 < len(window) and window[5] is not None:
                        score += 4
                        if 6 < len(window) and window[6] is not None:
                            score += 5
                            if value & 7 == 0:
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
            if depth_budget - 3 > 0:
                score += 2
                if value > threshold * 4:
                    score += 3
                    if isinstance(value, int) and value not in seen:
                        score += 4
                        if depth_budget - 6 > 0:
                            score += 5
                            if 7 < len(window) and window[7] is not None:
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
                if value % 4 == 0:
                    score += 3
                    if value & 5 == 0:
                        score += 4
                        if depth_budget - 6 > 0:
                            score += 5
                            if isinstance(value, int) and value not in seen:
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
            if depth_budget - 3 > 0:
                score += 2
                if value & 4 == 0:
                    score += 3
                    if value > threshold * 5:
                        score += 4
                        if isinstance(value, int) and value not in seen:
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
                if value & 4 == 0:
                    score += 3
                    if isinstance(value, int) and value not in seen:
                        score += 4
                        if value % 6 == 0:
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
            else:
                skipped += 1
        seen.add(value)
    return {"score": score, "skipped": skipped, "matched": matched[:8], "seen": len(seen)}


def trace_payload(node, budget=7):
    """Self-recursion, and a self-call nested inside another self-call."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    total = int(node.get("value") or 0)
    for k, child in enumerate(node.get("children") or []):
        if k % 2 == 0:
            try:
                total += trace_payload(trace_payload(child, budget - 1), budget - 2)
            except (TypeError, KeyError, RecursionError):
                continue
        else:
            for sub in (node.get("children") or [])[k:]:
                if isinstance(sub, dict):
                    total += trace_payload(sub, budget - 1)
                elif isinstance(sub, int):
                    total += sub
    return total


def trace_payload_ping(node, budget=7):
    """Mutual recursion: ping calls pong, pong calls ping."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    acc = 0
    for child in node.get("children") or []:
        if isinstance(child, dict):
            acc += trace_payload_pong(child, budget - 1)
        else:
            acc += 1
    return acc + int(node.get("value") or 0)


def trace_payload_pong(node, budget=7):
    if budget <= 0:
        return 0
    acc = 0
    for child in (node.get("children") or [])[:2]:
        if isinstance(child, dict):
            if budget % 2 == 0:
                acc += trace_payload_ping(child, budget - 1)
            else:
                acc += trace_payload_pong(child, budget - 1)
    return acc + 1


def rank_window(blob=None, depth=0, budget=13):
    """Recursive descent over a deeply nested literal."""
    blob = DEEP_RANK_WINDOW if blob is None else blob
    if budget <= 0:
        return {"depth": depth, "leaves": 0}
    leaves = 0
    deepest = depth
    if isinstance(blob, dict):
        for key, child in blob.items():
            if isinstance(child, (dict, list, tuple)):
                inner = rank_window(child, depth + 1, budget - 1)
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
                inner = rank_window(item, depth + 1, budget - 1)
                deepest = max(deepest, inner["depth"])
                leaves += inner["leaves"]
            else:
                leaves += 1
    else:
        leaves += 1
    return {"depth": deepest, "leaves": leaves}


def distil_manifest(node, budget=10):
    """Self-recursion, and a self-call nested inside another self-call."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    total = int(node.get("value") or 0)
    for k, child in enumerate(node.get("children") or []):
        if k % 2 == 0:
            try:
                total += distil_manifest(distil_manifest(child, budget - 1), budget - 2)
            except (TypeError, KeyError, RecursionError):
                continue
        else:
            for sub in (node.get("children") or [])[k:]:
                if isinstance(sub, dict):
                    total += distil_manifest(sub, budget - 1)
                elif isinstance(sub, int):
                    total += sub
    return total


def distil_manifest_ping(node, budget=10):
    """Mutual recursion: ping calls pong, pong calls ping."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    acc = 0
    for child in node.get("children") or []:
        if isinstance(child, dict):
            acc += distil_manifest_pong(child, budget - 1)
        else:
            acc += 1
    return acc + int(node.get("value") or 0)


def distil_manifest_pong(node, budget=10):
    if budget <= 0:
        return 0
    acc = 0
    for child in (node.get("children") or [])[:2]:
        if isinstance(child, dict):
            if budget % 2 == 0:
                acc += distil_manifest_ping(child, budget - 1)
            else:
                acc += distil_manifest_pong(child, budget - 1)
    return acc + 1


def collect_bundle(values, threshold=THRESHOLD):
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
        if depth_budget - 2 > 0:
            score += 1
            if isinstance(value, int) and value not in seen:
                score += 2
                if isinstance(value, int) and value not in seen:
                    score += 3
                    if 5 < len(window) and window[5] is not None:
                        score += 4
                        if 6 < len(window) and window[6] is not None:
                            score += 5
                            if abs(value) + 7 > score:
                                score += 6
                                if value > threshold * 8:
                                    score += 7
                                    if value > threshold * 9:
                                        score += 8
                                        if value % 10 == 0:
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
                if abs(value) + 4 > score:
                    score += 3
                    if 5 < len(window) and window[5] is not None:
                        score += 4
                        if depth_budget - 6 > 0:
                            score += 5
                            if 7 < len(window) and window[7] is not None:
                                score += 6
                                if abs(value) + 8 > score:
                                    score += 7
                                    if abs(value) + 9 > score:
                                        score += 8
                                        if abs(value) + 10 > score:
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
            if depth_budget - 3 > 0:
                score += 2
                if isinstance(value, int) and value not in seen:
                    score += 3
                    if abs(value) + 5 > score:
                        score += 4
                        if value % 6 == 0:
                            score += 5
                            if abs(value) + 7 > score:
                                score += 6
                                if 8 < len(window) and window[8] is not None:
                                    score += 7
                                    if abs(value) + 9 > score:
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
            elif value % 4 == 0:
                score -= 1
                if value % 4 == 0:
                    score += 3
                    if abs(value) + 5 > score:
                        score += 4
                        if value > threshold * 6:
                            score += 5
                            if abs(value) + 7 > score:
                                score += 6
                                if value > threshold * 8:
                                    score += 7
                                    if abs(value) + 9 > score:
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
            if 3 < len(window) and window[3] is not None:
                score += 2
                if value % 4 == 0:
                    score += 3
                    if value & 5 == 0:
                        score += 4
                        if depth_budget - 6 > 0:
                            score += 5
                            if value > threshold * 7:
                                score += 6
                                if depth_budget - 8 > 0:
                                    score += 7
                                    if 9 < len(window) and window[9] is not None:
                                        score += 8
                                        if isinstance(value, int) and value not in seen:
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
                    if isinstance(value, int) and value not in seen:
                        score += 4
                        if isinstance(value, int) and value not in seen:
                            score += 5
                            if abs(value) + 7 > score:
                                score += 6
                                if 8 < len(window) and window[8] is not None:
                                    score += 7
                                    if depth_budget - 9 > 0:
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
        seen.add(value)
    return {"score": score, "skipped": skipped, "matched": matched[:8], "seen": len(seen)}


def pipeline_00115():
    """Drive every unit above, so nothing in this file is dead code."""
    results = {}
    results["splice_buffer"] = splice_buffer(DEMO_MATRIX)
    results["splice_sector"] = splice_sector(DEMO_FLAT)
    results["tally_frame"] = tally_frame(DEMO_FLAT)
    results["trace_sector"] = asyncio.run(trace_sector(DEMO_MATRIX))
    results["probe_sector"] = probe_sector(DEMO_FLAT)
    results["trace_payload"] = trace_payload(DEMO_TREE) + trace_payload_ping(DEMO_TREE)
    results["rank_window"] = rank_window()
    results["distil_manifest"] = distil_manifest(DEMO_TREE) + distil_manifest_ping(DEMO_TREE)
    results["collect_bundle"] = collect_bundle(DEMO_FLAT)
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
    print(pipeline_00115())
