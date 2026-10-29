"""Ground truth for one Python file, read straight out of its AST.

The OPORD side had to have gold records written by hand, because nothing but a human knows what
an order means. Code does not have that problem: the parser already knows. So every sample in
this dataset carries a free, exact gold record, and a model extraction can be scored against it
without anyone annotating anything.

The record is the same shape the model is asked to produce (assets/schema/nested_code_schema_v1.json):
flat lists of scopes, blocks and relations that point at each other by id. Flat is right for
validation and scoring — every fact lives in exactly one place. `app.hierarchy` performs the join
afterwards for reading.

Two conventions worth stating, because they decide what the numbers mean:

  * `elif` is a nested `If` in Python's AST, so an if/elif/elif ladder counts as three levels of
    branch nesting. That is the convention the dataset manifest was measured with, and this
    module keeps it, so a scope's max_block_depth and the manifest's branch_depth agree.
  * A call is recorded only when it resolves to a scope declared in the same file. Calls to
    `len`, `print` or anything imported are not relations between scopes, and recording them
    would bury the structure in noise.
"""
from __future__ import annotations

import ast
from typing import Any, Dict, List, Optional, Set, Tuple

BLOCK_KIND: Dict[type, str] = {
    ast.For: "for",
    ast.AsyncFor: "async_for",
    ast.While: "while",
    ast.If: "if",
    ast.With: "with",
    ast.AsyncWith: "async_with",
}
for _name, _kind in (("Try", "try"), ("TryStar", "try"), ("Match", "match")):
    _node = getattr(ast, _name, None)
    if _node is not None:
        BLOCK_KIND[_node] = _kind

SCOPE_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
TRY_NODES = tuple(t for t in (getattr(ast, "Try", None), getattr(ast, "TryStar", None)) if t)


def _unparse(node: Optional[ast.AST], limit: int = 60) -> str:
    if node is None:
        return ""
    try:
        text = ast.unparse(node)
    except Exception:
        return ""
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


