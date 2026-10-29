from pathlib import Path
from typing import Any
import json

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def pretty_print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))

def extract_json(raw: str) -> Any:
    """
    Parse the JSON object/array in an LLM reply.
    Models sometimes wrap it in markdown fences or add text before/after it,
    so decode from the first { or [ and ignore anything after that value.
    Raises json.JSONDecodeError if no valid JSON starts there.
    """
    s = (raw or "").strip()
    starts = [i for i in (s.find("{"), s.find("[")) if i != -1]
    if not starts:
        return json.loads(s)
    return json.JSONDecoder().raw_decode(s, min(starts))[0]
