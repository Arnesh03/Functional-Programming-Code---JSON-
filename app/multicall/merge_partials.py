"""Merge the per-section answers into one record.

The merger starts from a complete record template, so no top-level key can go missing because a
section failed. A section that returns nothing costs that section's scopes and nothing else.

Scope ids are built here rather than asked for: the model reports names and a parent name within
its own section, which is all it can see, and the merger turns that into the dotted path the
schema wants. Relation typing is decided here too — a call to one's own name is recursion, and a
call that comes back around through the call graph is mutual recursion.
"""
from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple


def _text(value: Any) -> str:
    return str(value or "").strip()


def _dicts(value: Any) -> List[Dict[str, Any]]:
    return [v for v in (value or []) if isinstance(v, dict)]


def _cycles(graph: Dict[str, Set[str]]) -> Set[Tuple[str, str]]:
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

    return {(a, b) for a, outs in graph.items() for b in outs
            if b != a and b in graph and reaches(b, a)}


def merge(file_id: str, header: Dict[str, Any],
          section_results: List[Tuple[str, Dict[str, Any]]]) -> Dict[str, Any]:
    """section_results is [(section_name, parsed reply), ...] in file order."""
    scopes: List[Dict[str, Any]] = [{
        "scope_id": "module",
        "name": file_id,
        "kind": "module",
        "parent_id": "",
        "is_async": False,
        "is_recursive": False,
        "is_generator": False,
        "decorators": [],
        "params": [],
        "start_line": 1,
        "end_line": 0,
        "max_block_depth": int((header or {}).get("max_block_depth") or 0),
        "block_kinds": [_text(k) for k in ((header or {}).get("block_kinds") or []) if _text(k)],
    }]
    taken: Set[str] = {"module"}
    name_to_id: Dict[str, str] = {}
    pending_calls: List[Tuple[str, str]] = []

    for section_name, reply in section_results:
        local: Dict[str, str] = {}          # name within this section -> scope_id
        reported = _dicts((reply or {}).get("scopes"))

        # The section's own definition is the root here; anything claiming a parent we have not
        # seen hangs off it rather than being dropped.
        root_id = ""
        for s in reported:
            name = _text(s.get("name"))
            if not name:
                continue
            parent_name = _text(s.get("parent_name"))
            if not parent_name or parent_name == name:
                parent_id = "module"
            else:
                parent_id = local.get(parent_name) or root_id or "module"

            scope_id = f"{parent_id}.{name}"
            if scope_id in taken:
                n = 2
                while f"{scope_id}#{n}" in taken:
                    n += 1
                scope_id = f"{scope_id}#{n}"
            taken.add(scope_id)
            local.setdefault(name, scope_id)
            name_to_id.setdefault(name, scope_id)
            if not root_id:
                root_id = scope_id

            kind = _text(s.get("kind")) or "function"
            scopes.append({
                "scope_id": scope_id,
                "name": name,
                "kind": kind,
                "parent_id": parent_id,
                "is_async": kind.startswith("async"),
                "is_recursive": bool(s.get("is_recursive")),
                "is_generator": bool(s.get("is_generator")),
                "decorators": [],
                "params": [],
                "start_line": 0,
                "end_line": 0,
                "max_block_depth": int(s.get("max_block_depth") or 0),
                "block_kinds": [_text(k) for k in (s.get("block_kinds") or []) if _text(k)],
            })

        for c in _dicts((reply or {}).get("calls")):
            frm = _text(c.get("from_name")) or section_name
            to = _text(c.get("to_name"))
            if frm and to:
                pending_calls.append((frm, to))

    for c in _dicts((header or {}).get("calls")):
        to = _text(c.get("to_name"))
        if to:
            pending_calls.append((file_id, to))
    name_to_id.setdefault(file_id, "module")

    # Only calls naming a scope the file actually declares become relations; the rest were
    # built-ins or imports the model mentioned anyway.
    graph: Dict[str, Set[str]] = {}
    for frm, to in pending_calls:
        frm_id, to_id = name_to_id.get(frm), name_to_id.get(to)
        if frm_id and to_id:
            graph.setdefault(frm_id, set()).add(to_id)

    mutual = _cycles(graph)
    relations: List[Dict[str, Any]] = []
    by_id = {s["scope_id"]: s for s in scopes}
    for frm_id in sorted(graph):
        for to_id in sorted(graph[frm_id]):
            if frm_id == to_id:
                rtype = "self_recursive"
                if frm_id in by_id:
                    by_id[frm_id]["is_recursive"] = True
            elif (frm_id, to_id) in mutual:
                rtype = "mutually_recursive"
            else:
                rtype = "calls"
            relations.append({
                "relation_id": f"r{len(relations) + 1:04d}",
                "relation_type": rtype,
                "from_scope": frm_id,
                "to_scope": to_id,
                "notes": "",
            })

    return {
        "file_id": file_id,
        "scopes": scopes,
        "blocks": [],
        "relations": relations,
        "entrypoints": sorted(graph.get("module", set())),
    }
