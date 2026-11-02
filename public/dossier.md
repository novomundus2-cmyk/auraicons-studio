# DOSSIER MAESTRO PARA GEMINI NOTEBOOK (NOTEBOOKLM)
## MIKEL · NOVUSMUNDUS — DATA & AI SYSTEMS ARCHITECT & PRODUCT BUILDER
**Ubicación:** Donostia / Gipuzkoa, Spain  
**GitHub:** github.com/novomundus2-cmyk  
**Idiomas de Trabajo:** Español (Nativo) · Français (Fluido profesional, ~2 años en Bayonne + Ventas técnicas industriales España-Francia) · English (Fluido técnico en ingeniería y documentación)  
**Trayectoria y Enfoque:** 100% constructor autodidacta sin titulitis académica. Dominio técnico demostrado mediante sistemas en producción, proyectos reales de extremo a extremo, automatización, IA jerárquica y finanzas aplicadas.

---

## 1. RESUMEN EJECUTIVO Y PERFIL DE INGENIERO
Constructor de software y arquitecto de sistemas de datos enfocado en pipelines de streaming en tiempo real, plataformas analíticas financieras, enjambres jerárquicos de agentes de inteligencia artificial y computación distribuida de alto rendimiento.

Todo mi conocimiento técnico está respaldado por código verificado en repositorios y arquitecturas funcionando:
1. **Pipelines de Big Data Resilientes:** Ingesta con Apache NiFi y control de Backpressure, buses distribuidos con Apache Kafka en modo KRaft dimensionados con Teoría de Colas ($M/M/c$) y Ley de Little, procesamiento en micro-batches y streaming continuo con PySpark y Polars (motor Apache Arrow en Rust), y Lakehouses abiertos con Apache Iceberg (formato Parquet con compresión ZSTD y garantías transaccionales ACID).
2. **Infraestructura Jerárquica de Agentes IA:** Orquestación de agentes con memoria compartida auditable en SQL (`ai_insights_registry`), roles especializados y balanceo de carga mediante *Work-Stealing* (manteniendo 1 a 2 tareas por agente para minimizar la latencia), combinando inferencia local (Ollama, RAG, embeddings y protocolo MCP) con modelos fundacionales en la nube (Gemini 2.5 Flash, TimesFM 2.0 y Antigravity SDK).
3. **Validación Matemática y Algorítmica Senior:** Implementación de agregaciones algebraicas en una sola pasada asociativa con el *Monoide de Welford-Chan* (evitando cancelación catastrófica de coma flotante IEEE 754 con memoria $O(1)$) y escudos antifraude con *Mediana y MAD* (Desviación Absoluta Mediana) con un 50% de punto de ruptura, inmunes al efecto de enmascaramiento que sufren los modelos clásicos de media y varianza.
4. **Física Computacional y Simulación Energética:** Simulación de consumo eléctrico desde primeros principios físicos ($W \to kW \to kWh \to €$) con optimización en tuplas empaquetadas en C (`NamedTuple`) y resolución analítica exacta según tarifas contratadas.

---

## 2. MAPA DE CONOCIMIENTO TÉCNICO APLICADO EN PROYECTOS

### PROYECTO 1 · Novus Capital / NovusMundus — AI & Finance Platform
* **Áreas:** Backend, Bases de Datos Relacionales, Seguridad RLS, Finanzas Cuantitativas e IA.
* **Tecnologías:** Python, React, TypeScript, PostgreSQL, Supabase (Autenticación, Row-Level Security / RLS, migraciones, índices y restricciones relacionales), SQLite ACID (25.000 transacciones y 5,34 M€ auditados).
* **Conocimiento Aplicado:**
  - Diseño de bases de datos transaccionales y analíticas con políticas estrictas de seguridad por fila (RLS).
  - Implementación del Monoide de Welford-Chan para calcular medias y varianzas de carteras en tiempo constante $O(1)$.
  - Algoritmo Z-Score Robusto con Mediana y MAD ($Z_{\text{rob}} = 295.76$ frente a $Z_{\text{clásico}} = 2.83$), detectando anomalías que la media inflada oculta.
  - Conocimiento profundo de mercados, valoración de empresas, análisis macroeconómico y productos financieros derivado de la formación en la senda **EIP / EFA**.

