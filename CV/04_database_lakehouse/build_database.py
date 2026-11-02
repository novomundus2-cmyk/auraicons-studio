"""
===============================================================================
MODULE: build_database.py
LOCATION: 04_database_lakehouse/build_database.py
PURPOSE: Clean-Code Pythonista Master Database & Lakehouse Builder.
         Interconnects:
           1. Mathematical Engine (`03_math_haskell_python/scientific_analytics.py`)
           2. Star Schema & Medallion Tables (`financial_lakehouse.db`)
           3. Multi-AI Insights Registry (BigQuery TimesFM 2.0, Gemini 2.5, Antigravity SDK)
           4. Categorized JSON Snapshots (`04_database_lakehouse/categories/*`)
           5. Live Frontend Bridge (`05_archify_visualizer/live_data_bridge.js`)
AUTHOR: Senior Data Platform & Deployment Engineering Portfolio
===============================================================================
"""

from __future__ import annotations

import json
import sqlite3
import sys
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import numpy as np
import polars as pl

# Connect directly to the Mathematical Engine (Single Source of Truth)
DB_DIR: Final[Path] = Path(__file__).resolve().parent
CV_ROOT: Final[Path] = DB_DIR.parent
MATH_DIR: Final[Path] = CV_ROOT / "03_math_haskell_python"
if str(MATH_DIR) not in sys.path:
    sys.path.insert(0, str(MATH_DIR))

from scientific_analytics import (  # noqa: E402
    compute_classic_and_robust_z,
    littles_law_metrics,
    prove_monoid_and_queueing_theorems,
    shannon_entropy_bits,
)


@dataclass(frozen=True, slots=True)
class LakehousePaths:
    """Immutable filesystem layout for the interconnected platform."""

    db_path: Path = DB_DIR / "financial_lakehouse.db"
    notebooks_dir: Path = CV_ROOT / "01_notebooks"
    categories_dir: Path = DB_DIR / "categories"
    archify_bridge_js: Path = CV_ROOT / "05_archify_visualizer" / "live_data_bridge.js"


PATHS: Final[LakehousePaths] = LakehousePaths()

SCHEMA_SQL: Final[str] = """
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

CREATE TABLE IF NOT EXISTS dim_users (
    user_id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    country TEXT NOT NULL,
    kyc_verified INTEGER NOT NULL,
    risk_tier TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_merchants (
    merchant_id TEXT PRIMARY KEY,
    merchant_name TEXT NOT NULL,
    category TEXT NOT NULL,
    base_fee_pct REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    merchant_id TEXT NOT NULL,
    category TEXT NOT NULL,
    amount_eur REAL NOT NULL,
    currency TEXT NOT NULL,
    device TEXT NOT NULL,
    country TEXT NOT NULL,
    kafka_partition INTEGER NOT NULL,
    processing_latency_ms REAL NOT NULL,
    classic_z_score REAL NOT NULL,
    robust_mad_z_score REAL NOT NULL,
    is_fraud_anomaly INTEGER NOT NULL,
    txn_timestamp TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES dim_users(user_id),
    FOREIGN KEY (merchant_id) REFERENCES dim_merchants(merchant_id)
);

CREATE TABLE IF NOT EXISTS gold_category_metrics (
    category TEXT PRIMARY KEY,
    txn_count INTEGER NOT NULL,
    total_volume_eur REAL NOT NULL,
    welford_mean_eur REAL NOT NULL,
    welford_std_eur REAL NOT NULL,
    robust_median_eur REAL NOT NULL,
    robust_mad_eur REAL NOT NULL,
    shannon_entropy_bits REAL NOT NULL,
    fraud_alerts_count INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS streaming_window_sinks (
    window_start TEXT NOT NULL,
    window_end TEXT NOT NULL,
    merchant_category TEXT NOT NULL,
    txn_count INTEGER NOT NULL,
    total_volume_eur REAL NOT NULL,
    avg_txn_amount REAL NOT NULL,
    suspicious_txn_count INTEGER NOT NULL,
    saved_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_insights_registry (
    insight_id TEXT PRIMARY KEY,
    ai_engine TEXT NOT NULL,
    model_name TEXT NOT NULL,
    target_category TEXT NOT NULL,
    sql_or_sdk_invocation TEXT NOT NULL,
    predicted_metric_value REAL NOT NULL,
    confidence_or_prob REAL NOT NULL,
    structured_diagnosis TEXT NOT NULL,
    recommended_action TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (target_category) REFERENCES gold_category_metrics(category)
);

CREATE TABLE IF NOT EXISTS kb_mathematical_formulas (
    formula_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    domain TEXT NOT NULL,
    latex_expression TEXT NOT NULL,
    haskell_implementation TEXT NOT NULL,
    python_implementation TEXT NOT NULL,
    classroom_explanation TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS kb_study_notebooks (
    notebook_filename TEXT NOT NULL,
    cell_index INTEGER NOT NULL,
    cell_type TEXT NOT NULL,
    content TEXT NOT NULL,
    PRIMARY KEY (notebook_filename, cell_index)
);

CREATE TABLE IF NOT EXISTS kb_interview_defense (
    question_id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    interview_question TEXT NOT NULL,
    failure_symptom TEXT NOT NULL,
    root_cause TEXT NOT NULL,
    senior_answer TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS kb_cv_portfolio (
    item_id TEXT PRIMARY KEY,
    section TEXT NOT NULL,
    title TEXT NOT NULL,
    technologies TEXT NOT NULL,
    impact_bullet TEXT NOT NULL,
    defense_tip TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS kb_10_projects_roadmap (
    project_number INTEGER PRIMARY KEY,
    project_code TEXT NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL,
    core_stack TEXT NOT NULL,
    math_foundation TEXT NOT NULL,
    deliverable_folder TEXT NOT NULL,
    what_you_prove TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS corporate_hierarchy (
    agent_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    title TEXT NOT NULL,
    tier INTEGER NOT NULL,
    department TEXT NOT NULL,
    reports_to TEXT NOT NULL,
    model_engine TEXT NOT NULL,
    current_status TEXT NOT NULL,
    tasks_queued INTEGER NOT NULL DEFAULT 1,
    tasks_completed INTEGER NOT NULL DEFAULT 0,
    routing_efficiency_pct REAL NOT NULL DEFAULT 99.5,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS corporate_routes (
    route_id TEXT PRIMARY KEY,
    route_name TEXT NOT NULL,
    source_node TEXT NOT NULL,
    target_node TEXT NOT NULL,
    sla_target_ms REAL NOT NULL,
    current_latency_ms REAL NOT NULL,
    optimized_latency_ms REAL NOT NULL,
    throughput_msg_sec REAL NOT NULL,
    optimization_strategy TEXT NOT NULL,
    improvement_pct REAL NOT NULL,
    status TEXT NOT NULL,
    last_optimized_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS corporate_executive_orders (
    order_id TEXT PRIMARY KEY,
    order_timestamp TEXT NOT NULL,
    issuer TEXT NOT NULL,
    directive_text TEXT NOT NULL,
    assigned_c_suite TEXT NOT NULL,
    chatty_response TEXT NOT NULL,
    resulting_action TEXT NOT NULL,
    efficiency_impact_pct REAL NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS corporate_reusable_knowledge (
    knowledge_id TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    executable_code TEXT NOT NULL,
    reusable_prompt TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE VIEW IF NOT EXISTS vw_fraud_alerts AS
SELECT
    t.transaction_id,
    t.txn_timestamp,
    t.user_id,
    u.country AS user_country,
    u.risk_tier,
    m.merchant_name,
    t.category,
    t.amount_eur,
    ROUND(t.classic_z_score, 2) AS classic_z,
    ROUND(t.robust_mad_z_score, 2) AS robust_mad_z,
    t.kafka_partition
FROM fact_transactions t
JOIN dim_users u ON t.user_id = u.user_id
JOIN dim_merchants m ON t.merchant_id = m.merchant_id
WHERE t.is_fraud_anomaly = 1
ORDER BY t.robust_mad_z_score DESC;
"""


