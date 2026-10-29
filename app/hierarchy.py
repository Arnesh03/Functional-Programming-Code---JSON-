"""A scope-centric view of an extracted code record.

The stored record is flat and normalised: scopes, blocks and relations are separate lists that
point at each other by id. That shape is right for validation and for comparing against gold —
every fact lives in exactly one place — but it is hard to read, because answering "what does
tally() actually do?" means scanning three lists and joining them by hand.

This module performs that join once and returns the same facts arranged the way a reader reads
them: each scope, then its standing facts and relations, then its blocks grouped by nesting
depth. Depth is to a program what phase was to an operation — the ordered axis the work is laid
out along — so blocks are bucketed by it, deepest level last.

Nothing is added or dropped; a relation naming two scopes appears under both, which is
duplication the flat form deliberately avoids and a reading view deliberately wants.
"""
from __future__ import annotations

from typing import Any, Dict, List

# A block whose depth never got recorded is not "at depth one" — it is unplaced, and saying so
# is more useful than filing it under a level it may not belong to.
ANY_DEPTH = "any_depth"


def _text(value: Any) -> str:
    return str(value or "").strip()


def _dicts(value: Any) -> List[Dict[str, Any]]:
    return [v for v in (value or []) if isinstance(v, dict)]


def _depth_levels(blocks: List[Dict[str, Any]]) -> List[str]:
    """Depth labels present in the record, shallowest first."""
    levels = sorted({int(b.get("depth") or 0) for b in blocks if int(b.get("depth") or 0) >= 1})
    return [f"depth_{n}" for n in levels]


def _empty_buckets(levels: List[str]) -> Dict[str, list]:
    return {lvl: [] for lvl in [*levels, ANY_DEPTH]}


def _bucket_for(depth: Any, buckets: Dict[str, list]) -> list:
    key = f"depth_{int(depth or 0)}"
    return buckets[key] if key in buckets else buckets[ANY_DEPTH]


def _signature(scope: Dict[str, Any]) -> str:
    params = ", ".join(scope.get("params") or [])
    name = _text(scope.get("name"))
    if _text(scope.get("kind")) in ("class", "module"):
        return name
    prefix = "async def " if scope.get("is_async") else "def "
    return f"{prefix}{name}({params})"


