"""Talk to the configured LLM backend and ask it for the structure of a Python file.

Backends are unchanged from the OPORD build — Ollama locally, Groq or OpenRouter through their
OpenAI-compatible endpoints, chosen by LLM_BACKEND. What changed is the request: instead of an
order and a doctrine corpus, the model is given one source file, the schema it must answer in,
and a worked example.

The worked example is not written by hand. It is a short snippet run through `app.gold`, the same
extractor that produces the ground truth, so the example in the prompt can never drift away from
the format the answer is scored against.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from .config import MAX_SOURCE_CHARS
from .gold import record_from_source
from .learned_hints import hints_block
from .retriever import context_block
from .logger import get_logger

logger = get_logger("llm_client")

# Used when <BACKEND>_MODEL (OLLAMA_MODEL / GROQ_MODEL / OPENROUTER_MODEL) is not set
DEFAULT_MODELS = {
    "ollama": "qwen3:4b",
    "groq": "llama-3.1-8b-instant",
    "openrouter": "nvidia/nemotron-3-super-120b-a12b:free",
}

# Groq and OpenRouter both provide OpenAI-compatible endpoints: backend -> (base_url, api key env var)
OPENAI_COMPAT_BACKENDS = {
    "groq": ("https://api.groq.com/openai/v1", "GROQ_API_KEY"),
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
}

EXAMPLE_SNIPPET = '''def walk(node, budget=3):
    total = 0
    for child in node:
        if isinstance(child, list):
            total += walk(child, budget - 1)
        else:
            try:
                total += int(child)
            except ValueError:
                continue
    return total


class Counter:
    def tally(self, rows):
        return [walk(r) for r in rows]
'''

# The reply is constrained to this shape where the backend supports it (Ollama does, per request).
RESPONSE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": ["file_id", "scopes", "relations"],
    "properties": {
        "file_id": {"type": "string"},
        "scopes": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["scope_id", "name", "kind", "parent_id"],
                "properties": {
                    "scope_id": {"type": "string"},
                    "name": {"type": "string"},
                    "kind": {"type": "string",
                             "enum": ["module", "class", "function", "async_function",
                                      "method", "async_method", "lambda"]},
                    "parent_id": {"type": "string"},
                    "is_async": {"type": "boolean"},
                    "is_recursive": {"type": "boolean"},
                    "is_generator": {"type": "boolean"},
                    "max_block_depth": {"type": "integer"},
                    "block_kinds": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
        "relations": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["relation_id", "relation_type", "from_scope", "to_scope"],
                "properties": {
                    "relation_id": {"type": "string"},
                    "relation_type": {"type": "string",
                                      "enum": ["calls", "self_recursive", "mutually_recursive",
                                               "inherits", "yields_from"]},
                    "from_scope": {"type": "string"},
                    "to_scope": {"type": "string"},
                },
            },
        },
        "entrypoints": {"type": "array", "items": {"type": "string"}},
    },
}


def _post_json(url: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None,
               timeout: int = 900, retries: int = 2) -> Dict[str, Any]:
    """POST JSON. Rate limits and provider outages (429, 5xx) are retried briefly before giving up."""
    data = json.dumps(payload).encode("utf-8")
    delay = 5
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        if headers:
            for k, v in headers.items():
                req.add_header(k, v)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8", errors="ignore"))
        except urllib.error.HTTPError as e:
            # Surface the provider's explanation (bad key, unknown model, rate limit), not a bare status
            body = e.read().decode("utf-8", errors="ignore")[:500]
            if attempt < retries and (e.code == 429 or e.code >= 500):
                logger.warning("HTTP %s from provider; retrying in %ds", e.code, delay)
                time.sleep(delay)
                delay *= 2
                continue
            raise RuntimeError(f"HTTP {e.code} from {url}: {body}") from e
    raise RuntimeError(f"no response from {url}")


def _backend() -> str:
    return os.getenv("LLM_BACKEND", "ollama").strip().lower()


def active_model_name() -> str:
    """Model the active backend uses, recorded with each run."""
    backend = _backend()
    if backend in DEFAULT_MODELS:
        return os.getenv(f"{backend.upper()}_MODEL", "").strip() or DEFAULT_MODELS[backend]
    return backend


def _ollama_mode(model: str, messages: List[Dict[str, str]],
                 schema: Optional[Dict[str, Any]] = None) -> str:
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        # Ollama constrains the reply to a JSON schema when given one; "json" is the loose fallback
        "format": schema or "json",
        # Reasoning models (qwen3) otherwise spend minutes on a <think> block before the JSON.
        # OLLAMA_THINK=1 re-enables it.
        "think": os.getenv("OLLAMA_THINK", "0").strip() == "1",
        "options": {
            "temperature": float(os.getenv("LLM_TEMPERATURE", "0.2")),
            # A generated sample is ~850 lines ≈ 9k tokens, and the prompt adds the schema and the
            # worked example on top, so the OPORD-era 8192 would silently cut the file in half.
            "num_ctx": int(os.getenv("OLLAMA_NUM_CTX", "16384")),
        },
    }
    t0 = time.time()
    try:
        out = _post_json(host + "/api/chat", payload)
    except RuntimeError as e:
        if "think" not in str(e).lower():
            raise
        payload.pop("think")  # this model or Ollama build doesn't take the flag
        out = _post_json(host + "/api/chat", payload)
    resp_text = (out.get("message", {}) or {}).get("content", "") or ""
    logger.debug("Ollama call took %.2fs, %d chars back", time.time() - t0, len(resp_text))
    return resp_text


def _openai_compat_mode(base_url: str, api_key: str, model: str,
                        messages: List[Dict[str, str]]) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": float(os.getenv("LLM_TEMPERATURE", "0.2")),
        "response_format": {"type": "json_object"},
    }
    t0 = time.time()
    out = _post_json(url, payload, headers={"Authorization": f"Bearer {api_key}"})
    if not out.get("choices"):
        # OpenRouter reports some failures (rate limits, upstream errors) inside a 200 response
        err = out.get("error") if isinstance(out.get("error"), dict) else {"message": str(out)[:300]}
        raise RuntimeError(f"HTTP {err.get('code', 200)} from {url}: {err.get('message')}")
    resp_text = out["choices"][0]["message"].get("content") or ""
    logger.debug("OpenAI-compatible call took %.2fs, %d chars back", time.time() - t0, len(resp_text))
    return resp_text


def _chat(messages: List[Dict[str, str]], schema: Optional[Dict[str, Any]] = None) -> str:
    backend = _backend()
    if backend == "ollama":
        return _ollama_mode(active_model_name(), messages, schema)
    if backend in OPENAI_COMPAT_BACKENDS:
        base_url, key_var = OPENAI_COMPAT_BACKENDS[backend]
        key = os.getenv(key_var, "").strip()
        if not key:
            raise RuntimeError(f"{key_var} missing (set it in .env)")
        return _openai_compat_mode(base_url, key, active_model_name(), messages)
    raise ValueError(f"Unknown LLM_BACKEND={backend!r} (use ollama, groq or openrouter)")


def _example_block() -> str:
    """A worked example, extracted by the same code that produces the gold records."""
    record = record_from_source(EXAMPLE_SNIPPET, "example")
    slim = {
        "file_id": "example",
        "scopes": [{k: v for k, v in s.items()
                    if k in ("scope_id", "name", "kind", "parent_id", "is_recursive",
                             "is_generator", "max_block_depth", "block_kinds")}
                   for s in record["scopes"]],
        "relations": [{k: v for k, v in r.items()
                       if k in ("relation_id", "relation_type", "from_scope", "to_scope")}
                      for r in record["relations"]],
        "entrypoints": record["entrypoints"],
    }
    return (f"EXAMPLE INPUT:\n```python\n{EXAMPLE_SNIPPET}```\n"
            f"EXAMPLE OUTPUT:\n{json.dumps(slim, indent=1)}")


def build_prompt(source: str, file_id: str) -> List[Dict[str, str]]:
    body = source if len(source) <= MAX_SOURCE_CHARS else (
        source[:MAX_SOURCE_CHARS] + "\n# ... file truncated for the prompt ...\n")

    system = (
        "You read one Python file and report its structure as JSON. You do not summarise, "
        "explain or rewrite the code. Report only what the file contains."
    )
    rules = f"""Return a single JSON object describing this file.

