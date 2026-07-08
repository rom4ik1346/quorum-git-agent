from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def database_path() -> Path:
    configured = os.getenv("QUORUM_DATABASE_PATH", "data/quorum.db")
    path = Path(configured)
    return path if path.is_absolute() else PROJECT_ROOT / path


def github_token() -> str | None:
    value = os.getenv("GITHUB_TOKEN", "").strip()
    return value or None