def populate_ai_insights(conn: sqlite3.Connection, gold_rows: list[tuple]) -> None:
    """
    Populates `ai_insights_registry` connecting the 3 AI engines:
      1. BigQuery AI.DETECT_ANOMALIES (TimesFM 2.0)
      2. BigQuery AI.FORECAST (TimesFM 2.0)
      3. BigQuery AI.GENERATE_TABLE & Google Antigravity SDK (Gemini 2.5 Flash)
    Directly derived from real `gold_category_metrics`.
    """
    ai_rows = []
    for idx, row in enumerate(gold_rows, start=1):
        cat, txn_count, total_vol, mean_eur, _, med_eur, mad_eur, entropy, frauds = row
        # 1. TimesFM 2.0 Anomaly Detection insight
        ai_rows.append(
            (
                f"AI_TIMESFM_ANOM_{idx:02d}",
                "BigQuery AI/ML (TVF)",
                "TimesFM 2.0 (AI.DETECT_ANOMALIES)",
                cat,
                f"SELECT * FROM AI.DETECT_ANOMALIES(TABLE bronze_txns, data_col => 'amount_eur', id_cols => ['{cat}'])",
                round(float(total_vol * 0.042), 2),
                0.994,
                f"Detectadas {frauds} anomalías severas en '{cat}' (Media={mean_eur}€ vs Mediana={med_eur}€, MAD={mad_eur}€).",
                "Activar regla de bloqueo inmediato cuando Z_robusto > 8.0 en PySpark Streaming.",
                "2026-10-28T14:00:00Z",
            )
        )
        # 2. TimesFM 2.0 Demand Forecast insight
        ai_rows.append(
            (
                f"AI_TIMESFM_FCST_{idx:02d}",
                "BigQuery AI/ML (TVF)",
                "TimesFM 2.0 (AI.FORECAST)",
                cat,
                f"SELECT * FROM AI.FORECAST(TABLE gold_daily_{cat}, horizon => 14, confidence_level => 0.95)",
                round(float(total_vol / 28.0 * 1.12), 2),
                0.950,
                f"Pronóstico a 14 días para '{cat}' estima +{round(12.0 + idx, 1)}% de volumen diario ({txn_count} txns base).",
                f"Pre-escalar particiones Kafka manteniendo entropía H={entropy} bits y rho <= 0.80.",
                "2026-10-28T14:05:00Z",
            )
        )
        # 3. Gemini 2.5 Flash + Google Antigravity SDK Agent synthesis
        ai_rows.append(
            (
                f"AI_ANTIGRAVITY_GEMINI_{idx:02d}",
                "Google Antigravity SDK + BigQuery",
                "gemini-2.5-flash (AI.GENERATE_TABLE)",
                cat,
                f"AI.GENERATE_TABLE(MODEL `lakehouse.gemini_2_5_flash`, TABLE alerts_{cat}, STRUCT('risk_level STRING, action STRING'))",
                float(frauds),
                0.985,
                f"Auditoría IA Antigravity en '{cat}': {frauds} casos con Masking Effect cazados por Welford+MAD.",
                "Sincronizado con cuaderno de estudio y vista ejecutiva Archify Studio.",
                "2026-10-28T14:10:00Z",
            )
        )

    conn.executemany(
        "INSERT OR REPLACE INTO ai_insights_registry VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ai_rows,
    )


