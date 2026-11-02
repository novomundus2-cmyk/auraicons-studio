# ⚡ Enterprise Data Platform, Haskell/Python Mathematical Streaming & BigQuery AI/ML

[![Apache Spark](https://img.shields.io/badge/Apache%20Spark-3.5.0-E25A1C?logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-KRaft%20Mode-231F20?logo=apachekafka&logoColor=white)](https://kafka.apache.org/)
[![Apache NiFi](https://img.shields.io/badge/Apache%20NiFi-1.24.0-729B1B?logo=apachenifi&logoColor=white)](https://nifi.apache.org/)
[![Python](https://img.shields.io/badge/Python-3.14%20(SymPy%20%7C%20SciPy%20%7C%20Polars)-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Haskell](https://img.shields.io/badge/Haskell-Monoids%20%26%20Streaming%20Algebra-5D4F85?logo=haskell&logoColor=white)](https://www.haskell.org/)
[![BigQuery AI/ML](https://img.shields.io/badge/BigQuery%20AI%2FML-TimesFM%202.0%20%26%20Gemini%202.5-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/bigquery)

Repositorio de **Ingeniería de Plataformas de Datos, Despliegue y Matemática Funcional** organizado por categorías numeradas para portfolio profesional, producción y docencia magistral.

---

## 📁 Estructura Categorizada del Proyecto (`CV/`)

```text
CV/
├── 01_notebooks/                                  # 🎓 Academia en Gemini Notebooks (.ipynb)
│   ├── 01_big_data_deployment_masterclass.ipynb   # Kafka KRaft, NiFi, PySpark, K8s & ArgoCD
│   ├── 02_math_haskell_python_foundations.ipynb   # Monoides Haskell, SymPy, MAD Z-Score & Ley de Little
│   └── 03_bigquery_ai_ml_database.ipynb           # BigQuery AI/ML (TimesFM 2.0 & Gemini 2.5 Flash)
│
├── 02_streaming_platform/                         # ⚡ Ingesta & Procesamiento en Tiempo Real
│   ├── producers/
│   │   ├── requirements.txt
│   │   └── transaction_producer.py                # Productor Kafka conectado a dim_users y dim_merchants
│   ├── spark_jobs/
│   │   └── streaming_processor.py                 # PySpark Structured Streaming -> SQLite Sink
│   └── nifi/
│       └── README.md                              # Flujos de ingesta y Backpressure en NiFi
│
├── 03_math_haskell_python/                        # 📐 Motor Matemático (Haskell + Python Científico)
│   ├── StreamingMath.hs                           # Monoides Welford-Chan, Entropía de Shannon y M/M/c
│   └── scientific_analytics.py                    # Pruebas simbólicas SymPy, SciPy y Polars Arrow
│
├── 04_database_lakehouse/                         # 🗄️ Base de Datos Maestra & Categorías Exportadas
│   ├── build_database.py                          # Generador del Esquema en Estrella (25,000 filas)
│   ├── financial_lakehouse.db                     # Base de datos SQLite unificada
│   └── categories/                                # Exportaciones JSON categorizadas para inspección
│       ├── 01_dimensions/                         # dim_users.json, dim_merchants.json
│       ├── 02_gold_analytics/                     # gold_category_metrics.json, vw_fraud_alerts.json
│       ├── 03_knowledge_formulas/                 # kb_mathematical_formulas.json (LaTeX + Haskell + Python)
│       ├── 04_interview_defense/                  # kb_interview_defense.json (War Stories & Respuestas Senior)
│       └── 05_cv_portfolio/                       # kb_cv_portfolio.json (Impacto y métricas del CV)
│
├── 05_archify_visualizer/                         # 🖥️ Visualizador Interactivo en Tiempo Real
│   └── index.html                                 # Archify Studio con KaTeX, curva SVG M/M/c y Pizarra Docente
│
├── 06_ai_note_agent/                              # 🤖 Agente IA de Notas (Google Antigravity SDK + uv)
│   ├── agent.py                                   # Crea/sincroniza Gemini Notebooks y consulta la BD
│   └── pyproject.toml                             # Entorno Python 3.14 gestionado con uv
│
├── 07_cv_and_career/                              # 📄 Currículum Vitae & Manual de Defensa Técnica
│   └── CV.md                                      # Plantilla de CV de alto impacto y guía de entrevista
│
├── docker-compose.yml                             # 🐳 Clúster Kafka KRaft, NiFi, Spark Master/Worker, MinIO
├── Makefile                                       # 🛠️ Comandos rápidos en 1 paso
└── README.md                                      # 🏛️ Documentación general del repositorio
```

`10_learning_pipeline/` es el puntero al pipeline de estudio (CFA TBS + Data Engineer) del study pack. No duplica el currículo.

---

## 🚀 Comandos Rápidos (`Makefile`)

* **`make archify`** — Abre el visualizador interactivo **Archify Studio** (`05_archify_visualizer/index.html`).
* **`make db`** — Construye `04_database_lakehouse/financial_lakehouse.db` y exporta todas las subcarpetas de `04_database_lakehouse/categories/`.
* **`make math`** — Ejecuta las demostraciones simbólicas (`SymPy`) y estadísticas (`SciPy`, `NumPy`, `Polars`).
* **`make notes`** — Lanza el Agente de Notas IA (`google-antigravity` SDK).
* **`make up` / `make producer` / `make spark`** — Levanta Kafka KRaft, NiFi, Spark y MinIO y procesa streaming en vivo.
