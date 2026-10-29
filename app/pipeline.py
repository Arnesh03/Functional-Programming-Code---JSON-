"""One file in, one validated structural record out.

Same stages as the OPORD pipeline, in the same order, for the same reasons:

    load  ->  LLM  ->  parse JSON  ->  normalise  ->  validate  ->  score  ->  store  ->  render

Two stages differ. The retrieval step is gone: the OPORD build pulled doctrine out of a vector
store because the meaning of an order lives outside the order, whereas a Python file is complete
on its own — the worked example in the prompt is all the outside context that helps. And a
scoring stage is new, because `app.gold` can read the truth out of the AST, so every run is
scored against ground truth as it happens rather than in a separate evaluation pass.

Validation never blocks a save (the OPORD build called this save-and-mark): a record that fails
is stored with its errors, because a failed extraction is evidence and deleting it would hide the
failure mode.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .config import DATASET_DIR, DB_PATH, PREDS_DIR
from .evaluate import score_record
from .gold import record_from_source
from .hierarchy import render_text, render_tree_text, to_nested_tree, to_scope_hierarchy
from .llm_client import active_model_name, generate_code_json
from .logger import get_logger
from .new_validators import normalize_document, validate_report
from .utils import extract_json

logger = get_logger("pipeline")


def _load_source(filename_or_path: str) -> Tuple[str, str]:
    """Returns (file_id, source). Accepts a path, a bare filename, or a dataset sample id."""
    p = Path(filename_or_path)
    if not p.exists():
        for candidate in (DATASET_DIR / filename_or_path,
                          DATASET_DIR / f"{filename_or_path}.py"):
            if candidate.exists():
                p = candidate
                break
        else:
            matches = sorted(DATASET_DIR.glob(f"{Path(filename_or_path).stem}*.py"))
            if matches:
                p = matches[0]

    if not p.exists():
        logger.error("source file not found: %s", filename_or_path)
        raise FileNotFoundError(f"source file not found: {filename_or_path}")

    source = p.read_text(encoding="utf-8", errors="ignore")
    logger.info("Loaded %s — %d chars, %d lines", p, len(source), source.count("\n") + 1)
    return p.stem, source


def _ensure_db_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS code_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id TEXT,
            model_name TEXT,
            json_output TEXT,
            is_valid INTEGER DEFAULT 0,
            validation_errors TEXT,
            validation_warnings TEXT,
            score TEXT,
            overall REAL,
            elapsed_s REAL,
            created_at TEXT
        )
        """
    )
    cur.execute("PRAGMA table_info(code_runs)")
    cols = {row[1] for row in cur.fetchall()}
    wanted = {
        "is_valid": "INTEGER DEFAULT 0",
        "validation_errors": "TEXT",
        "validation_warnings": "TEXT",
        "score": "TEXT",
        "overall": "REAL",
        "elapsed_s": "REAL",
        "created_at": "TEXT",
    }
    for c, typ in wanted.items():
        if c not in cols:
            cur.execute(f"ALTER TABLE code_runs ADD COLUMN {c} {typ}")
    conn.commit()


def _save_to_db(file_id: str, model_name: str, obj: dict, is_valid: bool,
                errors: list, warnings: list, score: dict, elapsed: float) -> int:
    conn = sqlite3.connect(str(DB_PATH))
    try:
        _ensure_db_schema(conn)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO code_runs (
                file_id, model_name, json_output, is_valid, validation_errors,
                validation_warnings, score, overall, elapsed_s, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (file_id, model_name, json.dumps(obj, ensure_ascii=False), 1 if is_valid else 0,
             json.dumps(errors, ensure_ascii=False), json.dumps(warnings, ensure_ascii=False),
             json.dumps(score, ensure_ascii=False), float(score.get("overall") or 0.0),
             round(elapsed, 2)),
        )
        rid = cur.lastrowid
        conn.commit()
        logger.info("Saved run to DB: run_id=%d", rid)
        return rid
    finally:
        conn.close()


def _safe_name(s: str) -> str:
    s = (s or "").strip().replace("/", "__").replace(":", "__")
    s = re.sub(r"[^a-zA-Z0-9_.-]+", "_", s)
    return s[:120]