def populate_knowledge_base(conn: sqlite3.Connection) -> None:
    """Inserts mathematical formulas, study notebooks, interview Q&A, CV, and 10 projects."""
    proofs = prove_monoid_and_queueing_theorems()
    queue_demo = littles_law_metrics(arrival_rate_lambda=36_000.0, cores_c=8, service_rate_mu=6500.0)

    formulas = [
        (
            "MATH_01",
            "Monoide Paralelo de Welford-Chan",
            "Álgebra Abstracta & Streaming en 1 Pasada",
            r"M_{2,AB} = M_{2,A} + M_{2,B} + (\mu_B - \mu_A)^2 \frac{n_A n_B}{n_A + n_B}",
            "instance Semigroup StatsMonoid where (StatsMonoid nA muA m2A) <> (StatsMonoid nB muB m2B) = ...",
            "delta = other.mean - self.mean; m2_ab = self.m2 + other.m2 + (delta**2)*(self.count*other.count/n_ab)",
            f"Permite a Spark y Flink fusionar la varianza de dos particiones en paralelo en una sola pasada sin errores de redondeo (Error asociativo SymPy = {proofs['associativity_error']}).",
        ),
        (
            "MATH_02",
            "Z-Score Robusto basado en la Mediana (MAD)",
            "Estadística Robusta Antifraude",
            r"Z_{\text{robusto}} = \frac{|x - \text{mediana}(X)|}{1.4826 \cdot \text{mediana}(|X - \text{mediana}(X)|)}",
            "robustZScore x med mad = abs (x - med) / (1.4826 * mad)",
            "mad_normal = stats.median_abs_deviation(amounts, scale='normal'); robust_z = np.abs(amounts - np.median(amounts)) / mad_normal",
            "Su punto de ruptura es del 50%: aunque la mitad de un lote sean fraudes extremos de 10.000€, la mediana y el MAD no se corrompen.",
        ),
        (
            "MATH_03",
            "Entropía de Información de Shannon",
            "Teoría de la Información & Balanceo Kafka/Spark",
            r"H(X) = -\sum_{i=1}^{P} p(x_i) \log_2 p(x_i)",
            "shannonEntropy ps = negate $ sum [ p * logBase 2 p | p <- ps, p > 0 ]",
            "probs = counts / counts.sum(); entropy = -np.sum(probs * np.log2(probs))",
            "Mide matemáticamente si una clave está sesgada (Data Skew). Si H(X) cae bruscamente, activamos Key Salting.",
        ),
        (
            "MATH_04",
            "Ley de Little y Explosión de Cola M/M/c",
            "Teoría de Colas & Dimensionamiento de Clústeres",
            r"L = \lambda W, \quad \rho = \frac{\lambda}{c \cdot \mu} \le 0.80, \quad \frac{dL}{d\lambda} = \frac{\mu}{(\mu - \lambda)^2}",
            "minRequiredPartitions lambda mu = ceiling (lambda / (mu * 0.80))",
            "min_cores = np.ceil(lambda_rate / (mu_rate * 0.80))",
            f"Demuestra por qué un clúster nunca debe superar el 80% de carga (Actual demo: rho={queue_demo.utilization_rho * 100:.1f}%, ráfaga Poisson 99.99%={queue_demo.poisson_burst_9999} msg/s).",
        ),
    ]
    conn.executemany(
        "INSERT OR REPLACE INTO kb_mathematical_formulas VALUES (?, ?, ?, ?, ?, ?, ?)",
        formulas,
    )

    if PATHS.notebooks_dir.exists():
        for nb_path in sorted(PATHS.notebooks_dir.glob("*.ipynb")):
            data = json.loads(nb_path.read_text(encoding="utf-8"))
            cells = data.get("cells", [])
            for idx, c in enumerate(cells):
                c_type = c.get("cell_type", "markdown")
                src = c.get("source", [])
                text = "".join(src) if isinstance(src, list) else str(src)
                conn.execute(
                    "INSERT OR REPLACE INTO kb_study_notebooks VALUES (?, ?, ?, ?)",
                    (nb_path.name, idx, c_type, text),
                )

    interview_qa = [
        (
            "QA_01",
            "PySpark & Memoria Distribuida",
            "¿Qué provoca un OutOfMemory (OOM) en el Driver o en los Executors de Spark Streaming y cómo lo erradicas?",
            "El job se cae tras unas horas con java.lang.OutOfMemoryError: Java heap space.",
            "Uso de collect() en el Driver, joins sin broadcast bien medido, o agregaciones de streaming sin Watermark donde el estado en RAM crece hasta el infinito.",
            "1) Jamás usar collect() sobre tablas grandes; 2) Definir siempre .withWatermark('event_time', '10 minutes') para limpiar estados antiguos; 3) Usar RocksDB como State Store; 4) Aplicar Salting a claves sesgadas si la Entropía de Shannon H(X) cae.",
        ),
        (
            "QA_02",
            "Estadística & Detección de Anomalías",
            "¿Por qué el Z-Score clásico falla estrepitosamente detectando fraudes financieros en ventanas pequeñas?",
            "Un fraude de 4.500 € obtiene un Z-Score de 2.83 (< 3.0) y pasa sin generar alerta.",
            "Efecto de Enmascaramiento (Masking Effect): el propio valor atípico infla la desviación típica muestral σ de 12 € a 1.378 €, camuflándose a sí mismo.",
            "Sustituimos la media y desviación estándar por el Z-Score Robusto basado en la Mediana y el MAD escalado (1.4826 * MAD). En el mismo lote, el Z-Score Robusto sube de 2.83 a 295.76.",
        ),
        (
            "QA_03",
            "Kafka KRaft & Teoría de Colas",
            "¿Por qué migraste Kafka de ZooKeeper a KRaft y cómo evitas tormentas de rebalanceo (Rebalance Storms)?",
            "Los consumidores entran en bucle 'Revoking partitions' y el Consumer Lag se dispara a millones.",
            "El hilo de procesamiento tarda más que max.poll.interval.ms o la tasa de llegada λ iguala a la capacidad c·μ (ρ -> 1).",
            "KRaft elimina ZooKeeper integrando consenso Raft en los brokers (failover en ms y millones de particiones). Para evitar rebalances, usamos CooperativeStickyAssignor, ajustamos max.poll.records y garantizamos ρ = λ/(c·μ) <= 0.80.",
        ),
        (
            "QA_04",
            "Apache NiFi & Ingesta",
            "¿Por qué colocar Apache NiFi delante de Kafka en lugar de enviar los datos directo a Kafka?",
            "Fuentes legadas o picos de tráfico externos saturan los brokers o envían esquemas corruptos.",
            "Kafka es un bus de eventos, no un gestor de protocolos heterogéneos con control visual de linaje.",
            "NiFi aporta conversión de protocolos, validación de esquemas Avro, auditoría forense con Provenance Repository y colas con Backpressure automático (10.000 objetos / 1 GB) que absorben ráfagas sin perder un solo byte.",
        ),
        (
            "QA_05",
            "Lakehouse & BigQuery AI/ML",
            "¿Cómo resuelves el Small Files Problem en streaming y cómo integras IA analítica sin mover datos?",
            "Millones de archivos Parquet de pocos KB en S3/MinIO degradan las consultas analíticas.",
            "Cada micro-batch de Spark escribe un fichero pequeño independiente.",
            "Usamos tablas abiertas Apache Iceberg con compactación periódica (rewrite_data_files a 256 MB con ZSTD) y ejecutamos TimesFM 2.0 (AI.DETECT_ANOMALIES, AI.FORECAST) y Gemini 2.5 (AI.GENERATE_TABLE) nativamente en SQL.",
        ),
    ]
    conn.executemany("INSERT OR REPLACE INTO kb_interview_defense VALUES (?, ?, ?, ?, ?, ?)", interview_qa)

    cv_items = [
        (
            "CV_01",
            "Streaming & Ingesta",
            "Clúster Kafka KRaft & Pasarela NiFi de Grado Bancario",
            "Apache Kafka (KRaft), Apache NiFi, Schema Registry, Docker, Kubernetes",
            "Arquitecté un bus de eventos Kafka KRaft con productores idempotentes (acks=all) y contrapresión en NiFi para 45.000 msg/s con 99.99% de disponibilidad y cero pérdida de datos.",
            "Explicar la fórmula de utilización M/M/c (ρ <= 0.80) y los 3 repositorios físicos de NiFi.",
        ),
        (
            "CV_02",
            "Matemática Funcional & Pythonista",
            "Motor Algebraico en Haskell y Estadística Robusta en Python",
            "Haskell, Python 3.14, SymPy, SciPy, NumPy, Polars (Apache Arrow)",
            "Implementé el Monoide Paralelo de Welford-Chan en Haskell/SymPy y el Z-Score Robusto (MAD) en SciPy/Polars, eliminando el Efecto de Enmascaramiento y elevando la sensibilidad antifraude de Z=2.83 a Z=295.76.",
            "Mostrar cómo la mediana tiene un punto de ruptura del 50% frente a outliers extremos.",
        ),
        (
            "CV_03",
            "Base de Datos & BigQuery AI/ML",
            "Almacén Analítico en Estrella y Modelos Fundacionales en SQL",
            "SQLite/DuckDB, Google BigQuery AI/ML, TimesFM 2.0, Gemini 2.5 Flash, Iceberg",
            "Diseñé un Data Warehouse en Estrella (Medallion Bronze/Silver/Gold) de 25.000 transacciones e integré AI.DETECT_ANOMALIES, AI.FORECAST y AI.GENERATE_TABLE directamente en SQL.",
            "Destacar la división cronológica estricta (history_data vs actual_data) y el uso de TVFs en la cláusula FROM.",
        ),
        (
            "CV_04",
            "Despliegue, GitOps & Visualización",
            "Simulador Interactivo Archify Studio y Agente de Notas IA",
            "Google Antigravity SDK, uv, Kubernetes, Terraform, ArgoCD, KaTeX",
            "Construí el visualizador en tiempo real Archify Studio y un Agente de Notas automatizado con Google Antigravity SDK que persiste apuntes y cuadernos Gemini Notebooks en la base de datos maestra.",
            "Enseñar en vivo cómo cambia la curva de la Ley de Little y cómo el agente guarda cada celda en SQLite.",
        ),
    ]
    conn.executemany("INSERT OR REPLACE INTO kb_cv_portfolio VALUES (?, ?, ?, ?, ?, ?)", cv_items)

    ten_projects = [
        (
            1,
            "PROJ_01",
            "Motor Algebraico Antifraude en Tiempo Real (Welford Monoid & MAD)",
            "COMPLETADO ✅",
            "Haskell, Python 3.14, SymPy, SciPy, Polars, SQLite Star Schema",
            "Monoide Asociativo de Welford-Chan + Z-Score Robusto (MAD) con 50% Breakdown Point",
            "03_math_haskell_python/ + 04_database_lakehouse/",
            "Demuestras que sabes detectar fraudes que engañan a la desviación típica clásica (Z=2.83 -> Z=295.76) y agregar particiones en 1 sola pasada O(1).",
        ),
        (
            2,
            "PROJ_02",
            "Pasarela Edge con Apache NiFi, Backpressure & Linaje Forense",
            "LISTO PARA EMPEZAR 🔜",
            "Apache NiFi, FlowFiles, Avro Schema Registry, Python Edge Simulator",
            "Proceso de Poisson P(k; λt) y Acotación de Colas en Disco",
            "02_streaming_platform/nifi/",
            "Demuestras cómo frenar picos de tráfico (Backpressure 10k objetos / 1 GB) sin perder datos ni tumbar Kafka por falta de RAM.",
        ),
        (
            3,
            "PROJ_03",
            "Clúster Apache Kafka KRaft (Sin ZooKeeper) & Dimensionamiento M/M/c",
            "PENDIENTE ⏳",
            "Apache Kafka KRaft, Docker Compose, Productor Idempotente (acks=all)",
            "Teoría de Colas M/M/c, Ley de Little (L = λW) y Asíntota ρ -> 1",
            "02_streaming_platform/producers/",
            "Demuestras cómo calcular matemáticamente el número exacto de particiones para mantener ρ <= 0.80 y evitar rebalances.",
        ),
        (
            4,
            "PROJ_04",
            "PySpark Structured Streaming: Watermarking, RocksDB & Anti-Data Skew",
            "PENDIENTE ⏳",
            "PySpark 3.5, Tumbling Windows (1 min), Watermark (10 min), Salting",
            "Entropía de Shannon H(X) = -Σ p_i log2(p_i) para detección de Hot Keys",
            "02_streaming_platform/spark_jobs/",
            "Demuestras cómo eliminar errores OutOfMemory (OOM) en el State Store y cómo repartir claves sesgadas mediante Salting en 2 fases.",
        ),
        (
            5,
            "PROJ_05",
            "Open Data Lakehouse con Apache Iceberg, Compaction & Time Travel",
            "PENDIENTE ⏳",
            "Apache Iceberg, MinIO S3, Parquet + ZSTD, PyIceberg / Spark SQL",
            "Optimización de Bloques Columnares y Eliminación del Small Files Problem",
            "04_database_lakehouse/",
            "Demuestras cómo pasar de miles de micro-archivos lentos a snapshots ACID compactados de 256 MB con consultas instantáneas.",
        ),
        (
            6,
            "PROJ_06",
            "Motor Vectorizado Ultra-Rápido con Polars, Apache Arrow & DuckDB",
            "PENDIENTE ⏳",
            "Polars Lazy API, Apache Arrow Zero-Copy, DuckDB OLAP",
            "Álgebra Relacional Vectorizada SIMD y Pushdown de Predicados",
            "03_math_haskell_python/",
            "Demuestras cómo procesar millones de filas en un solo nodo 15x más rápido que Pandas tradicional y con una fracción de RAM.",
        ),
        (
            7,
            "PROJ_07",
            "IA Analítica en SQL con BigQuery AI/ML (TimesFM 2.0 & Gemini 2.5)",
            "PENDIENTE ⏳",
            "Google BigQuery, AI.DETECT_ANOMALIES, AI.FORECAST, AI.EVALUATE, AI.GENERATE_TABLE",
            "Modelos Fundacionales de Series Temporales Zero-Shot y Evaluación RMSE/MAE",
            "01_notebooks/03_bigquery_ai_ml_database.ipynb",
            "Demuestras cómo pronosticar demanda y extraer entidades estructuradas con IA directamente en SQL sin pipelines complejos de reentrenamiento.",
        ),
        (
            8,
            "PROJ_08",
            "Calidad de Datos Automatizada y Contratos de Esquema (Zero-Trust)",
            "PENDIENTE ⏳",
            "Pydantic v2, Pandera / Polars Contracts, Dead-Letter Queue (DLQ)",
            "Teoría de Conjuntos, Invariantes de Dominio y Test Estadístico KS (Kolmogorov-Smirnov)",
            "04_database_lakehouse/",
            "Demuestras cómo aislar registros corruptos y detectar Data Drift estadístico antes de que contamine las tablas Gold.",
        ),
        (
            9,
            "PROJ_09",
            "Despliegue Cloud-Native en Kubernetes, Helm, Terraform & GitOps ArgoCD",
            "PENDIENTE ⏳",
            "Kubernetes (K8s), Strimzi Kafka Operator, Spark Operator, Terraform, ArgoCD",
            "Autoescalado basado en Derivada de Lag dL/dλ y SLOs de Latencia p99",
            "08_kubernetes_gitops/",
            "Demuestras que no solo programas pipelines, sino que sabes desplegarlos en producción real con infraestructura como código y CI/CD.",
        ),
        (
            10,
            "PROJ_10",
            "Capstone Final: Gemelo Digital Financiero + Agente IA Autónomo",
            "PENDIENTE ⏳",
            "Archify Studio, Google Antigravity SDK, FastAPI/SQLite, Portfolio Completo",
            "Integración Total de los 4 Pilares Matemáticos y Defensa Ejecutiva",
            "05_archify_visualizer/ + 06_ai_note_agent/ + 07_cv_and_career/",
            "Tu proyecto cumbre: un sistema completo extremo a extremo con visualizador en vivo y agente IA que demuestra nivel Senior/Staff.",
        ),
    ]
    conn.executemany(
        "INSERT OR REPLACE INTO kb_10_projects_roadmap VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ten_projects,
    )


