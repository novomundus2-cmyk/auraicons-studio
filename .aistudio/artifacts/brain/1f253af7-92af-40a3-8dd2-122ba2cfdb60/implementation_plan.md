# NexusData · Senior Data & Software Engineer Portfolio

Un portfolio web y curriculum interactivo de calibre mundial diseñado para superar exponencialmente los CVs estáticos convencionales de ingeniería de software y datos. Transforma un currículum plano en una plataforma inmersiva con visualización 3D interactiva de pipelines de datos (Three.js), un simulador de orquestación ETL en tiempo real (Spark, Delta Lake, Airflow), un asistente de arquitectura con Gemini AI, persistencia de proyectos y recomendaciones técnicas con Firebase, y vitrina de benchmarks de ingeniería.

---

## User Review & Critical Decisions

> [!IMPORTANT]
> **Decisiones Críticas Confirmadas**:
> 1. **Perfil Profesional**: Posicionamiento como **Senior Data & Software Engineer / Lead Data Architect**, abarcando ingeniería distribuida de datos (Spark/Scala, Python, Delta Lake, Databricks, AWS/Azure, Airflow) y desarrollo full-stack moderno.
> 2. **Dirección Visual & UX**: Estilo **Dark Tech & Precision Engineering** con lienzo 3D Three.js procedural (cluster de procesamiento distribuido y nodos de datos en tiempo real), sin marcos de píldoras estáticas, tipografía arquitectónica (*Outfit* + *Plus Jakarta Sans* + *JetBrains Mono*), y retroalimentación de 60 FPS.
> 3. **Base de Datos de Ingeniería**: Base de datos Firestore con colecciones de proyectos de ingeniería, métricas de rendimiento ETL (latencia, throughput, compresión Parquet/Delta), certificaciones verificadas y bitácora técnica interactiva.
> 4. **Asistente Técnico de IA (Gemini)**: Chatbot técnico entrenado como *Engineering Technical Recruiter & Lead Architect* que responde sobre el stack, analiza diagramas de arquitectura y responde preguntas técnicas profundas.
> 5. **Demostración de Habilidades Prácticas ("Proof of Work")**: En lugar de solo listar tecnologías ("Spark, Airflow, SQL"), el portfolio incluye simuladores en vivo interactivos: Orquestador DAG de Airflow interactivo, visualizador de particiones Delta Lake/Parquet y consola SQL en vivo.

---

## 1. Overview & Core Concept

- **El Problema**: Los CVs tradicionales en PDF o webs planas (como el perfil de referencia de Julián Nevado) se limitan a listar tecnologías ("Scala, Spark, Airflow, AWS") en viñetas de texto blanco y negro sin demostrar maestría real, impacto cuantitativo ni interactividad.
- **La Solución**: Una experiencia interactiva de nivel élite que pone a prueba y demuestra en vivo cada competencia:
  - **3D Cluster Canvas (Three.js)**: Nodos procedurales interconectados que representan un cluster Spark/Kubernetes con flujo de datos en tiempo real y controles de cámara inmersivos.
  - **Simulador de Pipeline ETL & DAG**: Visualizador de orquestación interactiva donde los reclutadores y líderes de ingeniería pueden ejecutar un job de transformación Spark, ver métricas de throughput y examinar consultas SQL optimizadas.
  - **Expediente Profesional & CV Dinámico**: Comparativa directa de experiencia con métricas de impacto reales (ej. "+4.2 TB/día procesados", "-45% costos en S3/Delta Lake", "99.99% SLAs en Airflow").
  - **Agente de Entrevistas Técnicas (Gemini)**: Permite a los reclutadores técnicos consultar detalles de experiencia, desafíos resueltos y decisiones de arquitectura en lenguaje natural.
  - **Centro de Control con Autenticación & Firestore**: Los visitantes pueden dejar recomendaciones firmadas con Google Auth, votar proyectos destacados o descargar el CV ejecutivo generado en PDF limpio.

---

## 2. User Experience & Visual Design

### A. Estructura y Navegación
- **Top Bar Contract**:
  - *Zona 1*: Wordmark de ingeniería `NexusData // Senior Data Engineer` (una sola línea limpia).
  - *Zona 2*: Navegación concisa: `Overview`, `Pipeline 3D`, `Proyectos ETL`, `Stack Interactivo`, `Asistente IA`.
  - *Zona 3*: Botón de acción principal: `Descargar CV (PDF/JSON)` + acceso a Auth.

### B. Secciones Clave
1. **Hero Split de Alto Impacto**:
   - *Columna Izquierda*: Titular arquitectónico con `text-wrap: balance`: *"Construyendo infraestructuras de datos masivas y pipelines distribuidos de alta disponibilidad"*. Lead text conciso, especialidades clave sin píldoras decorativas y enlace directo al simulador.
   - *Columna Derecha*: Escena 3D Three.js viva (cluster distribuido con partículas de datos y nodos procedurales con PBR lighting).
   - *Franja Inferior*: KPIs cuantitativos verificables (`4.8 TB/día procesados`, `350+ DAGs orquestados`, `12ms P99 latency`, `5 años prod exp`).
2. **Cluster 3D Interactivo (Three.js)**:
   - Modelo procedural de 5–8 partes compuesto por servidores de procesamiento (Worker Nodes), almacenamiento distribuido (Lakehouse S3/Delta Lake) y broker de streaming (Kafka/EventHubs).
   - Controles de cámara amortiguados con física de resortes (`1 - Math.exp(-k * dt)`).
   - Dock inferior colapsable para inspeccionar métricas del nodo, velocidad de flujo y topología de red.
