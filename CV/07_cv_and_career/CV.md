# CURRICULUM VITAE — LEAD SOFTWARE ENGINEER & SYSTEMS ARCHITECT

**MIKEL IRASTORZA**  
📍 Donostia / Gipuzkoa, Spain • Movilidad transfronteriza España–Francia & Remoto  
✉️ Email: mikel@novusmundus.com • 💻 GitHub: [github.com/novomundus2-cmyk](https://github.com/novomundus2-cmyk) • 🌐 Portfolio: [http://127.0.0.1:8765/portfolio.html](http://127.0.0.1:8765/portfolio.html)  
🌍 Idiomas: **Español (Nativo) · Français (C1 · Fluido profesional en fábrica y empresa en Francia) · English (B2/C1 · Fluido técnico en ingeniería de software e IA)**

---

## 1. RESUMEN PROFESIONAL EJECUTIVO (EXECUTIVE PROFILE)

> **Lead Software Engineer & Systems Architect** con mentalidad de constructor técnico de principio a fin (*Project-First Builder*). Especializado en arquitectura backend distribuida, motores de concurrencia y streaming de baja latencia, asentamiento contable ACID en doble entrada y orquestación jerárquica de agentes de IA autónomos.
>
> Mi disciplina y aversión al error nacen del entorno industrial físico (operación de células robotizadas de conformado de chapa e interpretación de planos CAD milimétricos con tolerancias de ±0.2 mm en **EPTA France**, Hendaye), trasladando esa misma tolerancia cero a la consistencia de memoria, contratos de datos deterministas y suites de testing automatizado (**44 tests unitarios y de integración continuos sin fallos en producción**). Trayectoria real contrastable en Francia (**EPTA France** y desarrollo de software corporativo en **Bayonne**), consultoría ferroviaria bilateral en **IRC** y banca comercial en **BBVA**.

---

## 2. PROYECTOS DE INGENIERÍA DE SOFTWARE & SISTEMAS (PURO PROGRAMADOR)

*Todo el conocimiento técnico respaldado con código en producción y suites de pruebas automatizadas.*

### 🚀 P1: Novus Capital & Trading Core v3.0 (Motor Algorítmico Cuantitativo)
* **Dominio / Rol:** *Low-Latency Backend, Concurrency & Machine Learning*
* **Stack Tecnológico:** `Python 3.14 · TensorFlow 2.22 · PostgreSQL 17 · Supabase RLS · SQLite ACID · WebSocket`
* **Arquitectura & Retos de Programación Resueltos:**
  * **Inferencia Profunda Continua Online:** Modelo de redes neuronales profundas con **TensorFlow 2.22 Keras** entrenado y adaptado en tiempo real con datos de streaming, complementado con detección algorítmica de desbalances institucionales SMC (Smart Money Concepts: Order Blocks, Fair Value Gaps FVG y Market Structure Shifts MSS).
  * **Pacioli Core Ledger (Doble Entrada Inviolable):** Asentamiento contable formal (Luca Pacioli: ∑ Debe = ∑ Haber) con bloqueos a nivel de fila `SELECT ... FOR UPDATE` ordenados lexicográficamente (`min(A, B) → max(A, B)`), eliminando deadlocks concurrentes por diseño y firmando cada bloque con un hash inmutable **SHA-256**.
  * **Microestructura de Libro de Órdenes (L2/L3):** Procesamiento en memoria de profundidad de mercado, cálculo analítico de micro-precios y enrutamiento de órdenes en mercados líquidos con latencia sub-milisegundo.

### 🤖 P2: Enjambre Jerárquico Distribuido de Agentes Autónomos
* **Dominio / Rol:** *Distributed Systems, AI Agents & Tool Protocol Integration*
* **Stack Tecnológico:** `Google Antigravity SDK · Ollama · Model Context Protocol (MCP) · Python AsyncIO · Vector RAG · SQLite WAL`
* **Arquitectura & Retos de Programación Resueltos:**
  * **Planificador Work-Stealing:** Orquestación concurrente de un enjambre de 9 a 16 agentes autónomos organizados por jerarquía funcional (Estratégico, Analista, Ejecutor, Auditor), manteniendo 1-2 micro-tareas activas por nodo para evitar colas saturadas y contención de hilos.
  * **Memoria Compartida Transaccional:** Almacén de conocimiento persistente en SQL (`ai_insights_registry`) con latencia inter-agente < 5 ms y trazas de razonamiento reproducibles y auditables.
  * **Tolerancia a Fallos & Protocolo MCP:** Estandarización de herramientas e interfaces externas mediante Model Context Protocol con balanceo de carga automático y conmutación por error ante caídas de proveedores LLM.

### 🌊 P3: Streaming Lakehouse Big Data & Arquitectura de Ingesta
* **Dominio / Rol:** *High-Throughput Data Engineering & Stream Processing*
* **Stack Tecnológico:** `Apache Kafka (KRaft) · Apache NiFi · PySpark Structured Streaming · Apache Iceberg · Parquet ZSTD`
* **Arquitectura & Retos de Programación Resueltos:**
  * **Dimensionamiento Matemático de Pipelines:** Diseño formal del flujo de eventos aplicando la **Ley de Little (L = λ·W)** y la **Teoría de Colas M/M/c** (factor de carga ρ ≤ 0.80), dimensionando buffers de memoria para procesar ráfagas de 45.000 eventos/seg sin desbordamientos OutOfMemory (OOM).
  * **Control de Contrapresión (Backpressure):** NiFi calibrado con umbrales estrictos de 10.000 objetos / 1 GB por cola de flujo y particionado determinista por clave en Kafka en modo KRaft (sin dependencia de ZooKeeper).
  * **Almacenamiento ACID:** Tablas Apache Iceberg sobre almacenamiento distribuido con compactación automática y compresión Parquet ZSTD.

### 🔬 P4: Physics CAD Engine, Nanoclústeres de Oro (Au₂₀) & Dinámica Molecular
* **Dominio / Rol:** *Computational Physics, Nanotechnology & Materials Modeling*
* **Stack Tecnológico:** `C++ · Python · SymPy · SciPy · Potencial Sutton-Chen / EAM · Sobolev Spaces H¹ · JAX · LSPR`
* **Arquitectura & Retos de Programación Resueltos:**
  * **Nanoclústeres de Oro (Au₂₀) & Plasmónica Superficial:** Simulación de potenciales de muchos cuerpos de Sutton-Chen y Embedded Atom Method (EAM) para mallas cristalinas FCC de oro. Cálculo del confinamiento cuántico del nanoclúster tetraédrico Au₂₀ (gap HOMO-LUMO de 1.77 eV, comportamiento semiconductor cuántico) y de la resonancia plasmónica superficial (LSPR a 525 nm, color rojo rubí de Faraday) aplicable a fototermia oncológica, catálisis verde de Haruta (-70 °C) y transporte electrónico balístico ($G_0 = 77.48\,\mu\text{S}$) en computación cuántica.
  * **Geometría Computacional de Chapa & Planos CAD:** Cálculo de tolerancias geométricas dimensionales (±0.2 mm), secuencias de plegado CNC y matrices analíticas de transformación para el desarrollo plano de chapa metálica.
  * **Resolución de EDPs 2D & Metrología Patrón:** Modelado y solución de ecuaciones en derivadas parciales en espacios de Sobolev H¹ con cota de error acotada, utilizando el parámetro de red inmutable del oro ($a = 4.078\,\text{Å}$) como regla atómica patrón de calibración.

### 📐 P5: Algoritmia Monoidal de Streaming & Detección de Anomalías O(1)
* **Dominio / Rol:** *Algebraic Stream Processing & Real-Time Anomaly Detection*
* **Stack Tecnológico:** `Python · Haskell (Semigroups) · Welford-Chan Algorithm · Estadísticos Robustos MAD`
* **Arquitectura & Retos de Programación Resueltos:**
  * **Monoide Paralelo de Welford-Chan:** Algoritmo asociativo para agregación continua de media y varianza en un único paso con memoria O(1), formalmente demostrado bajo las leyes monoidales asociativas.
  * **Filtro Inmune al Efecto de Enmascaramiento:** Detección de fraude y colapsos de red con **Z-Score Robusto con Desviación Absoluta de la Mediana (MAD)** (Z_rob = 295.76 frente al colapso del Z-Score clásico a 2.83).

### 🖥️ P6: Plataforma Web Reactiva & Telemetría en Tiempo Real
* **Dominio / Rol:** *Full-Stack Platform & High-Performance UI Telemetry*
* **Stack Tecnológico:** `TypeScript · JavaScript (ES2024) · WebSockets · HTML5 Canvas GPU · Starlette / NetGUI`
* **Arquitectura & Retos de Programación Resueltos:**
  * **Zero Bloat & Alta Reactividad:** Interfaz en Vanilla JS y renderizado en Canvas acelerado por GPU a 60 FPS estables con simulaciones físicas de partículas magnéticas y gráficos interactivos sin librerías sobrecargadas.
  * **Streaming Bidireccional:** Pipeline de WebSockets para telemetría en vivo de órdenes, latencia de base de datos y logs de auditoría contable.

---

## 3. EXPERIENCIA PROFESIONAL & RAÍCES INDUSTRIALES (100% VERÍDICA)

### **Lead Software Engineer & Systems Architect** — NovusMundus / Novus Capital
*Periodo: 2025 – Actualidad | Donostia / Gipuzkoa, España · Plataforma Propia*
* Dirección técnica y programación del motor institucional **Trading Core v3.0**, APIs de streaming y arquitectura de agentes con suite de **44 tests unitarios y de integración continuos** ejecutándose sin fallos.
* Implementación del sistema contable en doble entrada con firmas de bloque criptográficas SHA-256 en PostgreSQL 17 y Supabase RLS.

### **Consultoría Comercial Técnica & Movilidad Ferroviaria PMR** — IRC (International Railway Consulting)
*Periodo: 2026 | España & Francia · Sector Ferroviario Industrial*
* Desarrollo de negocio técnico bilingüe (Francia–España) para proyectos de accesibilidad y movilidad para personas con movilidad reducida (PMR) en material rodante e infraestructuras.
* Negociación e interlocución técnica directa con oficinas de métodos, ingenieros de planta y fabricantes asegurando normativas técnicas europeas.

### **Desarrollador de Software y Aplicaciones Web** — Empresa Tecnológica
*Periodo: 2023 – 2024 (~2 años) | Bayonne, Nouvelle-Aquitaine, Francia*
* Desarrollo full-stack de arquitecturas web, integración de servicios backend, APIs REST y bases de datos relacionales en entorno corporativo francófono.
* Optimización de rendimiento en producción, resolución de incidencias en ciclo ágil y consolidación de fluidez técnica profesional en francés.

### **Técnico de Fabricación, Células Robóticas & Conformado de Chapa (Tôlerie)** — EPTA France
*Periodo: 2022 – 2023 | Hendaye, Nouvelle-Aquitaine, Francia · Planta de Refrigeración Comercial*
* **Interpretación rigurosa de planos técnicos:** Lectura y aplicación de planos mecánicos y esquemas de fabricación CAD diédricos (cotas dimensionales milimétricas ±0.2 mm, espesores de chapa, secuencias y radios de curvatura) para componentes y cerramientos de muebles frigoríficos comerciales e industriales.
* **Operación y control de células robóticas de chapa:** Trabajo en la nave industrial de conformado (*atelier de tôlerie / parte trasera de la planta*), operando, alimentando y supervisando células automatizadas y robotizadas de punzonado, corte y prensas plegadoras CNC de chapa metálica.
* **Control metrológico y Lean Manufacturing:** Verificación dimensional continua pieza a pieza contra plano técnico con calibres digitales, goniómetros y micrómetros antes del envío a pintura y ensamblaje final. Coordinación en francés técnico bajo estándares 5S.

### **Banca Comercial & Asesoramiento Financiero** — BBVA
*Periodo: 2021 – 2022 (~1 año) | España · Sector Bancario y Financiero*
* Atención directa a clientes particulares y empresas, análisis de solvencia, evaluación de riesgos crediticios y productos de inversión.
* Base de rigurosidad financiera y cumplimiento normativo que hoy vertebra el diseño cuantitativo de plataformas como Novus Capital y la senda **EIP/EFA**.

---

## 4. MATRIZ DE COMPETENCIAS TÉCNICAS (PURO PROGRAMADOR)

| Área de Ingeniería | Tecnologías y Herramientas en Producción |
| :--- | :--- |
| **Lenguajes de Programación** | **Python 3.14** (AsyncIO, CPython, Pydantic, NumPy), **TypeScript**, **JavaScript (ES2024)**, **C++**, **C11**, **SQL**, **Bash**, Haskell (álgebra monoidal). |
| **Backend & Concurrencia** | AsyncIO, Starlette, Multiprocessing, WebSockets, Worker Pools, Work-Stealing Task Scheduler, Locks lexicográficos (Zero Deadlocks), APIs RESTful. |
| **Bases de Datos & Almacenamiento** | **PostgreSQL 17** (Triggers, RLS, CTEs, Índices BRIN/B-Tree), **SQLite WAL** (ACID, PRAGMA query_only), Supabase Auth/RLS, **Apache Iceberg**, MinIO / S3. |
| **Big Data & Streaming** | **Apache Kafka (KRaft)**, **Apache NiFi** (Backpressure 10k/1GB), **PySpark Structured Streaming**, Parquet ZSTD, Ley de Little (L = λ·W). |
| **Inteligencia Artificial & ML** | **Google Antigravity SDK**, **TensorFlow 2.22 Keras** (Online Learning), Ollama (DeepSeek/Llama), Protocolo **MCP**, Gemini Flash, RAG Vectorial. |
| **DevOps & Metodología** | Docker, Git/GitHub, Linux (Ubuntu/Debian), **Pytest (44 tests pasando al 100%)**, Dinámica Molecular (Sutton-Chen Au₂₀), Lean 5S, Clean Code. |

---

## 5. PRINCIPIOS DE INGENIERÍA & DEFENSA TÉCNICA EN ENTREVISTAS

1. **¿Por qué un perfil con experiencia de taller industrial y planos en EPTA France es una ventaja radical en software?**
   > *"En el taller de chapa de EPTA France aprendí que un error de 0.2 mm en un plano o en el tope de una plegadora CNC destroza una pieza o colisiona la máquina. Esa disciplina física la traslado directamente a mis contratos de software: si un dato o payload viola su esquema de validación, se rechaza de inmediato antes de contaminar la memoria o la base de datos."*

2. **¿Cómo garantiza tu motor que nunca se pierda un céntimo en operaciones de alta concurrencia?**
   > *"Implementé un ledger de doble entrada estricta (Luca Pacioli: ∑ Debe = ∑ Haber) en PostgreSQL. Para evitar deadlocks y carreras críticas, bloqueamos las cuentas involucradas usando `SELECT ... FOR UPDATE` ordenadas lexicográficamente (`min(A, B) → max(A, B)`), y sellamos cada bloque con un hash SHA-256 encadenado."*

3. **¿Por qué usar el Monoide de Welford-Chan y MAD en lugar de cálculos estándar en streaming?**
   > *"Porque los algoritmos tradicionales de dos pasos exigen almacenar todo el historial (rompiendo la memoria O(1)) o son vulnerables al efecto de enmascaramiento donde un dato falso infla la varianza. Con Welford-Chan la agregación es asociativa y paralelizable en un paso, y con el MAD escalado (1.4826 · MAD) el estimador detecta anomalías al instante sin distorsión."*
