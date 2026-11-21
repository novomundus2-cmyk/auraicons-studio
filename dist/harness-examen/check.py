#!/usr/bin/env python3
"""Examen held-out. Solo las dos preguntas del scoring set. No editar este archivo en el ciclo."""
import argparse
import subprocess
import sys
from pathlib import Path

import pandas as pd


def q1_nulos_sin_cambiar_tipo(cleaned: pd.DataFrame, original: pd.DataFrame) -> bool:
    numeric_cols = ["amount", "qty"]
    if len(cleaned) != len(original):
        return False
    for col in numeric_cols:
        if col not in cleaned.columns:
            return False
        if cleaned[col].isna().any():
            return False
        if not pd.api.types.is_numeric_dtype(cleaned[col]):
            return False
        if not pd.api.types.is_numeric_dtype(original[col]):
            return False
        if str(cleaned[col].dtype) != str(original[col].dtype):
            return False
    return True


def q2_outliers_parquet(out_dir: Path, original: pd.DataFrame) -> bool:
    parquet_path = out_dir / "outliers.parquet"
    if not parquet_path.is_file():
        return False
    try:
        report = pd.read_parquet(parquet_path)
    except Exception:
        return False
    if report.empty or "amount" not in report.columns:
        return False
    if report["amount"].isna().any():
        return False
    if not pd.api.types.is_numeric_dtype(report["amount"]):
        return False
    roundtrip = pd.read_parquet(parquet_path)
    if not report["amount"].equals(roundtrip["amount"]):
        return False
    amounts = set(roundtrip["amount"].astype("float64").tolist())
    return 1000.0 in amounts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--harness", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    if out_dir.exists():
        for child in out_dir.iterdir():
            if child.is_file():
                child.unlink()
    else:
        out_dir.mkdir(parents=True)
    proc = subprocess.run(
        [args.python, args.harness, "--input", args.data, "--out-dir", str(out_dir)],
        capture_output=True,
        text=True,
    )
    original = pd.read_csv(args.data)
    cleaned_path = out_dir / "cleaned.csv"
    q1 = False
    q2 = False
    if proc.returncode == 0 and cleaned_path.is_file():
        cleaned = pd.read_csv(cleaned_path)
        q1 = q1_nulos_sin_cambiar_tipo(cleaned, original)
        q2 = q2_outliers_parquet(out_dir, original)
    print(f"Q1={'PASS' if q1 else 'FAIL'}")
    print(f"Q2={'PASS' if q2 else 'FAIL'}")
    print(f"SCORE={int(q1) + int(q2)}/2")
    if proc.returncode != 0:
        print("HARNESS_EXIT", proc.returncode)
        if proc.stderr:
            print(proc.stderr[-800:])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
