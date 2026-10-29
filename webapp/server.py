#!/usr/bin/env python3
"""Local web console for the nested-code pipeline.

The same idea as the OPORD test console it replaces: a dependency-free page you open, point at a
sample, and watch the pipeline run — plus the documentation of what the pipeline is, so the two
never drift apart. Standard library only, so it starts with `python3 webapp/server.py` and needs
nothing installed.

    python3 webapp/server.py            # http://localhost:8000
    PORT=8800 python3 webapp/server.py
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import (DATASET_DIR, DB_PATH, MANIFEST_JSONL, METRICS_DIR,  # noqa: E402
                        SCHEMA_JSON_PATH)
from app.evaluate import score_record  # noqa: E402
from app.gold import record_from_source  # noqa: E402
from app.hierarchy import (render_text, render_tree_text, to_nested_tree,  # noqa: E402
                           to_scope_hierarchy)
from app.llm_client import active_model_name  # noqa: E402
from app.new_validators import normalize_document, validate_report  # noqa: E402

STATIC = Path(__file__).resolve().parent / "static"
CONTENT_TYPES = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
                 ".js": "text/javascript; charset=utf-8", ".json": "application/json",
                 ".svg": "image/svg+xml"}

_manifest_cache: list = []


def manifest() -> list:
    global _manifest_cache
    if not _manifest_cache and MANIFEST_JSONL.exists():
        _manifest_cache = [json.loads(l) for l in MANIFEST_JSONL.read_text().splitlines() if l.strip()]
    return _manifest_cache


def find_sample(file_id: str) -> Path:
    direct = DATASET_DIR / f"{file_id}.py"
    if direct.exists():
        return direct
    hits = sorted(DATASET_DIR.glob(f"{file_id}*.py"))
    if not hits:
        raise FileNotFoundError(file_id)
    return hits[0]


def db_rows(limit: int = 60) -> list:
    if not DB_PATH.exists():
        return []
    conn = sqlite3.connect(str(DB_PATH))
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT id, file_id, model_name, is_valid, overall, elapsed_s, created_at,"
            " validation_errors, validation_warnings, score"
            " FROM code_runs ORDER BY id DESC LIMIT ?", (limit,))
        out = []
        for r in cur.fetchall():
            row = dict(r)
            for key in ("validation_errors", "validation_warnings", "score"):
                try:
                    row[key] = json.loads(row[key] or "null")
                except Exception:
                    row[key] = None
            out.append(row)
        return out
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()


def run_record(run_id: int) -> dict:
    conn = sqlite3.connect(str(DB_PATH))
    try:
        conn.row_factory = sqlite3.Row
        r = conn.execute("SELECT * FROM code_runs WHERE id = ?", (run_id,)).fetchone()
        if not r:
            return {}
        row = dict(r)
        record = json.loads(row.get("json_output") or "{}")
        return {
            "run": {k: v for k, v in row.items() if k != "json_output"},
            "record": record,
            "hierarchy": to_scope_hierarchy(record),
            "outline": render_text(to_scope_hierarchy(record)),
        }
    finally:
        conn.close()


def dataset_stats() -> dict:
    stats_path = DATASET_DIR / "stats.json"
    stats = json.loads(stats_path.read_text()) if stats_path.exists() else {}
    return stats


def metrics_runs() -> list:
    if not METRICS_DIR.exists():
        return []
    out = []
    for p in sorted(METRICS_DIR.glob("run_*.json"), reverse=True):
        try:
            data = json.loads(p.read_text())
        except Exception:
            continue
        out.append({"file": p.name, "strategy": data.get("strategy"),
                    "count": data.get("count"), "elapsed_s": data.get("elapsed_s"),
                    "aggregate": data.get("aggregate") or {},
                    "per_file": data.get("per_file") or [],
                    "failures": data.get("failures") or []})
    return out


class Handler(BaseHTTPRequestHandler):
    server_version = "NestedCodeConsole/1.0"

    def log_message(self, fmt, *args):   # keep the console quiet
        pass

    # -- plumbing ------------------------------------------------------------
    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code: int = 200) -> None:
        self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json")

    def _static(self, name: str) -> None:
        path = (STATIC / name).resolve()
        if not str(path).startswith(str(STATIC.resolve())) or not path.exists():
            self._send(404, b"not found", "text/plain")
            return
        self._send(200, path.read_bytes(),
                   CONTENT_TYPES.get(path.suffix, "application/octet-stream"))

    # -- routes --------------------------------------------------------------
    def do_GET(self):
        url = urlparse(self.path)
        path, query = url.path, parse_qs(url.query)
        try:
            if path in ("/", "/index.html"):
                return self._static("index.html")
            if path != "/" and (STATIC / path.lstrip("/")).is_file():
                return self._static(path.lstrip("/"))

            if path == "/api/health":
                return self._json({
                    "backend": os.getenv("LLM_BACKEND", "ollama"),
                    "model": active_model_name(),
                    "dataset_dir": str(DATASET_DIR),
                    "n_samples": len(manifest()),
                    "db": str(DB_PATH),
                    "db_exists": DB_PATH.exists(),
                    "n_runs": len(db_rows(1000)),
                    "schema": str(SCHEMA_JSON_PATH),
                })

            if path == "/api/dataset":
                limit = int((query.get("limit") or ["300"])[0])
                rows = [{"id": r["id"], "split": r.get("split"),
                         "unit_kinds": r.get("unit_kinds", []),
                         **{k: r["metrics"][k] for k in
                            ("n_lines", "block_depth", "loop_depth", "branch_depth",
                             "n_functions", "n_classes", "n_ast_nodes")
                            if k in r["metrics"]}}
                        for r in manifest()[:limit]]
                return self._json({"stats": dataset_stats(), "samples": rows})

            if path.startswith("/api/sample/"):
                fid = unquote(path.split("/api/sample/", 1)[1])
                src_path = find_sample(fid)
                source = src_path.read_text(encoding="utf-8", errors="ignore")
                gold = normalize_document(record_from_source(source, src_path.stem))
                view = to_scope_hierarchy(gold)
                tree = to_nested_tree(gold)
                return self._json({
                    "file_id": src_path.stem,
                    "path": str(src_path.relative_to(ROOT)),
                    "n_lines": source.count("\n") + 1,
                    "source": source,
                    "gold": gold,
                    "hierarchy": view,
                    "outline": render_text(view),
                    "tree": tree,
                    "tree_text": render_tree_text(tree),
                })

            if path == "/api/runs":
                return self._json({"runs": db_rows(int((query.get("limit") or ["60"])[0]))})

            if path.startswith("/api/run/"):
                return self._json(run_record(int(path.rsplit("/", 1)[1])) or {})

            if path == "/api/metrics":
                return self._json({"runs": metrics_runs()})

            if path == "/api/schema":
                return self._json(json.loads(SCHEMA_JSON_PATH.read_text()))

            return self._send(404, b"not found", "text/plain")
        except FileNotFoundError as e:
            return self._json({"error": f"not found: {e}"}, 404)
        except Exception as e:
            traceback.print_exc()
            return self._json({"error": f"{type(e).__name__}: {e}"}, 500)

    def do_POST(self):
        url = urlparse(self.path)
        try:
            length = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            return self._json({"error": "bad JSON body"}, 400)

        try:
            if url.path == "/api/extract":
                from app.pipeline import run_pipeline_for_file
                fid = str(payload.get("file_id") or "").strip()
                strategy = str(payload.get("strategy") or "gold").strip()
                if not fid:
                    return self._json({"error": "file_id is required"}, 400)
                result = run_pipeline_for_file(fid, save=bool(payload.get("save", True)),
                                               strategy=strategy)
                return self._json({
                    "file_id": result["file_id"],
                    "run_id": result["run_id"],
                    "model_name": result["model_name"],
                    "strategy": result["strategy"],
                    "is_valid": result["is_valid"],
                    "errors": result["errors"],
                    "warnings": result["warnings"],
                    "score": result["score"],
                    "record": result["record"],
                    "hierarchy": result["hierarchy"],
                    "outline": render_text(result["hierarchy"]),
                    "gold_hierarchy": to_scope_hierarchy(result["gold"]),
                    "tree": to_nested_tree(result["record"]),
                    "gold_tree": to_nested_tree(result["gold"]),
                    "elapsed_s": result["elapsed_s"],
                })

            if url.path == "/api/score":
                # Score an arbitrary record the user pastes in, against a sample's gold.
                fid = str(payload.get("file_id") or "").strip()
                record = normalize_document(payload.get("record") or {})
                source = find_sample(fid).read_text(encoding="utf-8", errors="ignore")
                gold = record_from_source(source, fid)
                ok, errors, warnings = validate_report(record)
                return self._json({"is_valid": ok, "errors": errors, "warnings": warnings,
                                   "score": score_record(record, gold)})

            return self._send(404, b"not found", "text/plain")
        except FileNotFoundError as e:
            return self._json({"error": f"not found: {e}"}, 404)
        except Exception as e:
            traceback.print_exc()
            return self._json({"error": f"{type(e).__name__}: {e}"}, 500)


def main() -> None:
    port = int(os.getenv("PORT", "8000"))
    srv = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"nested-code console  →  http://localhost:{port}")
    print(f"  dataset : {DATASET_DIR}  ({len(manifest())} samples)")
    print(f"  backend : {os.getenv('LLM_BACKEND', 'ollama')} / {active_model_name()}")
    print("  Ctrl-C to stop")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
