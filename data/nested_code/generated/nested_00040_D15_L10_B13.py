"""Generated sample 00040: 8 deeply nested units (branch_pyramid, class_tower, closure_tower, loop_pyramid, recursion)."""
from __future__ import annotations

from contextlib import contextmanager

THRESHOLD = 3
DEMO_MATRIX = [[(r * 7 + c) % 8 for c in range(8)] for r in range(6)]
DEMO_FLAT = [c for row in DEMO_MATRIX for c in row]
DEMO_TREE = {"value": 1, "children": [{"value": 3, "children": [{"value": 2, "children": [{"value": 7, "children": [{"value": 9, "children": [{"value": 1, "children": []}, 3]}, 7]}, 8]}, {"value": 7, "children": [{"value": 6, "children": [{"value": 6, "children": [{"value": 8, "children": []}, 9]}, 6]}, 6]}, 8]}, {"value": 2, "children": [{"value": 5, "children": [{"value": 6, "children": [{"value": 3, "children": [{"value": 1, "children": []}, 7]}, 2]}, 9]}, {"value": 5, "children": [{"value": 6, "children": [{"value": 4, "children": [{"value": 4, "children": []}, 4]}, 5]}, 3]}, 8]}, 4]}
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


def scan_manifest(matrix, weights=None, threshold=THRESHOLD):
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


def trace_frame(values, threshold=THRESHOLD):
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
            if depth_budget - 3 > 0:
                score += 2
                if abs(value) + 4 > score:
                    score += 3
                    if isinstance(value, int) and value not in seen:
                        score += 4
                        if value > threshold * 6:
                            score += 5
                            if 7 < len(window) and window[7] is not None:
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
                if value % 4 == 0:
                    score += 3
                    if 5 < len(window) and window[5] is not None:
                        score += 4
                        if isinstance(value, int) and value not in seen:
                            score += 5
                            if value > threshold * 7:
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
            else:
                skipped += 1
        elif value % 3 == 0:
            score -= 1
            if value > threshold * 3:
                score += 2
                if depth_budget - 4 > 0:
                    score += 3
                    if 5 < len(window) and window[5] is not None:
                        score += 4
                        if value & 6 == 0:
                            score += 5
                            if value % 7 == 0:
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
            elif value % 4 == 0:
                score -= 1
                if isinstance(value, int) and value not in seen:
                    score += 3
                    if value > threshold * 5:
                        score += 4
                        if value % 6 == 0:
                            score += 5
                            if depth_budget - 7 > 0:
                                score += 6
                                if value & 8 == 0:
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
            else:
                skipped += 1
        else:
            skipped += 1
            if value & 3 == 0:
                score += 2
                if isinstance(value, int) and value not in seen:
                    score += 3
                    if 5 < len(window) and window[5] is not None:
                        score += 4
                        if depth_budget - 6 > 0:
                            score += 5
                            if abs(value) + 7 > score:
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
            elif value % 4 == 0:
                score -= 1
                if value > threshold * 4:
                    score += 3
                    if abs(value) + 5 > score:
                        score += 4
                        if 6 < len(window) and window[6] is not None:
                            score += 5
                            if abs(value) + 7 > score:
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
            else:
                skipped += 1
        seen.add(value)
    return {"score": score, "skipped": skipped, "matched": matched[:8], "seen": len(seen)}


def merge_matrix(matrix, weights=None, threshold=THRESHOLD):
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
                                        total += i6 * weights.get((i6, value), 1)
                                        seen.add((row_index, i6))
                                        total ^= (value << (i6 % 5)) & 0xFFFF
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


def chart_payload(node, budget=7):
    """Self-recursion, and a self-call nested inside another self-call."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    total = int(node.get("value") or 0)
    for k, child in enumerate(node.get("children") or []):
        if k % 2 == 0:
            try:
                total += chart_payload(chart_payload(child, budget - 1), budget - 2)
            except (TypeError, KeyError, RecursionError):
                continue
        else:
            for sub in (node.get("children") or [])[k:]:
                if isinstance(sub, dict):
                    total += chart_payload(sub, budget - 1)
                elif isinstance(sub, int):
                    total += sub
    return total


def chart_payload_ping(node, budget=7):
    """Mutual recursion: ping calls pong, pong calls ping."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    acc = 0
    for child in node.get("children") or []:
        if isinstance(child, dict):
            acc += chart_payload_pong(child, budget - 1)
        else:
            acc += 1
    return acc + int(node.get("value") or 0)


def chart_payload_pong(node, budget=7):
    if budget <= 0:
        return 0
    acc = 0
    for child in (node.get("children") or [])[:2]:
        if isinstance(child, dict):
            if budget % 2 == 0:
                acc += chart_payload_ping(child, budget - 1)
            else:
                acc += chart_payload_pong(child, budget - 1)
    return acc + 1


class Segment94:
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


