"""The per-section request: one definition at a time, with the file's roster for context."""
from __future__ import annotations

from typing import Any, Dict, List

from ..learned_hints import hints_block
from ..retriever import context_block
from .sectioner import Section

SECTION_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": ["scopes"],
    "properties": {
        "scopes": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "kind", "parent_name", "max_block_depth"],
                "properties": {
                    "name": {"type": "string"},
                    "kind": {"type": "string",
                             "enum": ["class", "function", "async_function", "method",
                                      "async_method"]},
                    "parent_name": {"type": "string"},
                    "is_recursive": {"type": "boolean"},
                    "is_generator": {"type": "boolean"},
                    "max_block_depth": {"type": "integer"},
                    "block_kinds": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "calls": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["from_name", "to_name"],
                "properties": {"from_name": {"type": "string"}, "to_name": {"type": "string"}},
            },
        },
    },
}

SYSTEM = ("You read one Python definition and report its structure as JSON. "
          "You do not summarise or rewrite it. Report only what is there.")


def build_section_prompt(section: Section, roster: List[str], file_id: str) -> List[Dict[str, str]]:
    others = ", ".join(n for n in roster if n != section.name) or "(none)"
    rules = f"""Report the structure of this one definition.

scopes — the definition itself, plus every `def` or `class` nested inside it:
  name              its bare name
  kind              class | function | async_function | method | async_method
                    (a def directly inside a class is a method)
  parent_name       the name of the def or class it sits inside; "" when it is the outermost one here
  is_recursive      true when it calls its own name
  is_generator      true when it contains yield
  max_block_depth   the deepest chain of nested for / while / if / try / with / match inside it,
                    counting the outermost one as 1. An `elif` is one level deeper than its `if`,
                    because Python nests it that way. Count carefully by reading the indentation.
  block_kinds       which of these appear in it:
                    for, async_for, while, if, try, with, async_with, match, case, except, finally, else

calls — names this code calls that belong to this file. The file defines: {others}.
  Include a call to its own name when it recurses. Ignore built-ins such as len, range, print,
  int, isinstance, sorted, enumerate, and ignore anything imported.

Report nothing that is not in the code below.{context_block(section.text, exclude_file_id=file_id)}{hints_block(max_examples=1)}"""
    user = (f"{rules}\n\nDEFINITION FROM {file_id} "
            f"(lines {section.start_line}-{section.end_line}):\n```python\n{section.text}\n```")
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


HEADER_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": ["calls"],
    "properties": {
        "max_block_depth": {"type": "integer"},
        "block_kinds": {"type": "array", "items": {"type": "string"}},
        "calls": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["to_name"],
                "properties": {"to_name": {"type": "string"}},
            },
        },
    },
}


def build_header_prompt(section: Section, roster: List[str], file_id: str) -> List[Dict[str, str]]:
    names = ", ".join(roster) or "(none)"
    rules = f"""This is the module level of a Python file: everything outside any def or class,
including the `if __name__ == "__main__"` guard at the end if there is one.

Report:
  max_block_depth  deepest chain of nested for / while / if / try / with at module level, 1 if there
                   is a single unnested one, 0 if there are none
  block_kinds      which of for, while, if, try, with, match appear at module level
  calls            the file's own functions that module-level code calls. The file defines: {names}.
                   Ignore built-ins and imports."""
    user = (f"{rules}\n\nMODULE LEVEL OF {file_id}:\n```python\n{section.text}\n```")
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]