### PROYECTO 2 · Hierarchical AI Agent Infrastructure (Enjambre Multi-Agente)
* **Áreas:** Inteligencia Artificial Aplicada, Orquestación de Agentes, LLMs Locales y Cloud.
* **Tecnologías:** Ollama, RAG (Retrieval-Augmented Generation), Embeddings vectoriales, Model Context Protocol (MCP), Tool Use, Gemini 2.5 Flash, TimesFM 2.0 (Google Research), Antigravity SDK.
* **Conocimiento Aplicado:**
  - Arquitectura multi-agente donde cada agente tiene una función atómica (Ingesta, Validación Matemática, Detección de Fraude, Compactación de Almacén, Pronóstico de Series Temporales y Diagnóstico de Causa Raíz).
  - Protocolo *Work-Stealing*: los agentes que finalizan su cola roban automáticamente tareas a los agentes sobrecargados para mantener el principio de eficiencia óptimo (1 a 2 tareas por trabajador).
  - Memoria compartida estructurada y auditable en base de datos (`ai_insights_registry`) para trazabilidad de cada decisión algorítmica.

### PROYECTO 3 · Physics CAD Lab & Calculadora Energética de Alta Eficiencia
* **Áreas:** Física Aplicada, Python Científico, C/C++, Simulación de Restricciones y Testing.
* **Tecnologías:** Python 3.14 Clean Code, C, C++, Haskell, NumPy, SciPy, SymPy, Polars, pandas, Matplotlib, flujos CAD/CAE, pytest.
* **Conocimiento Aplicado:**
  - Modelado de consumo eléctrico real para optimizar facturas: despeje de potencia instantánea en Vatios ($W$) a kilovatios ($kW$), integración temporal a kilovatios-hora ($kWh$) y cálculo financiero según contratos reales (Caso verificado: tarifa de **0,1329 €/kWh** para una factura de **137,00 €** equivale a **1.030,85 kWh/mes** y **1.431,8 W continuos las 24 horas**).
  - Optimización de código con tuplas en C (`NamedTuple`) y bucles fusionados, logrando una reducción del **80,4% en memoria RAM** y un aumento del **69,6% en velocidad de CPU** (de 119,8 ms a 36,4 ms en 50.000 iteraciones).
  - Verificación formal de teoremas algebraicos con SymPy y testing unitario exhaustivo con pytest.

### PROYECTO 4 · Archify Streaming Lakehouse, Servidor Multi-PC LAN & AuraIcons Studio
* **Áreas:** Ingeniería de Datos Distribuida, Infraestructura de Red Local, Docker, Linux y Experiencia de Usuario.
* **Tecnologías:** Apache NiFi, Apache Kafka (KRaft), PySpark Structured Streaming, Apache Iceberg, BigQuery (DTS & Property Graph GQL), Docker, Linux, Servidor LAN (`0.0.0.0:8765`), sincronización con NAS RAID y React a 60 FPS.
* **Conocimiento Aplicado:**
  - Configuración de servidores centrales para conectar múltiples equipos en red local y replicar automáticamente datos a sistemas de almacenamiento masivo NAS con tolerancia a fallos.
  - Implementación del concepto de **Fraccionamiento Cognitivo**: interfaces diseñadas para que cualquier usuario, cliente o director entienda la arquitectura paso a paso pulsando conceptos interactivos.

---

## 3. ARQUITECTURA DEL PIPELINE DE STREAMING (6 ETAPAS)

```
[Fuentes Heterogéneas / APIs / Sensores / LAN Multi-PC]
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│  ETAPA 1: Apache NiFi (Ingesta en el Borde & Backpressure) │
│  - 3 Repositorios en disco: FlowFile, Content, Provenance│
│  - Umbral de Backpressure: 10.000 objetos / 1 GB          │
│  - Desacoplamiento total para evitar colapsos por OOM    │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│  ETAPA 2: Apache Kafka en Modo KRaft (Buffer Distribuido) │
│  - Eliminación de ZooKeeper mediante consenso Raft       │
│  - Particionado determinista con murmur2(clave)          │
│  - Dimensionamiento con Teoría de Colas M/M/c (ρ < 0.80) │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│  ETAPA 3: PySpark & Polars (Motor Vectorizado SIMD)      │
│  - Procesamiento Arrow en memoria sin bloqueo            │
│  - Watermarking de 10 minutos para eventos tardíos       │
│  - Detección de Data Skew y Salting con Entropía Shannon │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│  ETAPA 4: Validación Matemática & Estadística Robusta     │
│  - Monoide de Welford-Chan: media y varianza en O(1)     │
│  - Z-Score Robusto con Mediana y MAD (Punto ruptura 50%) │
│  - Inmunidad total al Efecto de Enmascaramiento          │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│  ETAPA 5: Open Data Lakehouse (Apache Iceberg & Parquet) │
│  - Transacciones ACID y aislamiento de snapshots         │
│  - Compactación de micro-batches a bloques de 256 MB     │
│  - Eliminación del Small Files Problem sobre almacenamiento│
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│  ETAPA 6: Capa Analítica, Grafos BigQuery & 3 IAs        │
│  - BigQuery GQL Property Graph (25.000 aristas trazadas) │
│  - TimesFM 2.0: pronóstico temporal de series a 14 días │
│  - Gemini 2.5 Flash: diagnóstico de causa raíz           │
│  - Antigravity SDK: orquestador de agentes en paralelo   │
└──────────────────────────────────────────────────────────┘
```

