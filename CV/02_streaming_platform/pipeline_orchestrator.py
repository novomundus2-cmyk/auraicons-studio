"""
===============================================================================
MODULE: pipeline_orchestrator.py
LOCATION: 02_streaming_platform/pipeline_orchestrator.py
PURPOSE: Clean-Code Pythonista End-to-End Pipeline Orchestrator.
         Executes all 6 pipeline stages deterministically and writes results
         directly into `04_database_lakehouse/financial_lakehouse.db` and
         `05_archify_visualizer/live_data_bridge.js`:
           Stage 1 -> Apache NiFi Edge Gatekeeper (FlowFile & Backpressure)
           Stage 2 -> Kafka KRaft Partitioner (Key Hash & Little's Law M/M/c)
           Stage 3 -> Stateful Window & Watermark Processor (Anti-Skew Salting)
           Stage 4 -> Algebraic Welford Monoid & Robust MAD Anomaly Engine
           Stage 5 -> Lakehouse ACID Sink (`streaming_window_sinks`)
           Stage 6 -> Multi-AI Insights Connector (`ai_insights_registry`)
AUTHOR: Senior Data Platform & Deployment Engineering Portfolio
===============================================================================
"""

from __future__ import annotations

import hashlib
import sqlite3
import sys
from contextlib import closing
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

import numpy as np

STREAM_DIR: Final[Path] = Path(__file__).resolve().parent
CV_ROOT: Final[Path] = STREAM_DIR.parent
MATH_DIR: Final[Path] = CV_ROOT / "03_math_haskell_python"
DB_DIR: Final[Path] = CV_ROOT / "04_database_lakehouse"

for folder in (MATH_DIR, DB_DIR):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

from build_database import PATHS, export_categorized_folders_and_bridge  # noqa: E402
from scientific_analytics import (  # noqa: E402
    StatsMonoid,
    compute_classic_and_robust_z,
    littles_law_metrics,
    shannon_entropy_bits,
)

NIFI_MAX_QUEUE_OBJECTS: Final[int] = 10_000
KAFKA_PARTITIONS: Final[int] = 8
SPARK_CORE_CAPACITY_MU: Final[float] = 6_500.0


@dataclass(frozen=True, slots=True)
class FlowFileEvent:
    """Immutable representation of a NiFi FlowFile -> Kafka Record."""

    transaction_id: str
    user_id: str
    merchant_id: str
    category: str
    amount_eur: float
    event_timestamp: str
    kafka_partition: int


