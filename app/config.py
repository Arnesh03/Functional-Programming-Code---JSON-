from pathlib import Path
import os

ROOT_DIR = Path(__file__).resolve().parents[1]

# Load .env automatically (so uv run works without "source .env")
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT_DIR / ".env")
except Exception:
    pass

SCHEMA_JSON_PATH = ROOT_DIR / "assets" / "schema" / "nested_code_schema_v1.json"
LEXICON_JSON_PATH = ROOT_DIR / "assets" / "lexicon" / "nested_code_lexicon_v1.json"

# Which dataset the pipeline runs against. DATASET_DIR=data/codecomplex switches corpora
# without touching code, so the generated set and a real-code set can coexist.
DATASET_DIR = (ROOT_DIR / os.getenv("DATASET_DIR", "data/nested_code/generated")).resolve()
DATASET_JSONL = DATASET_DIR / "dataset.jsonl"
MANIFEST_JSONL = DATASET_DIR / "manifest.jsonl"

DB_PATH = ROOT_DIR / "nested_code.db"

RESULTS_DIR = ROOT_DIR / "results"
PREDS_DIR = RESULTS_DIR / "preds"
METRICS_DIR = RESULTS_DIR / "metrics"

# A generated sample is ~26 KB. Anything past this is cut before the prompt is built, so a long
# file degrades to a partial extraction instead of silently overflowing the context window.
MAX_SOURCE_CHARS = int(os.getenv("MAX_SOURCE_CHARS", "28000"))

# Retrieval. RAG=0 turns it off (for a no-retrieval baseline); RAG_K_FOR_LLM sets how many
# already-solved sections are shown. The index covers the train split only.
SECTION_INDEX_PATH = ROOT_DIR / "assets" / "index" / "section_index.json"
RAG_K = int(os.getenv("RAG_K_FOR_LLM", "2"))