---

## 4. FUNDAMENTOS MATEMÁTICOS Y FÓRMULAS CLAVE

### A. Monoide de Welford-Chan (Media y Varianza Paralela en $O(1)$)
Para fusionar dos particiones independientes $A$ y $B$ de transacciones:
$$n_{AB} = n_A + n_B$$
$$\mu_{AB} = \mu_A + \frac{n_B}{n_{AB}} (\mu_B - \mu_A)$$
$$M2_{AB} = M2_A + M2_B + (\mu_B - \mu_A)^2 \cdot \frac{n_A \cdot n_B}{n_{AB}}$$
$$\sigma^2 = \frac{M2_{AB}}{n_{AB}}$$
* **Ventaja:** Requiere una sola lectura de datos, mantiene precisión numérica IEEE 754 y permite paralelización masiva en clúster.

### B. Z-Score Robusto con Mediana y MAD (Inmune a Outliers Gigantes)
$$\text{MAD} = \text{mediana}(|X - \text{mediana}(X)|)$$
$$Z_{\text{robusto}} = \frac{|x - \text{mediana}(X)|}{1.4826 \cdot \text{MAD}}$$
* **Ventaja:** La media clásica se desplaza ante un fraude masivo inflando la desviación típica y ocultando la anomalía ($Z < 3$). El MAD resiste hasta un 50% de datos contaminados.

### C. Teoría de Colas ($M/M/c$) y Ley de Little para Streaming
$$\rho = \frac{\lambda}{c \cdot \mu} < 0.80$$
$$L = \lambda \cdot W$$
* $\lambda$: tasa de llegada de eventos.
* $c$: número de núcleos o particiones en Kafka/Spark.
* $\mu$: capacidad de procesamiento por partición.
* $L$: número medio de paquetes en cola.
* $W$: tiempo medio de espera.
* **Ventaja:** Garantiza que el retardo (*Consumer Lag*) no crezca hacia el infinito en picos de tráfico.

### D. Entropía de Shannon para Detección de Data Skew
$$H(X) = -\sum_{i=1}^{n} P(x_i) \log_2 P(x_i)$$
* **Ventaja:** Permite medir cuantitativamente si el tráfico se distribuye uniformemente o si una sola partición acumula desproporcionadamente la carga, activando la técnica de *Salting* automáticamente.

### E. Despeje Físico y Financiero del Caso Energético Real
$$E_{\text{mes}} = \frac{\text{Factura (€)}}{\text{Tarifa (€/kWh)}} = \frac{137.00}{0.1329} = 1\,030.85\text{ kWh/mes}$$
$$P_{\text{media 24h}} = \frac{1\,030.85\text{ kWh}}{720\text{ h}} = 1.4318\text{ kW } (1\,431.8\text{ W continuos})$$
* **Desglose de los 7 consumidores auditados:**
  1. Termo Eléctrico / Calefacción ($2.000\text{ W} \times 6,8\text{ h/d}$): $408,0\text{ kWh} \to 54,22\text{ €/mes}$ (Cuello de botella principal).
  2. PC Workstation con IA ($420\text{ W} \times 10,5\text{ h/d}$): $132,3\text{ kWh} \to 17,58\text{ €/mes}$.
  3. Servidor Multi-PC LAN + NAS 24h ($95\text{ W} \times 24\text{ h/d}$): $68,4\text{ kWh} \to 9,09\text{ €/mes}$.
  4. Nevera Combi ($180\text{ W} \times 21\text{ h/d}$): $113,4\text{ kWh} \to 15,07\text{ €/mes}$.
  5. Cocina / Placa / Horno ($2.200\text{ W} \times 1,8\text{ h/d}$): $118,8\text{ kWh} \to 15,79\text{ €/mes}$.
  6. Lavadora / Secadora ($2.100\text{ W} \times 1,75\text{ h/d}$): $110,25\text{ kWh} \to 14,65\text{ €/mes}$.
  7. Iluminación / TV / Standby ($220\text{ W} \times 12,08\text{ h/d}$): $79,73\text{ kWh} \to 10,60\text{ €/mes}$.
  * **Total:** $1.030,88\text{ kWh/mes} = 137,00\text{ €}$.

