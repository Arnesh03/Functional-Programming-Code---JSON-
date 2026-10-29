"""Working memory: rules and corrected examples mined from evaluation failures.

`scripts/auto_improve.py` writes this file; the prompt builders in `llm_client.py` and
`multicall/segment_prompts.py` read it, so an accepted improvement applies to the next run
without retraining anything.

Ported from the OPORD build's `learned_hints.py`, with the content changed to what a code
extraction actually gets wrong. Scope, kind and parent are already perfect on the H200 run, so
there is nothing to learn there; what moves is **nesting depth** (the model undercounts deep
pyramids), the **generator flag**, and **relations** (invented or missed call edges).

Set LEARNED_HINTS=0 to ignore the file — that is how a baseline is measured.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from .config import ROOT_DIR
from .logger import get_logger

logger = get_logger("learned_hints")

HINTS_PATH = ROOT_DIR / "assets" / "eval" / "learned_hints.json"
MAX_EXAMPLES = 3
MAX_EXAMPLE_LINES = 28

EMPTY: Dict[str, Any] = {
    "version": 0,          # bumped on every accepted update
    "updated": None,
    "scores": {},          # the held-out score that got this version accepted
    "depth_rules": [],     # ["you are undercounting by ~2 levels; …"]
    "flag_rules": [],      # rules about is_generator / is_recursive
    "relation_rules": [],  # rules about which calls count
    "examples": [],        # [{"source": "...", "correct": {...}, "note": "..."}]
}


def enabled() -> bool:
    return os.getenv("LEARNED_HINTS", "1").strip() != "0"


def load() -> dict:
    """Current working memory, or an empty one when missing, unreadable or disabled."""
    if not enabled() or not HINTS_PATH.exists():
        return dict(EMPTY)
    try:
        return {**EMPTY, **json.loads(HINTS_PATH.read_text(encoding="utf-8"))}
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("Ignoring unreadable %s (%s)", HINTS_PATH.name, e)
        return dict(EMPTY)


def save(hints: dict) -> dict:
    """Write a new accepted version and return what was written."""
    out = {
        **EMPTY, **hints,
        "version": int(hints.get("version", 0)) + 1,
        "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    HINTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    HINTS_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Learned hints v%d saved to %s", out["version"], HINTS_PATH.name)
    return out


def write_candidate(hints: dict) -> None:
    """Put a candidate in place WITHOUT bumping the accepted version; rejected ones roll back."""
    HINTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    HINTS_PATH.write_text(json.dumps({**EMPTY, **hints}, indent=2, ensure_ascii=False),
                          encoding="utf-8")


def _rules_block(hints: dict) -> str:
    rules: List[str] = []
    for key in ("depth_rules", "flag_rules", "relation_rules"):
        rules.extend(r for r in (hints.get(key) or []) if str(r).strip())
    if not rules:
        return ""
    return "LEARNED RULES (from your own corrected output):\n- " + "\n- ".join(rules)


def _examples_block(hints: dict, limit: int = MAX_EXAMPLES) -> str:
    parts: List[str] = []
    for ex in (hints.get("examples") or [])[:limit]:
        src = str(ex.get("source") or "").strip()
        if not src:
            continue
        note = str(ex.get("note") or "")
        parts.append(
            f"LEARNED EXAMPLE{(' — ' + note) if note else ''}:\n"
            f"```python\n{src}\n```\n"
            f"CORRECT ANSWER: {json.dumps(ex.get('correct') or {}, ensure_ascii=False)}")
    return "\n\n".join(parts)


def hints_block(max_examples: int = MAX_EXAMPLES) -> str:
    """Everything learned so far, as text to append to a prompt.

    `max_examples` exists because the staged path sends one request per definition: a full set of
    worked examples on every section would cost more in tokens than the correction is worth, so
    section prompts take the rules plus one example, and the single-call prompt takes the lot.
    """
    hints = load()
    blocks = [b for b in (_rules_block(hints), _examples_block(hints, max_examples)) if b]
    return ("\n\n" + "\n\n".join(blocks)) if blocks else ""


def version() -> int:
    return int(load().get("version") or 0)