def deterministic_partition(key: str, num_partitions: int = KAFKA_PARTITIONS) -> int:
    """Deterministic hash partitioning (mirrors Kafka's murmur2 modulo P)."""
    digest = hashlib.blake2b(key.encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(digest, "big") % num_partitions


def run_interconnected_pipeline(batch_size: int = 2_400, simulated_lambda: float = 36_000.0) -> None:
    """Executes a complete 6-stage micro-batch cycle across the platform."""
    if not PATHS.db_path.exists():
        raise FileNotFoundError(f"Database not found at {PATHS.db_path}. Run `make db` first.")

    rng = np.random.default_rng(int(datetime.now(tz=UTC).timestamp()) % 100_000)

    with closing(sqlite3.connect(PATHS.db_path)) as conn, conn:
        # ---------------------------------------------------------------------
        # STAGE 1: APACHE NIFI EDGE INGESTION & BACKPRESSURE CHECK
        # ---------------------------------------------------------------------
        users = [r[0] for r in conn.execute("SELECT user_id FROM dim_users").fetchall()]
        merchants = conn.execute("SELECT merchant_id, category FROM dim_merchants").fetchall()

        queue_depth = min(batch_size, NIFI_MAX_QUEUE_OBJECTS)
        backpressure_state = "BACKPRESSURE_PAUSE" if queue_depth >= NIFI_MAX_QUEUE_OBJECTS else "ACTIVE_FLOW"

        # ---------------------------------------------------------------------
        # STAGE 2: KAFKA KRAFT PARTITIONING & M/M/c CAPACITY VALIDATION
        # ---------------------------------------------------------------------
        queue_report = littles_law_metrics(
            arrival_rate_lambda=simulated_lambda,
            cores_c=KAFKA_PARTITIONS,
            service_rate_mu=SPARK_CORE_CAPACITY_MU,
        )

        now_iso = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:00Z")
        events: list[FlowFileEvent] = []
        for i in range(batch_size):
            u_id = str(rng.choice(users))
            m_id, cat = merchants[int(rng.integers(0, len(merchants)))]
            is_spike = rng.random() < 0.008
            amt = float(rng.uniform(3800.0, 11500.0) if is_spike else rng.lognormal(4.15, 0.70))
            events.append(
                FlowFileEvent(
                    transaction_id=f"live_txn_{i:05d}",
                    user_id=u_id,
                    merchant_id=m_id,
                    category=cat,
                    amount_eur=round(amt, 2),
                    event_timestamp=now_iso,
                    kafka_partition=deterministic_partition(u_id),
                )
            )

        # ---------------------------------------------------------------------
        # STAGE 3 & 4: STATEFUL WINDOWING, SHANNON ENTROPY & WELFORD/MAD ENGINE
        # ---------------------------------------------------------------------
        partition_keys = np.array([e.kafka_partition for e in events], dtype=np.int64)
        partition_entropy = shannon_entropy_bits(partition_keys)

        global_monoid = StatsMonoid()
        categories = sorted({e.category for e in events})
        sink_rows: list[tuple] = []

        for cat in categories:
            cat_amounts = np.array([e.amount_eur for e in events if e.category == cat], dtype=np.float64)
            scores = compute_classic_and_robust_z(cat_amounts)
            # Combine partition monoid into global cluster monoid using associative `+` (`<>`)
            global_monoid = global_monoid + scores.welford_monoid

            sink_rows.append(
                (
                    now_iso,
                    now_iso,
                    cat,
                    scores.welford_monoid.count,
                    round(float(np.sum(cat_amounts)), 2),
                    round(scores.welford_monoid.mean, 2),
                    int(np.sum(scores.is_fraud)),
                    now_iso,
                )
            )

        # ---------------------------------------------------------------------
        # STAGE 5 & 6: LAKEHOUSE ACID SINK & LIVE BRIDGE REFRESH
        # ---------------------------------------------------------------------
        conn.executemany(
            "INSERT INTO streaming_window_sinks VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            sink_rows,
        )
        export_categorized_folders_and_bridge(conn)

    print("==================================================================")
    print("⚡ PIPELINE END-TO-END EJECUTADO Y SINCRONIZADO CON ÉXITO")
    print("==================================================================")
    print(f"  [Etapa 1 · NiFi Edge]       FlowFiles: {batch_size:,} | Estado: {backpressure_state}")
    print(
        f"  [Etapa 2 · Kafka KRaft]     Particiones: {KAFKA_PARTITIONS} | "
        f"Utilización ρ: {queue_report.utilization_rho * 100:.1f}% | "
        f"Ráfaga Poisson 99.99%: {queue_report.poisson_burst_9999:,} msg/s"
    )
    print(
        f"  [Etapa 3 · Spark Window]    Entropía de Particionado H(X): {partition_entropy:.3f} bits (máx 3.000)"
    )
    print(
        f"  [Etapa 4 · Welford Monoid]  Conteo Total: {global_monoid.count:,} | "
        f"Media Global: {global_monoid.mean:.2f} € | σ Global: {global_monoid.std_dev:.2f} €"
    )
    print(f"  [Etapa 5 · Lakehouse Sink]  {len(sink_rows)} ventanas escritas en `streaming_window_sinks`")
    print(f"  [Etapa 6 · Archify Bridge]  Datos en vivo actualizados en `{PATHS.archify_bridge_js.name}`")


if __name__ == "__main__":
    run_interconnected_pipeline()
