# MIKEL IRASTORZA · DOSSIER CURRICULAR DE INGENIERÍA
**Lead Software Engineer & Systems Architect · Concurrency, Backend & Applied AI**  
📍 Donostia / Gipuzkoa, Spain | 💻 GitHub: [github.com/novomundus2-cmyk](https://github.com/novomundus2-cmyk) | ✉️ Email: mikel@novusmundus.com | 🌐 Portfolio: [http://127.0.0.1:8765/portfolio.html](http://127.0.0.1:8765/portfolio.html)  
🌍 Idiomas: **Español (Nativo) · Français (C1 · Fluido profesional en fábrica y oficina en Francia) · English (B2/C1 · Fluido técnico en ingeniería de software e IA)**

---

## 1. PERFIL PROFESIONAL EJECUTIVO

Ingeniero de software sénior y constructor de sistemas ("Project-First Builder") especializado en arquitectura de backend distribuido, motores de concurrencia y streaming de baja latencia, asentamiento contable ACID de doble entrada y enjambres jerárquicos de agentes IA.

Mi disciplina técnica y rigor sin concesiones nacen de la precisión industrial física (operación de células robóticas de conformado de chapa y planos CAD con tolerancias de ±0.2 mm en **EPTA France**, Hendaye), trasladando esa misma aversión al error a la consistencia de memoria, contratos de datos deterministas y suites de tests automatizados (**44 tests sin fallos en producción**). Trayectoria real demostrable en Francia (**EPTA France** y desarrollo de software corporativo en **Bayonne**), consultoría técnica ferroviaria bilateral en **IRC** y banca comercial en **BBVA**.

---

## 2. PROYECTOS INSIGNIA EN PRODUCCIÓN (PURO PROGRAMADOR)

*Todo el conocimiento técnico está respaldado con código en ejecución, arquitecturas modulares y suites de tests automatizados.*

### 🚀 Proyecto 1 · Novus Capital & Trading Core v3.0 (Motor Algorítmico Cuantitativo)
- **Dominio / Rol:** *Low-Latency Backend, Concurrency & Machine Learning*
- **Stack:** `Python 3.14 · TensorFlow 2.22 · PostgreSQL 17 · Supabase RLS · SQLite ACID · WebSocket`
- **Retos de Programación Resueltos:**
  - **Inferencia Profunda Continua Online:** Modelo de redes neuronales profundas con **TensorFlow 2.22 Keras** entrenado y adaptado en tiempo real con datos de streaming, complementado con detección algorítmica de desbalances institucionales SMC (Smart Money Concepts: Order Blocks, Fair Value Gaps FVG y Market Structure Shifts MSS).
  - **Pacioli Core Ledger (Doble Entrada Inviolable):** Asentamiento contable formal (Luca Pacioli: ∑ Debe = ∑ Haber) con bloqueos a nivel de fila `SELECT ... FOR UPDATE` ordenados lexicográficamente (`min(A, B) → max(A, B)`), eliminando deadlocks concurrentes por diseño y firmando cada bloque con un hash inmutable **SHA-256**.
  - **Microestructura L2/L3:** Cálculo de micro-precios, profundidad acumulada de libro de órdenes y latencia sub-milisegundo en mercados líquidos.

### 🤖 Proyecto 2 · Enjambre Jerárquico Distribuido de Agentes Autónomos
- **Dominio / Rol:** *Distributed Multi-Agent Architecture & Tool Protocol Integration*
- **Stack:** `Google Antigravity SDK · Ollama · Model Context Protocol (MCP) · Python AsyncIO · Vector RAG · SQLite WAL`
- **Retos de Programación Resueltos:**
  - **Planificador Work-Stealing:** Orquestación concurrente de un enjambre de 9 a 16 agentes autónomos organizados por jerarquía funcional (Estratégico, Analista, Ejecutor, Auditor), manteniendo 1-2 micro-tareas activas por nodo para evitar colas saturadas y contención de hilos.
  - **Memoria Compartida Transaccional:** Almacén de conocimiento persistente en SQL (`ai_insights_registry`) con latencia inter-agente < 5 ms y trazas de razonamiento reproducibles y auditables.
  - **Tolerancia a Fallos & Protocolo MCP:** Estandarización de herramientas e interfaces externas mediante Model Context Protocol con balanceo de carga automático y conmutación por error ante caídas de proveedores LLM.

### 🌊 Proyecto 3 · Streaming Lakehouse Big Data & Arquitectura de Ingesta
- **Dominio / Rol:** *High-Throughput Data Engineering & Stream Processing*
- **Stack:** `Apache Kafka (KRaft) · Apache NiFi · PySpark Structured Streaming · Apache Iceberg · Parquet ZSTD`
- **Retos de Programación Resueltos:**
  - **Dimensionamiento Matemático de Pipelines:** Diseño formal del flujo de eventos aplicando la **Ley de Little (L = λ·W)** y la **Teoría de Colas M/M/c** (factor de carga ρ ≤ 0.80), dimensionando buffers de memoria para procesar ráfagas de 45.000 eventos/seg sin desbordamientos OutOfMemory (OOM).
  - **Control de Contrapresión (Backpressure):** NiFi calibrado con umbrales estrictos de 10.000 objetos / 1 GB por cola de flujo y particionado determinista por clave en Kafka en modo KRaft (sin dependencia de ZooKeeper).
  - **Almacenamiento ACID:** Tablas Apache Iceberg sobre almacenamiento distribuido con compactación automática y compresión Parquet ZSTD.

### 🔬 Proyecto 4 · Physics CAD Engine, Nanoclústeres de Oro (Au₂₀) & Dinámica Molecular
- **Dominio / Rol:** *Computational Physics, Nanotechnology & Materials Modeling*
- **Stack:** `C++ · Python · SymPy · SciPy · Potencial Sutton-Chen / EAM · Sobolev Spaces H¹ · JAX · LSPR`
- **Retos de Programación Resueltos:**
  - **Nanoclústeres de Oro (Au₂₀) & Plasmónica Superficial:** Simulación de potenciales interatómicos de muchos cuerpos Sutton-Chen y EAM para mallas cristalinas de oro. Determinación del confinamiento cuántico del nanoclúster tetraédrico Au₂₀ (gap HOMO-LUMO de 1.77 eV) y de la resonancia plasmónica superficial (LSPR a 525 nm, color rojo rubí de Faraday) aplicable a fototermia tumoral, catálisis verde de Haruta (-70 °C) y transporte cuántico balístico ($G_0 = 77.48\,\mu\text{S}$).
  - **Geometría Computacional de Chapa & Planos CAD:** Cálculo de tolerancias geométricas (±0.2 mm), secuencias de plegado CNC y matrices analíticas de transformación para desarrollos de chapa metálica.
  - **Resolución de EDPs 2D & Metrología Patrón:** Modelado y solución de ecuaciones en derivadas parciales en espacios de Sobolev H¹, utilizando el parámetro de red inmutable del oro ($a = 4.078\,\text{Å}$) como patrón absoluto de calibración física.

### 📐 Proyecto 5 · Algoritmia Monoidal de Streaming & Detección de Anomalías O(1)
- **Dominio / Rol:** *Algebraic Stream Processing & Real-Time Anomaly Detection*
- **Stack:** `Python · Haskell (Semigroups) · Welford-Chan Algorithm · Estadísticos Robustos MAD`
- **Retos de Programación Resueltos:**
  - **Monoide Paralelo de Welford-Chan:** Algoritmo asociativo para agregación continua de media y varianza en un único paso con memoria O(1), formalmente demostrado bajo las leyes monoidales asociativas.
  - **Filtro Inmune al Efecto de Enmascaramiento:** Detección de fraude y colapsos de red con **Z-Score Robusto con Desviación Absoluta de la Mediana (MAD)** (Z_rob = 295.76 frente al colapso del Z-Score clásico a 2.83).

### 🖥️ Proyecto 6 · Plataforma Web Reactiva & Telemetría en Tiempo Real
- **Dominio / Rol:** *Full-Stack Platform & High-Performance UI Telemetry*
- **Stack:** `TypeScript · JavaScript (ES2024) · WebSockets · HTML5 Canvas GPU · Starlette / NetGUI`
- **Retos de Programación Resueltos:**
  - **Zero Bloat & Alta Reactividad:** Interfaz en Vanilla JS y renderizado en Canvas acelerado por GPU a 60 FPS estables con simulaciones físicas de partículas magnéticas y gráficos interactivos sin librerías sobrecargadas.
  - **Streaming Bidireccional:** Pipeline de WebSockets para telemetría en vivo de órdenes, latencia de base de datos y logs de auditoría contable.

---

## 3. TRAYECTORIA LABORAL CRONOLÓGICA & RAÍCES INDUSTRIALES (100% VERÍDICA)

- **Lead Software Engineer & Systems Architect — NovusMundus / Novus Capital (2025 – Actualidad):**
  Dirección técnica y programación del motor institucional **Trading Core v3.0**, APIs de streaming y arquitectura de agentes con suite de **43 tests unitarios y de integración continuos** ejecutándose sin fallos. Implementación del sistema contable en doble entrada con firmas de bloque criptográficas SHA-256 en PostgreSQL 17 y Supabase RLS.
- **Consultoría Comercial Técnica & Movilidad Ferroviaria PMR — IRC International Railway Consulting (España & Francia, 2026):**
  Desarrollo de negocio técnico bilingüe (Francia–España) para proyectos de accesibilidad y movilidad para personas con movilidad reducida (PMR) en material rodante e infraestructuras. Negociación e interlocución técnica directa con oficinas de métodos, ingenieros de planta y fabricantes asegurando normativas técnicas europeas.
- **Desarrollador de Software y Aplicaciones Web — Empresa Tecnológica (Bayonne, Francia, 2023 – 2024 · ~2 años):**
  Desarrollo full-stack de arquitecturas web, integración de servicios backend, APIs REST y bases de datos relacionales en entorno corporativo francófono. Optimización de rendimiento en producción, resolución de incidencias en ciclo ágil y consolidación de fluidez técnica profesional en francés.
- **Técnico de Fabricación, Células Robóticas & Conformado de Chapa (Tôlerie) — EPTA France (Hendaye, Francia, 2022 – 2023):**
  En la nave industrial de conformado de chapa (*atelier de tôlerie / parte trasera de la planta*):
  - **Interpretación rigurosa de planos técnicos:** Lectura y aplicación de planos mecánicos y esquemas de fabricación CAD diédricos (cotas dimensionales milimétricas ±0.2 mm, espesores de chapa, secuencias y radios de curvatura) para componentes y cerramientos de muebles frigoríficos comerciales e industriales.
  - **Operación y control de células robóticas de chapa:** Configuración, alimentación y supervisión de células automatizadas y robotizadas de punzonado, corte y prensas plegadoras CNC de chapa metálica.
  - **Control metrológico y Lean Manufacturing:** Verificación dimensional continua pieza a pieza contra plano técnico con calibres digitales, goniómetros y micrómetros antes del envío a pintura y ensamblaje final. Coordinación en francés técnico bajo estándares 5S.
- **Banca Comercial & Asesoramiento Financiero — BBVA (España, 2021 – 2022 · ~1 año):**
  Atención directa a clientes particulares y empresas, análisis de solvencia, evaluación de riesgos crediticios y productos de inversión. Base de rigor financiero que hoy vertebra el diseño cuantitativo de plataformas como Novus Capital y la preparación de la senda **EIP/EFA**.

---

## 4. STACK TÉCNICO & MATRIZ DE COMPETENCIAS (PURO PROGRAMADOR)

- **Lenguajes:** Python 3.14 (AsyncIO, CPython, Pydantic, NumPy), TypeScript, JavaScript (ES2024), C++, C11, SQL (PostgreSQL, SQLite), Bash scripting.
- **Backend & Concurrencia:** AsyncIO, Multiprocessing, Starlette, WebSockets, Worker Pools, Work-Stealing Task Scheduler, Locks lexicográficos (Zero Deadlocks), APIs RESTful.
- **Bases de Datos & Almacenamiento:** PostgreSQL 17 (Triggers, RLS, CTEs, BRIN/B-Tree), SQLite WAL (ACID, PRAGMA query_only), Supabase Auth/RLS, Apache Iceberg, MinIO / S3.
- **Big Data & Streaming:** Apache Kafka (KRaft), Apache NiFi (Backpressure 10k/1GB), PySpark Structured Streaming, Parquet ZSTD, Ley de Little (L = λ·W), Teoría de Colas M/M/c.
- **Inteligencia Artificial & ML:** Google Antigravity SDK, TensorFlow 2.22 Keras (Online Learning), Ollama (DeepSeek/Llama), Protocolo MCP, Gemini Flash, RAG Vectorial.
- **DevOps & Testing:** Docker, Git/GitHub, Linux (Ubuntu/Debian), **Pytest (44 tests pasando al 100%)**, Dinámica Molecular (Sutton-Chen Au₂₀), Lean 5S, Clean Code.