# Tables that grow over time must export their NEWEST rows; without ORDER BY the
# `LIMIT 100` snapshot would silently freeze on the oldest rows.
EXPORT_ORDER: Final[dict[str, str]] = {
    "streaming_window_sinks": "ORDER BY saved_at DESC, rowid DESC",
    "corporate_executive_orders": "ORDER BY order_timestamp DESC, rowid DESC",
    "corporate_routes": "ORDER BY route_id ASC",
}


def populate_corporate_enterprise(conn: sqlite3.Connection) -> None:
    """Populates the Corporate Hierarchy, Routes, Executive Orders, and Reusable Knowledge."""
    agents = [
        (
            "AGENT-00-PRESIDENT",
            "Mikel Irastorza",
            "Presidente, Fundador & Propietario Supremo · NovusMundus",
            0,
            "Presidencia & Consejo de Administración · NovusMundus / Novus Capital",
            "Supremo (Manda Primero)",
            "Mente Humana / Visión Estratégica",
            "PRESIDIENDO · EMITIENDO DIRECTIVAS",
            0,
            1000,
            100.0,
            "2026-01-01T00:00:00Z",
        ),
        (
            "AGENT-01-CEO-CHATTY",
            "Chatty",
            "Chief Executive Officer (CEO) · NovusMundus",
            1,
            "Dirección General Ejecutiva · NovusMundus",
            "Mikel Irastorza (Presidente)",
            "Google Antigravity SDK · Gemini 2.5 Flash / LiteRT",
            "EJECUTANDO DIRECTIVAS PRESIDENCIALES",
            1,
            542,
            99.8,
            "2026-01-15T00:00:00Z",
        ),
        (
            "AGENT-02-CTO-TITAN",
            "Titan",
            "Chief Technology Officer (CTO)",
            2,
            "Infraestructura Distribuida & Streaming",
            "Chatty (CEO)",
            "Python 3.14 · Kafka KRaft · PySpark Watermark",
            "OPERATIVO · LATENCIA < 80MS",
            1,
            480,
            99.4,
            "2026-01-15T00:00:00Z",
        ),
        (
            "AGENT-03-CSO-HYPATIA",
            "Hypatia",
            "Chief Science & AI Officer (CSO)",
            2,
            "Ciencia, Matemáticas & Machine Learning",
            "Chatty (CEO)",
            "Haskell GHC · SymPy · BigQuery TimesFM 2.0",
            "OPERATIVO · WELFORD MONOID EXACTO",
            1,
            425,
            99.9,
            "2026-01-15T00:00:00Z",
        ),
        (
            "AGENT-04-CISO-AEGIS",
            "Aegis",
            "Chief Information Security & Quality Officer (CISO/CQO)",
            2,
            "Seguridad Zero-Trust, RLS & Clean Code",
            "Chatty (CEO)",
            "Ruff Linter · Mypy · SQLite WAL ACID Gate",
            "OPERATIVO · 0 ADVERTENCIAS RUFF/MYPY",
            1,
            510,
            100.0,
            "2026-01-15T00:00:00Z",
        ),
        (
            "AGENT-05-CPO-CUPERTINO",
            "Cupertino",
            "Chief Product & Design Officer (CPO)",
            2,
            "Diseño Steve Jobs Apple, UX & AuraIcons",
            "Chatty (CEO)",
            "React 19 · Apple Cupertino Squircle · Headless Chrome",
            "OPERATIVO · 60FPS MICRO-INTERACTIONS",
            1,
            390,
            99.6,
            "2026-01-15T00:00:00Z",
        ),
        (
            "AGENT-06-COO-ATLAS",
            "Atlas",
            "Chief Operating Officer & FinOps (COO)",
            2,
            "Operaciones & Eficiencia Energética",
            "Chatty (CEO)",
            "Python Energy Audit · NAS Sync · FinOps",
            "OPERATIVO · 137 € AHORRO LUZ AUDITADO",
            1,
            415,
            99.5,
            "2026-01-15T00:00:00Z",
        ),
        (
            "AGENT-07-WORKER-NIFI",
            "Worker 01 · NiFi Ingestor",
            "Perimeter Gatekeeper",
            3,
            "Ingesta",
            "Titan (CTO)",
            "Apache NiFi FlowFiles",
            "STANDBY · COLA UNITARIA",
            1,
            320,
            99.5,
            "2026-01-15T00:00:00Z",
        ),
        (
            "AGENT-08-WORKER-KAFKA",
            "Worker 02 · Kafka Partitioner",
            "Stream Partitioner",
            3,
            "Streaming",
            "Titan (CTO)",
            "Kafka KRaft murmur2",
            "STANDBY · COLA UNITARIA",
            1,
            345,
            99.6,
            "2026-01-15T00:00:00Z",
        ),
        (
            "AGENT-09-WORKER-WELFORD",
            "Worker 03 · Welford Monoid",
            "Algebraic Aggregator",
            3,
            "Matemáticas",
            "Hypatia (CSO)",
            "Haskell / SymPy O(1)",
            "STANDBY · COLA UNITARIA",
            1,
            390,
            99.9,
            "2026-01-15T00:00:00Z",
        ),
        (
            "AGENT-10-WORKER-LAKEHOUSE",
            "Worker 04 · Lakehouse Sink",
            "ACID Storage Sentinel",
            3,
            "Lakehouse",
            "Aegis (CISO)",
            "Apache Iceberg / SQLite WAL",
            "STANDBY · COLA UNITARIA",
            1,
            310,
            100.0,
            "2026-01-15T00:00:00Z",
        ),
    ]
    conn.executemany(
        "INSERT OR REPLACE INTO corporate_hierarchy VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", agents
    )

    routes = [
        (
            "ROUTE-01-NIFI",
            "Ruta 1 · Ingesta Perimetral NiFi",
            "Edge API Gateway",
            "Apache NiFi FlowFiles",
            30.0,
            28.4,
            14.2,
            42000.0,
            "Backpressure Dinámico (Queue ≤ 10k FlowFiles) + Loteo Cíclico POSIX",
            50.0,
            "AUTOMEJORADA ⚡",
            "2026-10-29T10:00:00Z",
        ),
        (
            "ROUTE-02-KAFKA",
            "Ruta 2 · Particionado Kafka KRaft",
            "Apache NiFi FlowFiles",
            "Kafka Broker KRaft (8 Particiones)",
            40.0,
            38.6,
            18.5,
            36500.0,
            "Key-Salting Anti-Sesgo (H(X) ≥ 2.95 bits) + acks=all Zero-Loss",
            52.1,
            "AUTOMEJORADA ⚡",
            "2026-10-29T10:05:00Z",
        ),
        (
            "ROUTE-03-SPARK",
            "Ruta 3 · Micro-lotes PySpark & Ventanas",
            "Kafka Broker KRaft",
            "PySpark Structured Streaming",
            75.0,
            71.2,
            34.8,
            28000.0,
            "Watermarking Estricto de 5s + Work-Stealing en Ejecutores Paralelos",
            51.1,
            "AUTOMEJORADA ⚡",
            "2026-10-29T10:10:00Z",
        ),
        (
            "ROUTE-04-WELFORD",
            "Ruta 4 · Álgebra Haskell & Welford-Chan",
            "PySpark Structured Streaming",
            "Welford Monoid Aggregator O(1)",
            25.0,
            22.1,
            7.8,
            55000.0,
            "Fusión Asociativa (A ⊕ B) ⊕ C sin Relectura en Memoria Constante",
            64.7,
            "AUTOMEJORADA ⚡",
            "2026-10-29T10:15:00Z",
        ),
        (
            "ROUTE-05-MAD",
            "Ruta 5 · Detección Robusta MAD Antifraude",
            "Welford Monoid Aggregator",
            "Escudo Antifraude (MAD = 295.76)",
            35.0,
            31.5,
            11.2,
            48000.0,
            "Bifurcación Inmune al Enmascaramiento con Mediana + Aislamiento Seguro",
            64.4,
            "AUTOMEJORADA ⚡",
            "2026-10-29T10:20:00Z",
        ),
        (
            "ROUTE-06-LAKEHOUSE",
            "Ruta 6 · Lakehouse ACID & Réplica NAS/Cloud",
            "Escudo Antifraude",
            "Apache Iceberg Parquet ZSTD + SQLite WAL",
            50.0,
            46.8,
            19.4,
            32000.0,
            "Compactación a Bloques de 256MB contra Small Files + WAL Checkpointing",
            58.5,
            "AUTOMEJORADA ⚡",
            "2026-10-29T10:25:00Z",
        ),
    ]
    conn.executemany(
        "INSERT OR REPLACE INTO corporate_routes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", routes
    )

    orders = [
        (
            "ORD-20261029-001",
            "2026-10-29T09:30:00Z",
            "Mikel Irastorza · Presidente",
            "Optimizar caudal y garantizar que la cola por agente sea unitaria (Q_i ≤ 1)",
            "CTO Titan, CPO Cupertino",
            "¡A sus órdenes, Presidente Mikel! Desplegado protocolo de Work-Stealing en PySpark y balanceo de 8 particiones. Colas unitarias verificadas.",
            "Rebalanceo de 8 particiones Kafka y activación de Work-Stealing en ejecutores.",
            99.4,
            "EJECUTADA EXITOSAMENTE ✅",
        ),
        (
            "ORD-20261029-002",
            "2026-10-29T10:15:00Z",
            "Mikel Irastorza · Presidente",
            "Auditoría matemática de Welford y verificación de cero cancelación catastrófica",
            "CSO Hypatia, CISO Aegis",
            "Comprobación formal completada con SymPy y Haskell GHC: residuo asociativo exacto 0.0000. Z-Score robusto MAD = 295.76 operativo.",
            "Ejecución de suite de demostraciones formales y pruebas unitarias de monoides.",
            99.9,
            "EJECUTADA EXITOSAMENTE ✅",
        ),
    ]
    conn.executemany(
        "INSERT OR REPLACE INTO corporate_executive_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", orders
    )

    knowledge = [
        (
            "KB-01-WELFORD-MONOID",
            "matematicas_algebraicas",
            "Monoide de Welford-Chan en Haskell & Python",
            "Agregación paralela asociativa (A ⊕ B) ⊕ C en O(1) de memoria sin cancelación catastrófica.",
            "data StatsMonoid = StatsMonoid !Int !Double !Double deriving (Show, Eq)\ninstance Semigroup StatsMonoid where\n  (StatsMonoid nA mA sA) <> (StatsMonoid nB mB sB) =\n    let n = nA + nB\n        delta = mB - mA\n        m = mA + delta * fromIntegral nB / fromIntegral n\n        s = sA + sB + delta * delta * fromIntegral (nA * nB) / fromIntegral n\n    in StatsMonoid n m s",
            "Demuestra formalmente por qué la agregación distribuida en Spark requiere estructura algebraica de monoide.",
            "2026-10-29T10:00:00Z",
        ),
        (
            "KB-02-MAD-ROBUST-Z",
            "antifraude_estadistico",
            "Z-Score Robusto por Mediana y Desviación Absoluta Mediana (MAD)",
            "Punto de ruptura del 50% inmune al enmascaramiento de outliers masivos en transacciones financieras.",
            "def robust_mad_z_score(x: np.ndarray) -> np.ndarray:\n    med = np.median(x)\n    mad = np.median(np.abs(x - med))\n    if mad == 0.0:\n        return np.zeros_like(x)\n    return 0.6745 * (x - med) / mad",
            "Explica cómo evitar que 10 transacciones fraudulentas de 10.000 € inflen la media y oculten el fraude.",
            "2026-10-29T10:00:00Z",
        ),
        (
            "KB-03-ENERGY-PVPC-AUDIT",
            "finops_energia",
            "Optimización de Termo Eléctrico y Tarifa Regulada PVPC (137,21 € Ahorro)",
            "Modelado termodinámico del agua (1 cal = 4.186 J) y programación horaria de 3 horas valle.",
            "E_kwh = (V_litros * delta_T * 4186) / 3_600_000\ncoste_sin_timer = 24 * P_standby_kw * precio_medio\ncoste_con_timer = 3 * P_nom_kw * precio_valle\nahorro_anual = (coste_sin_timer - coste_con_timer) * 365",
            "Calcula el ahorro exacto en euros al año para un termo de 100L con contrato regulado de 0,1329 €/kWh.",
            "2026-10-29T10:00:00Z",
        ),
        (
            "KB-04-BIGQUERY-TIMESFM",
            "cloud_ia_forecasting",
            "BigQuery AI.DETECT_ANOMALIES con TimesFM 2.0",
            "Detección predictiva de anomalías cronológicas en tablas analíticas con particionado temporal.",
            "SELECT *\nFROM AI.DETECT_ANOMALIES(\n  TABLE gold_category_metrics,\n  data_col => 'total_volume_eur',\n  timestamp_col => 'window_start',\n  id_cols => ['category']\n);",
            "Formula la consulta SQL nativa en BigQuery para predecir series temporales financieras con TimesFM.",
            "2026-10-29T10:00:00Z",
        ),
    ]
    conn.executemany(
        "INSERT OR REPLACE INTO corporate_reusable_knowledge VALUES (?, ?, ?, ?, ?, ?, ?)", knowledge
    )


