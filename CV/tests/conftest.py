"""Shared fixtures: every test runs against a throw-away database, never the real one."""

from __future__ import annotations

import sqlite3
import sys
import types
from pathlib import Path

import pytest

CV_ROOT = Path(__file__).resolve().parent.parent
for sub in (
    "02_streaming_platform",
    "03_math_haskell_python",
    "04_database_lakehouse",
    "05_archify_visualizer",
    "06_ai_note_agent",
    "07_notebooklm_enterprise_dossier",
    "08_autonomous_executive_presenter",
    "09_antigravity_perfect_pipeline",
):
    sys.path.insert(0, str(CV_ROOT / sub))

import build_database  # noqa: E402


@pytest.fixture()
def tmp_paths(tmp_path: Path) -> types.SimpleNamespace:
    """A PATHS-like object pointing at an empty, schema-initialised temp lakehouse."""
    paths = types.SimpleNamespace(
        db_path=tmp_path / "test.db",
        notebooks_dir=tmp_path / "notebooks",
        categories_dir=tmp_path / "categories",
        archify_bridge_js=tmp_path / "bridge.js",
    )
    with sqlite3.connect(paths.db_path) as conn:
        conn.executescript(build_database.SCHEMA_SQL)
        conn.execute("INSERT INTO dim_users VALUES ('u1','Ana','ES',1,'LOW','2026-01-01')")
        build_database.populate_corporate_enterprise(conn)
    return paths