---

## 5. EXPERIENCIA PROFESIONAL REAL, IDIOMAS Y CULTURA DE NEGOCIO

### 🌍 Idiomas de Trabajo:
* **Español:** Nativo.
* **Francés:** Fluido profesional. Cerca de 2 años de experiencia directa desarrollando software y aplicaciones web en Bayonne (Francia), además de trabajo comercial técnico en la industria ferroviaria entre España y Francia.
* **Inglés:** Fluido profesional en documentación técnica, diseño de arquitectura de datos y comunicación internacional.

### 💼 Trayectoria Profesional Aplicada:
* **Desarrollo de Software / Web — Empresa tecnológica en Bayonne, Francia (~2 años):**
  Desarrollo de aplicaciones, maquetación de interfaces, entrega continua de software e integración de servicios trabajando en entorno completamente francófono.
* **Ventas Internacionales y Equipamiento Ferroviario PMR — IRC International Railway Consulting (España & Francia, 2026):**
  Negociación comercial bilingüe, consultoría técnica de equipamiento de movilidad para personas con movilidad reducida (PMR) y coordinación con fabricantes e industrias de ambos países.
* **Banca Comercial — BBVA (~1 año):**
  Gestión directa de clientes, análisis de riesgos y necesidades operativas, consolidando una visión financiera práctica que hoy nutre la plataforma Novus Capital.

### 🎓 Formación Continua Práctica:
* Cursos especializados en la senda **EIP / EFA** (European Investment Practitioner / Financial Advisor), análisis fundamental y valoración de empresas.
* Formación autodidacta intensiva en Ingeniería de Datos (Kafka, NiFi, Spark, Iceberg), Sistemas de Agentes de IA (MCP, RAG, Ollama) y Python Científico.

---

## 6. PREGUNTAS Y RESPUESTAS CLAVE PARA PRESENTACIONES O ENTREVISTAS

**P: ¿Por qué no tienes un título universitario formal en informática?**  
*R:* Porque aprendo construyendo. Todo lo que sé está demostrado en repositorios abiertos con arquitecturas completas en funcionamiento: pipelines de datos con tolerancia a fallos, enjambres de agentes con algoritmos de equilibrio de carga, modelos matemáticos verificados simbólicamente y sistemas desplegados en servidores reales. Un título acredita que escuchaste clases; mi portafolio demuestra que resuelvo problemas de ingeniería complejos desde el primer día.

**P: ¿Cómo gestionas el escalado y los picos de datos en streaming?**  
*R:* Aplico desacoplamiento y dimensionamiento formal. En la entrada utilizo Apache NiFi con límites estrictos de backpressure para que la cola en disco proteja la memoria del clúster. Para el bus de eventos uso Kafka KRaft particionado con murmur2, dimensionado con la Ley de Little y modelos de colas $M/M/c$ para mantener la utilización del sistema por debajo del 80%. En el procesamiento utilizo PySpark y Polars con watermarking para limitar el estado en RAM y salting para eliminar el sesgo de datos.

**P: ¿Qué aporta tu dominio del francés y del inglés?**  
*R:* Capacidad inmediata para integrarme en equipos multinacionales en remoto (Francia, Suiza, Bélgica, Reino Unido o EE.UU.), comprender documentación técnica de vanguardia sin barreras y liderar la interlocución técnica con clientes y proveedores internacionales.

---

## 7. ORGANIZACIÓN CORPORATIVA DE ENJAMBRE DE AGENTES, TEST HARNESSES Y MATEMÁTICAS