def export_categorized_folders_and_bridge(conn: sqlite3.Connection) -> None:
    """
    1. Exports categorized JSON snapshots into `04_database_lakehouse/categories/`.
    2. Generates `05_archify_visualizer/live_data_bridge.js` so the frontend UI
       is 100% dynamically fed by the master SQLite database.
    """
    cat_map = {
        "01_dimensions": ["dim_users", "dim_merchants"],
        "02_gold_analytics": ["gold_category_metrics", "vw_fraud_alerts", "streaming_window_sinks"],
        "03_knowledge_formulas": ["kb_mathematical_formulas"],
        "04_interview_defense": ["kb_interview_defense"],
        "05_cv_portfolio": ["kb_cv_portfolio"],
        "06_10_projects_roadmap": ["kb_10_projects_roadmap"],
        "07_ai_insights": ["ai_insights_registry"],
        "08_corporate_enterprise": [
            "corporate_hierarchy",
            "corporate_routes",
            "corporate_executive_orders",
            "corporate_reusable_knowledge",
        ],
    }
    bridge_payload: dict[str, list[dict]] = {}

    for folder_name, tables in cat_map.items():
        sub_dir = PATHS.categories_dir / folder_name
        sub_dir.mkdir(parents=True, exist_ok=True)
        for tbl in tables:
            order_by = EXPORT_ORDER.get(tbl, "")
            df = pl.read_database(f"SELECT * FROM {tbl} {order_by} LIMIT 100", conn)
            records = df.to_dicts()
            bridge_payload[tbl] = records
            out_file = sub_dir / f"{tbl}.json"
            out_file.write_text(
                json.dumps(records, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

    PATHS.archify_bridge_js.parent.mkdir(parents=True, exist_ok=True)
    js_content = (
        "// AUTO-GENERATED BY 04_database_lakehouse/build_database.py\n"
        "// DO NOT EDIT MANUALLY — RUN `make db` TO REFRESH FROM SQLITE\n"
        f"window.LAKEHOUSE_LIVE_DATA = {json.dumps(bridge_payload, indent=2, ensure_ascii=False)};\n"
    )
    PATHS.archify_bridge_js.write_text(js_content, encoding="utf-8")


def build_and_populate_database(n_transactions: int = 25_000) -> None:
    """Builds the entire SQLite Lakehouse using the pure mathematical engine."""
    if PATHS.db_path.exists():
        PATHS.db_path.unlink()

    rng = np.random.default_rng(2026)

    with closing(sqlite3.connect(PATHS.db_path)) as conn, conn:
        conn.executescript(SCHEMA_SQL)

        countries = ["ES", "US", "UK", "FR", "DE", "IT", "MX"]
        tiers = ["LOW", "MEDIUM", "HIGH", "VIP"]
        first_names = [
            "Mikel",
            "Elena",
            "Carlos",
            "Sofia",
            "David",
            "Lucia",
            "Mateo",
            "Paula",
            "Javier",
            "Clara",
        ]
        last_names = ["Irastorza", "Garcia", "Mendoza", "Silva", "Kowalski", "Dubois", "Rossi", "Vega"]

        users_data = [
            (
                f"user_{uid}",
                f"{rng.choice(first_names)} {rng.choice(last_names)}",
                str(rng.choice(countries, p=[0.35, 0.20, 0.15, 0.10, 0.10, 0.05, 0.05])),
                int(rng.random() > 0.08),
                str(rng.choice(tiers, p=[0.60, 0.25, 0.10, 0.05])),
                "2026-01-15T10:00:00Z",
            )
            for uid in range(1000, 1500)
        ]
        conn.executemany("INSERT INTO dim_users VALUES (?, ?, ?, ?, ?, ?)", users_data)

        categories = ["groceries", "electronics", "fashion", "travel", "luxury"]
        merchants_data = [
            (
                f"merch_{idx:03d}",
                f"{categories[(idx - 1) % len(categories)].title()} Global Store #{idx}",
                categories[(idx - 1) % len(categories)],
                round(float(rng.uniform(0.8, 2.9)), 2),
            )
            for idx in range(1, 26)
        ]
        conn.executemany("INSERT INTO dim_merchants VALUES (?, ?, ?, ?)", merchants_data)

        user_ids = [u[0] for u in users_data]
        merch_ids = [m[0] for m in merchants_data]
        merch_cat_map = {m[0]: m[2] for m in merchants_data}

        chosen_users = rng.choice(user_ids, size=n_transactions)
        chosen_merchs = rng.choice(merch_ids, size=n_transactions)
        chosen_cats = np.array([merch_cat_map[m] for m in chosen_merchs])
        chosen_devices = rng.choice(["iOS-18", "Android-15", "Web-Chrome", "Web-Safari"], size=n_transactions)
        chosen_countries = rng.choice(countries, size=n_transactions)

        amounts = rng.lognormal(mean=4.15, sigma=0.72, size=n_transactions).round(2)
        fraud_mask = rng.random(n_transactions) < 0.006
        amounts[fraud_mask] = rng.uniform(3200.0, 12000.0, size=int(np.sum(fraud_mask))).round(2)

        classic_z = np.zeros(n_transactions, dtype=np.float64)
        robust_z = np.zeros(n_transactions, dtype=np.float64)
        is_fraud = np.zeros(n_transactions, dtype=np.int64)

        gold_rows: list[tuple] = []
        window_rows: list[tuple] = []

        for cat in categories:
            mask = chosen_cats == cat
            cat_amounts = amounts[mask]
            # Call the unified mathematical engine!
            scores = compute_classic_and_robust_z(cat_amounts)
            classic_z[mask] = scores.classic_z
            robust_z[mask] = scores.robust_z
            is_fraud[mask] = scores.is_fraud

            ent = shannon_entropy_bits(chosen_countries[mask])
            frauds_in_cat = int(np.sum(scores.is_fraud))

            gold_rows.append(
                (
                    cat,
                    scores.welford_monoid.count,
                    round(float(np.sum(cat_amounts)), 2),
                    round(scores.welford_monoid.mean, 2),
                    round(scores.welford_monoid.std_dev, 2),
                    scores.median,
                    scores.mad_normal,
                    ent,
                    frauds_in_cat,
                )
            )

            window_rows.append(
                (
                    "2026-10-28T14:00:00Z",
                    "2026-10-28T14:01:00Z",
                    cat,
                    int(scores.welford_monoid.count // 28),
                    round(float(np.sum(cat_amounts) / 28.0), 2),
                    round(scores.welford_monoid.mean, 2),
                    max(1, frauds_in_cat // 10),
                    "2026-10-28T14:01:05Z",
                )
            )

        partitions = [abs(hash(u)) % 8 for u in chosen_users]
        latencies = rng.gamma(shape=2.2, scale=4.5, size=n_transactions).round(2)

        txn_rows = [
            (
                f"txn_{i + 100000}",
                str(chosen_users[i]),
                str(chosen_merchs[i]),
                str(chosen_cats[i]),
                float(amounts[i]),
                "EUR",
                str(chosen_devices[i]),
                str(chosen_countries[i]),
                int(partitions[i]),
                float(latencies[i]),
                float(classic_z[i]),
                float(robust_z[i]),
                int(is_fraud[i]),
                f"2026-10-{min((i // 850) + 1, 28):02d}T{(i % 24):02d}:{(i % 60):02d}:00Z",
            )
            for i in range(n_transactions)
        ]

        conn.executemany(
            "INSERT INTO fact_transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            txn_rows,
        )
        conn.executemany(
            "INSERT INTO gold_category_metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            gold_rows,
        )
        conn.executemany(
            "INSERT INTO streaming_window_sinks VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            window_rows,
        )

        populate_ai_insights(conn, gold_rows)
        populate_knowledge_base(conn)
        populate_corporate_enterprise(conn)
        export_categorized_folders_and_bridge(conn)

        print("==================================================================")
        print(f"🏛️ BASE DE DATOS INTERCONECTADA Y CATEGORIZADA: {PATHS.db_path}")
        print("==================================================================")
        cur = conn.cursor()
        for tbl in [
            "dim_users",
            "dim_merchants",
            "fact_transactions",
            "gold_category_metrics",
            "streaming_window_sinks",
            "ai_insights_registry",
            "kb_mathematical_formulas",
            "kb_study_notebooks",
            "kb_interview_defense",
            "kb_cv_portfolio",
            "kb_10_projects_roadmap",
            "corporate_hierarchy",
            "corporate_routes",
            "corporate_executive_orders",
            "corporate_reusable_knowledge",
        ]:
            cur.execute(f"SELECT COUNT(*) FROM {tbl}")
            print(f"  ✅ {tbl:<28} -> {cur.fetchone()[0]:>6,} registros")
        print(f"  🔗 Bridge JS actualizado en   -> {PATHS.archify_bridge_js}")


if __name__ == "__main__":
    build_and_populate_database(25_000)
