"""The retrieval corpus: train-split code sections paired with their AST-gold answers.

The OPORD build retrieved doctrine, because the meaning of an order lives in documents outside
it. Code has no doctrine — but it does have something an order never had: 800 training files
whose correct answer is already known exactly, for free, from the parser. So the corpus here is
*worked examples*. Given the section being extracted, retrieve the most similar sections that
have already been solved, and show the model those solutions.

**Only the train split is indexed.** A val or test file appearing in the corpus would leak its own
answer into its own extraction, and every number after that would be meaningless. `build_index`
filters on the manifest's split, and `retriever.get_context` additionally drops any chunk from the
file being extracted.

Scoring is lexical TF-IDF over code identifiers with an inverted index — stdlib only, because the
GPU box has no working pip and the rest of this pipeline has no dependencies either. The place to
swap in neural embeddings is `_vector()`; nothing else needs to change.
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .config import DATASET_DIR, MANIFEST_JSONL, ROOT_DIR
from .logger import get_logger

logger = get_logger("rag_store")

INDEX_PATH = ROOT_DIR / "assets" / "index" / "section_index.json"
TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
TOP_TOKENS_PER_CHUNK = 48      # keeps the index small without hurting recall much
MAX_CHUNK_LINES = 22           # what is shown back to the model

_index_cache: Dict[str, Any] | None = None


def tokenize(source: str) -> List[str]:
    """Identifiers and keywords, lowercased. Structure survives: `for`, `while`, `yield` are tokens."""
    return [t.lower() for t in TOKEN_RE.findall(source or "")]


def _vector(source: str, df: Dict[str, int], n_docs: int) -> Dict[str, float]:
    """TF-IDF, L2-normalised. Swap this for an embedding call to go neural."""
    tf = Counter(tokenize(source))
    if not tf:
        return {}
    vec: Dict[str, float] = {}
    for token, count in tf.items():
        idf = math.log((n_docs + 1) / (df.get(token, 0) + 1)) + 1.0
        vec[token] = (1.0 + math.log(count)) * idf
    norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
    return {t: v / norm for t, v in vec.items()}


def _trim(source: str) -> str:
    lines = source.split("\n")
    if len(lines) <= MAX_CHUNK_LINES:
        return source
    return "\n".join(lines[:MAX_CHUNK_LINES - 2] + ["    # … body continues …"])


def build_index(limit: int = 250, rebuild: bool = False) -> Dict[str, Any]:
    """Index the train split's sections. `limit` caps how many files are read."""
    from .gold import record_from_source
    from .multicall.sectioner import split_sections

    if INDEX_PATH.exists() and not rebuild:
        return load_index()

    rows = [json.loads(l) for l in MANIFEST_JSONL.read_text().splitlines() if l.strip()]
    train = [r for r in rows if r.get("split") == "train"][:limit]
    logger.info("Indexing %d train files", len(train))

    raw: List[Dict[str, Any]] = []
    for row in train:
        hits = sorted(DATASET_DIR.glob(f"{row['id']}*.py"))
        if not hits:
            continue
        source = hits[0].read_text(encoding="utf-8", errors="ignore")
        try:
            gold = record_from_source(source, row["id"])
        except SyntaxError:
            continue
        by_name = {s["name"]: s for s in gold["scopes"]}
        for section in split_sections(source):
            if section.kind_hint.startswith("module"):
                continue
            answer = by_name.get(section.name)
            if not answer:
                continue
            raw.append({
                "file_id": row["id"],
                "name": section.name,
                "source": _trim(section.text),
                "full": section.text,
                "answer": {
                    "name": answer["name"],
                    "kind": answer["kind"],
                    "max_block_depth": answer["max_block_depth"],
                    "block_kinds": answer["block_kinds"],
                    "is_recursive": answer["is_recursive"],
                    "is_generator": answer["is_generator"],
                },
            })

    df: Counter = Counter()
    for chunk in raw:
        df.update(set(tokenize(chunk["full"])))
    n_docs = len(raw)

    chunks, postings = [], {}
    for i, chunk in enumerate(raw):
        vec = _vector(chunk["full"], df, n_docs)
        top = dict(sorted(vec.items(), key=lambda kv: -kv[1])[:TOP_TOKENS_PER_CHUNK])
        chunks.append({k: v for k, v in chunk.items() if k != "full"})
        for token, weight in top.items():
            postings.setdefault(token, []).append([i, round(weight, 5)])

    index = {"version": 1, "n_docs": n_docs, "n_files": len(train),
             "df": {t: c for t, c in df.items() if c > 1},
             "postings": postings, "chunks": chunks}

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(json.dumps(index), encoding="utf-8")
    size_mb = INDEX_PATH.stat().st_size / 1_048_576
    logger.info("Index built: %d chunks from %d files, %.1f MB", n_docs, len(train), size_mb)
    return index


def load_index() -> Dict[str, Any]:
    global _index_cache
    if _index_cache is not None:
        return _index_cache
    if not INDEX_PATH.exists():
        return {"version": 0, "n_docs": 0, "df": {}, "postings": {}, "chunks": []}
    try:
        _index_cache = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("Ignoring unreadable index (%s)", e)
        _index_cache = {"version": 0, "n_docs": 0, "df": {}, "postings": {}, "chunks": []}
    return _index_cache


def build_or_load_index(rebuild: bool = False, limit: int = 250) -> Dict[str, Any]:
    global _index_cache
    if rebuild:
        _index_cache = None
        return build_index(limit=limit, rebuild=True)
    return load_index()


def search(query: str, k: int = 8, exclude_file_id: str = "") -> List[Tuple[float, Dict[str, Any]]]:
    """Top-k chunks by cosine similarity, via the inverted index."""
    index = load_index()
    chunks = index.get("chunks") or []
    if not chunks:
        return []

    qvec = _vector(query, index.get("df") or {}, index.get("n_docs") or 1)
    scores: Dict[int, float] = {}
    postings = index.get("postings") or {}
    for token, qw in qvec.items():
        for idx, w in postings.get(token, ()):
            scores[idx] = scores.get(idx, 0.0) + qw * w

    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    out: List[Tuple[float, Dict[str, Any]]] = []
    for idx, score in ranked:
        chunk = chunks[idx]
        # never retrieve from the file being extracted
        if exclude_file_id and chunk.get("file_id", "").startswith(exclude_file_id[:20]):
            continue
        out.append((score, chunk))
        if len(out) >= k:
            break
    return out
