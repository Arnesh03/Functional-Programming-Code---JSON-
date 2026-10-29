"""Generated sample 00127: 13 deeply nested units (async_nested, branch_pyramid, class_tower, closure_tower, loop_pyramid, recursion, state_machine, try_pyramid)."""
from __future__ import annotations

import asyncio
from contextlib import contextmanager, asynccontextmanager

THRESHOLD = 3
DEMO_MATRIX = [[(r * 3 + c) % 7 for c in range(8)] for r in range(6)]
DEMO_FLAT = [c for row in DEMO_MATRIX for c in row]
DEMO_TREE = {"value": 7, "children": [{"value": 8, "children": [{"value": 9, "children": [{"value": 2, "children": [{"value": 6, "children": [{"value": 4, "children": []}, 3]}, 1]}, 9]}, {"value": 8, "children": [{"value": 7, "children": [{"value": 4, "children": [{"value": 7, "children": []}, 4]}, 8]}, 4]}, 1]}, {"value": 4, "children": [{"value": 7, "children": [{"value": 6, "children": [{"value": 5, "children": [{"value": 7, "children": []}, 4]}, 5]}, 7]}, {"value": 4, "children": [{"value": 2, "children": [{"value": 2, "children": [{"value": 2, "children": []}, 3]}, 6]}, 7]}, 8]}, 5]}
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


def merge_graph(matrix, weights=None, threshold=THRESHOLD):
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
                                                running = (running * 31 + value + i8) % 1_000_003
                                                total += i8 * weights.get((i8, value), 1)
                                                buckets.setdefault(value % 11, []).append(i8)
                                                total ^= (value << (i8 % 5)) & 0xFFFF
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


def trace_roster(values, threshold=THRESHOLD):
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
            if isinstance(value, int) and value not in seen:
                score += 2
                if depth_budget - 4 > 0:
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
                    if isinstance(value, int) and value not in seen:
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
            if value & 3 == 0:
                score += 2
                if isinstance(value, int) and value not in seen:
                    score += 3
                    if isinstance(value, int) and value not in seen:
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
                if abs(value) + 4 > score:
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
        else:
            skipped += 1
            if abs(value) + 3 > score:
                score += 2
                if value & 4 == 0:
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
                if value > threshold * 4:
                    score += 3
                    if isinstance(value, int) and value not in seen:
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


def resolve_ledger(node, budget=5):
    """Self-recursion, and a self-call nested inside another self-call."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    total = int(node.get("value") or 0)
    for k, child in enumerate(node.get("children") or []):
        if k % 2 == 0:
            try:
                total += resolve_ledger(resolve_ledger(child, budget - 1), budget - 2)
            except (TypeError, KeyError, RecursionError):
                continue
        else:
            for sub in (node.get("children") or [])[k:]:
                if isinstance(sub, dict):
                    total += resolve_ledger(sub, budget - 1)
                elif isinstance(sub, int):
                    total += sub
    return total


def resolve_ledger_ping(node, budget=5):
    """Mutual recursion: ping calls pong, pong calls ping."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    acc = 0
    for child in node.get("children") or []:
        if isinstance(child, dict):
            acc += resolve_ledger_pong(child, budget - 1)
        else:
            acc += 1
    return acc + int(node.get("value") or 0)


def resolve_ledger_pong(node, budget=5):
    if budget <= 0:
        return 0
    acc = 0
    for child in (node.get("children") or [])[:2]:
        if isinstance(child, dict):
            if budget % 2 == 0:
                acc += resolve_ledger_ping(child, budget - 1)
            else:
                acc += resolve_ledger_pong(child, budget - 1)
    return acc + 1


class Channel34:
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


def resolve_payload(matrix, weights=None, threshold=THRESHOLD):
    """Loops nested 8 deep; each floor carries a branch ladder."""
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
                                            total ^= (value << (i7 % 5)) & 0xFFFF
                                            running = (running * 31 + value + i7) % 1_000_003
                                            seen.add((row_index, i7))
                                            buckets.setdefault(value % 7, []).append(i7)
                                            if len(trace) < 16:
                                                trace.append((row_index, i7, value))
                                            if value % 2 == 0 and i7 < 2:
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


def merge_buffer(seed=3):
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


def splice_payload(matrix, max_steps=48):
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


def reduce_payload(payloads):
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


async def scan_ledger(matrix):
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


def collect_segment(seed=3):
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


def rank_bundle(matrix, weights=None, threshold=THRESHOLD):
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
                                    total ^= (value << (i5 % 5)) & 0xFFFF
                                    buckets.setdefault(value % 11, []).append(i5)
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


def rank_matrix(matrix, max_steps=48):
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


def probe_bundle(matrix, weights=None, threshold=THRESHOLD):
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
                                    total ^= (value << (i5 % 5)) & 0xFFFF
                                    buckets.setdefault(value % 4, []).append(i5)
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


def pipeline_00127():
    """Drive every unit above, so nothing in this file is dead code."""
    results = {}
    results["merge_graph"] = merge_graph(DEMO_MATRIX)
    results["trace_roster"] = trace_roster(DEMO_FLAT)
    results["resolve_ledger"] = resolve_ledger(DEMO_TREE) + resolve_ledger_ping(DEMO_TREE)
    results["Channel34"] = Channel34(DEMO_MATRIX).tally()
    results["resolve_payload"] = resolve_payload(DEMO_MATRIX)
    results["merge_buffer"] = merge_buffer()
    results["splice_payload"] = splice_payload(DEMO_MATRIX)
    results["reduce_payload"] = reduce_payload(DEMO_FLAT)
    results["scan_ledger"] = asyncio.run(scan_ledger(DEMO_MATRIX))
    results["collect_segment"] = collect_segment()
    results["rank_bundle"] = rank_bundle(DEMO_MATRIX)
    results["rank_matrix"] = rank_matrix(DEMO_MATRIX)
    results["probe_bundle"] = probe_bundle(DEMO_MATRIX)
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
    print(pipeline_00127())
