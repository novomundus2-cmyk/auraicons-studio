#!/usr/bin/env python3
"""Puntero al pipeline de aprendizaje del study pack. No duplica el currículo."""
from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path

CANDIDATES = [
    Path.home()
    / "Library/Mobile Documents/com~apple~CloudDocs/Desktop/01 - PROYECTOS/05 - Aprendizaje/DATA ENGINNEER FINAL STUDY",
    Path.home()
    / "Desktop/01 - PROYECTOS/05 - Aprendizaje/DATA ENGINNEER FINAL STUDY",
]


def find_study() -> Path:
    env = os.environ.get("STUDY_PACK")
    if env:
        p = Path(env)
        if (p / "Herramientas/pipeline-aprendizaje/hoy.py").exists():
            return p
    for c in CANDIDATES:
        if (c / "Herramientas/pipeline-aprendizaje/hoy.py").exists():
            return c
    raise SystemExit(
        "No encuentro el study pack. Abre DATA ENGINNEER FINAL STUDY o define STUDY_PACK."
    )


def main() -> None:
    study = find_study()
    target = study / "Herramientas/pipeline-aprendizaje/hoy.py"
    os.chdir(study)
    sys.argv[0] = str(target)
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()
