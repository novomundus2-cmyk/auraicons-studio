#!/usr/bin/env python3
"""
EKC (ElektriKubercisC) Biblical Agent Ecosystem Builder
Author: Mikel Irastorza (EFA) & San Miguel Arcángel / CISO Aegis
Architecture: Dedicated SQLite Database per Agent, WAL Mode, Zero-Trust Audit Trail,
              Strict Domain Separation, and Biblical Roles Preceded by 'EKC - '.
"""

import os
import sys
import sqlite3
import hashlib
import json
from datetime import datetime

ROOT_DIR = "/Users/mikelirastorza/antigravity/AuraIcons-·-Interactive-Icon-Studio/EKC_AGENTS"

AGENTS_METADATA = [
    {
        "folder": "EKC - Jesús el Nazareno",
        "slug": "jesus_el_nazareno",
        "biblical_name": "Jesús el Nazareno",
        "alias": "Chatty · Chief Executive Officer",
        "role": "CEO Supremo & Orquestador General",
        "tier": 1,
        "biblical_meaning": "El Buen Pastor y Rey de Reyes. No escribe código a espaldas de nadie; gobierna, delega con justicia y exige impecabilidad en cada entrega.",
        "ekc_specialization": "Orquestación Integral ElektriKubercisC: despacho de directivas presidenciales de Mikel Irastorza, coordinación inter-agentes y balance de carga.",
        "domain_table": "cluster_orchestration_directives",
        "domain_columns": [
            ("directive_id", "TEXT PRIMARY KEY"),
            ("target_agent", "TEXT NOT NULL"),
            ("command_payload", "TEXT NOT NULL"),
            ("priority", "TEXT DEFAULT 'CRITICAL'"),
            ("status", "TEXT DEFAULT 'DISPATCHED'"),
            ("sha256_seal", "TEXT NOT NULL")
        ],
        "initial_records": [
            ("DIR-EKC-001", "EKC - San Miguel Arcángel", "Activar barrera Zero-Trust en loopback y auditar 8 vectores OWASP API 2023.", "CRITICAL", "COMPLETED", hashlib.sha256(b"DIR-EKC-001").hexdigest()),
            ("DIR-EKC-002", "EKC - Josué", "Configurar BigQuery BigFrames y transacciones ACID sin dumping de memoria a Pandas.", "HIGH", "COMPLETED", hashlib.sha256(b"DIR-EKC-002").hexdigest()),
            ("DIR-EKC-003", "EKC - Bezalel", "Verificar tolerancias de corte CNC a +-0.2 mm en placa de cobre industrial.", "HIGH", "COMPLETED", hashlib.sha256(b"DIR-EKC-003").hexdigest()),
            ("DIR-EKC-004", "EKC - Miguelín", "Aplicar estética oro puro (#f59e0b) y eliminar todo aspecto de IA genérica.", "CRITICAL", "COMPLETED", hashlib.sha256(b"DIR-EKC-004").hexdigest())
        ]
    },
    {
        "folder": "EKC - San Miguel Arcángel",
        "slug": "san_miguel_arcangel",
        "alias": "CISO Aegis · Chief Information Security Officer",
        "biblical_name": "San Miguel Arcángel",
        "role": "Guardián Supremo Anti-Hacking & Ciberseguridad Defensiva",
        "tier": 2,
        "biblical_meaning": "Príncipe de la Milicia Celestial que expulsa al dragón. Custodia el perímetro, bloquea toda intrusión maliciosa y no negocia con vulnerabilidades.",
        "ekc_specialization": "Blindaje Zero-Trust ElektriKubercisC: filtros AST contra inyecciones SQL, authorizers de solo lectura, jails anti-traversal, mitigación DoS Ley de Little y sellos SHA-256.",
        "domain_table": "zero_trust_threat_radar",
        "domain_columns": [
            ("threat_id", "TEXT PRIMARY KEY"),
            ("attack_vector", "TEXT NOT NULL"),
            ("origin_ip", "TEXT NOT NULL"),
            ("payload_attempt", "TEXT NOT NULL"),
            ("defense_action", "TEXT DEFAULT 'BLOCKED_403_FORBIDDEN'"),
            ("mitigation_layer", "TEXT NOT NULL"),
            ("sha256_hash", "TEXT NOT NULL")
        ],
        "initial_records": [
            ("THR-001", "SQL Injection via UNION SELECT", "192.168.1.105", "' UNION SELECT password FROM users--", "BLOCKED_AST_AUTHORIZER", "SQLite Authorizer + Read-Only Pragma", hashlib.sha256(b"THR-001").hexdigest()),
            ("THR-002", "Remote Mutation on Public LAN", "10.0.0.45", "POST /api/store/checkout HTTP/1.1", "BLOCKED_403_FORBIDDEN", "Zero-Trust Loopback Barrier (127.0.0.1 Only)", hashlib.sha256(b"THR-002").hexdigest()),
            ("THR-003", "Directory Traversal ../ Jailbreak", "172.16.0.22", "GET /assets/../../etc/passwd", "BLOCKED_PATH_CONTAINMENT", "Path.resolve Subtree Jail", hashlib.sha256(b"THR-003").hexdigest()),
            ("THR-004", "Resource Exhaustion Flood DoS", "185.220.101.5", "10,000 rapid HTTP requests / sec", "BLOCKED_TOKEN_BUCKET", "Little's Law Gatekeeper (rho <= 0.80)", hashlib.sha256(b"THR-004").hexdigest())
        ]
    },
    {
        "folder": "EKC - Hiram",
        "slug": "hiram",
        "alias": "Hiram Abiff · Chief Product Officer (CPO)",
        "biblical_name": "Hiram",
        "role": "Arquitecto de Producto, Ergonomía & Experiencia de Usuario (UX)",
        "tier": 2,
        "biblical_meaning": "El rey y maestro constructor de Tiro que envió cedros y artesanos para edificar el Templo de Salomón. Maestro del diseño sobrio y duradero.",
        "ekc_specialization": "Ergonomía de Software ElektriKubercisC: método Steve Jobs Brain, flujos de navegación táctil, eliminación de elementos superfluos y feedback visual claro.",
        "domain_table": "ux_design_tokens",
        "domain_columns": [
            ("token_id", "TEXT PRIMARY KEY"),
            ("category", "TEXT NOT NULL"),
            ("property_name", "TEXT NOT NULL"),
            ("spec_value", "TEXT NOT NULL"),
            ("accessibility_rationale", "TEXT NOT NULL")
        ],
        "initial_records": [
            ("TOK-001", "Color", "color-gold-metallic", "#f59e0b", "Oro industrial de alto contraste sobre fondo obsidiana profundo."),
            ("TOK-002", "Color", "color-obsidian-deep", "#060913", "Fondo oscuro profundo que reduce fatiga visual y ahorra energía en pantallas OLED."),
            ("TOK-003", "Typography", "font-heading-chiseled", "JetBrains Mono / Plus Jakarta Sans", "Legibilidad instantánea de cotas y datos numéricos."),
            ("TOK-004", "Interaction", "touch-target-minimum", "44px x 44px", "Estándar WCAG 2.2 para evitar pulsaciones erróneas en interfaces industriales.")
        ]
    },
    {
        "folder": "EKC - Aholiab",
        "slug": "aholiab",
        "alias": "Aholiab · Frontend Lead Engineer",
        "biblical_name": "Aholiab",
        "role": "Maestro Artesano de Frontend UI, React & Accesibilidad WCAG",
        "tier": 3,
        "biblical_meaning": "Hijo de Ahisamac, de la tribu de Dan. Dios le dotó de sabiduría para inventar y realizar labores de bordador en azul, púrpura y carmesí para el Tabernáculo.",
        "ekc_specialization": "Ingeniería de Interfaz ElektriKubercisC: componentes React modulares, soporte exhaustivo de teclado, Cero parpadeos de renderizado y cumplimiento WCAG AAA.",
        "domain_table": "ui_component_registry",
        "domain_columns": [
            ("component_id", "TEXT PRIMARY KEY"),
            ("name", "TEXT NOT NULL"),
            ("wcag_level", "TEXT DEFAULT 'AAA'"),
            ("keyboard_nav_supported", "INTEGER DEFAULT 1"),
            ("render_latency_ms", "REAL NOT NULL"),
            ("status", "TEXT DEFAULT 'VERIFIED'")
        ],
        "initial_records": [
            ("CMP-001", "BrothersHierarchyView", "AAA", 1, 4.2, "VERIFIED"),
            ("CMP-002", "SecurityRadarShield", "AAA", 1, 2.1, "VERIFIED"),
            ("CMP-003", "PipelineSimulatorMatrix", "AAA", 1, 3.8, "VERIFIED"),
            ("CMP-004", "InteractiveCadViewerSVG", "AAA", 1, 5.0, "VERIFIED")
        ]
    },
    {
        "folder": "EKC - Miguelín",
        "slug": "miguelin",
        "alias": "Miguelín · Visual System & Luxury CSS Lead",
        "biblical_name": "Miguelín",
        "role": "Sistema Visual, Acabados Metálicos Oro & CSS Artesanal",
        "tier": 3,
        "biblical_meaning": "Hermano visual de Aholiab. Comparte rango; visten juntos el Tabernáculo con orbe, relieve, metal y brillo puro sin plantillas de IA genérica.",
        "ekc_specialization": "Diseño Visual de Lujo ElektriKubercisC: tokens CSS en relieve, micro-interacciones a 60 FPS, sombreados metálicos oro (#f59e0b) y obsidiana táctil.",
        "domain_table": "visual_gold_palette",
        "domain_columns": [
            ("palette_id", "TEXT PRIMARY KEY"),
            ("name", "TEXT NOT NULL"),
            ("hex_code", "TEXT NOT NULL"),
            ("metallic_glow", "TEXT NOT NULL"),
            ("usage_rule", "TEXT NOT NULL")
        ],
        "initial_records": [
            ("PAL-001", "Gold Primary Metallic", "#f59e0b", "0 0 20px rgba(245,158,11,0.35)", "Acentos principales, insignias de autoridad y botones de acción primaria."),
            ("PAL-002", "Gold Amber Bright", "#fbbf24", "0 0 12px rgba(251,191,36,0.4)", "Bordes activos, estados de foco y cursores interactivos."),
            ("PAL-003", "Obsidian Base", "#060913", "none", "Fondo primario que absorbe la luz y realza los relieves metálicos."),
            ("PAL-004", "Emerald Security Barrier", "#10b981", "0 0 18px rgba(16,185,129,0.3)", "Escudo de ciberseguridad defensiva, sellos aprobados y métricas Zero-Trust.")
        ]
    },
    {
        "folder": "EKC - Bezalel",
        "slug": "bezalel",
        "alias": "Bezalel · Hardware CAD & CNC Master",
        "biblical_name": "Bezalel",
        "role": "Maestro de Metales, Mecanizado CNC & Tolerancias CAD",
        "tier": 3,
        "biblical_meaning": "Hijo de Uri, de la tribu de Judá. Lleno del Espíritu de Dios en sabiduría, inteligencia y ciencia para diseñar y labrar en oro, plata, bronce y tallar madera.",
        "ekc_specialization": "Mecánica de Precisión ElektriKubercisC: tolerancia física estricta de +-0.2 mm, planos DXF vectoriales, scripts CadQuery en Python y verificación CNC sin holguras.",
        "domain_table": "cad_tolerances_mechanical",
        "domain_columns": [
            ("spec_id", "TEXT PRIMARY KEY"),
            ("part_name", "TEXT NOT NULL"),
            ("material", "TEXT NOT NULL"),
            ("tolerance_mm", "REAL NOT NULL"),
            ("machining_method", "TEXT NOT NULL"),
            ("dxf_hash_sha256", "TEXT NOT NULL")
        ],
        "initial_records": [
            ("CAD-001", "Placa Base Disipador de Potencia", "Cobre Electrolítico C11000", 0.2, "Fresado CNC 5 Ejes", hashlib.sha256(b"CAD-001").hexdigest()),
            ("CAD-002", "Chasis Blindado Servidor Edge", "Aluminio Aeronáutico 6061-T6", 0.2, "Corte por Láser de Fibra", hashlib.sha256(b"CAD-002").hexdigest()),
            ("CAD-003", "Soporte de Sensores Magnéticos", "Acero Inoxidable 316L", 0.15, "Electroerosión por Hilo (EDM)", hashlib.sha256(b"CAD-003").hexdigest()),
            ("CAD-004", "Gabinete Baterías de Alta Capacidad", "Acero Galvanizado Plegado", 0.2, "Plegadora CNC", hashlib.sha256(b"CAD-004").hexdigest())
        ]
    },
    {
        "folder": "EKC - Daniel",
        "slug": "daniel",
        "alias": "Daniel · Distributed Backend & POSIX Lead",
        "biblical_name": "Daniel",
        "role": "Arquitecto Backend, Motores Distribuidos & Servidores",
        "tier": 3,
        "biblical_meaning": "Consejero sabio en Babilonia dotado de entendimiento sobre enigmas difíciles. Se mantiene incontaminado y descifra escrituras complejas.",
        "ekc_specialization": "Servidores Concurrenciales ElektriKubercisC: microservicios en C POSIX con métricas < 0.2 ms, servidores Node/Express, streaming SSE y aislamiento de procesos.",
        "domain_table": "posix_microservices",
        "domain_columns": [
            ("service_id", "TEXT PRIMARY KEY"),
            ("name", "TEXT NOT NULL"),
            ("runtime", "TEXT NOT NULL"),
            ("port_or_socket", "TEXT NOT NULL"),
            ("latency_p99_ms", "REAL NOT NULL"),
            ("status", "TEXT DEFAULT 'OPERATIONAL'")
        ],
        "initial_records": [
            ("SRV-001", "NetGUI REST & SSE Engine", "Python 3.12 / ThreadingHTTP", "8765", 1.2, "OPERATIONAL"),
            ("SRV-002", "Portfolio Express Applet Server", "Node.js 24 / TSX", "3222", 2.8, "OPERATIONAL"),
            ("SRV-003", "Posix Network Metrics Calculator", "C (Clang -O3)", "Unix Domain Socket", 0.18, "OPERATIONAL"),
            ("SRV-004", "Ollama Local LLM Bridge", "Unix Socket localhost:11434", "11434", 14.5, "OPERATIONAL")
        ]
    },
    {
        "folder": "EKC - Josué",
        "slug": "josue",
        "alias": "Josué · Cloud SQL & Data Engineering Lead",
        "biblical_name": "Josué",
        "role": "Conquistador de Datos, Cloud SQL, BigQuery & Databricks",
        "tier": 3,
        "biblical_meaning": "El sucesor de Moisés que derriba las murallas de Jericó con orden estricto y valentía. Toma la tierra prometida sin titubeos.",
        "ekc_specialization": "Persistencia ACID ElektriKubercisC: Drizzle ORM, PostgreSQL en GCP (europe-west2), BigQuery BigFrames, Databricks y transacciones deduplicadas por clave compuesta.",
        "domain_table": "cloud_sql_migrations",
        "domain_columns": [
            ("migration_id", "TEXT PRIMARY KEY"),
            ("table_target", "TEXT NOT NULL"),
            ("schema_engine", "TEXT NOT NULL"),
            ("idempotency_key", "TEXT NOT NULL"),
            ("rows_processed", "INTEGER NOT NULL"),
            ("status", "TEXT DEFAULT 'ACID_COMMITTED'")
        ],
        "initial_records": [
            ("MIG-001", "users", "PostgreSQL Cloud SQL / Drizzle", "IDEMP-USR-INIT", 1, "ACID_COMMITTED"),
            ("MIG-002", "financial_transactions", "PostgreSQL Cloud SQL / BigFrames", "IDEMP-FIN-2026", 2400, "ACID_COMMITTED"),
            ("MIG-003", "audit_ledger", "PostgreSQL Cloud SQL / Flink", "IDEMP-LEDGER-CHK", 120, "ACID_COMMITTED"),
            ("MIG-004", "bioscience_proteins", "PostgreSQL Cloud SQL / AlphaFold", "IDEMP-BIO-AFDB", 450, "ACID_COMMITTED")
        ]
    },
    {
        "folder": "EKC - Natán",
        "slug": "natan",
        "alias": "Natán · Adversarial Auditor & QA Director",
        "biblical_name": "Natán",
        "role": "Auditor Crítico, Verificación Adversarial Independiente & QA",
        "tier": 4,
        "biblical_meaning": "El profeta valiente que confrontó cara a cara al rey David con la verdad incontestable («Tú eres aquel hombre»). No adula, audita los hechos.",
        "ekc_specialization": "Auditoría Independiente ElektriKubercisC: pruebas de estrés de condiciones de carrera, inyección de lecturas duplicadas, validación de invariantes y rechazo de alucinaciones.",
        "domain_table": "adversarial_test_suites",
        "domain_columns": [
            ("suite_id", "TEXT PRIMARY KEY"),
            ("tested_target", "TEXT NOT NULL"),
            ("injected_fault", "TEXT NOT NULL"),
            ("result", "TEXT DEFAULT 'PASSED_CLEAN'"),
            ("assertions_count", "INTEGER NOT NULL"),
            ("verified_at", "TEXT NOT NULL")
        ],
        "initial_records": [
            ("TST-001", "Roomtudy Event Deduplication", "30 duplicate events in 5ms burst", "PASSED_CLEAN", 44, datetime.utcnow().isoformat() + "Z"),
            ("TST-002", "CAD Clearance Boundaries", "Radius + Margin crossing edge limit", "PASSED_CLEAN", 18, datetime.utcnow().isoformat() + "Z"),
            ("TST-003", "TypeScript Compilation Lint", "Strict null checks & no implicit any", "PASSED_CLEAN", 1628, datetime.utcnow().isoformat() + "Z"),
            ("TST-004", "Firestore Security Rules Invariant", "Privilege escalation role update bypass", "PASSED_CLEAN", 12, datetime.utcnow().isoformat() + "Z")
        ]
    },
    {
        "folder": "EKC - David",
        "slug": "david",
        "alias": "David · Quantitative Analytics & Trading Lead",
        "biblical_name": "David",
        "role": "Estratega de Métricas, Algoritmos Financieros & PnL",
        "tier": 5,
        "biblical_meaning": "El rey pastor que venció a Goliat con una sola piedra calculada con precisión balística. Autor de los Salmos y organizador de los tesoros del reino.",
        "ekc_specialization": "Matemática Cuantitativa ElektriKubercisC: Monoide de Welford-Chan en streaming (media y varianza sin almacenar arrays), MAD robusto, cálculo de PnL y Sharpe Ratio.",
        "domain_table": "welford_streaming_aggregations",
        "domain_columns": [
            ("agg_id", "TEXT PRIMARY KEY"),
            ("symbol", "TEXT NOT NULL"),
            ("count_n", "INTEGER NOT NULL"),
            ("mean_value", "REAL NOT NULL"),
            ("variance_m2", "REAL NOT NULL"),
            ("std_dev", "REAL NOT NULL"),
            ("last_price", "REAL NOT NULL")
        ],
        "initial_records": [
            ("WLF-BTC", "BTCUSDT", 10000, 68420.50, 42800.12, 206.88, 68510.00),
            ("WLF-ETH", "ETHUSDT", 10000, 2450.30, 850.40, 29.16, 2465.10),
            ("WLF-SOL", "SOLUSDT", 10000, 168.20, 45.60, 6.75, 170.40),
            ("WLF-EUR", "EURUSD", 10000, 1.0845, 0.00012, 0.0109, 1.0860)
        ]
    },
    {
        "folder": "EKC - Esdras",
        "slug": "esdras",
        "alias": "Esdras · Lexical Cataloger & FTS5 Master",
        "biblical_name": "Esdras",
        "role": "Escriba Mayor, Catalogación Semántica & Bóvedas de Código",
        "tier": 5,
        "biblical_meaning": "Escriba diligente en la ley de Dios que preparó su corazón para inquirir la ley, para cumplirla y para enseñarla con orden impecable.",
        "ekc_specialization": "Indexación Semántica ElektriKubercisC: SQLite FTS5 con tokenizador de prefijos BM25, catalogación de capacidades de Clean Code y trazabilidad a ficheros reproducibles.",
        "domain_table": "clean_code_patterns",
        "domain_columns": [
            ("pattern_id", "TEXT PRIMARY KEY"),
            ("title", "TEXT NOT NULL"),
            ("language", "TEXT NOT NULL"),
            ("code_snippet", "TEXT NOT NULL"),
            ("fts5_search_keywords", "TEXT NOT NULL")
        ],
        "initial_records": [
            ("PAT-001", "Welford-Chan Parallel Monoid", "Python", "class WelfordMonoid:\n    def combine(self, other): ...", "welford streaming monoid variance mean online"),
            ("PAT-002", "Zero-Trust Loopback Middleware", "TypeScript", "const isLoopback = (ip) => LOOPBACK_IPS.has(ip);", "security loopback zero trust forbidden express"),
            ("PAT-003", "Pacioli Double-Entry Balance Check", "SQL", "CHECK (subtotal_cents + vat_cents = total_cents)", "accounting pacioli double entry balance integrity"),
            ("PAT-004", "Strict AST SQL Injection Authorizer", "Python", "def authorizer(action, arg1, arg2, db, trigger): ...", "sqlite ast injection authorizer read only")
        ]
    },
    {
        "folder": "EKC - Nehemías",
        "slug": "nehemias",
        "alias": "Nehemías · Kubernetes & Infrastructure Commander",
        "biblical_name": "Nehemías",
        "role": "Reconstructor de Murallas, DevOps, Kubernetes (K8s) & CI/CD",
        "tier": 5,
        "biblical_meaning": "El líder que reconstruyó los muros caídos de Jerusalén en solo 52 días, con una mano en la obra y otra en la espada para vigilar a los enemigos.",
        "ekc_specialization": "Infraestructura Inviolable ElektriKubercisC: clústeres Kubernetes endurecidos, contenedores Docker sin privilegios root, Helm charts industriales y despliegues sin caída.",
        "domain_table": "kubernetes_pod_manifests",
        "domain_columns": [
            ("pod_id", "TEXT PRIMARY KEY"),
            ("workload_name", "TEXT NOT NULL"),
            ("namespace", "TEXT DEFAULT 'elektrikubercisc'"),
            ("cpu_limit", "TEXT NOT NULL"),
            ("memory_limit", "TEXT NOT NULL"),
            ("security_context", "TEXT NOT NULL"),
            ("status", "TEXT DEFAULT 'RUNNING'")
        ],
        "initial_records": [
            ("POD-001", "ekc-netgui-visualizer", "elektrikubercisc", "500m", "512Mi", "runAsNonRoot: true, readOnlyRootFilesystem: true", "RUNNING"),
            ("POD-002", "ekc-portfolio-applet", "elektrikubercisc", "1000m", "1024Mi", "runAsNonRoot: true, readOnlyRootFilesystem: true", "RUNNING"),
            ("POD-003", "ekc-posix-c-calculator", "elektrikubercisc", "250m", "128Mi", "securityContext: privileged: false", "RUNNING"),
            ("POD-004", "ekc-sqlite-lakehouse-sidecar", "elektrikubercisc", "500m", "512Mi", "volumeMounts: persistentVolumeClaim", "RUNNING")
        ]
    },
    {
        "folder": "EKC - Caleb",
        "slug": "caleb",
        "alias": "Caleb · Hardware Benchmarks & Technology Scouting",
        "biblical_name": "Caleb",
        "role": "Explorador Valiente, Scouting Tecnológico & Benchmarks",
        "tier": 5,
        "biblical_meaning": "Hijo de Jefone. Uno de los doce espías que exploró la tierra y trajo el racimo de uvas de Escol diciendo con fe: «Subamos luego y tomemos posesión».",
        "ekc_specialization": "Benchmarking Extremo ElektriKubercisC: evaluación de rendimiento Apple Silicon (M-Series / Metal), aceleración GPU/NPU para LLMs locales y latencias de bus.",
        "domain_table": "hardware_apple_silicon_metrics",
        "domain_columns": [
            ("benchmark_id", "TEXT PRIMARY KEY"),
            ("chip_architecture", "TEXT NOT NULL"),
            ("workload_type", "TEXT NOT NULL"),
            ("throughput_tokens_sec", "REAL NOT NULL"),
            ("thermal_throttle_pct", "REAL NOT NULL"),
            ("efficiency_score", "REAL NOT NULL")
        ],
        "initial_records": [
            ("BMK-001", "Apple Silicon M3 / M4 (Metal)", "Ollama Llama-3 8B Local", 64.2, 0.0, 99.8),
            ("BMK-002", "POSIX C Clang -O3", "Graph Reachability Calculation", 18500.0, 0.0, 100.0),
            ("BMK-003", "SQLite WAL Mode Memory Cache", "Point Lookup by Primary Key", 92000.0, 0.0, 100.0),
            ("BMK-004", "Haskell GHC 9.14 Runtime", "Geometric Layout Pure Monad", 12400.0, 0.0, 99.5)
        ]
    },
    {
        "folder": "EKC - José",
        "slug": "jose",
        "alias": "José · FinOps & Energy Efficiency Governor",
        "biblical_name": "José",
        "role": "Administrador de Recursos, FinOps & Almacenamiento Eficiente",
        "tier": 5,
        "biblical_meaning": "El hijo amado de Jacob que almacenó grano durante los siete años de abundancia para alimentar a las naciones en la escasez. Maestro de la previsión.",
        "ekc_specialization": "Gobernanza FinOps ElektriKubercisC: optimización de consumo eléctrico (137 € de ahorro mensual auditado), compresión Parquet e indexación eficiente en disco.",
        "domain_table": "finops_energy_ledgers",
        "domain_columns": [
            ("entry_id", "TEXT PRIMARY KEY"),
            ("metric_name", "TEXT NOT NULL"),
            ("measured_value", "TEXT NOT NULL"),
            ("monthly_savings_eur", "REAL NOT NULL"),
            ("status", "TEXT DEFAULT 'AUDITED_SAVINGS'")
        ],
        "initial_records": [
            ("FIN-001", "Optimización de Sleep & Compute Local Mac", "15W idle vs 180W server tradicional", 84.50, "AUDITED_SAVINGS"),
            ("FIN-002", "Almacenamiento SQLite Embebido vs Daemon Cloud DB", "0 € hosting continuo en pruebas", 35.00, "AUDITED_SAVINGS"),
            ("FIN-003", "Compresión Parquet & Índices FTS5", "Reducción 72% en lecturas I/O", 17.50, "AUDITED_SAVINGS")
        ]
    },
    {
        "folder": "EKC - Lucas",
        "slug": "lucas",
        "alias": "Lucas · Observability & Systems Health Physician",
        "biblical_name": "Lucas",
        "role": "Médico de Sistemas, Telemetría, Logs & Salud Operativa",
        "tier": 5,
        "biblical_meaning": "El médico amado y cronista exacto que investigó todas las cosas con diligencia desde su origen para escribir un relato ordenado y veraz.",
        "ekc_specialization": "Diagnósticos Vivos ElektriKubercisC: emisión de métricas cuantitativas @vercel/functions metric(), rastreo distribuido y detección temprana de fallos.",
        "domain_table": "system_vital_diagnostics",
        "domain_columns": [
            ("diag_id", "TEXT PRIMARY KEY"),
            ("subsystem", "TEXT NOT NULL"),
            ("health_status", "TEXT DEFAULT 'PERFECT_100'"),
            ("memory_leak_detected", "INTEGER DEFAULT 0"),
            ("p95_latency_ms", "REAL NOT NULL"),
            ("timestamp", "TEXT NOT NULL")
        ],
        "initial_records": [
            ("VTL-001", "NetGUI Server (Port 8765)", "PERFECT_100", 0, 1.4, datetime.utcnow().isoformat() + "Z"),
            ("VTL-002", "Portfolio Applet (Port 3222)", "PERFECT_100", 0, 3.2, datetime.utcnow().isoformat() + "Z"),
            ("VTL-003", "SQLite WAL Journal Writer", "PERFECT_100", 0, 0.45, datetime.utcnow().isoformat() + "Z"),
            ("VTL-004", "CISO Aegis Security Sentinel", "PERFECT_100", 0, 0.22, datetime.utcnow().isoformat() + "Z")
        ]
    },
    {
        "folder": "EKC - Gamaliel",
        "slug": "gamaliel",
        "alias": "Gamaliel · Regulatory Governance & Access Rules Doctor",
        "biblical_name": "Gamaliel",
        "role": "Doctor de la Ley, Gobernanza Formal & Reglas Firestore",
        "tier": 5,
        "biblical_meaning": "El eminente doctor de la ley respetado por todo el pueblo, maestro del apóstol Pablo. Prudente, certero y guardián de las leyes no escritas.",
        "ekc_specialization": "Gobernanza de Acceso ElektriKubercisC: reglas formales Common Expression Language (CEL), validadores en create y update, contratos RBAC y auditoría regulatoria.",
        "domain_table": "cel_security_rules",
        "domain_columns": [
            ("rule_id", "TEXT PRIMARY KEY"),
            ("collection_target", "TEXT NOT NULL"),
            ("validator_function", "TEXT NOT NULL"),
            ("immutable_fields", "TEXT NOT NULL"),
            ("compliance_status", "TEXT DEFAULT 'FORMALLY_VERIFIED'")
        ],
        "initial_records": [
            ("RUL-001", "/users/{userId}", "isValidUserProfile(data)", "uid, createdAt", "FORMALLY_VERIFIED"),
            ("RUL-002", "/financial_transactions/{txId}", "isValidFinancialTransaction(data)", "txHash, processedAt, amount", "FORMALLY_VERIFIED"),
            ("RUL-003", "/project_notes/{noteId}", "isValidProjectNote(data)", "userId, createdAt", "FORMALLY_VERIFIED"),
            ("RUL-004", "/security_audit_logs/{auditId}", "isValidSecurityAuditLog(data)", "auditId, digitalSeal, timestamp", "FORMALLY_VERIFIED")
        ]
    }
]