def to_scope_hierarchy(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Regroup a validated code record as scope -> {structure, blocks} -> depth -> records."""
    if not isinstance(doc, dict):
        return {"file_id": "", "depths": [], "scopes": [], "unassigned": {}}

    scopes = _dicts(doc.get("scopes"))
    blocks = _dicts(doc.get("blocks"))
    relations = _dicts(doc.get("relations"))

    levels = _depth_levels(blocks)
    labels = {lvl: lvl.replace("_", " ") for lvl in levels}
    labels[ANY_DEPTH] = "Unplaced (no depth recorded)"

    by_id: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []
    for s in scopes:
        sid = _text(s.get("scope_id"))
        if not sid or sid in by_id:
            continue
        by_id[sid] = {
            "scope_id": sid,
            "name": _text(s.get("name")) or sid,
            "kind": _text(s.get("kind")),
            "signature": _signature(s),
            "parent_id": _text(s.get("parent_id")),
            "is_async": bool(s.get("is_async")),
            "is_recursive": bool(s.get("is_recursive")),
            "is_generator": bool(s.get("is_generator")),
            "decorators": list(s.get("decorators") or []),
            "start_line": int(s.get("start_line") or 0),
            "end_line": int(s.get("end_line") or 0),
            "max_block_depth": int(s.get("max_block_depth") or 0),
            "block_kinds": list(s.get("block_kinds") or []),
            "structure": [],
            "blocks": _empty_buckets(levels),
        }
        order.append(sid)

    # Records naming a scope that was never declared are kept rather than dropped: a dangling
    # reference is a real finding, and hiding it here would make the view disagree with the
    # validator that reports it.
    unassigned: Dict[str, list] = {"blocks": [], "relations": []}

    # A scope's own record carries structural facts before any relation is considered: where it
    # sits, what it is, and whether it recurses or yields.
    for sid in order:
        s = by_id[sid]
        standing = {
            "kind": "standing",
            "parent_id": s["parent_id"],
            "parent_name": by_id.get(s["parent_id"], {}).get("name", ""),
            "scope_kind": s["kind"],
            "is_async": s["is_async"],
            "is_generator": s["is_generator"],
            "is_recursive": s["is_recursive"],
            "decorators": s["decorators"],
            "max_block_depth": s["max_block_depth"],
            "block_kinds": s["block_kinds"],
        }
        if any((standing["parent_id"], standing["is_async"], standing["is_generator"],
                standing["is_recursive"], standing["decorators"], standing["block_kinds"])):
            s["structure"].append(standing)

    for r in relations:
        frm, to = _text(r.get("from_scope")), _text(r.get("to_scope"))
        rel = {
            "relation_id": _text(r.get("relation_id")),
            "relation_type": _text(r.get("relation_type")),
            "from_scope": frm,
            "to_scope": to,
            "notes": _text(r.get("notes")),
        }
        placed = False
        for sid, role, other in ((frm, "from", to), (to, "to", frm)):
            if sid in by_id:
                by_id[sid]["structure"].append(
                    dict(rel, role=role, counterpart=other,
                         counterpart_name=by_id.get(other, {}).get("name", other)))
                placed = True
        if not placed:
            unassigned["relations"].append(rel)

    # Blocks are referenced by parent_block_id from inside one another; resolving the parent here
    # means the reader sees "inside for row in matrix" instead of chasing an id into another list.
    block_by_id = {_text(b.get("block_id")): b for b in blocks if _text(b.get("block_id"))}

    for b in blocks:
        sid = _text(b.get("scope_id"))
        parent = block_by_id.get(_text(b.get("parent_block_id")))
        entry = {
            "block_id": _text(b.get("block_id")),
            "kind": _text(b.get("kind")),
            "depth": int(b.get("depth") or 0),
            "line": int(b.get("line") or 0),
            "test": _text(b.get("test")),
            "parent_block_id": _text(b.get("parent_block_id")),
            "parent_kind": _text(parent.get("kind")) if parent else "",
            "parent_test": _text(parent.get("test")) if parent else "",
        }
        if sid in by_id:
            _bucket_for(entry["depth"], by_id[sid]["blocks"]).append(entry)
        else:
            unassigned["blocks"].append(dict(entry, scope_id=sid))

    for sid in order:
        buckets = by_id[sid]["blocks"]
        # An empty unplaced-bucket is noise; an empty depth bucket is information
        # ("this scope has nothing at depth 4"), so only the former is removed.
        if not buckets[ANY_DEPTH]:
            buckets.pop(ANY_DEPTH)
        by_id[sid]["blocks"] = {k: sorted(v, key=lambda x: (x["line"], x["block_id"]))
                                for k, v in buckets.items()}

    # Parents before children, so the printed view reads as the file reads.
    def depth_of(sid: str, seen: frozenset = frozenset()) -> int:
        parent = by_id[sid]["parent_id"]
        if not parent or parent not in by_id or parent in seen:
            return 0
        return 1 + depth_of(parent, seen | {sid})

    # Positions are captured first: sort() empties the list as it works, so a key that read
    # order.index() would be looking at a list that no longer holds the item.
    original = {sid: i for i, sid in enumerate(order)}
    order.sort(key=lambda sid: (depth_of(sid), original[sid]))
    nesting = {sid: depth_of(sid) for sid in order}
    for sid in order:
        by_id[sid]["scope_nesting"] = nesting[sid]

    return {
        "file_id": _text(doc.get("file_id")),
        "depths": [{"level": lvl, "name": labels[lvl]} for lvl in levels],
        "depth_labels": labels,
        "entrypoints": [e for e in (doc.get("entrypoints") or [])],
        "scopes": [by_id[sid] for sid in order],
        "unassigned": {k: v for k, v in unassigned.items() if v},
    }


def render_text(view: Dict[str, Any], max_blocks_per_scope: int = 24) -> str:
    """The same view as an indented outline, for the terminal and for eyeballing a run."""
    lines: List[str] = [f"{view.get('file_id') or '(no file_id)'}"]
    entry = view.get("entrypoints") or []
    if entry:
        lines.append(f"entrypoints: {', '.join(entry)}")

    for s in view.get("scopes") or []:
        pad = "  " * s.get("scope_nesting", 0)
        flags = []
        if s["is_recursive"]:
            flags.append("RECURSIVE")
        if s["is_generator"]:
            flags.append("generator")
        if s["is_async"]:
            flags.append("async")
        suffix = f"  [{', '.join(flags)}]" if flags else ""
        span = f"  L{s['start_line']}-{s['end_line']}" if s["end_line"] else ""
        lines.append("")
        lines.append(f"{pad}{s['signature']}  <{s['kind']}>{span}"
                     f"  depth {s['max_block_depth']}{suffix}")

        rels = [r for r in s["structure"] if r.get("kind") != "standing"]
        if rels:
            shown = []
            for r in rels[:8]:
                arrow = "->" if r["role"] == "from" else "<-"
                shown.append(f"{r['relation_type']} {arrow} {r['counterpart_name'] or '?'}")
            more = f"  (+{len(rels) - 8} more)" if len(rels) > 8 else ""
            lines.append(f"{pad}  relations: {'; '.join(shown)}{more}")

        buckets = s.get("blocks") or {}
        flat = [b for items in buckets.values() for b in items]
        if not flat:
            continue
        lines.append(f"{pad}  blocks:")
        # The buckets keep the depth axis for the data; the outline walks the parent links in
        # line order instead, because that is the order the nesting appears in the file.
        children: Dict[str, List[Dict[str, Any]]] = {}
        known = {b["block_id"] for b in flat}
        for b in flat:
            key = b["parent_block_id"] if b["parent_block_id"] in known else ""
            children.setdefault(key, []).append(b)
        for kids in children.values():
            kids.sort(key=lambda x: (x["line"], x["block_id"]))

        shown = 0

        def walk(parent_key: str) -> None:
            nonlocal shown
            for b in children.get(parent_key, []):
                if shown >= max_blocks_per_scope:
                    return
                indent = "  " * max(0, b["depth"] - 1)
                test = f" {b['test']}" if b["test"] else ""
                lines.append(f"{pad}    {indent}{b['kind']}{test}  (line {b['line']})")
                shown += 1
                walk(b["block_id"])

        walk("")
        if len(flat) > shown:
            lines.append(f"{pad}    … {len(flat) - shown} more blocks")

    un = view.get("unassigned") or {}
    if un:
        lines.append("")
        lines.append("UNRESOLVED (references a scope that was never declared):")
        for b in un.get("blocks") or []:
            lines.append(f"  - block {b['block_id']} ({b['kind']}) in scope {b['scope_id'] or '(blank)'}")
        for r in un.get("relations") or []:
            lines.append(f"  - relation {r['relation_id']}: "
                         f"{r['from_scope'] or '(blank)'} -> {r['to_scope'] or '(blank)'}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------------------
# A true nested tree
# ---------------------------------------------------------------------------------------
# `to_scope_hierarchy` above is the OPORD-shaped view: a flat list of scopes, each holding its
# own records bucketed by depth. That shape is right for a table and for scoring, but it is not
# actually a tree — the nesting is implied by a `scope_nesting` number rather than carried by the
# structure. Code is a tree, so this builds the real thing: one root, every scope under the scope
# that encloses it, every block under the block that encloses it, and a scope's nested functions
# sitting where they are defined, in line order, among its blocks.
#
# The result is self-similar, so a renderer draws it with one recursive function, and a consumer
# can walk it without consulting any other list.

def _flags_for(scope: Dict[str, Any]) -> List[str]:
    return [name for name, on in (("recursive", scope.get("is_recursive")),
                                  ("generator", scope.get("is_generator")),
                                  ("async", scope.get("is_async"))) if on]


def to_nested_tree(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Return the record as one nested tree: scopes inside scopes, blocks inside blocks."""
    if not isinstance(doc, dict):
        return {"file_id": "", "root": None}

    scopes = _dicts(doc.get("scopes"))
    blocks = _dicts(doc.get("blocks"))
    relations = _dicts(doc.get("relations"))

    by_id = {_text(s.get("scope_id")): s for s in scopes if _text(s.get("scope_id"))}

    rel_by_scope: Dict[str, List[Dict[str, Any]]] = {}
    for r in relations:
        for sid, role, other in ((_text(r.get("from_scope")), "from", _text(r.get("to_scope"))),
                                 (_text(r.get("to_scope")), "to", _text(r.get("from_scope")))):
            if sid in by_id:
                rel_by_scope.setdefault(sid, []).append({
                    "relation_type": _text(r.get("relation_type")),
                    "role": role,
                    "counterpart": other,
                    "counterpart_name": by_id.get(other, {}).get("name", other),
                })

    scope_kids: Dict[str, List[Dict[str, Any]]] = {}
    roots: List[Dict[str, Any]] = []
    for s in scopes:
        parent = _text(s.get("parent_id"))
        (scope_kids.setdefault(parent, []) if parent in by_id else roots).append(s)

    blocks_of: Dict[str, List[Dict[str, Any]]] = {}
    for b in blocks:
        blocks_of.setdefault(_text(b.get("scope_id")), []).append(b)

    def block_node(block: Dict[str, Any], siblings: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        bid = _text(block.get("block_id"))
        kids = sorted(siblings.get(bid, []), key=lambda x: (int(x.get("line") or 0), _text(x.get("block_id"))))
        children = [block_node(k, siblings) for k in kids]
        depth = int(block.get("depth") or 0)
        return {
            "id": bid,
            "node_type": "block",
            "kind": _text(block.get("kind")),
            "label": _text(block.get("kind")) + (f" {_text(block.get('test'))}" if _text(block.get("test")) else ""),
            "test": _text(block.get("test")),
            "line": int(block.get("line") or 0),
            "depth": depth,
            "counts": {
                "scopes": 0,
                "blocks": sum(1 + c["counts"]["blocks"] for c in children),
                "max_depth": max([depth] + [c["counts"]["max_depth"] for c in children]),
            },
            "children": children,
        }

    def scope_node(scope: Dict[str, Any]) -> Dict[str, Any]:
        sid = _text(scope.get("scope_id"))
        own = blocks_of.get(sid, [])
        known = {_text(b.get("block_id")) for b in own}
        kids_by_parent: Dict[str, List[Dict[str, Any]]] = {}
        block_roots: List[Dict[str, Any]] = []
        for b in own:
            parent = _text(b.get("parent_block_id"))
            (kids_by_parent.setdefault(parent, []) if parent in known else block_roots).append(b)

        children = [block_node(b, kids_by_parent)
                    for b in sorted(block_roots, key=lambda x: int(x.get("line") or 0))]
        children += [scope_node(c) for c in scope_kids.get(sid, [])]
        # A nested def is defined at a point in the body, so it is placed among the blocks by line.
        children.sort(key=lambda n: (n.get("line") or n.get("start_line") or 0, n["node_type"] != "scope"))

        n_scopes = sum(1 + c["counts"]["scopes"] for c in children if c["node_type"] == "scope")
        n_blocks = sum((1 + c["counts"]["blocks"]) if c["node_type"] == "block"
                       else c["counts"]["blocks"] for c in children)
        deepest = max([int(scope.get("max_block_depth") or 0)]
                      + [c["counts"]["max_depth"] for c in children] or [0])

        return {
            "id": sid,
            "node_type": "scope",
            "kind": _text(scope.get("kind")),
            "name": _text(scope.get("name")),
            "label": _signature(scope),
            "flags": _flags_for(scope),
            "params": list(scope.get("params") or []),
            "decorators": list(scope.get("decorators") or []),
            "start_line": int(scope.get("start_line") or 0),
            "line": int(scope.get("start_line") or 0),
            "end_line": int(scope.get("end_line") or 0),
            "max_block_depth": int(scope.get("max_block_depth") or 0),
            "block_kinds": list(scope.get("block_kinds") or []),
            "relations": rel_by_scope.get(sid, []),
            "counts": {"scopes": n_scopes, "blocks": n_blocks, "max_depth": deepest},
            "children": children,
        }

    if not roots:
        return {"file_id": _text(doc.get("file_id")), "root": None, "orphans": []}

    # One file has one module scope; anything else parentless is kept beside it rather than lost.
    primary = next((s for s in roots if _text(s.get("kind")) == "module"), roots[0])
    tree = scope_node(primary)
    others = [scope_node(s) for s in roots if s is not primary]
    if others:
        tree["children"].extend(others)
        tree["counts"]["scopes"] += sum(1 + o["counts"]["scopes"] for o in others)

    return {
        "file_id": _text(doc.get("file_id")),
        "entrypoints": list(doc.get("entrypoints") or []),
        "totals": {
            "scopes": tree["counts"]["scopes"] + 1,
            "blocks": tree["counts"]["blocks"],
            "max_depth": tree["counts"]["max_depth"],
            "relations": len(relations),
        },
        "root": tree,
    }


def render_tree_text(tree: Dict[str, Any], max_nodes: int = 400) -> str:
    """The nested tree as box-drawing characters, for the terminal."""
    root = tree.get("root") if "root" in tree else tree
    if not root:
        return "(empty)"
    lines: List[str] = [f"{tree.get('file_id', '')}"]
    shown = 0

    def walk(node: Dict[str, Any], prefix: str, last: bool, top: bool) -> None:
        nonlocal shown
        if shown >= max_nodes:
            return
        shown += 1
        if top:
            head = ""
            nxt = ""
        else:
            head = prefix + ("└── " if last else "├── ")
            nxt = prefix + ("    " if last else "│   ")
        if node["node_type"] == "scope":
            flags = f"  [{', '.join(node['flags'])}]" if node.get("flags") else ""
            lines.append(f"{head}{node['label']}  <{node['kind']}>  "
                         f"L{node['start_line']}-{node['end_line']}  depth {node['max_block_depth']}{flags}")
        else:
            lines.append(f"{head}{node['label']}  :{node['line']}")
        kids = node.get("children") or []
        for i, kid in enumerate(kids):
            walk(kid, nxt, i == len(kids) - 1, False)

    walk(root, "", True, True)
    if shown >= max_nodes:
        lines.append("…")
    return "\n".join(lines)