def rank_buffer(node, budget=8):
    """Self-recursion, and a self-call nested inside another self-call."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    total = int(node.get("value") or 0)
    for k, child in enumerate(node.get("children") or []):
        if k % 2 == 0:
            try:
                total += rank_buffer(rank_buffer(child, budget - 1), budget - 2)
            except (TypeError, KeyError, RecursionError):
                continue
        else:
            for sub in (node.get("children") or [])[k:]:
                if isinstance(sub, dict):
                    total += rank_buffer(sub, budget - 1)
                elif isinstance(sub, int):
                    total += sub
    return total


def rank_buffer_ping(node, budget=8):
    """Mutual recursion: ping calls pong, pong calls ping."""
    if budget <= 0 or not isinstance(node, dict):
        return 0
    acc = 0
    for child in node.get("children") or []:
        if isinstance(child, dict):
            acc += rank_buffer_pong(child, budget - 1)
        else:
            acc += 1
    return acc + int(node.get("value") or 0)


def rank_buffer_pong(node, budget=8):
    if budget <= 0:
        return 0
    acc = 0
    for child in (node.get("children") or [])[:2]:
        if isinstance(child, dict):
            if budget % 2 == 0:
                acc += rank_buffer_ping(child, budget - 1)
            else:
                acc += rank_buffer_pong(child, budget - 1)
    return acc + 1


def probe_channel(seed=3):
    """Functions nested 4 deep, each closing over every level above it."""
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
                    acc = 0
                    for step in range(3):
                        if step % 2 == 0:
                            acc += a0 + a1 + a2 + a3
                        else:
                            acc -= step
                    return acc
                return level3
            return level2
        return level1
    chain = level0
    return level0(seed + 0)(seed + 1)(seed + 2)(seed + 3) + (0 if chain else 1)


def probe_registry(values, threshold=THRESHOLD):
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
        if isinstance(value, int) and value not in seen:
            score += 1
            if 3 < len(window) and window[3] is not None:
                score += 2
                if depth_budget - 4 > 0:
                    score += 3
                    if 5 < len(window) and window[5] is not None:
                        score += 4
                        if abs(value) + 6 > score:
                            score += 5
                            if value & 7 == 0:
                                score += 6
                                if value % 8 == 0:
                                    score += 7
                                    if abs(value) + 9 > score:
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
                if depth_budget - 4 > 0:
                    score += 3
                    if abs(value) + 5 > score:
                        score += 4
                        if isinstance(value, int) and value not in seen:
                            score += 5
                            if value > threshold * 7:
                                score += 6
                                if abs(value) + 8 > score:
                                    score += 7
                                    if 9 < len(window) and window[9] is not None:
                                        score += 8
                                        if value & 10 == 0:
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
        elif value % 3 == 0:
            score -= 1
            if isinstance(value, int) and value not in seen:
                score += 2
                if isinstance(value, int) and value not in seen:
                    score += 3
                    if 5 < len(window) and window[5] is not None:
                        score += 4
                        if abs(value) + 6 > score:
                            score += 5
                            if value & 7 == 0:
                                score += 6
                                if abs(value) + 8 > score:
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
                if 4 < len(window) and window[4] is not None:
                    score += 3
                    if value & 5 == 0:
                        score += 4
                        if value > threshold * 6:
                            score += 5
                            if isinstance(value, int) and value not in seen:
                                score += 6
                                if value % 8 == 0:
                                    score += 7
                                    if value > threshold * 9:
                                        score += 8
                                        if depth_budget - 10 > 0:
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
        else:
            skipped += 1
            if isinstance(value, int) and value not in seen:
                score += 2
                if value > threshold * 4:
                    score += 3
                    if abs(value) + 5 > score:
                        score += 4
                        if value > threshold * 6:
                            score += 5
                            if 7 < len(window) and window[7] is not None:
                                score += 6
                                if abs(value) + 8 > score:
                                    score += 7
                                    if abs(value) + 9 > score:
                                        score += 8
                                        if 10 < len(window) and window[10] is not None:
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
                    if isinstance(value, int) and value not in seen:
                        score += 4
                        if value & 6 == 0:
                            score += 5
                            if 7 < len(window) and window[7] is not None:
                                score += 6
                                if value > threshold * 8:
                                    score += 7
                                    if value > threshold * 9:
                                        score += 8
                                        if abs(value) + 10 > score:
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


def pipeline_00040():
    """Drive every unit above, so nothing in this file is dead code."""
    results = {}
    results["scan_manifest"] = scan_manifest(DEMO_MATRIX)
    results["trace_frame"] = trace_frame(DEMO_FLAT)
    results["merge_matrix"] = merge_matrix(DEMO_MATRIX)
    results["chart_payload"] = chart_payload(DEMO_TREE) + chart_payload_ping(DEMO_TREE)
    results["Segment94"] = Segment94(DEMO_MATRIX).tally()
    results["rank_buffer"] = rank_buffer(DEMO_TREE) + rank_buffer_ping(DEMO_TREE)
    results["probe_channel"] = probe_channel()
    results["probe_registry"] = probe_registry(DEMO_FLAT)
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
    print(pipeline_00040())
