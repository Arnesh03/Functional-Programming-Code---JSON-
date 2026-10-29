"""Normalise then judge a structural code record.

Same two-stage contract as before: `normalize_document` first says the answer in the lexicon's
words, `validate_report` then decides whether it is right. The order matters — an extraction that
writes "foreach" where the lexicon says "for", or "def" where it says "function", is correct about
the code and wrong only about vocabulary, and failing it for that would measure the wrong thing.

Errors are facts the record gets wrong about itself: an id that is declared twice, a block whose
scope was never declared, a parent chain that loops. Warnings are things that are suspicious but
survivable: a scope claiming a depth its own blocks do not support, a `self_recursive` relation on
a scope whose is_recursive flag says otherwise, an extraction that lists no blocks at all.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .config import LEXICON_JSON_PATH, SCHEMA_JSON_PATH

_schema_cache: Any = None
_lexicon_cache: Any = None


def _load_json(p: Path) -> Any:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _get_schema_obj() -> Any:
    global _schema_cache
    if _schema_cache is None:
        _schema_cache = _load_json(SCHEMA_JSON_PATH)
    return _schema_cache


def _get_lexicon_obj() -> Any:
    global _lexicon_cache
    if _lexicon_cache is None:
        _lexicon_cache = _load_json(LEXICON_JSON_PATH)
    return _lexicon_cache


def _text(value: Any) -> str:
    return str(value or "").strip()


def _dicts(value: Any) -> List[Dict[str, Any]]:
    return [v for v in (value or []) if isinstance(v, dict)]


# ---------------------------------------------------------------------------- normalise
def _canon(value: Any, allowed: List[str], aliases: Dict[str, str]) -> str:
    """Map a written kind onto the lexicon's spelling; unknown values are left alone to be flagged."""
    raw = _text(value)
    if not raw:
        return ""
    low = raw.lower().replace("-", " ").replace("_", " ").strip()
    flat = low.replace(" ", "_")
    for candidate in (raw, raw.lower(), flat, low):
        if candidate in allowed:
            return candidate
    for key in (low, flat, raw.lower()):
        if key in aliases:
            return aliases[key]
    return raw


def normalize_document(obj: Any) -> Any:
    """Fill in the record's shape and spell every kind the way the lexicon spells it."""
    if not isinstance(obj, dict):
        return obj

    lex = _get_lexicon_obj()
    scope_kinds = lex.get("scope_kinds") or []
    block_kinds = lex.get("block_kinds") or []
    rel_types = lex.get("relation_types") or []
    scope_alias = {k.lower(): v for k, v in (lex.get("scope_kind_aliases") or {}).items()}
    block_alias = {k.lower(): v for k, v in (lex.get("block_kind_aliases") or {}).items()}
    rel_alias = {k.lower(): v for k, v in (lex.get("relation_type_aliases") or {}).items()}

    obj.setdefault("file_id", "")
    for key in ("scopes", "blocks", "relations", "entrypoints"):
        if not isinstance(obj.get(key), list):
            obj[key] = []

    obj["scopes"] = _dicts(obj["scopes"])
    obj["blocks"] = _dicts(obj["blocks"])
    obj["relations"] = _dicts(obj["relations"])

    for s in obj["scopes"]:
        s["name"] = _text(s.get("name"))
        s["scope_id"] = _text(s.get("scope_id")) or s["name"]
        s["parent_id"] = _text(s.get("parent_id"))
        s["kind"] = _canon(s.get("kind"), scope_kinds, scope_alias)
        if not s["kind"]:
            # A scope with a parent that is a class is a method; otherwise a plain function.
            s["kind"] = "function"
        s["is_async"] = bool(s.get("is_async")) or s["kind"].startswith("async")
        s["is_recursive"] = bool(s.get("is_recursive"))
        s["is_generator"] = bool(s.get("is_generator"))
        s["decorators"] = [_text(d) for d in (s.get("decorators") or []) if _text(d)]
        s["params"] = [_text(p) for p in (s.get("params") or []) if _text(p)]
        for num in ("start_line", "end_line", "max_block_depth"):
            try:
                s[num] = int(s.get(num) or 0)
            except (TypeError, ValueError):
                s[num] = 0
        s["block_kinds"] = sorted({_canon(k, block_kinds, block_alias)
                                   for k in (s.get("block_kinds") or []) if _text(k)})

    for i, b in enumerate(obj["blocks"], 1):
        b["block_id"] = _text(b.get("block_id")) or f"b{i:04d}"
        b["scope_id"] = _text(b.get("scope_id"))
        b["parent_block_id"] = _text(b.get("parent_block_id"))
        b["kind"] = _canon(b.get("kind"), block_kinds, block_alias)
        for num in ("depth", "line"):
            try:
                b[num] = int(b.get(num) or 0)
            except (TypeError, ValueError):
                b[num] = 0
        b["test"] = _text(b.get("test"))

    for i, r in enumerate(obj["relations"], 1):
        r["relation_id"] = _text(r.get("relation_id")) or f"r{i:04d}"
        r["relation_type"] = _canon(r.get("relation_type"), rel_types, rel_alias)
        r["from_scope"] = _text(r.get("from_scope"))
        r["to_scope"] = _text(r.get("to_scope"))
        r["notes"] = _text(r.get("notes"))

    obj["entrypoints"] = [_text(e) for e in obj["entrypoints"] if _text(e)]
    return obj


