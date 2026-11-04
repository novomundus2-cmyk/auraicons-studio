#!/usr/bin/env python3
"""
10-PASS RIGOROUS VERIFICATION SUITE
Verifies:
  Pass 1: Static assets HTTP 200 checks (atlas-cover-concept.png, local-ai-concept.png)
  Pass 2: Tri-Core endpoint /api/ekc/math/verify returns PASS, 0.00 Pacioli diff, and C latency
  Pass 3: EKC Agents endpoint /api/ekc/agents returns 16 biblical agents from WAL SQLite
  Pass 4: Real HTTP auth/privacy controls and honest unavailable audit (not a full security audit)
  Pass 5: C byte engine libekc_byte_engine.dylib memory struct size == 32 bytes packed
  Pass 6: Haskell binary ekc_math_proofs exits 0 with all invariants verified
  Pass 7: Python Clean Code ekc_clean_math.py verifies exact Decimal and ctypes bindings
  Pass 8: Web Audio source declares the four expected routines (static check)
  Pass 9: TypeScript & Vite production build (npm run check 0 errors)
  Pass 10: Headless Chrome screenshot of Slide 4 (Architecture, Math, Photo) (capture only; image content requires review)
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from decimal import Decimal, InvalidOperation
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
PORTFOLIO_DIR = Path(os.environ.get(
    "EKC_PORTFOLIO_DIR",
    "/Users/mikelirastorza/Documents/Codex/2026-11-03/portfolio-improvements/work/portfolio",
))
BASE_URL = os.environ.get("EKC_VERIFY_BASE_URL", "http://127.0.0.1:3222").rstrip("/")
ARTIFACTS_DIR = tempfile.mkdtemp(prefix="ekc-verification-")
CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def math_audit_passed(data: object, expected_script_sha256: str) -> bool:
    """Comprobar evidencia C, Haskell y Python; la etiqueta PASS sola no basta."""
    if not isinstance(data, dict) or data.get("ok") is not True:
        return False
    execution = data.get("execution", {})
    if (not isinstance(execution, dict)
            or execution.get("source") != "local_process"
            or execution.get("script_sha256") != expected_script_sha256):
        return False
    audit = data.get("audit")
    if not isinstance(audit, dict) or audit.get("status") != "PASS":
        return False
    clean = audit.get("clean_code_python", {})
    c_engine = audit.get("c_byte_engine", {})
    proofs = audit.get("haskell_formal_proofs", {})
    if not all(isinstance(part, dict) for part in (clean, c_engine, proofs)):
        return False
    stats = c_engine.get("welford_stream_stats", {})
    if not isinstance(stats, dict):
        return False
    try:
        expected_stats = {"mean": 55.4, "m2": 8244.9, "variance": 824.49,
                          "std_dev": math.sqrt(824.49)}
        return (
            clean.get("pacioli_balance_exact") is True
            and Decimal(str(clean.get("pacioli_diff_decimal"))) == Decimal("0.00")
            and clean.get("cad_tolerance_compliant") is True
            and abs(Decimal(str(clean.get("cad_delta_mm")))) <= Decimal("0.200")
            and c_engine.get("available") is True
            and c_engine.get("record_packed_size_bytes") == 32
            and stats.get("count") == 10
            and all(math.isclose(float(stats.get(key)), expected, rel_tol=1e-12)
                    for key, expected in expected_stats.items())
            and all(proofs.get(key) is True for key in (
                "all_invariants_verified", "welford_monoid_associativity",
                "welford_monoid_identity", "cad_physical_tolerance_0_2mm",
                "pacioli_rational_balance_exact"))
            and Decimal(str(proofs.get("pacioli_diff_cents"))) == 0
        )
    except (TypeError, ValueError, InvalidOperation):
        return False


def http_json(method: str, path: str, payload: dict | None = None) -> tuple[int, dict]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(BASE_URL + path, data=body, method=method,
                                     headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read())


def audit_is_unavailable(status: int, data: object) -> bool:
    """No aceptar una puntuación inventada como sustituto de una auditoría."""
    return (status == 503 and isinstance(data, dict)
            and data.get("ok") is False and data.get("status") == "no_evaluado"
            and "report" not in data and "overall_score" not in data
            and "security_grade" not in data)


def verify_http_controls() -> tuple[bool, str]:
    checks = []
    status, data = http_json("GET", "/api/security/audit")
    checks.append(("audit unavailable without fabricated score", audit_is_unavailable(status, data)))
    for method, path, payload, expected in (
        ("GET", "/api/notes", None, 401),
        ("GET", "/api/job-requests", None, 401),
        ("POST", "/api/db/benchmark", {"recordCount": 100}, 401),
        ("POST", "/api/tech-grounding", {"query": "test"}, 401),
        ("GET", "/api/db/table/job_requests", None, 404),
        ("POST", "/api/db/query", {"sql": "SELECT * FROM job_requests"}, 400),
    ):
        actual, _ = http_json(method, path, payload)
        checks.append((f"{method} {path}: {actual} expected {expected}", actual == expected))
    status, metadata = http_json("GET", "/api/db/metadata")
    tables = metadata.get("tables")
    names = {item.get("name") for item in tables if isinstance(item, dict)} if isinstance(tables, list) else set()
    private = {"job_requests", "users", "project_notes", "drive_exports"}
    checks.append(("metadata contains only public table names",
                   status == 200 and isinstance(tables, list) and bool(names)
                   and len(names) == len(tables) and all(isinstance(name, str) for name in names)
                   and not (names & private)))
    return all(passed for _, passed in checks), "; ".join(
        f"{name}={'PASS' if passed else 'FAIL'}" for name, passed in checks)


def log_pass(pass_num: int, title: str, details: str, passed: bool):
    status_icon = "✓ [PASS]" if passed else "✗ [FAIL]"
    print(f"Pass {pass_num:02d}/10: {status_icon} - {title}")
    print(f"        Details: {details}\n")
    if not passed:
        raise RuntimeError(f"Pass {pass_num} failed: {details}")

def main():
    print("=" * 72)
    print("   EKC ARCHITECTURE: 10-PASS COMPREHENSIVE VERIFICATION SUITE       ")
    print("   Author: Mikel Irastorza (Data & Deployment Engineer · EFA)       ")
    print("=" * 72 + "\n")

    print(f"Candidate: {REPO_DIR} | Portfolio: {PORTFOLIO_DIR} | URL: {BASE_URL}")

    # Pass 1: Static Assets HTTP 200
    try:
        req1 = urllib.request.Request(f"{BASE_URL}/assets/atlas-cover-concept.png", method="HEAD")
        resp1 = urllib.request.urlopen(req1, timeout=5)
        len1 = resp1.headers.get("Content-Length")

        req2 = urllib.request.Request(f"{BASE_URL}/assets/local-ai-concept.png", method="HEAD")
        resp2 = urllib.request.urlopen(req2, timeout=5)
        len2 = resp2.headers.get("Content-Length")

        log_pass(1, "Static Assets HTTP 200 & Byte Verification",
                 f"Slide 1 asset: {len1} bytes (200 OK) | Slide 4 asset: {len2} bytes (200 OK)",
                 resp1.status == 200 and resp2.status == 200 and int(len2) > 1000000)
    except Exception as e:
        log_pass(1, "Static Assets HTTP 200", str(e), False)

    # Pass 2: Tri-Core Math API Endpoint
    try:
        resp = urllib.request.urlopen(f"{BASE_URL}/api/ekc/math/verify", timeout=5)
        data = json.loads(resp.read().decode("utf-8"))
        audit = data.get("audit", {})
        log_pass(2, "Tri-Core Math API (/api/ekc/math/verify)",
                 f"Status: {audit.get('status')} | Pacioli Diff: {audit.get('clean_code_python', {}).get('pacioli_diff_decimal')} EUR | C Latency: {audit.get('c_byte_engine', {}).get('welford_stream_stats', {}).get('duration_microseconds')} us",
                 math_audit_passed(data, hashlib.sha256(
                     (REPO_DIR / "CV/03_math_haskell_python/ekc_clean_math.py").read_bytes()).hexdigest()))
    except Exception as e:
        log_pass(2, "Tri-Core Math API", str(e), False)

    # Pass 3: EKC Agents 16 Databases
    try:
        resp = urllib.request.urlopen(f"{BASE_URL}/api/ekc/agents", timeout=5)
        data = json.loads(resp.read().decode("utf-8"))
        total = data.get("total_agents", 0)
        log_pass(3, "EKC Agents SQLite WAL Ecosystem (/api/ekc/agents)",
                 f"Total agents connected: {total} | Brand: {data.get('brand')} | Meaning: {data.get('meaning')}",
                 data.get("ok") is True and total == 16
                 and data.get("verified_agents") == 16
                 and data.get("verification") == "sqlite_readonly_quick_check"
                 and isinstance(data.get("agents"), list) and len(data["agents"]) == 16
                 and len({agent.get("folder") for agent in data["agents"]}) == 16
                 and all(agent.get("status") == "verified" and agent.get("integrity") == "ok"
                         and agent.get("has_manifest") is True and agent.get("journal_mode") == "wal"
                         for agent in data["agents"]))
    except Exception as e:
        log_pass(3, "EKC Agents SQLite WAL Ecosystem", str(e), False)

    # Pass 4: Auth/privacy HTTP regressions; not a comprehensive security audit.
    try:
        passed, details = verify_http_controls()
        log_pass(4, "HTTP auth/privacy controls and honest audit status", details, passed)
    except Exception as e:
        log_pass(4, "HTTP auth/privacy controls", str(e), False)

    # Pass 5: C Byte Engine Compiled Memory Layout
    try:
        import ctypes
        dylib = str(REPO_DIR / "CV/03_math_haskell_python/libekc_byte_engine.dylib")
        clib = ctypes.CDLL(dylib)
        clib.ekc_record_size_bytes.restype = ctypes.c_size_t
        rec_size = clib.ekc_record_size_bytes()
        log_pass(5, "C Byte Engine Packed Struct Size (libekc_byte_engine.dylib)",
                 f"EkcStreamRecord size: {rec_size} bytes (Exactly 2 records per 64-byte L1 cache line)",
                 rec_size == 32)
    except Exception as e:
        log_pass(5, "C Byte Engine Packed Struct Size", str(e), False)

    # Pass 6: Haskell Formal Proofs Binary Execution
    try:
        hs_bin = str(REPO_DIR / "CV/03_math_haskell_python/ekc_math_proofs")
        res = subprocess.run([hs_bin], capture_output=True, text=True, check=True)
        hs_data = json.loads(res.stdout.strip())
        log_pass(6, "Haskell Formal Proofs Execution (ekc_math_proofs)",
                 f"All Invariants: {hs_data.get('all_invariants_verified')} | Welford Assoc: {hs_data.get('welford_monoid_associativity')} | CAD: {hs_data.get('cad_physical_tolerance_0_2mm')}",
                 hs_data.get("all_invariants_verified") is True)
    except Exception as e:
        log_pass(6, "Haskell Formal Proofs Execution", str(e), False)

    # Pass 7: Python Clean Code Cross-Language Verification
    try:
        py_bin = sys.executable
        py_script = str(REPO_DIR / "CV/03_math_haskell_python/ekc_clean_math.py")
        res = subprocess.run([py_bin, py_script], capture_output=True, text=True, check=True)
        log_pass(7, "Python Clean Code Engine (ekc_clean_math.py)",
                 "Executed cross-language arithmetic audit successfully",
                 "[SUCCESS]" in res.stdout)
    except Exception as e:
        log_pass(7, "Python Clean Code Engine", str(e), False)

    # Pass 8: Web Audio System Sound Engine File Integrity
    try:
        audio_ts = PORTFOLIO_DIR / "src/utils/audioSystem.ts"
        with open(audio_ts, "r", encoding="utf-8") as f:
            content = f.read()
        has_page_flip = "playPageFlip" in content
        has_cash_reg = "playCashRegister" in content
        has_relay = "playMechanicalRelay" in content
        has_shield = "playShieldEngage" in content
        log_pass(8, "Web Audio routine names present in source (audioSystem.ts)",
                 "Includes pageFlip (Libro), cashRegister (Monedas), mechanicalRelay (C Engine), and shieldEngage (Anti-Hacking)",
                 has_page_flip and has_cash_reg and has_relay and has_shield)
    except Exception as e:
        log_pass(8, "Web Audio Procedural Sound Engine", str(e), False)

    # Pass 9: TypeScript & Vite Build Pipeline
    try:
        portfolio_dir = PORTFOLIO_DIR
        res = subprocess.run(["npm", "run", "check"], cwd=portfolio_dir, capture_output=True, text=True, check=True)
        log_pass(9, "TypeScript & Vite Production Check (npm run check)",
                 "Zero type errors (tsc --noEmit), successful production bundling (vite build), configured tests passing",
                 res.returncode == 0)
    except Exception as e:
        log_pass(9, "TypeScript & Vite Production Check", str(e), False)

    # Pass 10: Headless Chrome Visual Capture of Slide 4 (capture only)
    try:
        screenshot_path = os.path.join(ARTIFACTS_DIR, "evidence_pass10_slide4_fresh_verified.png")
        url = f"{BASE_URL}/?tab=the-brothers&slide=4"
        cmd = [
            CHROME_BIN,
            "--headless=new",
            "--disable-gpu",
            "--window-size=1280,900",
            f"--screenshot={screenshot_path}",
            url
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        exists = os.path.exists(screenshot_path) and os.path.getsize(screenshot_path) > 10000
        log_pass(10, "Headless Chrome screenshot capture (Slide 4)",
                 f"Captured {screenshot_path} ({os.path.getsize(screenshot_path) if exists else 0} bytes) ; PNG generated (image content requires review)",
                 exists)
    except Exception as e:
        log_pass(10, "Headless Chrome screenshot capture", str(e), False)

    print("\n" + "=" * 72)
    print("   ALL 10 CHECKS PASSED; HTTP CONTROLS ARE NOT A FULL SECURITY AUDIT")
    print("=" * 72)

if __name__ == "__main__":
    main()