### 🧠 Mapa Mental del Sistema Unificado
```mermaid
mindmap
  root((Plataforma de Datos & Agentes))
    Dirección Corporativa
      CEO Orchestrator
        Descompone objetivos
        Supervisa fidelidad al objetivo
        Mantiene ritmo 3h continuas
    Especialistas de Tarea Única
      Agente Sentinel NiFi
        Valida schemas JSON
        Monitorea contrapresión
      Agente Traffic Kafka
        Hash Blake2b
        Balanceo 8 particiones
      Agente Math Welford
        Haskell & Python Monoid
        Media y Varianza asociativas
      Agente Security MAD
        Z-Score robusto 50% breakdown
        Alertas de fraude > 8.0
      Agente Lakehouse ACID
        Transacciones SQLite / Iceberg
        Commit y verificación
      Agente Reporting
        Infografía y Métricas en vivo
        Bridge JS y Dossier
    Test Harnesses Bancos de Prueba
      Pre-condiciones de entrada
      Post-condiciones de salida
      Aislamiento de fallos
      Contratos estrictos
    Matemáticas Rigurosas
      Haskell Types & Semigroups
      Ley de Little L = lambda * W
      Entropía de Shannon H_X
      Estadística Robusta MAD
```

---

### 🏢 Estructura de Agentes como una Empresa (Single Responsibility Principle)
Para garantizar que el sistema opere sin intervención, sin fatiga y fiel al objetivo macro:

```mermaid
flowchart TD
    CEO["👔 CEO Orchestrator Agent\n(Define objetivos y asigna micro-tareas simples)"]
    
    subgraph Pipeline["Cadena de Trabajo Especializada (1 Tarea por Agente)"]
        A1["🛡️ Agente Sentinel (NiFi)\nTarea: Validar JSON & Backpressure"]
        A2["🚦 Agente Traffic (Kafka)\nTarea: Hash & Asignación Partición (0..7)"]
        A3["🧮 Agente Math (Haskell/Python)\nTarea: Combinar Monoide Welford A ⊕ B"]
        A4["🚨 Agente Security (MAD)\nTarea: Detectar Anomalías Robusto Z > 8.0"]
        A5["💾 Agente Lakehouse (ACID Sink)\nTarea: Transacción y Persistencia"]
        A6["📊 Agente Reporting & UI\nTarea: Generar Dossier y Actualizar Web"]
    end

    subgraph Harness["🛡️ Arquitectura de Test Harnesses (Contratos)"]
        H1["Pre-Check / Post-Check de Invariantes"]
        H2["Aislamiento: ningún error tumba a otro agente"]
        H3["Garantía de ejecución continua (3 horas sin deriva)"]
    end

    CEO --> A1
    A1 -->|Harness 1 OK| A2
    A2 -->|Harness 2 OK| A3
    A3 -->|Harness 3 OK| A4
    A4 -->|Harness 4 OK| A5
    A5 -->|Harness 5 OK| A6
    
    Pipeline -.-> Harness
```

---

### 📐 Las Fórmulas Matemáticas: Por qué Haskell y Pythonista
1. **Monoide Paralelo de Welford ($A \oplus B$):**
   Permite calcular la media y la varianza exacta combinando particiones sin cargar todos los datos en memoria:
   $$\mu_{AB} = \mu_A + (\mu_B - \mu_A) \frac{n_B}{n_A + n_B}, \qquad M_{2,AB} = M_{2,A} + M_{2,B} + (\mu_B - \mu_A)^2 \frac{n_A n_B}{n_A + n_B}$$
2. **Ley de Little y Teoría de Colas ($M/M/c$):**
   Dimensiona el número de núcleos de Kafka y Spark para evitar cuellos de botella:
   $$L = \lambda W, \qquad \rho = \frac{\lambda}{c \cdot \mu} \le 0.80$$
3. **Estadística Robusta ($\text{MAD}$):**
   A diferencia de la desviación clásica $\sigma$ que se infla con un solo fraude gigante, el MAD tiene un punto de ruptura del 50%:
   $$\text{MAD} = \text{mediana}(|X_i - \text{mediana}(X)|), \qquad Z_{\text{robusto}} = \frac{|X_i - \text{mediana}(X)|}{1.4826 \cdot \text{MAD}}$$
4. **Entropía de Shannon ($H(X)$):**
   Mide en bits la homogeneidad del particionado en Kafka para neutralizar *Hot Keys*:
   $$H(X) = -\sum_{i=1}^{k} p_i \log_2(p_i)$$

---

*Dossier generado y compilado para Google NotebookLM / Gemini Notebook. Listo para generar resúmenes ejecutivos, mapas conceptuales, análisis de grafos y guías de estudio interactivas.*