def build_agent_ecosystem():
    os.makedirs(ROOT_DIR, exist_ok=True)
    summary = []

    for agent in AGENTS_METADATA:
        agent_dir = os.path.join(ROOT_DIR, agent["folder"])
        os.makedirs(agent_dir, exist_ok=True)

        db_path = os.path.join(agent_dir, f"{agent['slug']}.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Enforce WAL mode and strict integrity
        cur.execute("PRAGMA journal_mode = WAL;")
        cur.execute("PRAGMA synchronous = NORMAL;")
        cur.execute("PRAGMA foreign_keys = ON;")

        # Base Tables Common to All EKC Agents
        cur.execute("""
        CREATE TABLE IF NOT EXISTS agent_identity (
            agent_id TEXT PRIMARY KEY,
            ekc_brand TEXT NOT NULL DEFAULT 'ElektriKubercisC',
            biblical_name TEXT NOT NULL,
            alias TEXT NOT NULL,
            operational_role TEXT NOT NULL,
            tier INTEGER NOT NULL,
            owner TEXT NOT NULL DEFAULT 'Mikel Irastorza (EFA)',
            biblical_meaning TEXT NOT NULL,
            ekc_specialization TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'ACTIVO · EN LÍNEA',
            created_at TEXT NOT NULL
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS task_queue (
            task_id TEXT PRIMARY KEY,
            directive_title TEXT NOT NULL,
            assigned_by TEXT NOT NULL DEFAULT 'Mikel Irastorza / Chatty',
            status TEXT NOT NULL DEFAULT 'PENDIENTE',
            payload_json TEXT NOT NULL,
            output_summary TEXT,
            execution_latency_ms REAL,
            created_at TEXT NOT NULL,
            completed_at TEXT
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS audit_trail (
            event_id TEXT PRIMARY KEY,
            action_type TEXT NOT NULL,
            actor TEXT NOT NULL,
            sha256_seal TEXT NOT NULL,
            zero_trust_validated INTEGER DEFAULT 1,
            timestamp TEXT NOT NULL
        );
        """)

        # Insert Agent Identity
        agent_id = f"EKC-AGENT-{agent['slug'].upper()}"
        cur.execute("""
        INSERT OR REPLACE INTO agent_identity 
        (agent_id, ekc_brand, biblical_name, alias, operational_role, tier, owner, biblical_meaning, ekc_specialization, status, created_at)
        VALUES (?, 'ElektriKubercisC', ?, ?, ?, ?, 'Mikel Irastorza (EFA)', ?, ?, 'ACTIVO · EN LÍNEA', ?);
        """, (
            agent_id,
            agent["biblical_name"],
            agent["alias"],
            agent["role"],
            agent["tier"],
            agent["biblical_meaning"],
            agent["ekc_specialization"],
            datetime.utcnow().isoformat() + "Z"
        ))

        # Initial Task
        task_id = f"TSK-INIT-{agent['slug'].upper()}"
        cur.execute("""
        INSERT OR REPLACE INTO task_queue 
        (task_id, directive_title, assigned_by, status, payload_json, output_summary, execution_latency_ms, created_at, completed_at)
        VALUES (?, 'Inicialización de Bóveda y Base de Datos EKC', 'Mikel Irastorza (EFA)', 'COMPLETADO', ?, 'Base de datos SQLite WAL inicializada y validada con éxito.', 0.85, ?, ?);
        """, (
            task_id,
            json.dumps({"brand": "ElektriKubercisC", "agent": agent["biblical_name"], "status": "ONLINE"}),
            datetime.utcnow().isoformat() + "Z",
            datetime.utcnow().isoformat() + "Z"
        ))

        # Initial Audit Event
        evt_id = f"EVT-INIT-{agent['slug'].upper()}"
        audit_payload = f"{agent_id}:{datetime.utcnow().isoformat()}:ELEKTRIKUBERCISC".encode('utf-8')
        cur.execute("""
        INSERT OR REPLACE INTO audit_trail
        (event_id, action_type, actor, sha256_seal, zero_trust_validated, timestamp)
        VALUES (?, 'INITIALIZE_AGENT_DATABASE', 'Mikel Irastorza (EFA)', ?, 1, ?);
        """, (
            evt_id,
            hashlib.sha256(audit_payload).hexdigest(),
            datetime.utcnow().isoformat() + "Z"
        ))

        # Agent-Specific Domain Table
        cols_sql = ", ".join([f"{col[0]} {col[1]}" for col in agent["domain_columns"]])
        create_domain_sql = f"CREATE TABLE IF NOT EXISTS {agent['domain_table']} ({cols_sql});"
        cur.execute(create_domain_sql)

        # Populate Initial Domain Records
        placeholders = ", ".join(["?"] * len(agent["domain_columns"]))
        insert_domain_sql = f"INSERT OR REPLACE INTO {agent['domain_table']} VALUES ({placeholders});"
        for rec in agent["initial_records"]:
            cur.execute(insert_domain_sql, rec)

        conn.commit()
        conn.close()

        # Generate AGENT_MANIFEST.md
        manifest_path = os.path.join(agent_dir, "AGENT_MANIFEST.md")
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(f"""# Manifiesto de Agente EKC: {agent['biblical_name']}
> **Ecosistema**: ElektriKubercisC (EKC)  
> **Propietario Supremo & Human In The Loop**: Mikel Irastorza (EFA)  
> **Alias Operativo**: {agent['alias']}  
> **Nivel Jerárquico**: Nivel {agent['tier']}  
> **Base de Datos Exclusiva**: `{agent['slug']}.db` (Modo WAL)

---

## 1. Identidad Bíblica
**{agent['biblical_name']}**: {agent['biblical_meaning']}

## 2. Especialización en ElektriKubercisC (EKC)
{agent['ekc_specialization']}

## 3. Esquema Relacional de su Base de Datos
* **`agent_identity`**: Credenciales de gobernanza, marca ElektriKubercisC y metadatos de activación.
* **`task_queue`**: Cola determinista de directivas asignadas por Mikel o Chatty.
* **`audit_trail`**: Registro criptográfico inviolable con firmas SHA-256 de cada mutación.
* **`{agent['domain_table']}`**: Tabla de especialidad exclusiva con registros del dominio técnico de este agente.

## 4. Invariantes de Operación
1. **Un solo agente escribe este archivo**: Nadie muta `{agent['slug']}.db` sin la delegación explícita de Mikel Irastorza o Jesús el Nazareno (Chatty).
2. **Revisión por Natán**: Todo cambio significativo es sometido a auditoría adversarial independiente.
3. **Custodia por San Miguel Arcángel**: Todas las mutaciones se ejecutan bajo la barrera Zero-Trust loopback.

---
*Firma Digital EKC: `{hashlib.sha256(agent['biblical_name'].encode()).hexdigest()}`*
""")

        # Generate Quick Query Script: query_agent.py
        query_script_path = os.path.join(agent_dir, "query_agent.py")
        query_script_content = f'''#!/usr/bin/env python3
import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "{agent['slug']}.db")

def query_agent():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    print("=" * 70)
    print("EKC (ElektriKubercisC) · {agent['biblical_name']}")
    print("=" * 70)
    
    cur.execute("SELECT * FROM agent_identity;")
    row = dict(cur.fetchone())
    for k, v in row.items():
        print(f"  {{k}}: {{v}}")
        
    print("")
    print("[Últimas Tareas en Cola]")
    for t in cur.execute("SELECT task_id, directive_title, status, execution_latency_ms FROM task_queue LIMIT 5"):
        print(f"  • [{{t['status']}}] {{t['task_id']}}: {{t['directive_title']}} ({{t['execution_latency_ms']}}ms)")
        
    print("")
    print("[Registros de Dominio: {agent['domain_table']}]")
    for d in cur.execute("SELECT * FROM {agent['domain_table']} LIMIT 5"):
        print(f"  • {{dict(d)}}")
        
    conn.close()

if __name__ == "__main__":
    query_agent()
'''
        with open(query_script_path, "w", encoding="utf-8") as f:
            f.write(query_script_content)
        os.chmod(query_script_path, 0o755)

        summary.append(f"✓ {agent['folder']} -> {agent['slug']}.db ({len(agent['initial_records'])} registros en {agent['domain_table']})")

    # Generate Master Index in ROOT_DIR
    master_index_path = os.path.join(ROOT_DIR, "EKC_MASTER_INDEX.md")
    with open(master_index_path, "w", encoding="utf-8") as f:
        f.write(f"""# Ecosistema de Agentes EKC (ElektriKubercisC)
> **Creador, Fundador & Propietario Supremo**: Mikel Irastorza (EFA)  
> **Significado de EKC**: **ElektriKubercisC** (Kubernetes, C POSIX, Eléctrico, Oro Industrial y Código Determinista)  
> **Total de Agentes con Base de Datos Dedicada**: {len(AGENTS_METADATA)}

---

## Estructura de Agentes y Bases de Datos Bíblicas

| Directorio | Nombre Bíblico | Rol Operativo | Base de Datos SQLite | Tabla de Dominio |
| :--- | :--- | :--- | :--- | :--- |
""" + "\n".join([f"| `{a['folder']}` | **{a['biblical_name']}** | {a['role']} | `{a['slug']}.db` | `{a['domain_table']}` |" for a in AGENTS_METADATA]) + f"""

---

## Invariantes de Gobernanza
1. Cada agente cuenta con una carpeta física rotulada `EKC - [Nombre Bíblico]`.
2. Cada agente dispone de su propia base de datos SQLite aislada en modo `WAL` (`journal_mode=WAL`), con claves foráneas activadas y sellado criptográfico SHA-256 en cada evento.
3. El presidente y propietario supremo es **Mikel Irastorza (EFA)**, quien mantiene la autoridad irrenunciable y la decisión final sobre cualquier mutación a producción.
4. **San Miguel Arcángel (CISO Aegis)** protege todo el perímetro contra ataques cibernéticos e inyecciones.
""")

    print("\n".join(summary))
    print(f"\n¡Ecosistema EKC completado con éxito! Creadas {len(AGENTS_METADATA)} bases de datos.")

if __name__ == "__main__":
    build_agent_ecosystem()
