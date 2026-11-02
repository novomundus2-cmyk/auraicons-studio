"""
===============================================================================
MODULE: agent.py
LOCATION: 06_ai_note_agent/agent.py
PURPOSE: Clean-Code Multi-AI Orchestrator & Note Agent (Google Antigravity SDK +
         BigQuery AI/ML TimesFM 2.0 + Gemini 2.5 Flash + SQLite Lakehouse).
AUTHOR: Senior Data Platform & Deployment Engineering Portfolio
===============================================================================
"""

from __future__ import annotations

import asyncio
import json
import re
import sqlite3
import sys
from contextlib import closing
from pathlib import Path
from typing import Final

from google.antigravity import Agent, LocalAgentConfig
from google.antigravity.types import TemplatedSystemInstructions

AGENT_DIR: Final[Path] = Path(__file__).resolve().parent
CV_ROOT: Final[Path] = AGENT_DIR.parent
MATH_DIR: Final[Path] = CV_ROOT / "03_math_haskell_python"
DB_DIR: Final[Path] = CV_ROOT / "04_database_lakehouse"

for folder in (MATH_DIR, DB_DIR):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

from build_database import PATHS  # noqa: E402
from scientific_analytics import prove_monoid_and_queueing_theorems  # noqa: E402

# Notebook names the LLM may use: letters, digits, `_` and `-` only (no `/`, no `..`).
SAFE_NOTEBOOK_NAME: Final[re.Pattern[str]] = re.compile(r"^[\w\-]{1,80}(\.ipynb)?$")
# Only single read statements are accepted by `query_project_database`.
READ_ONLY_SQL: Final[re.Pattern[str]] = re.compile(r"^\s*(SELECT|WITH)\b", re.IGNORECASE)
MAX_RESULT_ROWS: Final[int] = 25


def resolve_notebook_path(filename: str) -> tuple[str, Path]:
    """Validates an LLM-supplied notebook name and returns (clean_name, path inside 01_notebooks/)."""
    if not SAFE_NOTEBOOK_NAME.fullmatch(filename):
        raise ValueError(f"Nombre de notebook no válido: {filename!r}. Usa solo letras, números, '_' o '-'.")
    clean_name = filename if filename.endswith(".ipynb") else f"{filename}.ipynb"
    return clean_name, PATHS.notebooks_dir / clean_name


def sync_cell_to_database(filename: str, cell_index: int, cell_type: str, content: str) -> None:
    """Persists a Gemini Notebook cell into `kb_study_notebooks` in `financial_lakehouse.db`."""
    with closing(sqlite3.connect(PATHS.db_path)) as conn, conn:
        conn.execute(
            "INSERT OR REPLACE INTO kb_study_notebooks VALUES (?, ?, ?, ?)",
            (filename, cell_index, cell_type, content),
        )


def create_study_notebook(filename: str, title: str) -> str:
    """Creates a new Gemini Notebook (.ipynb) in `01_notebooks/` and syncs to `financial_lakehouse.db`."""
    clean_name, nb_path = resolve_notebook_path(filename)
    PATHS.notebooks_dir.mkdir(parents=True, exist_ok=True)
    header_content = (
        f"# 🎓 {title}\n"
        "> Generado por el Agente de Notas (Google Antigravity SDK) y sincronizado en `financial_lakehouse.db`"
    )

    notebook_data = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [line + "\n" for line in header_content.splitlines()],
            }
        ],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.14"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }

    nb_path.write_text(json.dumps(notebook_data, indent=2, ensure_ascii=False), encoding="utf-8")
    sync_cell_to_database(clean_name, 0, "markdown", header_content)
    return f"Notebook creado en {nb_path} y sincronizado en financial_lakehouse.db."


def add_notebook_cell(filename: str, cell_type: str, content: str) -> str:
    """Appends a 'markdown' or 'code' cell to a Gemini Notebook and persists it in SQLite."""
    clean_name, nb_path = resolve_notebook_path(filename)
    if not nb_path.exists():
        create_study_notebook(clean_name, clean_name.removesuffix(".ipynb").replace("_", " ").title())

    notebook_data = json.loads(nb_path.read_text(encoding="utf-8"))
    lines = [line + "\n" for line in content.splitlines()]
    if lines:
        lines[-1] = lines[-1].rstrip("\n")

    normalized_type = "code" if cell_type.lower() == "code" else "markdown"
    new_cell: dict = {"cell_type": normalized_type, "metadata": {}, "source": lines}
    if normalized_type == "code":
        new_cell["execution_count"] = None
        new_cell["outputs"] = []

    cell_idx = len(notebook_data["cells"])
    notebook_data["cells"].append(new_cell)
    nb_path.write_text(json.dumps(notebook_data, indent=2, ensure_ascii=False), encoding="utf-8")
    sync_cell_to_database(clean_name, cell_idx, normalized_type, content)
    return f"Celda #{cell_idx} ({normalized_type}) añadida en {clean_name} y persistida en SQLite."