3. **Simulador de Orquestador ETL & Big Data**:
   - Interfaz interactiva de DAG similar a Apache Airflow / Databricks con nodos: `Ingesta S3` → `Validación Schemas` → `Transformación PySpark` → `Escritura Delta Lake`.
   - Botón "Ejecutar Job" con cálculo de particionado, consumo de memoria y verificación de calidad de datos.
4. **Comparativa de Stack Tecnológico Superada**:
   - Muestra las tecnologías del CV de referencia (Spark, Python, Scala, SQL, Airflow, AWS, Azure, Delta Lake) pero expandidas con benchmarks reales, ejemplos de código interactivos y arquitecturas de referencia.
5. **Asistente de Consulta Técnica (Gemini Chat)**:
   - Panel conversacional flotante o embebido para interrogar al CV: "¿Cómo optimizaste los jobs de Spark para evitar data skew?", "¿Qué experiencia tienes con Delta Lake vs Iceberg?", etc.

### C. Paleta de Colores & Tipografía
- **Lienzo Neutral (60%)**: Dark Slate profundo `#090D16` con acentos de superficie `#0F172A`.
- **Estructura y Paneles (30%)**: Paneles de precisión con bordes sutiles de 1px `#1E293B`, sin sombras excesivas.
- **Acentos Focales (10%)**: Cyan tecnológico `#38BDF8` y Esmeralda de ejecución `#10B981`.
- **Tipografía**:
  - *Display / Títulos*: `Outfit` (geométrica, moderna y asertiva).
  - *Cuerpo y Lectura*: `Plus Jakarta Sans` (14-16px, alta legibilidad).
  - *Métricas, Schemas y Código*: `JetBrains Mono` con `tabular-nums`.

---

## 3. Key Product Decisions & Trade-Offs

- **Three.js Procedural vs Modelos Externos .GLTF**:
  - *Decisión*: Generar la topología del cluster 3D de forma 100% procedural en código mediante `THREE.Group` y geometrías compuestas con `RoomEnvironment`.
  - *Por qué*: Cero dependencias de red externas, cero riesgo de error 404, carga instantánea y rendimiento de 60fps garantizado.
- **Simulador Interactivo de Pipeline en lugar de solo capturas**:
  - *Decisión*: Proporcionar un motor interactivo donde el usuario puede activar pasos del pipeline y ver el flujo de datos.
  - *Por qué*: Demuestra conocimiento práctico de ingeniería y distingue radicalmente al candidato sobre cualquier PDF estático.
- **Gemini Server-Side Proxy**:
  - *Decisión*: Enrutar las consultas del asistente a través de `/api/chat` usando el SDK `@google/genai` con modelo `gemini-3.8-flash` y `gemini-4-argon` para razonamiento profundo de arquitectura.
  - *Por qué*: Protege la clave de API y permite inyectar el contexto profesional estructurado en el `systemInstruction`.

---

## 4. Technical Architecture & Data Strategy

### Diagrama de Arquitectura

```
┌────────────────────────────────────────────────────────────────────────┐
│                        NEXUSDATA CLIENT (Vite + React)                 │
├────────────────────────────┬─────────────────────────────┬─────────────┤
│   Hero & Top Bar           │   Three.js 3D Cluster       │ Interactive │
│   (3-Zone Contract)        │   (ACESFilmic, PBR Nodes)   │ DAG & ETL   │
├────────────────────────────┴─────────────────────────────┴─────────────┤
│   Asistente Gemini AI      │   Vitrina de Proyectos      │ Firebase    │
│   (Chat Técnico)           │   (Delta Lake, Spark, AWS)  │ Auth/Store  │
└─────────────┬───────────────────────────┬──────────────────────────────┘
              │                           │
              ▼                           ▼
┌───────────────────────────┐ ┌──────────────────────────────────────────┐
│   EXPRESS BACKEND ROUTE   │ │      FIREBASE FIRESTORE & AUTH           │
│   POST /api/chat          │ │  • /projects (Casos de ingeniería)       │
│   @google/genai SDK       │ │  • /endorsements (Recomendaciones)       │
│   (gemini-3.8-flash)      │ │  • /metrics (Benchmarks de rendimiento)  │
└───────────────────────────┘ └──────────────────────────────────────────┘
```

### Entidades de Base de Datos (`firebase-blueprint.json`)
- `projects`: Documentos con título, arquitectura, stack, métricas de rendimiento (GB/s, ahorro de costos) y enlaces a repositorios simulados.
- `skills`: Catálogo clasificado de competencias (Ingeniería de Datos, Nube, Almacenamiento, Orquestación, Calidad) con nivel de maestría y casos de uso en producción.
- `endorsements`: Testimonios y recomendaciones técnicas de colegas o líderes de equipo con autenticación verificada de Google.
- `telemetry`: Registros de benchmarks en vivo del simulador ETL.

---

## 5. Implementation Roadmap (Phases)

1. **Fase 1: Configuración de Base de Datos & Auth (Firebase)**:
   - Activar aprovisionamiento con `show_aistudio_ui(firebase_setup)`.
   - Establecer `firebase-blueprint.json` y `firestore.rules` con modelo de ingeniería.
2. **Fase 2: Motor 3D Three.js**:
   - Escena procedural del cluster distribuido con nodos Spark, Kafka y Delta Lake.
   - PBR lighting, sombras de contacto y controles de órbita amortiguados.
3. **Fase 3: Simulador de Pipelines & Dashboard de Proyectos**:
   - Orquestador DAG interactivo con ejecución en vivo, métricas y código de transformación.
4. **Fase 4: Asistente Técnico Gemini AI**:
   - Integración server-side de chat para preguntas técnicas y entrevistas simuladas.
5. **Fase 5: Exportación Ejecutiva & Verificación Final**:
   - Generador de CV descargable optimizado para ATS y reclutadores.
   - Verificación de compilación y linter.