class _Builder:
    def __init__(self, file_id: str) -> None:
        self.file_id = file_id
        self.scopes: List[Dict[str, Any]] = []
        self.blocks: List[Dict[str, Any]] = []
        self.by_id: Dict[str, Dict[str, Any]] = {}
        self.calls: Dict[str, Set[str]] = {}
        self.inherits: List[Tuple[str, str]] = []
        self.yields_from: Set[Tuple[str, str]] = set()
        self._block_n = 0

    # -- scopes ------------------------------------------------------------------
    def add_scope(self, scope_id: str, name: str, kind: str, parent_id: str,
                  node: Optional[ast.AST] = None) -> Dict[str, Any]:
        rec: Dict[str, Any] = {
            "scope_id": scope_id,
            "name": name,
            "kind": kind,
            "parent_id": parent_id,
            "is_async": kind.startswith("async"),
            "is_recursive": False,
            "is_generator": False,
            "decorators": [_unparse(d) for d in getattr(node, "decorator_list", [])] if node else [],
            "params": [a.arg for a in getattr(getattr(node, "args", None), "args", [])] if node else [],
            "start_line": getattr(node, "lineno", 1) if node else 1,
            "end_line": getattr(node, "end_lineno", 1) if node else 1,
            "max_block_depth": 0,
            "block_kinds": [],
        }
        self.scopes.append(rec)
        self.by_id[scope_id] = rec
        self.calls.setdefault(scope_id, set())
        return rec

    # -- blocks ------------------------------------------------------------------
    def add_block(self, scope_id: str, kind: str, parent_block_id: str, depth: int,
                  line: int, test: str) -> str:
        self._block_n += 1
        bid = f"b{self._block_n:04d}"
        self.blocks.append({
            "block_id": bid,
            "scope_id": scope_id,
            "kind": kind,
            "parent_block_id": parent_block_id,
            "depth": depth,
            "line": line,
            "test": test,
        })
        scope = self.by_id.get(scope_id)
        if scope:
            scope["max_block_depth"] = max(scope["max_block_depth"], depth)
            if kind not in scope["block_kinds"]:
                scope["block_kinds"].append(kind)
        return bid

    # -- traversal ---------------------------------------------------------------
    def walk_body(self, body: List[ast.stmt], scope_id: str, parent_block: str, depth: int) -> None:
        for stmt in body:
            self.walk_stmt(stmt, scope_id, parent_block, depth)

    def walk_stmt(self, node: ast.stmt, scope_id: str, parent_block: str, depth: int) -> None:
        # A nested def or class opens a new scope; its body belongs to that scope, not this one,
        # and its block depth starts again from zero.
        if isinstance(node, SCOPE_NODES):
            self.enter_scope(node, scope_id)
            return

        self.collect_calls(node, scope_id)
        self.collect_yields(node, scope_id)

        kind = BLOCK_KIND.get(type(node))
        if kind is None:
            # Not a block of its own, but it may still contain nested statements worth walking.
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.stmt):
                    self.walk_stmt(child, scope_id, parent_block, depth)
            return

        here = depth + 1
        test = ""
        if isinstance(node, (ast.For, ast.AsyncFor)):
            test = f"{_unparse(node.target, 24)} in {_unparse(node.iter, 32)}"
        elif isinstance(node, (ast.While, ast.If)):
            test = _unparse(node.test)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            test = ", ".join(_unparse(i.context_expr, 28) for i in node.items)
        elif getattr(ast, "Match", None) and isinstance(node, ast.Match):
            test = _unparse(node.subject)

        bid = self.add_block(scope_id, kind, parent_block, here, node.lineno, test)

        if isinstance(node, TRY_NODES):
            self.walk_body(node.body, scope_id, bid, here)
            for handler in node.handlers:
                hid = self.add_block(scope_id, "except", bid, here + 1, handler.lineno,
                                     _unparse(handler.type, 40))
                self.walk_body(handler.body, scope_id, hid, here + 1)
            if node.orelse:
                eid = self.add_block(scope_id, "else", bid, here + 1, node.orelse[0].lineno, "")
                self.walk_body(node.orelse, scope_id, eid, here + 1)
            if node.finalbody:
                fid = self.add_block(scope_id, "finally", bid, here + 1, node.finalbody[0].lineno, "")
                self.walk_body(node.finalbody, scope_id, fid, here + 1)
            return

        if getattr(ast, "Match", None) and isinstance(node, ast.Match):
            for case in node.cases:
                cid = self.add_block(scope_id, "case", bid, here + 1,
                                     case.pattern.lineno, _unparse(case.pattern, 40))
                self.walk_body(case.body, scope_id, cid, here + 1)
            return

        self.walk_body(node.body, scope_id, bid, here)
        orelse = getattr(node, "orelse", None)
        if orelse:
            # `elif` is an If inside orelse: Python nests it, the measurement follows Python.
            self.walk_body(orelse, scope_id, bid, here)

    def enter_scope(self, node: ast.AST, parent_id: str) -> None:
        name = node.name
        scope_id = f"{parent_id}.{name}"
        parent = self.by_id.get(parent_id)
        if isinstance(node, ast.ClassDef):
            kind = "class"
        elif parent is not None and parent["kind"] == "class":
            kind = "async_method" if isinstance(node, ast.AsyncFunctionDef) else "method"
        else:
            kind = "async_function" if isinstance(node, ast.AsyncFunctionDef) else "function"

        if scope_id in self.by_id:  # same name twice in one namespace: keep both, distinct ids
            n = 2
            while f"{scope_id}#{n}" in self.by_id:
                n += 1
            scope_id = f"{scope_id}#{n}"

        self.add_scope(scope_id, name, kind, parent_id, node)

        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if isinstance(base, ast.Name):
                    self.inherits.append((scope_id, base.id))

        for deco in getattr(node, "decorator_list", []):
            self.collect_calls_expr(deco, parent_id)
        self.walk_body(node.body, scope_id, "", 0)

    # -- call / yield collection --------------------------------------------------
    def _prune_walk(self, node: ast.AST):
        """Walk a statement's expressions without crossing into a nested scope's body."""
        stack = [node]
        while stack:
            cur = stack.pop()
            for child in ast.iter_child_nodes(cur):
                if isinstance(child, SCOPE_NODES):
                    continue
                yield child
                stack.append(child)

    def collect_calls(self, node: ast.stmt, scope_id: str) -> None:
        for child in self._prune_walk(node):
            if isinstance(child, ast.Call):
                self._record_call(child, scope_id)

    def collect_calls_expr(self, node: ast.AST, scope_id: str) -> None:
        for child in [node, *self._prune_walk(node)]:
            if isinstance(child, ast.Call):
                self._record_call(child, scope_id)

    def _record_call(self, call: ast.Call, scope_id: str) -> None:
        func = call.func
        if isinstance(func, ast.Name):
            self.calls[scope_id].add(func.id)
        elif isinstance(func, ast.Attribute):
            self.calls[scope_id].add(func.attr)

    def collect_yields(self, node: ast.stmt, scope_id: str) -> None:
        scope = self.by_id.get(scope_id)
        if scope is None:
            return
        for child in self._prune_walk(node):
            if isinstance(child, (ast.Yield, ast.YieldFrom)):
                scope["is_generator"] = True
                if isinstance(child, ast.YieldFrom) and isinstance(child.value, ast.Call):
                    f = child.value.func
                    target = f.id if isinstance(f, ast.Name) else getattr(f, "attr", "")
                    if target:
                        self.yields_from.add((scope_id, target))


