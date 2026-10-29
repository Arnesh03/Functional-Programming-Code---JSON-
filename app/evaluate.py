"""Score an extracted record against the AST gold record.

Matching is done on bare names, not on scope_ids. Two records can describe the same file
correctly and still disagree about whether the path is "module.Counter.tally" or "Counter.tally",
and penalising that would measure prompt compliance rather than whether the model read the code.
Parent links are compared the same way: by the parent's name, not its id.

Everything here is set arithmetic over names, so the numbers say what they appear to say.
"""
from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple


def _dicts(value: Any) -> List[Dict[str, Any]]:
    return [v for v in (value or []) if isinstance(v, dict)]


def _text(value: Any) -> str:
    return str(value or "").strip()


def _prf(pred: Set, gold: Set) -> Dict[str, float]:
    tp = len(pred & gold)
    precision = tp / len(pred) if pred else (1.0 if not gold else 0.0)
    recall = tp / len(gold) if gold else (1.0 if not pred else 0.0)
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return {"precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4),
            "tp": tp, "n_pred": len(pred), "n_gold": len(gold)}


def _scope_index(record: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Bare name -> scope. A name declared twice keeps the first; both records resolve it the same."""
    by_id = {_text(s.get("scope_id")): s for s in _dicts(record.get("scopes"))}
    out: Dict[str, Dict[str, Any]] = {}
    for s in _dicts(record.get("scopes")):
        name = _text(s.get("name"))
        if name and name not in out:
            parent = by_id.get(_text(s.get("parent_id")))
            out[name] = dict(s, _parent_name=_text(parent.get("name")) if parent else "")
    return out


def _relation_triples(record: Dict[str, Any]) -> Set[Tuple[str, str, str]]:
    by_id = {_text(s.get("scope_id")): _text(s.get("name"))
             for s in _dicts(record.get("scopes"))}
    out = set()
    for r in _dicts(record.get("relations")):
        frm = by_id.get(_text(r.get("from_scope")), _text(r.get("from_scope")))
        to = by_id.get(_text(r.get("to_scope")), _text(r.get("to_scope")))
        out.add((_text(r.get("relation_type")), frm, to))
    return out


def _entry_names(record: Dict[str, Any]) -> Set[str]:
    by_id = {_text(s.get("scope_id")): _text(s.get("name"))
             for s in _dicts(record.get("scopes"))}
    return {by_id.get(_text(e), _text(e)) for e in (record.get("entrypoints") or []) if _text(e)}


def score_record(pred: Dict[str, Any], gold: Dict[str, Any]) -> Dict[str, Any]:
    """Compare a predicted record with the gold one; all figures are per file."""
    p_scopes, g_scopes = _scope_index(pred), _scope_index(gold)
    shared = sorted(set(p_scopes) & set(g_scopes))

    scopes = _prf(set(p_scopes), set(g_scopes))

    def agreement(field: str) -> float:
        if not shared:
            return 0.0
        hits = sum(1 for n in shared if _text(p_scopes[n].get(field)) == _text(g_scopes[n].get(field)))
        return round(hits / len(shared), 4)

    kind_acc = agreement("kind")
    parent_acc = agreement("_parent_name")

    def flag_prf(field: str) -> Dict[str, float]:
        return _prf({n for n in p_scopes if p_scopes[n].get(field)},
                    {n for n in g_scopes if g_scopes[n].get(field)})

    depth_abs, depth_exact, depth_n = 0, 0, 0
    for n in shared:
        claimed = int(p_scopes[n].get("max_block_depth") or 0)
        truth = int(g_scopes[n].get("max_block_depth") or 0)
        if claimed or truth:
            depth_n += 1
            depth_abs += abs(claimed - truth)
            depth_exact += int(claimed == truth)

    relations = _prf(_relation_triples(pred), _relation_triples(gold))
    entrypoints = _prf(_entry_names(pred), _entry_names(gold))

    overall = round(
        (scopes["f1"] + relations["f1"] + kind_acc + parent_acc) / 4, 4)

    return {
        "scopes": scopes,
        "kind_accuracy": kind_acc,
        "parent_accuracy": parent_acc,
        "recursive_flags": flag_prf("is_recursive"),
        "generator_flags": flag_prf("is_generator"),
        "max_block_depth": {
            "scored": depth_n,
            "mae": round(depth_abs / depth_n, 3) if depth_n else 0.0,
            "exact_rate": round(depth_exact / depth_n, 4) if depth_n else 0.0,
        },
        "relations": relations,
        "entrypoints": entrypoints,
        "overall": overall,
    }


def aggregate(scores: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Mean of per-file scores. Files are weighted equally, whatever their size."""
    if not scores:
        return {}

    def mean(path: Tuple[str, ...]) -> float:
        vals = []
        for s in scores:
            cur: Any = s
            for key in path:
                cur = (cur or {}).get(key) if isinstance(cur, dict) else None
            if isinstance(cur, (int, float)):
                vals.append(float(cur))
        return round(sum(vals) / len(vals), 4) if vals else 0.0

    out = {
        "n_files": len(scores),
        "scope_f1": mean(("scopes", "f1")),
        "scope_precision": mean(("scopes", "precision")),
        "scope_recall": mean(("scopes", "recall")),
        "kind_accuracy": mean(("kind_accuracy",)),
        "parent_accuracy": mean(("parent_accuracy",)),
        "recursive_f1": mean(("recursive_flags", "f1")),
        "generator_f1": mean(("generator_flags", "f1")),
        "depth_mae": mean(("max_block_depth", "mae")),
        "depth_exact_rate": mean(("max_block_depth", "exact_rate")),
        "relation_f1": mean(("relations", "f1")),
        "entrypoint_f1": mean(("entrypoints", "f1")),
        "overall": mean(("overall",)),
    }
    # `overall` is deliberately frozen so old runs stay comparable, and it does not include
    # depth — which is exactly what the learning loop is trying to fix. So the loop optimises
    # this instead: every metric a prompt change can actually move, weighted equally.
    out["learning_score"] = round(sum(
        out[k] for k in ("scope_f1", "relation_f1", "kind_accuracy", "parent_accuracy",
                         "depth_exact_rate", "generator_f1", "entrypoint_f1")) / 7, 4)
    return out