# ---------------------------------------------------------------------------- validate
def _shape_validate(obj: Any) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    if not isinstance(obj, dict):
        return False, ["top level is not a JSON object"]

    schema = _get_schema_obj()
    required = (schema.get("required") or ["file_id", "scopes", "relations"])
    for key in required:
        if key not in obj:
            errors.append(f"missing required key: {key}")

    if not _text(obj.get("file_id")):
        errors.append("file_id is empty")

    for key in ("scopes", "blocks", "relations"):
        if key in obj and not isinstance(obj[key], list):
            errors.append(f"{key} must be a list")

    for i, s in enumerate(_dicts(obj.get("scopes"))):
        for field in ("scope_id", "name", "kind"):
            if not _text(s.get(field)):
                errors.append(f"scopes[{i}]: {field} is empty")
    for i, b in enumerate(_dicts(obj.get("blocks"))):
        for field in ("block_id", "scope_id", "kind"):
            if not _text(b.get(field)):
                errors.append(f"blocks[{i}]: {field} is empty")
    for i, r in enumerate(_dicts(obj.get("relations"))):
        for field in ("relation_id", "relation_type", "from_scope", "to_scope"):
            if not _text(r.get(field)):
                errors.append(f"relations[{i}]: {field} is empty")

    if not _dicts(obj.get("scopes")):
        errors.append("no scopes extracted")

    return (not errors), errors


