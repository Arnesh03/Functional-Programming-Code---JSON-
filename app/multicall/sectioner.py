"""Cut a source file into sections, one per top-level definition.

The OPORD build split an order on its paragraph headings before extracting, because one request
could not hold the whole document and its answer at once. A long generated sample has the same
problem for the same reason, so it is split the same way — on the markers the text itself
provides. This is deliberately a text-level split (a line starting with `def`, `async def`,
`class` or a decorator at column zero), not an AST walk: the splitter is allowed to see where the
definitions start, and the model still has to say what is inside them.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

TOP_LEVEL = re.compile(r"^(?:@|def |async def |class )")
# Module-level code that resumes after a definition — the `if __name__` guard, usually.
# Without this the guard is swallowed by the last function's section, the header prompt never
# sees it, and entrypoints come back empty.
RESUMES_MODULE = re.compile(r"^(?!def |async def |class |@|#)[A-Za-z_]")
NAME_OF = re.compile(r"^(?:async\s+def|def|class)\s+([A-Za-z_]\w*)")


@dataclass
class Section:
    section_id: str
    name: str
    kind_hint: str          # module_header | function | async_function | class
    start_line: int
    end_line: int
    text: str

    @property
    def n_lines(self) -> int:
        return self.text.count("\n") + 1


def _name_and_kind(block: List[str]) -> tuple:
    for line in block:
        m = NAME_OF.match(line)
        if m:
            if line.startswith("class "):
                return m.group(1), "class"
            return m.group(1), "async_function" if line.startswith("async ") else "function"
    return "", "function"


def split_sections(source: str) -> List[Section]:
    lines = source.split("\n")
    starts: List[int] = [i for i, ln in enumerate(lines) if TOP_LEVEL.match(ln)]

    # A decorator run belongs to the definition it decorates, so only the first line of a
    # consecutive decorator + def group opens a section.
    cleaned: List[int] = []
    for i in starts:
        if cleaned and all(lines[j].startswith("@") or lines[j].strip() == ""
                           for j in range(cleaned[-1], i)):
            continue
        cleaned.append(i)

    sections: List[Section] = []
    header_end = cleaned[0] if cleaned else len(lines)
    header = "\n".join(lines[:header_end]).strip("\n")
    if header.strip():
        sections.append(Section("s000", "module_header", "module_header", 1, header_end, header))

    trailers: List[Section] = []
    for n, start in enumerate(cleaned, 1):
        end = cleaned[n] if n < len(cleaned) else len(lines)

        # A column-zero statement inside this span means the definition ended and module-level
        # code resumed; that tail belongs to the module, not to the definition.
        cut = end
        for i in range(start + 1, end):
            if RESUMES_MODULE.match(lines[i]):
                cut = i
                break

        block = lines[start:cut]
        name, kind = _name_and_kind(block)
        sections.append(Section(
            section_id=f"s{n:03d}",
            name=name or f"section_{n}",
            kind_hint=kind,
            start_line=start + 1,
            end_line=cut,
            text="\n".join(block).strip("\n"),
        ))

        if cut < end:
            tail = "\n".join(lines[cut:end]).strip("\n")
            if tail.strip():
                trailers.append(Section(
                    section_id=f"s{n:03d}t",
                    name="module_trailer",
                    kind_hint="module_trailer",
                    start_line=cut + 1,
                    end_line=end,
                    text=tail,
                ))

    return sections + trailers


def roster(sections: List[Section]) -> List[str]:
    """Top-level names in the file, handed to every section so cross-section calls resolve."""
    return [s.name for s in sections
            if s.kind_hint not in ("module_header", "module_trailer")]