def _write_pred_files(file_id: str, rid: int, model_name: str, obj: dict, gold: dict,
                      ok: bool, errors: list, warnings: list, score: dict, view: dict) -> None:
    d = PREDS_DIR / file_id
    d.mkdir(parents=True, exist_ok=True)
    base = f"{rid:06d}__{_safe_name(model_name)}"

    (d / f"{base}__pred.json").write_text(
        json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    (d / "gold.json").write_text(
        json.dumps(gold, ensure_ascii=False, indent=2), encoding="utf-8")
    (d / f"{base}__report.json").write_text(json.dumps({
        "run_id": rid,
        "file_id": file_id,
        "model_name": model_name,
        "is_valid": bool(ok),
        "errors": errors,
        "warnings": warnings,
        "score": score,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    (d / f"{base}__hierarchy.txt").write_text(render_text(view), encoding="utf-8")
    # The outline is for reading; the same join as JSON is what the web console and any
    # downstream consumer actually want, so both are written.
    (d / f"{base}__hierarchy.json").write_text(
        json.dumps(view, ensure_ascii=False, indent=2), encoding="utf-8")
    gold_view = to_scope_hierarchy(gold)
    (d / "gold_hierarchy.json").write_text(
        json.dumps(gold_view, ensure_ascii=False, indent=2), encoding="utf-8")
    # The nested tree: one root, scopes inside scopes, blocks inside blocks.
    tree = to_nested_tree(obj)
    (d / f"{base}__tree.json").write_text(
        json.dumps(tree, ensure_ascii=False, indent=2), encoding="utf-8")
    (d / f"{base}__tree.txt").write_text(render_tree_text(tree), encoding="utf-8")
    (d / "gold_tree.json").write_text(
        json.dumps(to_nested_tree(gold), ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Prediction files saved under %s", d)


def run_pipeline_for_file(filename_or_path: str, save: bool = True,
                          print_hierarchy: bool = False, strategy: str = "single") -> Dict[str, Any]:
    """Extract, validate, score and store the structure of one Python file.

    `strategy` picks how the extraction is generated: "single" sends the whole file in one
    request, "multicall" sends one request per top-level definition and merges, "gold" skips the
    model entirely. Everything after generation is identical for all three, so the strategies
    stay comparable.
    """
    t0 = time.time()
    logger.info("=" * 60)
    logger.info("PIPELINE START — input=%s", filename_or_path)

    file_id, source = _load_source(filename_or_path)

    # The AST gold is built first: it is the thing the run is scored against, and if the file
    # does not parse there is no point calling a model about it.
    gold = record_from_source(source, file_id)
    logger.info("Gold record: %d scopes, %d blocks, %d relations",
                len(gold["scopes"]), len(gold["blocks"]), len(gold["relations"]))

    backend = os.getenv("LLM_BACKEND", "ollama").strip().lower()
    if strategy == "gold":
        backend = "gold"
    if backend == "gold":
        # Exercises every stage below without a model, which is how the rest of this file gets
        # tested when no backend is reachable.
        obj: Any = json.loads(json.dumps(gold))
        logger.info("Backend 'gold' — skipping the model call")
    elif strategy == "multicall":
        from .multicall import run_multicall_for_source
        llm_t0 = time.time()
        obj = run_multicall_for_source(source, file_id)
        logger.info("Multicall complete in %.2fs", time.time() - llm_t0)
    else:
        llm_t0 = time.time()
        raw = generate_code_json(source, file_id)
        logger.info("LLM replied — %d chars in %.2fs", len(raw), time.time() - llm_t0)
        obj = extract_json(raw)

    if isinstance(obj, dict) and not str(obj.get("file_id") or "").strip():
        obj["file_id"] = file_id

    # Say a correct answer in the lexicon's words before judging it, so an extraction is not
    # failed for writing "def" where the lexicon says "function". The run is saved after this,
    # so the stored JSON is the normalised one.
    obj = normalize_document(obj)

    ok, errors, warnings = validate_report(obj)
    logger.info("Validation: ok=%s, errors=%d, warnings=%d", ok, len(errors), len(warnings))
    if not ok:
        for e in errors[:10]:
            logger.warning("  Error: %s", e)

    score = score_record(obj, gold)
    logger.info("Score: overall=%.3f scope_f1=%.3f relation_f1=%.3f",
                score["overall"], score["scopes"]["f1"], score["relations"]["f1"])

    view = to_scope_hierarchy(obj)
    elapsed = time.time() - t0
    model_name = "gold" if backend == "gold" else f"{active_model_name()}+{strategy}"

    rid = -1
    if save:
        rid = _save_to_db(file_id, model_name, obj, ok, errors, warnings, score, elapsed)
        if os.getenv("SAVE_PRED_FILES", "1").strip() == "1":
            _write_pred_files(file_id, rid, model_name, obj, gold, ok, errors, warnings, score, view)

    if print_hierarchy:
        print(render_text(view))

    logger.info("PIPELINE COMPLETE — file_id=%s, valid=%s, overall=%.3f, %.2fs",
                file_id, ok, score["overall"], elapsed)
    logger.info("=" * 60)

    return {
        "run_id": rid,
        "file_id": file_id,
        "model_name": model_name,
        "strategy": strategy,
        "record": obj,
        "gold": gold,
        "is_valid": ok,
        "errors": errors,
        "warnings": warnings,
        "score": score,
        "hierarchy": view,
        "elapsed_s": round(elapsed, 2),
    }


def run_gold_hierarchy(filename_or_path: str) -> Dict[str, Any]:
    """The hierarchy view of the ground truth, with no model involved."""
    file_id, source = _load_source(filename_or_path)
    record = normalize_document(record_from_source(source, file_id))
    return to_scope_hierarchy(record)