def _read_only_authorizer(action: int, *_: object) -> int:
    """SQLite authorizer: permits reads only; any write/DDL/ATTACH/PRAGMA is denied."""
    allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}
    return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY


def query_project_database(sql_query: str) -> str:
    """Executes a read-only SQL query against `04_database_lakehouse/financial_lakehouse.db`."""
    if not PATHS.db_path.exists():
        return "La base de datos no existe aún. Ejecuta `make db`."
    statement = sql_query.strip().rstrip(";")
    if not READ_ONLY_SQL.match(statement) or ";" in statement:
        return "Solo se permiten consultas SELECT/WITH de una única sentencia."
    # `mode=ro` cannot open this WAL database, so safety comes from query_only + an authorizer.
    with closing(sqlite3.connect(PATHS.db_path)) as conn:
        conn.execute("PRAGMA query_only = ON")
        conn.set_authorizer(_read_only_authorizer)
        try:
            cur = conn.execute(statement)
            cols = [d[0] for d in cur.description] if cur.description else []
            rows = cur.fetchmany(MAX_RESULT_ROWS)
        except sqlite3.Error as exc:
            return f"Consulta rechazada o inválida: {exc}"
        return json.dumps({"columns": cols, "rows": rows}, ensure_ascii=False, indent=2)


def run_interconnected_ai_audit() -> None:
    """
    Runs a deterministic audit across:
      - Mathematical Engine (`SymPy` symbolic verification)
      - Multi-AI Registry (`ai_insights_registry`: BigQuery TimesFM 2.0 + Gemini 2.5 + Antigravity)
      - 10-Project Roadmap (`kb_10_projects_roadmap`)
    """
    proofs = prove_monoid_and_queueing_theorems()
    with closing(sqlite3.connect(PATHS.db_path)) as conn:
        ai_rows = conn.execute(
            "SELECT ai_engine, model_name, target_category, predicted_metric_value, confidence_or_prob "
            "FROM ai_insights_registry ORDER BY insight_id LIMIT 6"
        ).fetchall()
        projects = conn.execute(
            "SELECT project_number, project_code, title, status FROM kb_10_projects_roadmap ORDER BY project_number"
        ).fetchall()

    print("==================================================================")
    print("🤖 AUDITORÍA MULTI-IA INTERCONECTADA (Antigravity + BigQuery AI/ML)")
    print("==================================================================")
    print(
        f"  • Verificación Simbólica SymPy (Welford Monoid): residuo = {proofs['associativity_error']} (EXACTO)"
    )
    print("  • Predicciones Registradas en `ai_insights_registry` (Top 6):")
    for engine, model, cat, val, conf in ai_rows:
        print(f"    - [{engine}] {model:<33} | cat={cat:<11} | valor={val:>9.2f} | conf={conf * 100:.1f}%")
    print("\n  • Estado de los 10 Proyectos en `kb_10_projects_roadmap`:")
    for num, code, title, status in projects:
        print(f"    {num:02d}. [{code}] {title:<64} -> {status}")


PERSONA_INSTRUCTIONS: Final[str] = """
Eres un Arquitecto e Ingeniero Senior de Big Data & Deployment (Apache Spark, Kafka KRaft, NiFi,
Haskell, Python Científico SymPy/SciPy/Polars, BigQuery AI/ML, Kubernetes y ArgoCD).
Todo lo que generes se sincroniza en `01_notebooks/*.ipynb` y en `04_database_lakehouse/financial_lakehouse.db`.
"""


async def run_interactive_agent(prompt: str) -> None:
    """Runs the live Google Antigravity SDK conversational agent with database tools."""
    config = LocalAgentConfig(
        system_instructions=TemplatedSystemInstructions(identity=PERSONA_INSTRUCTIONS),
        tools=[create_study_notebook, add_notebook_cell, query_project_database],
    )
    async with Agent(config) as agent:
        response = await agent.chat(prompt)
        async for chunk in response:
            print(chunk, end="", flush=True)
        print()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != "--audit":
        asyncio.run(run_interactive_agent(" ".join(sys.argv[1:])))
    else:
        run_interconnected_ai_audit()
