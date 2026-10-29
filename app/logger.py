"""
Centralized logging module for the OPORD→JSON pipeline.

Configures Python's logging with:
- File handler  → logs/training_run.log  (DEBUG level, full detail)
- Console handler → stderr  (INFO level, concise)

Usage in any module:
    from app.logger import get_logger
    logger = get_logger(__name__)
    logger.info("message")
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from datetime import datetime

_ROOT_DIR = Path(__file__).resolve().parents[1]
_LOG_DIR = _ROOT_DIR / "logs"
_LOG_DIR.mkdir(parents=True, exist_ok=True)

_LOG_FILE = _LOG_DIR / "training_run.log"

_configured = False


def _setup_logging() -> None:
    global _configured
    if _configured:
        return
    _configured = True

    root = logging.getLogger("opord2json")
    root.setLevel(logging.DEBUG)

    # ── File handler (detailed) ──────────────────────────────
    fh = logging.FileHandler(str(_LOG_FILE), mode="a", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(
        logging.Formatter(
            "[%(asctime)s] %(levelname)-8s %(name)-30s │ %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root.addHandler(fh)

    # ── Console handler (concise) ─────────────────────────────
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(
        logging.Formatter(
            "%(levelname)-8s │ %(message)s",
        )
    )
    root.addHandler(ch)

    # Write a session separator on first setup
    with open(_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*100}\n")
        f.write(f"  NEW SESSION — {datetime.now().isoformat()}\n")
        f.write(f"{'='*100}\n\n")


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the 'opord2json' namespace."""
    _setup_logging()
    return logging.getLogger(f"opord2json.{name}")
