"""Staged extraction: one request per top-level definition instead of one per file.

Same reasoning as the OPORD multicall it replaces. A single request has to fit the prompt and the
entire answer in one context window; on an 850-line file a small model spends its whole budget
reading and answers with almost nothing. Eleven small requests each have room, and the merger
starts from a complete record template so no key can go missing because one section failed.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple

from ..logger import get_logger
from ..utils import extract_json
from .merge_partials import merge
from .sectioner import roster, split_sections
from .segment_prompts import (HEADER_SCHEMA, SECTION_SCHEMA, build_header_prompt,
                              build_section_prompt)

logger = get_logger("multicall")


def run_multicall_for_source(source: str, file_id: str,
                             progress: Optional[Callable[[str, int, int], None]] = None
                             ) -> Dict[str, Any]:
    from ..llm_client import _chat  # imported here so the package can be read without a backend

    sections = split_sections(source)
    names = roster(sections)
    logger.info("Split %s into %d sections (%d definitions)", file_id, len(sections), len(names))

    header: Dict[str, Any] = {}
    results: List[Tuple[str, Dict[str, Any]]] = []

    for i, section in enumerate(sections, 1):
        if progress:
            progress(section.name, i, len(sections))
        is_header = section.kind_hint in ("module_header", "module_trailer")
        messages = (build_header_prompt(section, names, file_id) if is_header
                    else build_section_prompt(section, names, file_id))
        schema = HEADER_SCHEMA if is_header else SECTION_SCHEMA
        try:
            raw = _chat(messages, schema=schema)
            parsed = extract_json(raw)
        except Exception as exc:
            # A section that fails costs that section, not the run.
            logger.warning("section %s (%s) failed: %s", section.section_id, section.name, exc)
            continue
        if not isinstance(parsed, dict):
            logger.warning("section %s returned %s, not an object", section.section_id, type(parsed).__name__)
            continue
        if is_header:
            # Header and trailer are both module level; their calls merge into one record.
            merged_calls = (header.get("calls") or []) + (parsed.get("calls") or [])
            header = {**header, **parsed, "calls": merged_calls}
        else:
            results.append((section.name, parsed))

    record = merge(file_id, header, results)
    logger.info("Merged %d sections into %d scopes and %d relations",
                len(results), len(record["scopes"]), len(record["relations"]))
    return record
