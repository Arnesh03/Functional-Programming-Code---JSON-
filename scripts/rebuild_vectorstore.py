#!/usr/bin/env python3
"""Build the retrieval index over the train split.

    python3 scripts/rebuild_vectorstore.py --limit 250

Only train-split files are indexed; a val or test file in the corpus would leak its own answer
into its own extraction.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.rag_store import INDEX_PATH, build_index  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description="Build the section retrieval index")
    ap.add_argument("--limit", type=int, default=250, help="train files to index")
    args = ap.parse_args()

    index = build_index(limit=args.limit, rebuild=True)
    size = INDEX_PATH.stat().st_size / 1_048_576
    print(f"indexed {index['n_docs']} sections from {index['n_files']} train files")
    print(f"vocabulary: {len(index['df'])} tokens · postings: {len(index['postings'])}")
    print(f"written to {INDEX_PATH}  ({size:.1f} MB)")


if __name__ == "__main__":
    main()