def _resolve_names(builder: _Builder) -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = {}
    for s in builder.scopes:
        out.setdefault(s["name"], []).append(s["scope_id"])
    return out


def _cycles(graph: Dict[str, Set[str]]) -> Set[Tuple[str, str]]:
    """Pairs on a call cycle of length >= 2 — mutual recursion, direct or through a third scope."""
    def reaches(start: str, target: str) -> bool:
        stack, seen = list(graph.get(start, ())), set()
        while stack:
            cur = stack.pop()
            if cur == target:
                return True
            if cur in seen:
                continue
            seen.add(cur)
            stack.extend(graph.get(cur, ()))
        return False

    pairs: Set[Tuple[str, str]] = set()
    for a, outs in graph.items():
        for b in outs:
            if b != a and b in graph and reaches(b, a):
                pairs.add((a, b))
    return pairs


def record_from_source(source: str, file_id: str) -> Dict[str, Any]:
    """Parse `source` and return the gold structural record for it."""
    tree = ast.parse(source)
    b = _Builder(file_id)
    b.add_scope("module", file_id, "module", "", None)
    module_scope = b.by_id["module"]
    module_scope["end_line"] = source.count("\n") + 1
    b.walk_body(tree.body, "module", "", 0)

    names = _resolve_names(b)

    # Only calls that land on a scope declared in this file become relations.
    resolved: Dict[str, Set[str]] = {}
    for src, targets in b.calls.items():
        hits: Set[str] = set()
        for t in targets:
            candidates = names.get(t) or []
            if len(candidates) == 1:
                hits.add(candidates[0])
            elif len(candidates) > 1:
                # Prefer a sibling in the same namespace, then the shortest path.
                parent = src.rsplit(".", 1)[0]
                sibling = [c for c in candidates if c.rsplit(".", 1)[0] == parent]
                hits.add(sorted(sibling or candidates, key=len)[0])
        resolved[src] = hits

    mutual = _cycles(resolved)

    relations: List[Dict[str, Any]] = []

    def add_rel(rtype: str, frm: str, to: str, notes: str = "") -> None:
        relations.append({
            "relation_id": f"r{len(relations) + 1:04d}",
            "relation_type": rtype,
            "from_scope": frm,
            "to_scope": to,
            "notes": notes,
        })

    for src in sorted(resolved):
        for dst in sorted(resolved[src]):
            if dst == src:
                b.by_id[src]["is_recursive"] = True
                add_rel("self_recursive", src, dst)
            elif (src, dst) in mutual:
                add_rel("mutually_recursive", src, dst)
            else:
                add_rel("calls", src, dst)

    for child, base_name in b.inherits:
        for target in names.get(base_name, []):
            add_rel("inherits", child, target)

    for src, target_name in sorted(b.yields_from):
        for target in names.get(target_name, []):
            add_rel("yields_from", src, target)

    entrypoints = sorted(resolved.get("module", set()))

    return {
        "file_id": file_id,
        "scopes": b.scopes,
        "blocks": b.blocks,
        "relations": relations,
        "entrypoints": entrypoints,
    }


def record_from_path(path) -> Dict[str, Any]:
    from pathlib import Path
    p = Path(path)
    return record_from_source(p.read_text(encoding="utf-8", errors="ignore"), p.stem)
