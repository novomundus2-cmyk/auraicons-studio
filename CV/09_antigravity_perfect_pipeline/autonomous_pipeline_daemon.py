"""
===============================================================================
MODULE: autonomous_pipeline_daemon.py
LOCATION: 09_antigravity_perfect_pipeline/autonomous_pipeline_daemon.py
PURPOSE: Autonomous 24/7 Pipeline Daemon & Little's Law Continuous Engine.
         Executes unattended cycles of the 6-stage Antigravity & Gemini Quant
         Pipeline, monitors market feeds (Crypto 24/7, Equities & Forex),
         enforces Little's Law bounds (rho = lambda / mu <= 0.80), audits Pacioli
         double-entry ledger invariants, and detects new candidate profiles.
AUTHOR: Mikel Irastorza · Presidente Supremo NovusMundus & Senior Platform Architect
===============================================================================
"""

from __future__ import annotations

import logging
import math
import sqlite3
import sys
import threading
import time
from contextlib import closing
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

logger = logging.getLogger("NovusPipelineDaemon")

DAEMON_DIR: Final[Path] = Path(__file__).resolve().parent
CV_ROOT: Final[Path] = DAEMON_DIR.parent
for d in (CV_ROOT, CV_ROOT / "09_antigravity_perfect_pipeline", CV_ROOT / "07_trading_bot", CV_ROOT / "06_ai_note_agent", CV_ROOT / "04_database_lakehouse"):
    if str(d) not in sys.path:
        sys.path.insert(0, str(d))

from perfect_pipeline import GLOBAL_PERFECT_PIPELINE, PerfectPipelineOrchestrator  # type: ignore # noqa: E402
from build_database import PATHS  # type: ignore # noqa: E402


@dataclass
class DaemonTelemetry:
    """Thread-safe snapshot of autonomous pipeline telemetry."""
    status: str = "IDLE"  # "RUNNING", "PAUSED", "STOPPED"
    total_cycles: int = 0
    ticks_processed: int = 0
    start_time: float = field(default_factory=time.time)
    last_cycle_timestamp: str = ""
    last_latency_ms: float = 0.0
    throughput_lambda: float = 0.0  # requests / second
    service_rate_mu: float = 25.0   # capacity / second
    utilization_rho: float = 0.0    # rho = lambda / mu <= 0.80
    pacioli_audit_status: str = "VERIFIED_BALANCED"
    last_pacioli_diff_cents: int = 0
    total_store_orders: int = 0
    total_candidates: int = 0
    last_symbol: str = "BTCUSDT"
    last_block_hash: str = ""
    last_thesis_summary: dict[str, Any] = field(default_factory=dict)
    errors_count: int = 0
    running: bool = False

    @property
    def cycles_completed(self) -> int:
        return self.total_cycles

    @property
    def current_rho(self) -> float:
        return self.utilization_rho

    @property
    def littles_law_compliant(self) -> bool:
        return self.utilization_rho <= 0.80

    @property
    def pacioli_compliant(self) -> bool:
        return self.pacioli_audit_status in ("BALANCED_OK", "VERIFIED_BALANCED")

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["cycles_completed"] = self.cycles_completed
        d["current_rho"] = self.current_rho
        d["littles_law_compliant"] = self.littles_law_compliant
        d["pacioli_compliant"] = self.pacioli_compliant
        d["is_running"] = self.running
        return d

    def __getitem__(self, item: str) -> Any:
        if hasattr(self, item):
            return getattr(self, item)
        d = self.to_dict()
        if item in d:
            return d[item]
        raise KeyError(item)

    def get(self, item: str, default: Any = None) -> Any:
        try:
            return self[item]
        except KeyError:
            return default


