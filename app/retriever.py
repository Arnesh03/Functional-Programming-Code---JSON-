"""Turn a query into prompt context: the nearest already-solved sections.

Mirrors the OPORD `retriever.py` API — `get_context(query, k, rebuild)` returning strings ready
to paste into a prompt — including its diversity pass, which exists for the same reason: the
top-k by raw similarity are often near-duplicates of each other, and three copies of the same
example teach less than three different ones.

Set RAG=0 to retrieve nothing; that is how a no-retrieval baseline is measured.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Tuple

from .logger import get_logger
from .rag_store import build_or_load_index, search

logger = get_logger("retriever")

DEFAULT_K = int(os.getenv("RAG_K_FOR_LLM", "2"))


def enabled() -> bool:
    return os.getenv("RAG", "1").strip() != "0"


def _pick_diverse(hits: List[Tuple[float, Dict[str, Any]]], k: int) -> List[Dict[str, Any]]:
    """Take the best, then skip anything too close to what is already picked."""
    picked: List[Dict[str, Any]] = []
    seen_shapes: set = set()
    for _score, chunk in hits:
        answer = chunk.get("answer") or {}
        # Two examples with the same kind and the same depth teach the same lesson.
        shape = (answer.get("kind"), answer.get("max_block_depth"),
                 tuple(sorted(answer.get("block_kinds") or []))[:3])
        if shape in seen_shapes:
            continue
        seen_shapes.add(shape)
        picked.append(chunk)
        if len(picked) >= k:
            break
    # If diversity was too strict to fill k, top up with the best of the rest.
    if len(picked) < k:
        for _score, chunk in hits:
            if chunk not in picked:
                picked.append(chunk)
            if len(picked) >= k:
                break
    return picked


def get_context_docs(query: str, k: int = DEFAULT_K, rebuild: bool = False,
                     exclude_file_id: str = "") -> List[Dict[str, Any]]:
    if not enabled():
        return []
    build_or_load_index(rebuild=rebuild)
    hits = search(query, k=max(k * 4, 8), exclude_file_id=exclude_file_id)
    return _pick_diverse(hits, k)


def get_context(query: str, k: int = DEFAULT_K, rebuild: bool = False,
                exclude_file_id: str = "") -> List[str]:
    """Retrieved sections rendered as worked examples, ready to append to a prompt."""
    docs = get_context_docs(query, k=k, rebuild=rebuild, exclude_file_id=exclude_file_id)
    out: List[str] = []
    for d in docs:
        out.append(
            f"SIMILAR DEFINITION ALREADY SOLVED (from the training split):\n"
            f"```python\n{d['source']}\n```\n"
            f"CORRECT ANSWER: {json.dumps(d['answer'], ensure_ascii=False)}")
    return out


def context_block(query: str, k: int = DEFAULT_K, exclude_file_id: str = "") -> str:
    """The same thing as one string, or empty when retrieval is off or the index is missing."""
    chunks = get_context(query, k=k, exclude_file_id=exclude_file_id)
    return ("\n\n" + "\n\n".join(chunks)) if chunks else ""