scopes — one entry per namespace, in the order they appear:
  scope_id   dotted path from the module, e.g. "module", "module.walk", "module.Counter.tally"
  name       the bare name; for the module itself use the file_id
  kind       module | class | function | async_function | method | async_method
  parent_id  scope_id of the enclosing scope; "" for the module
  is_recursive     true when the function calls its own name
  is_generator     true when it yields
  max_block_depth  deepest chain of nested for/while/if/try/with/match inside it, counting from 1
                   (an elif counts as one level deeper, because Python nests it)
  block_kinds      the distinct constructs used in it, from:
                   for, async_for, while, if, try, with, async_with, match, case, except, finally, else

relations — one entry per edge between two scopes declared in THIS file. Ignore calls to
built-ins and imports.
  relation_type  calls | self_recursive | mutually_recursive | inherits | yields_from
  from_scope, to_scope   scope_ids that appear in your scopes list
  self_recursive has from_scope == to_scope.
  mutually_recursive is for two functions that call each other.

entrypoints — scope_ids called from module level or from the `if __name__ == "__main__"` guard.

Every parent_id, from_scope and to_scope must be a scope_id you listed. file_id is "{file_id}".

{_example_block()}{context_block(body, exclude_file_id=file_id)}{hints_block()}"""

    user = f"{rules}\n\nFILE TO EXTRACT (file_id = {file_id}):\n```python\n{body}```"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def generate_code_json(source: str, file_id: str) -> str:
    """Ask the active backend for the structural record of one file; returns the raw reply."""
    messages = build_prompt(source, file_id)
    logger.info("Prompt built — %d chars for %s", sum(len(m["content"]) for m in messages), file_id)
    return _chat(messages, schema=RESPONSE_SCHEMA)