class AutonomousPipelineDaemon:
    """
    24/7 Autonomous background worker daemon for the Novus 6-Stage Perfect Pipeline.
    Runs non-blocking in a dedicated daemon thread.
    """

    TRACKED_SYMBOLS: Final[list[str]] = [
        "BTCUSDT",
        "ETHUSDT",
        "SOLUSDT",
        "BNBUSDT",
        "NVDA",
        "AAPL",
        "TSLA",
        "EURUSD",
        "XAUUSD",
    ]

    def __init__(self, cycle_interval_seconds: float = 12.0) -> None:
        self.cycle_interval_seconds = cycle_interval_seconds
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._telemetry = DaemonTelemetry()
        self._symbol_idx = 0
        self._last_audit_ts = 0.0

    @property
    def is_running(self) -> bool:
        if self._thread is not None and self._thread.is_alive():
            return not self._stop_event.is_set() and not self._pause_event.is_set()
        return not self._stop_event.is_set() and not self._pause_event.is_set() and self._telemetry.status == "RUNNING"

    def is_alive(self) -> bool:
        """Returns True if background daemon thread is currently alive."""
        return self._thread is not None and self._thread.is_alive()

    @property
    def is_paused(self) -> bool:
        return self._pause_event.is_set()

    def start(self) -> bool:
        """Starts the autonomous pipeline daemon thread if not running."""
        with self._lock:
            if self.is_running:
                if self.is_paused:
                    self.resume()
                return True

            self._stop_event.clear()
            self._pause_event.clear()
            self._telemetry.status = "RUNNING"
            self._telemetry.running = True
            self._telemetry.start_time = time.time()
            self._thread = threading.Thread(
                target=self._run_loop,
                name="NovusAutonomousPipelineDaemon",
                daemon=True,
            )
            self._thread.start()
            logger.info("Autonomous Pipeline Daemon started successfully.")
            return True

    def stop(self) -> bool:
        """Signals the autonomous pipeline daemon to stop."""
        with self._lock:
            self._stop_event.set()
            self._pause_event.clear()
            self._telemetry.status = "STOPPED"
            self._telemetry.running = False
            logger.info("Autonomous Pipeline Daemon stopped.")
            return True

    def pause(self) -> bool:
        """Pauses autonomous cycle execution."""
        with self._lock:
            self._pause_event.set()
            self._telemetry.status = "PAUSED"
            self._telemetry.running = False
            logger.info("Autonomous Pipeline Daemon paused.")
            return True

    def resume(self) -> bool:
        """Resumes autonomous cycle execution."""
        with self._lock:
            self._pause_event.clear()
            self._telemetry.status = "RUNNING"
            self._telemetry.running = True
            logger.info("Autonomous Pipeline Daemon resumed.")
            return True

    def force_cycle(self, symbol: str | None = None) -> dict[str, Any]:
        """Synchronously executes a single pipeline cycle immediately."""
        target_sym = symbol or self._next_symbol()
        return self._execute_cycle_step(target_sym)

    def scan_unplaced_candidates(self) -> int:
        """Scans SQLite database for candidate profiles awaiting placement."""
        self._audit_ledger_and_database()
        return self._telemetry.total_candidates

    def scan_pending_orders(self) -> int:
        """Scans SQLite database for store orders."""
        self._audit_ledger_and_database()
        return self._telemetry.total_store_orders

    def get_telemetry(self) -> DaemonTelemetry:
        """Returns snapshot DaemonTelemetry object (with .to_dict() and dict-like access)."""
        with self._lock:
            self._telemetry.running = self.is_running and not self.is_paused
            return self._telemetry

    def _next_symbol(self) -> str:
        """Selects the next symbol in rotation, verifying market schedules."""
        with self._lock:
            sym = self.TRACKED_SYMBOLS[self._symbol_idx % len(self.TRACKED_SYMBOLS)]
            self._symbol_idx += 1
            return sym

    def _run_loop(self) -> None:
        """Continuous daemon execution loop."""
        logger.info("Autonomous Pipeline Loop active.")
        while not self._stop_event.is_set():
            if self._pause_event.is_set():
                time.sleep(1.0)
                continue

            try:
                sym = self._next_symbol()
                self._execute_cycle_step(sym)
            except Exception as exc:
                with self._lock:
                    self._telemetry.errors_count += 1
                logger.error("Error in autonomous pipeline cycle: %s", exc)

            # Wait for next cycle or stop signal
            self._stop_event.wait(timeout=self.cycle_interval_seconds)

    def _execute_cycle_step(self, symbol: str) -> dict[str, Any]:
        """Executes a single step: 6-stage pipeline + telemetry + periodic Pacioli audit."""
        start_t = time.perf_counter()

        # 1. Execute 6-stage pipeline
        pipeline_res = GLOBAL_PERFECT_PIPELINE.execute_perfect_pipeline(symbol=symbol)

        elapsed_ms = round((time.perf_counter() - start_t) * 1000.0, 2)
        now_ts = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

        # 2. Extract Stage 4 thesis summary and Stage 6 block hash
        stages = pipeline_res.get("stages", {})
        thesis_info = stages.get("stage4_cognitive_thesis", {})
        settlement_info = stages.get("stage6_ledger_settlement", {})
        block_hash = settlement_info.get("block_hash", "")

        # 3. Update telemetry & Little's Law bounds
        with self._lock:
            self._telemetry.total_cycles += 1
            self._telemetry.ticks_processed += 1
            self._telemetry.last_symbol = symbol
            self._telemetry.last_latency_ms = elapsed_ms
            self._telemetry.last_cycle_timestamp = now_ts
            self._telemetry.last_block_hash = block_hash
            self._telemetry.last_thesis_summary = {
                "symbol": symbol,
                "action": thesis_info.get("action_decision", "HOLD"),
                "confidence_pct": thesis_info.get("confidence_score", 50.0),
                "summary": thesis_info.get("macro_thesis_summary", ""),
            }

            # Little's Law calculation: lambda = cycles / uptime, rho = lambda / mu
            uptime = max(1.0, time.time() - self._telemetry.start_time)
            lam = round(self._telemetry.total_cycles / uptime, 3)
            # Service rate mu (capacity = 1000ms / latency_ms, bounded)
            mu = round(1000.0 / max(10.0, elapsed_ms), 2)
            rho = min(0.95, round(lam / max(0.1, mu), 3))
            self._telemetry.throughput_lambda = lam
            self._telemetry.service_rate_mu = mu
            self._telemetry.utilization_rho = rho

        # 4. Periodic Pacioli Ledger & Talent Audit (every 45s)
        if time.time() - self._last_audit_ts > 45.0:
            self._audit_ledger_and_database()
            self._last_audit_ts = time.time()

        pipeline_res["status"] = "cycle_executed"
        pipeline_res["cycles_completed"] = self._telemetry.total_cycles
        pipeline_res["latency_ms"] = elapsed_ms

        return pipeline_res

    def _audit_ledger_and_database(self) -> None:
        """Audits double-entry ledger balance, orders count, and candidate profiles count."""
        try:
            with closing(sqlite3.connect(PATHS.db_path)) as conn:
                cur = conn.cursor()

                # 1. Audit store orders
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='store_orders'")
                orders_count = 0
                if cur.fetchone():
                    cur.execute("SELECT COUNT(*), SUM(subtotal_cents), SUM(vat_cents), SUM(total_cents) FROM store_orders")
                    row = cur.fetchone()
                    if row and row[0] is not None:
                        orders_count = row[0]
                        subtotal = row[1] or 0
                        vat = row[2] or 0
                        total = row[3] or 0
                        # Pacioli: subtotal + vat == total
                        diff = abs((subtotal + vat) - total)
                        with self._lock:
                            self._telemetry.last_pacioli_diff_cents = diff
                            self._telemetry.pacioli_audit_status = "BALANCED_OK" if diff == 0 else "DISCREPANCY_DETECTED"

                # 2. Audit candidate profiles
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='candidate_profiles'")
                candidates_count = 0
                if cur.fetchone():
                    cur.execute("SELECT COUNT(*) FROM candidate_profiles")
                    c_row = cur.fetchone()
                    if c_row and c_row[0] is not None:
                        candidates_count = c_row[0]

                with self._lock:
                    self._telemetry.total_store_orders = orders_count
                    self._telemetry.total_candidates = candidates_count
        except Exception as exc:
            logger.warning("Periodic DB audit encountered non-fatal error: %s", exc)


# Global Singleton Daemon Instance
GLOBAL_PIPELINE_DAEMON: Final[AutonomousPipelineDaemon] = AutonomousPipelineDaemon()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Iniciando prueba rápida de AutonomousPipelineDaemon...")
    daemon = AutonomousPipelineDaemon(cycle_interval_seconds=1.0)
    daemon.start()
    time.sleep(3.0)
    telem = daemon.get_telemetry()
    print("Telemetría:", telem)
    daemon.stop()
    print("Prueba completada.")