def _semantic_validate(obj: Any) -> Tuple[bool, List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    lex = _get_lexicon_obj()
    scope_kinds = set(lex.get("scope_kinds") or [])
    block_kinds = set(lex.get("block_kinds") or [])
    rel_types = set(lex.get("relation_types") or [])

    scopes = _dicts(obj.get("scopes"))
    blocks = _dicts(obj.get("blocks"))
    relations = _dicts(obj.get("relations"))

    by_id: Dict[str, Dict[str, Any]] = {}
    for s in scopes:
        sid = _text(s.get("scope_id"))
        if sid in by_id:
            errors.append(f"scope_id declared twice: {sid}")
            continue
        by_id[sid] = s
        if _text(s.get("kind")) not in scope_kinds:
            errors.append(f"scope {sid}: kind {s.get('kind')!r} is not in the lexicon")

    modules = [s for s in scopes if _text(s.get("kind")) == "module"]
    if not modules:
        warnings.append("no module scope declared")
    elif len(modules) > 1:
        errors.append(f"{len(modules)} module scopes declared; a file has one")

    for s in scopes:
        sid, pid = _text(s.get("scope_id")), _text(s.get("parent_id"))
        if pid and pid not in by_id:
            errors.append(f"scope {sid}: parent_id {pid!r} was never declared")
        if not pid and _text(s.get("kind")) != "module":
            warnings.append(f"scope {sid}: no parent_id on a non-module scope")
        if s.get("is_async") and not _text(s.get("kind")).startswith("async"):
            warnings.append(f"scope {sid}: is_async set but kind is {s.get('kind')!r}")

    # A parent chain that loops would make the hierarchy view recurse forever.
    for sid in by_id:
        seen, cur = set(), sid
        while cur:
            if cur in seen:
                errors.append(f"scope {sid}: parent_id chain is circular")
                break
            seen.add(cur)
            cur = _text(by_id.get(cur, {}).get("parent_id"))

    seen_blocks: Dict[str, Dict[str, Any]] = {}
    for b in blocks:
        bid = _text(b.get("block_id"))
        if bid in seen_blocks:
            errors.append(f"block_id declared twice: {bid}")
            continue
        seen_blocks[bid] = b
        if _text(b.get("kind")) not in block_kinds:
            errors.append(f"block {bid}: kind {b.get('kind')!r} is not in the lexicon")
        if _text(b.get("scope_id")) not in by_id:
            errors.append(f"block {bid}: scope_id {b.get('scope_id')!r} was never declared")
        if int(b.get("depth") or 0) < 1:
            errors.append(f"block {bid}: depth must start at 1")

    for b in blocks:
        parent = _text(b.get("parent_block_id"))
        if not parent:
            continue
        if parent not in seen_blocks:
            errors.append(f"block {b.get('block_id')}: parent_block_id {parent!r} was never declared")
        elif int(seen_blocks[parent].get("depth") or 0) != int(b.get("depth") or 0) - 1:
            warnings.append(
                f"block {b.get('block_id')}: depth {b.get('depth')} does not sit one below its parent")

    if scopes and not blocks:
        warnings.append("no blocks enumerated; the nesting inside each scope is not described")

    if blocks:
        measured: Dict[str, int] = {}
        for b in blocks:
            sid = _text(b.get("scope_id"))
            measured[sid] = max(measured.get(sid, 0), int(b.get("depth") or 0))
        for sid, s in by_id.items():
            claimed = int(s.get("max_block_depth") or 0)
            if claimed and claimed != measured.get(sid, 0):
                warnings.append(
                    f"scope {sid}: max_block_depth {claimed} but its blocks reach {measured.get(sid, 0)}")

    seen_rel = set()
    for r in relations:
        rid = _text(r.get("relation_id"))
        if rid in seen_rel:
            errors.append(f"relation_id declared twice: {rid}")
        seen_rel.add(rid)
        rtype = _text(r.get("relation_type"))
        if rtype not in rel_types:
            errors.append(f"relation {rid}: relation_type {rtype!r} is not in the lexicon")
        frm, to = _text(r.get("from_scope")), _text(r.get("to_scope"))
        for side, val in (("from_scope", frm), ("to_scope", to)):
            if val not in by_id:
                errors.append(f"relation {rid}: {side} {val!r} was never declared")
        if rtype == "self_recursive":
            if frm != to:
                errors.append(f"relation {rid}: self_recursive must point at its own scope")
            elif frm in by_id and not by_id[frm].get("is_recursive"):
                warnings.append(f"relation {rid}: {frm} is self_recursive but is_recursive is false")

    declared_recursive = {sid for sid, s in by_id.items() if s.get("is_recursive")}
    claimed_recursive = {_text(r.get("from_scope")) for r in relations
                         if _text(r.get("relation_type")) in ("self_recursive", "mutually_recursive")}
    for sid in sorted(declared_recursive - claimed_recursive):
        warnings.append(f"scope {sid}: is_recursive is true but no recursion relation says so")

    for e in (obj.get("entrypoints") or []):
        if _text(e) not in by_id:
            warnings.append(f"entrypoint {e!r} is not a declared scope")

    return (not errors), errors, warnings


def validate_report(obj: Any) -> Tuple[bool, List[str], List[str]]:
    """(ok, errors, warnings) — shape first, then what the record says about itself."""
    shape_ok, shape_errors = _shape_validate(obj)
    if not shape_ok:
        return False, shape_errors, []
    sem_ok, sem_errors, warnings = _semantic_validate(obj)
    return sem_ok, sem_errors, warnings


def validate_all(obj: Any) -> Tuple[bool, List[str]]:
    ok, errors, warnings = validate_report(obj)
    return ok, errors + [f"WARN: {w}" for w in warnings]
