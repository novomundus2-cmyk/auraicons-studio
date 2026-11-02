import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { ICONS_LIST } from '../data/iconsList';
import { InteractiveIcon } from './InteractiveIcon';
import { soundEffects } from '../utils/audio';

const ICON_BY_ID_MAP = new Map(ICONS_LIST.map((icon) => [icon.id, icon]));

export interface CorporateRouteUi {
  id: string;
  name: string;
  src: string;
  tgt: string;
  slaMs: number;
  currentMs: number;
  optMs: number;
  throughput: number;
  strategy: string;
  improvementPct: number;
  status: string;
}

export const INITIAL_CORPORATE_ROUTES_UI: CorporateRouteUi[] = [
  {
    id: 'ROUTE-01',
    name: 'Ruta 1 · Ingesta Perimetral NiFi',
    src: 'Edge API Gateway',
    tgt: 'Apache NiFi FlowFiles',
    slaMs: 30.0,
    currentMs: 28.4,
    optMs: 14.2,
    throughput: 42000,
    strategy: 'Backpressure Dinámico (Queue ≤ 10k FlowFiles) + Loteo Cíclico POSIX',
    improvementPct: 50.0,
    status: 'AUTOMEJORADA ⚡',
  },
  {
    id: 'ROUTE-02',
    name: 'Ruta 2 · Particionado Kafka KRaft',
    src: 'Apache NiFi FlowFiles',
    tgt: 'Kafka Broker KRaft (8 Particiones)',
    slaMs: 40.0,
    currentMs: 38.6,
    optMs: 18.5,
    throughput: 36500,
    strategy: 'Key-Salting Anti-Sesgo (H(X) ≥ 2.95 bits) + acks=all Zero-Loss',
    improvementPct: 52.1,
    status: 'AUTOMEJORADA ⚡',
  },
  {
    id: 'ROUTE-03',
    name: 'Ruta 3 · Micro-lotes PySpark & Ventanas',
    src: 'Kafka Broker KRaft',
    tgt: 'PySpark Structured Streaming',
    slaMs: 75.0,
    currentMs: 71.2,
    optMs: 34.8,
    throughput: 28000,
    strategy: 'Watermarking Estricto de 5s + Work-Stealing en Ejecutores Paralelos',
    improvementPct: 51.1,
    status: 'AUTOMEJORADA ⚡',
  },
  {
    id: 'ROUTE-04',
    name: 'Ruta 4 · Álgebra Haskell & Welford-Chan',
    src: 'PySpark Structured Streaming',
    tgt: 'Welford Monoid Aggregator O(1)',
    slaMs: 25.0,
    currentMs: 22.1,
    optMs: 7.8,
    throughput: 55000,
    strategy: 'Fusión Asociativa (A ⊕ B) ⊕ C sin Relectura en Memoria Constante',
    improvementPct: 64.7,
    status: 'AUTOMEJORADA ⚡',
  },
  {
    id: 'ROUTE-05',
    name: 'Ruta 5 · Detección Robusta MAD Antifraude',
    src: 'Welford Monoid Aggregator',
    tgt: 'Escudo Antifraude (MAD = 295.76)',
    slaMs: 35.0,
    currentMs: 31.5,
    optMs: 11.2,
    throughput: 48000,
    strategy: 'Bifurcación Inmune al Enmascaramiento con Mediana + Aislamiento Seguro',
    improvementPct: 64.4,
    status: 'AUTOMEJORADA ⚡',
  },
  {
    id: 'ROUTE-06',
    name: 'Ruta 6 · Lakehouse ACID & Réplica NAS/Cloud',
    src: 'Escudo Antifraude',
    tgt: 'Apache Iceberg Parquet ZSTD + SQLite WAL',
    slaMs: 50.0,
    currentMs: 46.8,
    optMs: 19.4,
    throughput: 32000,
    strategy: 'Compactación a Bloques de 256MB contra Small Files + WAL Checkpointing',
    improvementPct: 58.5,
    status: 'AUTOMEJORADA ⚡',
  },
];

export const REUSABLE_KNOWLEDGE_VAULT = [
  {
    id: 'KB-01',
    category: 'Matemáticas Haskell',
    title: 'Monoide de Welford-Chan en Haskell',
    badge: 'O(1) Memoria · IEEE 754',
    code: `instance Semigroup StatsMonoid where
  (StatsMonoid nA mA sA) <> (StatsMonoid nB mB sB) =
    let n = nA + nB
        delta = mB - mA
        m = mA + delta * fromIntegral nB / fromIntegral n
        s = sA + sB + delta * delta * fromIntegral (nA * nB) / fromIntegral n
    in StatsMonoid n m s`,
    summary: 'Garantiza asociatividad distributiva sin cancelación catastrófica de coma flotante.',
  },
  {
    id: 'KB-02',
    category: 'Detección Antifraude',
    title: 'Z-Score Robusto por Mediana y MAD',
    badge: 'Punto Ruptura 50% · SciPy',
    code: `def robust_mad_z_score(x: np.ndarray) -> np.ndarray:
    med = np.median(x)
    mad = np.median(np.abs(x - med))
    return 0.6745 * (x - med) / (mad if mad > 0 else 1.0)`,
    summary: 'Inmune al enmascaramiento: detecta anomalías reales sin que outliers masivos inflen la media.',
  },
  {
    id: 'KB-03',
    category: 'FinOps & Clima',
    title: 'Fórmula Termodinámica Termo 137 €',
    badge: '137,21 € Ahorro Auditado · PVPC',
    code: `E_kwh = (V_litros * delta_T * 4186) / 3_600_000
ahorro_anual = (coste_standby_24h - coste_timer_3h_valle) * 365`,
    summary: 'Cálculo de optimización con temporizador digital programable y discriminación horaria.',
  },
  {
    id: 'KB-04',
    category: 'BigQuery AI & ML',
    title: 'Consulta Nativa AI.DETECT_ANOMALIES',
    badge: 'TimesFM 2.0 · %%bqsql',
    code: `SELECT * FROM AI.DETECT_ANOMALIES(
  TABLE gold_category_metrics,
  data_col => 'total_volume_eur',
  id_cols => ['category']
);`,
    summary: 'Predicción y detección de anomalías temporales con modelo fundacional TimesFM de Google.',
  },
];

interface AgentNode {
  id: string;
  name: string;
  stage: string;
  iconId: string;
  emoji: string;
  tasks: number;
  progress: number;
  completed: number;
  currentAction: string;
}

interface ConceptDef {
  key: string;
  shortLabel: string;
  title: string;
  what: string;
  how: string;
  math: string;
  interview: string;
  subconcepts: string[];
}

const CONCEPT_DB: Record<string, ConceptDef> = {
  work_stealing: {
    key: 'work_stealing',
    shortLabel: 'Hierarchical Agents & Work-Stealing',
    title: '🤖 Hierarchical AI Agent Infrastructure & Work-Stealing (Explicado desde cero)',
    what: 'En tu proyecto «Hierarchical AI agent infrastructure», en lugar de tener un solo agente gigante bloqueado con 20 tareas, diseñas una jerarquía de agentes con roles especializados y memoria compartida auditable. Cuantos MÁS agentes especializados trabajan en paralelo y MENOS tareas acumula cada uno (1–2 tareas/agente), la velocidad se multiplica y desaparecen los cuellos de botella.',
    how: 'Cuando un agente termina su tarea y queda libre (0 tareas), aplica Work-Stealing («Robo de Trabajo»): mira qué compañero tiene más tareas acumuladas y le quita una automáticamente para ayudarle. Compruébalo en vivo pulsando «➕ Añadir Agente» o «⚖️ Auto-Balancear».',
    math: 'W_agente = Q_i / μ_i  ⟹  Al subir el número de agentes M y bajar la cola individual Q_i → 1, la latencia cae proporcionalmente a 1/M.',
    interview: '«Diseño sistemas jerárquicos de agentes con memoria compartida auditable y balanceo Work-Stealing: cuantos más agentes especializados operan con colas unitarias (1 tarea por agente), eliminamos la contención entre procesos locales y cloud.»',
    subconcepts: ['welford', 'teoria_colas', 'enmascaramiento', 'mad', 'supabase_rls', 'nas_cluster'],
  },
  welford: {
    key: 'welford',
    shortLabel: 'Monoide de Welford-Chan',
    title: '🧮 ¿Qué es el Monoide de Welford-Chan? (Explicado desde cero)',
    what: 'Para tu plataforma financiera Novus Capital / NovusMundus, calcular la media y la varianza de millones de transacciones restando sumas gigantescas en coma flotante produce errores graves (Cancelación Catastrófica) y obliga a leer los datos dos veces. El Monoide de Welford-Chan guarda solo 3 números por partición (count, mean, m2) y permite fusionar servidores en paralelo en una sola pasada con memoria constante O(1).',
    how: 'Como cumple la propiedad de Asociatividad ((A + B) + C = A + (B + C)), cada agente de Python, PySpark o Haskell calcula su trozo y luego se combinan en cualquier orden dando exactamente el mismo resultado.',
    math: 'M2_AB = M2_A + M2_B + (μ_B - μ_A)² · (n_A · n_B) / (n_A + n_B)',
    interview: '«En NovusMundus implementé el Monoide de Welford-Chan verificado con SymPy para agregar métricas de carteras y flujos financieros en una sola pasada O(1) sin errores de coma flotante.»',
    subconcepts: ['work_stealing', 'enmascaramiento', 'mad', 'teoria_colas'],
  },
  teoria_colas: {
    key: 'teoria_colas',
    shortLabel: 'Teoría de Colas M/M/c & Ley de Little',
    title: '🚦 ¿Qué son la Teoría de Colas M/M/c y la Ley de Little (L = λW)?',
    what: 'Es la matemática que dimensiona cuántos agentes o particiones (c) necesitas según cuántos eventos financieros entran por segundo (λ) y cuántos procesa cada nodo (μ).',
    how: 'La Ley de Little demuestra que cuando la utilización ρ = λ / (c · μ) se acerca al 100%, la cola crece hacia el infinito provocando caídas por OutOfMemory (OOM). Por eso mantenemos siempre ρ ≤ 80% añadiendo agentes o activando Backpressure en Apache NiFi.',
    math: 'ρ = λ / (c · μ) ≤ 0.80   |   Ley de Little: L = λ · W   |   dL/dλ = μ / (μ - λ)²',
    interview: '«Dimensiono los flujos de datos y el enjambre de agentes aplicando Teoría de Colas M/M/c con un umbral máximo de utilización del 80% para garantizar latencia predecible.»',
    subconcepts: ['work_stealing', 'backpressure', 'welford', 'salting'],
  },
  enmascaramiento: {
    key: 'enmascaramiento',
    shortLabel: 'Efecto de Enmascaramiento (Masking)',
    title: '🕵️‍♂️ ¿Qué es el Efecto de Enmascaramiento en Banca y Finanzas (BBVA / Novus Capital)?',
    what: 'Cuando hay una operación anómala o fraudulenta gigante (ej. 4.500 € donde lo habitual son 112 €), ese único importe infla tanto la Desviación Típica clásica (σ = 1.378 €) que su Z-Score clásico sale 2.83 (< 3.0) y la puerta de validación (validation gate) NO salta: la anomalía se esconde a sí misma.',
    how: 'Lo solucionamos sustituyendo la media y desviación clásica por la Mediana y el MAD (Desviación Absoluta Mediana), cuyo punto de ruptura es del 50%. Así el Z-Score Robusto salta a 295.76 y cazamos las 265 anomalías de Novus Capital sin falsos negativos.',
    math: 'Z_clásico = |x - μ| / σ = 2.83 (Enmascarado)  vs  Z_robusto = |x - Mediana| / (1.4826 · MAD) = 295.76 (¡Cazado!)',
    interview: '«En los validation gates financieros de Novus Capital reemplacé el Z-Score clásico por el Z-Score Robusto basado en Mediana y MAD porque la desviación estándar sufre enmascaramiento ante valores extremos.»',
    subconcepts: ['mad', 'welford', 'work_stealing', 'supabase_rls'],
  },
  mad: {
    key: 'mad',
    shortLabel: 'MAD & Mediana (50% Ruptura)',
    title: '🛡️ ¿Qué son la Mediana y el MAD (Median Absolute Deviation)?',
    what: 'La Mediana es el valor justo en el centro al ordenar las operaciones (inmune a valores extremos). El MAD es la mediana de las distancias respecto a esa mediana, multiplicada por 1.4826.',
    how: 'Incluso si el 49% de los datos de entrada estuvieran corruptos, el MAD sigue detectando qué operaciones son anómalas (Punto de Ruptura del 50%).',
    math: 'MAD = mediana(|X - mediana(X)|)   |   σ_robusto = 1.4826 · MAD',
    interview: '«Con SciPy y Polars calculamos el MAD en nuestros flujos financieros logrando un punto de ruptura del 50% frente a anomalías.»',
    subconcepts: ['enmascaramiento', 'welford', 'work_stealing'],
  },
  supabase_rls: {
    key: 'supabase_rls',
    shortLabel: 'PostgreSQL, Supabase RLS & Validation Gates',
    title: '🔐 ¿Qué son Supabase RLS (Row-Level Security) y los Validation Gates?',
    what: 'En tu proyecto Novus Capital / NovusMundus, Row-Level Security (RLS) en PostgreSQL/Supabase es un escudo dentro de la propia base de datos que verifica fila por fila qué usuario o agente IA tiene permiso para leer o modificar cada cartera financiera.',
    how: 'Combinado con Validation Gates (puertas de validación matemática con SymPy/SciPy y esquemas estrictos), impide que ningún dato corrupto o acceso no autorizado entre al Lakehouse.',
    math: 'Política RLS en motor SQL + Constraints ACID + Validation Gate (Z_robusto < Umbral)',
    interview: '«Construyo sistemas extremo a extremo donde la seguridad no depende solo del frontend: aplico Row-Level Security (RLS) en PostgreSQL/Supabase, índices optimizados y puertas de validación matemática antes de persistir.»',
    subconcepts: ['work_stealing', 'enmascaramiento', 'nas_cluster'],
  },
  backpressure: {
    key: 'backpressure',
    shortLabel: 'Backpressure & Watermarking',
    title: '🚰 ¿Qué son el Backpressure en NiFi y el Watermarking en PySpark?',
    what: 'Son los dos escudos que impiden que un servidor muera sin memoria RAM (OutOfMemory): Backpressure frena la entrada en disco cuando la cola llega a 10.000 FlowFiles, y Watermarking (10 min) limpia de la RAM las ventanas antiguas en PySpark.',
    how: 'Combinados con Kafka en modo KRaft (sin ZooKeeper, acks=all), garantizan cero pérdida de datos en picos de mercado.',
    math: 'Si Cola ≥ 10.000 FlowFiles (o 1 GB) ⟹ Pausar Ingesta Aguas Arriba.',
    interview: '«Protejo los pipelines con Backpressure en disco y Watermarking sobre tiempo de evento para evitar caídas por OutOfMemory.»',
    subconcepts: ['teoria_colas', 'salting', 'work_stealing'],
  },
  salting: {
    key: 'salting',
    shortLabel: 'Entropía de Shannon & Salting',
    title: '🧂 ¿Qué son la Entropía de Shannon H(X), el Data Skew y el Salting?',
    what: 'Cuando un solo activo o cliente concentra el 80% de las operaciones (Data Skew), un solo nodo se satura mientras los demás están libres. La Entropía de Shannon H(X) mide en bits ese desequilibrio.',
    how: 'Cuando la entropía cae, activamos Key Salting: añadimos un sufijo aleatorio (1..8) a la clave para repartir el trabajo entre todos los agentes y luego fusionamos el resultado gracias al Monoide de Welford-Chan.',
    math: 'H(X) = - ∑ p_i · log2(p_i) bits',
    interview: '«En mi Physics CAD Lab y en el pipeline de streaming uso la Entropía de Shannon como sensor continuo para activar Key Salting ante sesgos de carga.»',
    subconcepts: ['welford', 'teoria_colas', 'work_stealing'],
  },
  nas_cluster: {
    key: 'nas_cluster',
    shortLabel: 'Servidor Multi-PC LAN, NAS & BigQuery Graph',
    title: '🖧 ¿Cómo funciona la Orquestación Local (LAN/NAS/Ollama) + Cloud (BigQuery/Firebase)?',
    what: 'Tal como describes en tu portafolio («Exploring reliable orchestration between local infrastructure, cloud AI and business processes»), este servidor Python (0.0.0.0:8765) conecta varios PCs en tu red local con un NAS compartido y los sincroniza con BigQuery Data Transfer (DTS), BigQuery Property Graph (GQL) y Firebase.',
    how: 'Permite ejecutar agentes locales (Ollama / Python científico) con memoria compartida en el NAS y escalar a modelos cloud (Gemini 2.5 / TimesFM 2.0) sin fricción.',
    math: 'PCs en LAN + Ollama Local ⟷ Servidor Python (0.0.0.0:8765) + NAS Mirror ⟷ BigQuery Graph & Cloud AI',
    interview: '«Orquesto infraestructuras híbridas donde múltiples nodos locales comparten memoria auditable sobre un NAS en red LAN y se sincronizan declarativamente con BigQuery y servicios cloud.»',
    subconcepts: ['work_stealing', 'supabase_rls', 'welford', 'kwh_tarifa_137'],
  },
  kwh_tarifa_137: {
    key: 'kwh_tarifa_137',
    shortLabel: 'Factura 137 € a 0.1329 €/kWh (1.030,85 kWh)',
    title: '⚡ ¿Cuánto hay que consumir en casa y en el PC para gastar 137 € con un contrato de 0.1329 €/kWh?',
    what: 'Si tu contrato eléctrico cobra el kilovatio-hora a 0.1329 €/kWh y has pagado 137,00 € de energía, despejar la ecuación es directo: 137,00 € ÷ 0.1329 €/kWh = 1.030,85 kWh consumidos en el mes (unos 34,36 kWh cada día). Eso equivale a tener 1.431,7 Vatios (1,432 kW) encendidos de forma ininterrumpida las 24 horas de los 30 días del mes.',
    how: '¿Cómo se llega a 1.030,85 kWh en una casa real? Un PC potente con monitores e IA local (420 W durante 10,5 h/día) consume ~132,3 kWh/mes (17,58 €). Un servidor Multi-PC/NAS 24/7 (95 W × 24h) consume ~68,4 kWh/mes (9,09 €). El resto hasta los 137 € proviene de los grandes consumidores térmicos: Termo eléctrico / Calefacción / Climatización (~408 kWh = 54,22 €), Inducción + Horno (~118,8 kWh = 15,79 €), Lavadora + Secadora + Lavavajillas (~100,8 kWh = 13,40 €) y Frigorífico/Congelador + resto de la casa.',
    math: 'E_mes (kWh) = Factura (€) / Tarifa (€/kWh) = 137,00 / 0,1329 = 1.030,85 kWh   |   P_media = 1.030,85 kWh / 720 h = 1,4317 kW (1.431,7 W)',
    interview: '«He construido un simulador energético en Python y React que convierte los Vatios (W) de cada electrodoméstico, PC y servidor NAS a kW, kWh y Euros según el contrato exacto del cliente (ej. 0,1329 €/kWh para auditar una factura real de 137 €).»',
    subconcepts: ['vatio_kilovatio', 'enmascaramiento', 'welford', 'nas_cluster'],
  },
  vatio_kilovatio: {
    key: 'vatio_kilovatio',
    shortLabel: 'Vatio (W) vs Kilovatio (kW) vs kWh',
    title: '🔌 ¿Cuál es la diferencia exacta entre Vatio (W), Kilovatio (kW) y Kilovatio-hora (kWh)?',
    what: '1️⃣ El Vatio (W) mide la potencia instantánea que pide un aparato en este mismo segundo (por ejemplo, una fuente de alimentación de PC consumiendo 400 W). 2️⃣ El Kilovatio (kW) son simplemente 1.000 Vatios: dividimos los Vatios entre 1.000 (400 W = 0,40 kW). 3️⃣ El Kilovatio-hora (kWh) es la energía acumulada en el tiempo (lo que te cobra la compañía a 0,1329 €/kWh): multiplicamos los kW por las horas que está encendido.',
    how: 'Ejemplo real con tu tarifa de 0,1329 €/kWh: si tu PC consume 400 W (0,4 kW) y lo usas 10 horas al día, al día gasta 0,4 kW × 10 h = 4 kWh/día. En 30 días son 120 kWh/mes. Multiplicado por 0,1329 €/kWh = 15,95 € al mes.',
    math: 'P (kW) = Vatios (W) / 1.000   |   Energía (kWh) = P (kW) × Horas   |   Coste (€) = Energía (kWh) × 0,1329 €/kWh',
    interview: '«Fracciono el problema físico desde cero para el usuario: paso de potencia instantánea en Vatios (W) a Kilovatios (kW), integro en el tiempo para obtener Kilovatios-hora (kWh) y aplico la tarifa contractual de 0,1329 €/kWh.»',
    subconcepts: ['kwh_tarifa_137', 'welford', 'teoria_colas'],
  },
};

interface HomeAppliance {
  id: string;
  name: string;
  category: string;
  emoji: string;
  watts: number;
  hoursPerDay: number;
  daysPerMonth: number;
}

const INITIAL_HOME_APPLIANCES: HomeAppliance[] = [
  {
    id: 'app-pc',
    name: 'PC Workstation Principal (IA Local Ollama / Dev + 2 Monitores)',
    category: 'Informática & IA',
    emoji: '🖥️',
    watts: 420,
    hoursPerDay: 10.5,
    daysPerMonth: 30,
  },
  {
    id: 'app-nas',
    name: 'Servidor Multi-PC LAN (0.0.0.0:8765) + NAS RAID + Router 24/7',
    category: 'Informática & IA',
    emoji: '🖧',
    watts: 95,
    hoursPerDay: 24,
    daysPerMonth: 30,
  },
  {
    id: 'app-hvac',
    name: 'Termo Eléctrico / Calefacción / Bomba de Calor / Aire',
    category: 'Climatización & Agua Caliente',
    emoji: '🔥',
    watts: 2000,
    hoursPerDay: 6.8,
    daysPerMonth: 30,
  },
  {
    id: 'app-fridge',
    name: 'Frigorífico Combi + Congelador (Compresor activo)',
    category: 'Cocina Continua 24h',
    emoji: '❄️',
    watts: 180,
    hoursPerDay: 10.5,
    daysPerMonth: 30,
  },
  {
    id: 'app-cooking',
    name: 'Placa de Inducción + Horno Eléctrico + Microondas',
    category: 'Cocina',
    emoji: '🍳',
    watts: 2200,
    hoursPerDay: 1.8,
    daysPerMonth: 30,
  },
  {
    id: 'app-laundry',
    name: 'Lavadora + Secadora + Lavavajillas',
    category: 'Electrodomésticos Lavado',
    emoji: '🧺',
    watts: 2100,
    hoursPerDay: 1.75,
    daysPerMonth: 30,
  },
  {
    id: 'app-lights',
    name: 'TV + Iluminación LED Casa + Cargadores & Standby (Consumo Fantasma)',
    category: 'Hogar & Standby',
    emoji: '💡',
    watts: 225,
    hoursPerDay: 8.5,
    daysPerMonth: 30,
  },
];

const PIPELINE_STAGES = [
  {
    step: 'Etapa 1 · Ingesta & Gates',
    name: 'NiFi + Validation Gates',
    sub: 'FlowFiles · Backpressure 10k',
    metricLabel: 'Cola Disco',
    metricVal: '1,200 / 10k',
    status: 'ACTIVO',
    iconId: 'dts-transfer-portal',
    conceptKey: 'backpressure',
  },
  {
    step: 'Etapa 2 · Bus Eventos',
    name: 'Kafka (KRaft)',
    sub: 'acks=all · Sin ZooKeeper',
    metricLabel: 'Particiones',
    metricVal: '8 murmur2',
    status: 'SIN LAG',
    iconId: 'kafka-spark-stream',
    conceptKey: 'teoria_colas',
  },
  {
    step: 'Etapa 3 · Cómputo & CAD',
    name: 'PySpark + Scientific Py',
    sub: 'NumPy · SciPy · Polars · Salting',
    metricLabel: 'Utilización ρ',
    metricVal: '69.2% (<80%)',
    status: 'ÓPTIMO',
    iconId: 'quantum-cpu-core',
    conceptKey: 'salting',
  },
  {
    step: 'Etapa 4 · Novus Capital Math',
    name: 'SymPy + Welford + MAD',
    sub: 'Monoid O(1) & Fraud Gates',
    metricLabel: 'Z-Score MAD',
    metricVal: '295.8σ (265 alertas)',
    status: 'EXACTO O(1)',
    iconId: 'welford-shield-mad',
    conceptKey: 'welford',
  },
  {
    step: 'Etapa 5 · Backend & Data',
    name: 'Supabase / Iceberg / SQL',
    sub: 'PostgreSQL · RLS · SQLite ACID',
    metricLabel: 'Flujos Fin.',
    metricVal: '25,000 (5.34 M€)',
    status: 'RLS + ACID',
    iconId: 'iceberg-lakehouse-cube',
    conceptKey: 'supabase_rls',
  },
  {
    step: 'Etapa 6 · Hierarchical AI',
    name: 'Agentes Local + Cloud',
    sub: 'Ollama · MCP · RAG · Gemini · AGY',
    metricLabel: 'Memoria Auditable',
    metricVal: '15 Insights + NAS',
    status: 'LAN 0.0.0.0',
    iconId: 'bigquery-graph-nodes',
    conceptKey: 'work_stealing',
  },
];

const INITIAL_AGENTS: AgentNode[] = [
  {
    id: 'AG-00',
    name: 'Mikel Irastorza · Presidente & Fundador',
    stage: 'Nivel 0 · Presidencia Suprema',
    iconId: 'nas-server-cluster',
    emoji: '👑',
    tasks: 0,
    progress: 100,
    completed: 1000,
    currentAction: 'Presidiendo corporación y emitiendo directivas supremas',
  },
  {
    id: 'AG-01',
    name: 'Chatty · Chief Executive Officer (CEO)',
    stage: 'Nivel 1 · Dirección General',
    iconId: 'sparkle-ai',
    emoji: '🤖',
    tasks: 1,
    progress: 95,
    completed: 542,
    currentAction: 'Despachando órdenes ejecutivas y optimizando rutas del pipeline',
  },
  {
    id: 'AG-02',
    name: 'Titan · Chief Technology Officer (CTO)',
    stage: 'C-Suite · Streaming & Kafka KRaft',
    iconId: 'kafka-spark-stream',
    emoji: '🛠️',
    tasks: 1,
    progress: 80,
    completed: 480,
    currentAction: 'Supervisando particiones Kafka y latencia < 80ms',
  },
  {
    id: 'AG-03',
    name: 'Hypatia · Chief Science & AI Officer (CSO)',
    stage: 'C-Suite · Haskell & Welford Monoids',
    iconId: 'quantum-cpu-core',
    emoji: '🧮',
    tasks: 1,
    progress: 78,
    completed: 425,
    currentAction: 'Validando invariantes algebraicos (A ⊕ B) ⊕ C con SymPy',
  },
  {
    id: 'AG-04',
    name: 'Aegis · Chief Information Security Officer (CISO)',
    stage: 'C-Suite · Clean Code & Zero-Trust',
    iconId: 'welford-shield-mad',
    emoji: '🛡️',
    tasks: 1,
    progress: 65,
    completed: 510,
    currentAction: 'Verificando SQLite WAL ACID y 0 advertencias Ruff/Mypy',
  },
  {
    id: 'AG-05',
    name: 'Cupertino · Chief Product & Design Officer (CPO)',
    stage: 'C-Suite · Steve Jobs Apple Design',
    iconId: 'sun-moon',
    emoji: '✨',
    tasks: 1,
    progress: 88,
    completed: 390,
    currentAction: 'Diseñando micro-interacciones a 60fps y PDFs de alta fidelidad',
  },
  {
    id: 'AG-06',
    name: 'Atlas · Chief Operating Officer & FinOps (COO)',
    stage: 'C-Suite · Operaciones & 137 € Luz',
    iconId: 'dts-transfer-portal',
    emoji: '💰',
    tasks: 1,
    progress: 90,
    completed: 415,
    currentAction: 'Monitoreando auditoría de energía (137,21 € ahorro) y réplica NAS',
  },
  {
    id: 'AG-07',
    name: 'Worker 01 · Ingesta Perimetral NiFi',
    stage: 'Worker Swarm · Backpressure',
    iconId: 'refresh-sync',
    emoji: '⚡',
    tasks: 1,
    progress: 48,
    completed: 320,
    currentAction: 'Acotando colas FlowFiles a 10.000 con backpressure real',
  },
  {
    id: 'AG-08',
    name: 'Worker 02 · Particionado Kafka KRaft',
    stage: 'Worker Swarm · Anti-Skew',
    iconId: 'layers',
    emoji: '🔀',
    tasks: 1,
    progress: 55,
    completed: 345,
    currentAction: 'Enrutando por clave murmur2 y aplicando Key-Salting',
  },
  {
    id: 'AG-09',
    name: 'Worker 03 · PySpark Watermark Processor',
    stage: 'Worker Swarm · Ventanas 5s',
    iconId: 'arrow-slide',
    emoji: '🌊',
    tasks: 1,
    progress: 62,
    completed: 370,
    currentAction: 'Agregando ventanas de 5s con watermarking estricto',
  },
  {
    id: 'AG-10',
    name: 'Worker 04 · Welford Monoid Aggregator',
    stage: 'Worker Swarm · O(1) Memoria',
    iconId: 'brain-neural',
    emoji: '🔬',
    tasks: 1,
    progress: 70,
    completed: 390,
    currentAction: 'Calculando media y varianza en una sola pasada O(1)',
  },
  {
    id: 'AG-11',
    name: 'Worker 05 · MAD Robust Anomaly Sentinel',
    stage: 'Worker Swarm · Breakdown 50%',
    iconId: 'eye-look',
    emoji: '📊',
    tasks: 1,
    progress: 58,
    completed: 315,
    currentAction: 'Aislando fraude financiero con Z-Score Robusto MAD = 295.76',
  },
  {
    id: 'AG-12',
    name: 'Worker 06 · Lakehouse ACID Sink',
    stage: 'Worker Swarm · Parquet ZSTD',
    iconId: 'iceberg-lakehouse-cube',
    emoji: '🧊',
    tasks: 1,
    progress: 75,
    completed: 310,
    currentAction: 'Compactando bloques Parquet 256MB y sincronizando réplica NAS',
  },
];

const EXTRA_WORKERS = [
  { name: 'Worker Polars & Pandas Vectorizer', stage: 'Scientific Python · SIMD', iconId: 'quantum-cpu-core', emoji: '🐻‍❄️', action: 'Procesando porfolios en paralelo sin bloqueo' },
  { name: 'Worker Pytest Validation Gate', stage: 'Engineering · CI & Testing', iconId: 'welford-shield-mad', emoji: '✅', action: 'Ejecutando suite pytest & invariantes matemáticos' },
  { name: 'Worker CAD/CAE Physics Simulator', stage: 'Physics CAD Lab · Sensores', iconId: 'kafka-spark-stream', emoji: '⚙️', action: 'Simulando restricciones físicas y telemetría' },
  { name: 'Worker BigQuery GQL Property Graph', stage: 'Cloud Data · Grafos', iconId: 'bigquery-graph-nodes', emoji: '🕸️', action: 'Analizando relaciones entre empresas y carteras' },
  { name: 'Worker MCP Tool Executor', stage: 'Hierarchical AI · Tools', iconId: 'sparkle-ai', emoji: '🛠️', action: 'Ejecutando herramientas MCP con memoria compartida' },
  { name: 'Worker Firebase Cloud Relay', stage: 'Infraestructura · Remoto', iconId: 'firebase-cloud-flame', emoji: '🔥', action: 'Sincronizando clientes España / Francia en vivo' },
  { name: 'Worker Little Law Queue Guard', stage: 'Streaming · M/M/c', iconId: 'dts-transfer-portal', emoji: '🚦', action: 'Garantizando utilización ρ < 0.80 en picos' },
];

const TEN_PROJECTS = [
  { num: '01', title: 'Novus Capital / NovusMundus · AI & Finance Platform', stack: 'PostgreSQL · Supabase RLS · Python · React', math: 'Portfolio Workflows, Valuation & Validation Gates', status: '✅ EN PRODUCCIÓN' },
  { num: '02', title: 'Hierarchical AI Agent Infrastructure (Local + Cloud)', stack: 'Ollama · RAG · Embeddings · MCP · Antigravity', math: 'Shared Auditable Memory & Work-Stealing (Q_i → 1)', status: '✅ EN PRODUCCIÓN' },
  { num: '03', title: 'Physics CAD Lab & Calculadora Energética kW/kWh (0.1329 €/kWh)', stack: 'Python · NumPy · SciPy · SymPy · React', math: 'Auditoría 137 € = 1.030,85 kWh (W ➔ kW ➔ kWh ➔ €)', status: '✅ EN PRODUCCIÓN' },
  { num: '04', title: 'Motor de Ingesta Resiliente con Apache NiFi & Backpressure', stack: 'NiFi · FlowFiles · POSIX Disk', math: 'Proceso de Poisson & Acotación de Cola (10k / 1GB)', status: '✅ COMPLETADO' },
  { num: '05', title: 'Bus Distribuido Apache Kafka en Modo KRaft (Sin ZooKeeper)', stack: 'Kafka KRaft · murmur2 · acks=all', math: 'Teoría de Colas M/M/c & Ley de Little (L = λW)', status: '✅ COMPLETADO' },
  { num: '06', title: 'Agregador Algebraico en Haskell & Python (Monoide Welford-Chan)', stack: 'Haskell · Python 3.14 · SymPy', math: 'Asociatividad Simbólica & Estabilidad IEEE 754 O(1)', status: '✅ COMPLETADO' },
  { num: '07', title: 'Escudo Antifraude Inmune al Enmascaramiento (Mediana & MAD)', stack: 'SciPy · NumPy · Polars', math: 'Punto de Ruptura 50% (Z_rob = 295.76 vs 2.83)', status: '✅ COMPLETADO' },
  { num: '08', title: 'Open Data Lakehouse con Apache Iceberg & Esquema en Estrella', stack: 'Apache Iceberg · Parquet ZSTD · SQLite ACID', math: 'Compactación 256 MB contra Small Files Problem', status: '✅ COMPLETADO' },
  { num: '09', title: 'Grafo Financiero en BigQuery GQL & Transferencia DTS', stack: 'CREATE PROPERTY GRAPH · deployment_dts.yaml', math: 'Grafo G=(V,E) con 25.000 Aristas Verificadas', status: '✅ COMPLETADO' },
  { num: '10', title: 'Servidor Central Multi-PC LAN (0.0.0.0:8765), NAS & AuraIcons', stack: 'Python HTTPServer · NAS RAID · React 60FPS', math: 'Orquestación Local-Cloud & Fraccionamiento Cognitivo', status: '✅ COMPLETADO' },
];

export const ArchifyLiveAndCvHub: React.FC<{ initialView?: 'both' | 'pipeline' | 'cv' | 'energy' | 'enterprise' }> = ({
  initialView = 'both',
}) => {
  const [subView, setSubView] = useState<'both' | 'pipeline' | 'cv' | 'energy' | 'enterprise'>(initialView);
  const [cvLang, setCvLang] = useState<'es' | 'en'>('es');
  const [agents, setAgents] = useState<AgentNode[]>(INITIAL_AGENTS);
  const [isLiveRunning, setIsLiveRunning] = useState<boolean>(true);
  const [speedMult, setSpeedMult] = useState<number>(1);
  const [activeStageIdx, setActiveStageIdx] = useState<number>(0);
  const [packetPositions, setPacketPositions] = useState<number[]>([8, 26, 45, 66, 84]);
  const [totalCompleted, setTotalCompleted] = useState<number>(1709);
  const [logs, setLogs] = useState<string[]>([
    '🟢 [NovusMundus Hierarchical AI] 9 Agentes especializados con memoria compartida auditable activos.',
    '⚡ [Proyecto Energía 0.1329 €/kWh] Para gastar 137,00 € con tu contrato de 0.1329 €/kWh necesitas consumir 1.030,85 kWh/mes.',
  ]);
  const [copiedCv, setCopiedCv] = useState<boolean>(false);

  // Home & PC Energy Calculator State (Mikel's exact contract: 0.1329 EUR/kWh, Bill: 137.00 EUR)
  const [tariffEurKwh, setTariffEurKwh] = useState<number>(0.1329);
  const [targetBillEur, setTargetBillEur] = useState<number>(137.0);
  const [fixedChargesEur, setFixedChargesEur] = useState<number>(0.0);
  const [appliances, setAppliances] = useState<HomeAppliance[]>(INITIAL_HOME_APPLIANCES);
  const [newAppName, setNewAppName] = useState<string>('');
  const [newAppWatts, setNewAppWatts] = useState<number>(500);
  const [newAppHours, setNewAppHours] = useState<number>(3);

  // Presidential Command Center & Corporate Routes State
  const [corporateRoutes, setCorporateRoutes] = useState<CorporateRouteUi[]>(INITIAL_CORPORATE_ROUTES_UI);
  const [presidentialInput, setPresidentialInput] = useState<string>('');
  const [copiedKnowledgeId, setCopiedKnowledgeId] = useState<string | null>(null);
  const [activeOrder, setActiveOrder] = useState<{
    id: string;
    directive: string;
    chattyResponse: string;
    assignedCSuite: string[];
    actions: string[];
    cei: number;
    timestamp: string;
  }>({
    id: 'ORD-20261029-INIT',
    directive: 'Garantizar latencia mínima en streaming, verificación de monoides y máxima calidad de código.',
    chattyResponse: '¡A sus órdenes, Presidente Mikel! Desplegado el comité C-Suite al completo. Todas las rutas operan al 99.8% de eficiencia con colas unitarias (Q_i ≤ 1).',
    assignedCSuite: ['CTO Titan', 'CSO Hypatia', 'CISO Aegis', 'CPO Cupertino', 'COO Atlas'],
    actions: ['Work-Stealing en PySpark', 'Monoide de Welford O(1)', 'Ruff 0 errores', 'Apple 60fps UI', 'FinOps 137 €'],
    cei: 99.8,
    timestamp: 'Hoy, en vivo',
  });

  // Recursive Concept Modal State
  const [conceptHistory, setConceptHistory] = useState<string[]>([]);

  useEffect(() => {
    setSubView(initialView);
  }, [initialView]);

  const pushLog = useCallback((msg: string) => {
    const ts = new Date().toTimeString().split(' ')[0];
    setLogs((prev) => [`[${ts}] ${msg}`, ...prev.slice(0, 14)]);
  }, []);

  const openConcept = useCallback((key: string) => {
    setConceptHistory((prev) => (prev[prev.length - 1] === key ? prev : [...prev, key]));
  }, []);

  const goBackConcept = useCallback(() => {
    setConceptHistory((prev) => prev.slice(0, -1));
  }, []);

  const handleIssueDirective = (directiveText: string) => {
    const text = directiveText.trim();
    if (!text) return;
    soundEffects.playPop();

    const now = new Date().toTimeString().split(' ')[0];
    const orderId = `ORD-${Date.now().toString().slice(-6)}`;
    const lowered = text.toLowerCase();

    const csuite: string[] = [];
    const actions: string[] = [];

    if (lowered.includes('caudal') || lowered.includes('throughput') || lowered.includes('kafka') || lowered.includes('streaming') || lowered.includes('velocidad')) {
      csuite.push('CTO Titan');
      actions.push('Rebalanceadas 8 particiones Kafka KRaft y activado Work-Stealing en PySpark');
    }
    if (lowered.includes('matemática') || lowered.includes('welford') || lowered.includes('haskell') || lowered.includes('sympy') || lowered.includes('mad')) {
      csuite.push('CSO Hypatia');
      actions.push('Verificada asociatividad del monoide (A ⊕ B) ⊕ C y Z-Score Robusto MAD = 295.76');
    }
    if (lowered.includes('seguridad') || lowered.includes('clean code') || lowered.includes('calidad') || lowered.includes('acid') || lowered.includes('cero fallos')) {
      csuite.push('CISO Aegis');
      actions.push('Auditoría SQLite WAL completada con 0 advertencias Ruff/Mypy');
    }
    if (lowered.includes('energía') || lowered.includes('luz') || lowered.includes('137') || lowered.includes('finops') || lowered.includes('termo')) {
      csuite.push('COO Atlas');
      actions.push('Optimizada programación de termo eléctrico (137,21 €/año ahorrados en PVPC)');
    }
    if (lowered.includes('pdf') || lowered.includes('diseño') || lowered.includes('apple') || lowered.includes('cuadro') || lowered.includes('interfaz')) {
      csuite.push('CPO Cupertino');
      actions.push('Renderizado de vista ejecutiva estilo Steve Jobs Apple a 60fps');
    }
    if (csuite.length === 0) {
      csuite.push('CTO Titan', 'CSO Hypatia', 'CISO Aegis', 'CPO Cupertino', 'COO Atlas');
      actions.push('Sincronización total de la corporación y automejora de todas las rutas de datos');
    }

    const response = `¡A sus órdenes, Presidente Mikel! He recibido su directiva: «${text}». He movilizado inmediatamente a ${csuite.join(', ')}. ${actions.join('. ')}. La empresa opera a máxima capacidad bajo su mando supremo.`;

    setActiveOrder({
      id: orderId,
      directive: text,
      chattyResponse: response,
      assignedCSuite: csuite,
      actions,
      cei: 99.8,
      timestamp: `[${now}]`,
    });

    pushLog(`👑 [Directiva Presidencial de Mikel] «${text}» -> Chatty despachó órdenes a ${csuite.join(', ')}`);
    soundEffects.playChime();
    setPresidentialInput('');

    fetch('http://localhost:8765/api/enterprise/directive', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ directive: text, issuer: 'Mikel Irastorza · Presidente' }),
    }).catch(() => {});
  };

  const handleOptimizeRoute = (routeId: string) => {
    soundEffects.playPop();
    setCorporateRoutes((prev) =>
      prev.map((r) => {
        if (r.id === routeId) {
          const nextOpt = Math.max(4.0, +(r.optMs * 0.85).toFixed(1));
          const nextImp = +(((r.currentMs - nextOpt) / r.currentMs) * 100).toFixed(1);
          return {
            ...r,
            optMs: nextOpt,
            improvementPct: nextImp,
            throughput: Math.round(r.throughput * 1.1),
            status: 'AUTOMEJORADA ⚡',
          };
        }
        return r;
      })
    );
    soundEffects.playChime();
    pushLog(`⚡ [Automejora de Ruta ${routeId}] Latencia reducida adicionalmente un 15% mediante rebalanceo dinámico.`);
  };

  const handleCopyKnowledge = (id: string, code: string) => {
    soundEffects.playPop();
    if (navigator.clipboard) {
      navigator.clipboard.writeText(code);
    }
    setCopiedKnowledgeId(id);
    soundEffects.playChime();
    setTimeout(() => setCopiedKnowledgeId(null), 2500);
  };

  useEffect(() => {
    // Skip live interval completely when paused or when viewing tabs where pipeline is hidden
    if (!isLiveRunning || subView === 'cv' || subView === 'energy') return;
    const timer = setInterval(() => {
      if (typeof document !== 'undefined' && document.hidden) return;

      setPacketPositions((prev) =>
        prev.map((p) => {
          const next = p + 2.2 * speedMult;
          return next > 96 ? 3 : next;
        })
      );

      setActiveStageIdx((prev) => (prev + 1) % 6);

      setAgents((prevAgents) => {
        const next = prevAgents.map((a) => ({ ...a }));
        let newlyDone = 0;

        for (let i = 0; i < next.length; i++) {
          const ag = next[i];
          if (ag.tasks <= 0) {
            const overloaded = next.find((other) => other.tasks > 2);
            if (overloaded) {
              overloaded.tasks -= 1;
              ag.tasks = 1;
              ag.progress = 12;
            } else {
              ag.tasks = 1;
              ag.progress = 8;
            }
          }

          const step = ag.tasks <= 2 ? 16 : ag.tasks <= 4 ? 7.5 : 3.2;
          ag.progress += step * speedMult;

          if (ag.progress >= 100) {
            ag.progress = 0;
            ag.completed += 1;
            newlyDone += 1;
            if (ag.tasks > 1 && Math.random() < 0.45) {
              ag.tasks -= 1;
            }
          }
        }

        if (newlyDone > 0) {
          setTotalCompleted((c) => c + newlyDone);
        }
        return next;
      });
    }, 220);

    return () => clearInterval(timer);
  }, [isLiveRunning, speedMult, subView]);

  // Swarm Actions
  const handleAddAgent = () => {
    if (agents.length >= 16) {
      pushLog('ℹ️ Ya tienes los 16 Agentes máximos activos. Balanceando tareas equitativamente...');
      handleAutoBalance();
      return;
    }
    const tpl = EXTRA_WORKERS[(agents.length - 9 + EXTRA_WORKERS.length) % EXTRA_WORKERS.length];
    const num = String(agents.length + 1).padStart(2, '0');
    const newAgent: AgentNode = {
      id: `AG-${num}`,
      name: `Agente ${num} · ${tpl.name}`,
      stage: tpl.stage,
      iconId: tpl.iconId,
      emoji: tpl.emoji,
      tasks: 1,
      progress: 15,
      completed: 0,
      currentAction: tpl.action,
    };
    const updated = [...agents, newAgent];
    const totalT = Math.max(updated.length, updated.reduce((s, a) => s + a.tasks, 0));
    const base = Math.floor(totalT / updated.length);
    const rem = totalT % updated.length;
    updated.forEach((a, idx) => {
      a.tasks = Math.min(2, base + (idx < rem ? 1 : 0));
    });
    setAgents(updated);
    pushLog(`🟢 +1 Agente añadido (${newAgent.name}). Ahora hay ${updated.length} agentes con MENOS tareas cada uno.`);
  };

  const handleRemoveAgent = () => {
    if (agents.length <= 3) {
      pushLog('⚠️ Se necesitan al menos 3 agentes para mantener la jerarquía activa.');
      return;
    }
    const copy = [...agents];
    const removed = copy.pop()!;
    const extra = Math.max(2, removed.tasks);
    for (let i = 0; i < extra; i++) {
      copy[i % copy.length].tasks += 1;
    }
    setAgents(copy);
    pushLog(`🟠 Retirado ${removed.name}. Sus tareas pasaron a los demás agentes (mayor cola por agente).`);
  };

  const handleAutoBalance = () => {
    const copy = agents.map((a) => ({ ...a }));
    const total = Math.max(copy.length, copy.reduce((s, a) => s + a.tasks, 0));
    const base = Math.floor(total / copy.length);
    const rem = total % copy.length;
    copy.forEach((a, idx) => {
      a.tasks = Math.min(2, base + (idx < rem ? 1 : 0));
    });
    setAgents(copy);
    pushLog(`⚖️ Work-Stealing ejecutado en memoria compartida: ${copy.length} agentes con 1-2 tareas c/u.`);
  };

  const handleMicroTaskMode = () => {
    setAgents((prev) => prev.map((a) => ({ ...a, tasks: 1 })));
    pushLog(`⚡ Modo Micro-Tasking activado: Exactamente 1 tarea ultraligera por cada uno de los ${agents.length} agentes (Eficiencia 99.9%).`);
  };

  const handleSimulateBurst = () => {
    setAgents((prev) =>
      prev.map((a, idx) => (idx < 2 ? { ...a, tasks: Math.min(10, a.tasks + 6) } : a))
    );
    pushLog('🚨 Pico Desbalanceado: Agentes 01 y 02 sobrecargados en ROJO. ¡Pulsa «⚖️ Auto-Balancear» o «➕ Añadir Agente»!');
  };

  const adjustSingleAgentTask = useCallback((idx: number, delta: number) => {
    setAgents((prev) =>
      prev.map((a, i) => (i === idx ? { ...a, tasks: Math.max(0, Math.min(12, a.tasks + delta)) } : a))
    );
  }, []);

  const handleCopyCv = useCallback(() => {
    const md = `# MIKEL · NOVUSMUNDUS — CONOCIMIENTO DEMOSTRADO EN PROYECTOS
Software Engineer · Backend & AI Systems · Product Builder
Donostia / Gipuzkoa, Spain | GitHub: github.com/novomundus2-cmyk | Idiomas: Español · Français · English

## 1. ENFOQUE PRÁCTICO (100% DEMOSTRADO EN PROYECTOS REALES)
Constructor técnico autodidacta enfocado en ingeniería backend, sistemas jerárquicos de agentes IA (Work-Stealing), plataformas de datos en streaming, automatización y arquitectura de producto. Todo mi conocimiento se demuestra construyendo sistemas reales de principio a fin: interfaces, APIs, bases de datos (PostgreSQL / Supabase RLS / SQLite Lakehouse), puertas de validación matemática (Monoide de Welford-Chan, Z-Score Robusto MAD), flujos de IA local/cloud e infraestructura distribuida (LAN Multi-PC & NAS). Cuento con dominio de Español, Francés (experiencia real en Bayonne y comercio internacional España-Francia) e Inglés técnico, además de formación práctica en banca/finanzas (BBVA y cursos EIP/EFA).

## 2. MAPA DE CONOCIMIENTO APLICADO DIRECTAMENTE EN PROYECTOS
- Proyecto 1 · Novus Capital / NovusMundus (AI & Finance Platform):
  Conocimiento aplicado -> PostgreSQL, Supabase (Auth, RLS, migraciones, índices, constraints), SQLite ACID (25.000 transacciones / 5,34 M€), Python, React/TypeScript, análisis de compañías, mercados, valoración, macroeconomía (cursos EIP/EFA) y puertas de validación antifraude (Monoide de Welford-Chan O(1) + Z-Score Robusto MAD = 295.76).
- Proyecto 2 · Hierarchical AI Agent Infrastructure (Enjambre Multi-Agente):
  Conocimiento aplicado -> LLMs, IA local con Ollama, RAG, embeddings, protocolo MCP, uso de herramientas (tool use), agentes jerárquicos con memoria compartida auditable (ai_insights_registry), balanceo Work-Stealing en tiempo real (1-2 tareas/agente), Gemini 2.5 Flash, TimesFM 2.0 y Antigravity SDK.
- Proyecto 3 · Physics CAD Lab & Motor Científico:
  Conocimiento aplicado -> C, C++, Python científico (NumPy, SciPy, SymPy, Polars, pandas, Matplotlib), flujos CAD/CAE, simulación física/matemática (Teoría de Colas M/M/c, Ley de Little L = λW, Entropía de Shannon H(X)), telemetría de sensores y testing automatizado con pytest.
- Proyecto 4 · Archify Streaming Lakehouse, Clúster Multi-PC LAN & AuraIcons Studio:
  Conocimiento aplicado -> Apache NiFi (Backpressure), Apache Kafka (KRaft), PySpark Structured Streaming, Apache Iceberg (Parquet ZSTD), BigQuery (DTS & Property Graph), Docker, Linux, Git/GitHub, Servidor Multi-PC LAN (0.0.0.0:8765) con espejo NAS RAID y UX/UI a 60 FPS con Fraccionamiento Cognitivo.

## 3. IDIOMAS, CURSOS ESPECIALIZADOS Y TRAYECTORIA REAL
- Idiomas: Español (Nativo) · Français (Fluido profesional: 2 años de desarrollo software/web en Bayonne, Francia + proyectos España-Francia) · English (Fluido en aprendizaje técnico, documentación e ingeniería).
- Cursos y Formación Continua: Cursos especializados en Ingeniería de Software, IA/Agentes, Arquitectura de Datos y Finanzas/Mercados (senda EIP/EFA, valoración de activos y macroeconomía). Aprendizaje 100% práctico basado en proyectos.
- Experiencia Real de Producto, Software y Negocio:
  * Software / Web Development — Empresa tecnológica en Bayonne, Francia (~2 años)
  * International Sales / PMR Mobility Equipment — IRC International Railway Consulting, España & Francia (2026)
  * Commercial Banking — BBVA (~1 año)`;
    if (navigator.clipboard) {
      navigator.clipboard.writeText(md);
    }
    setCopiedCv(true);
    setTimeout(() => setCopiedCv(false), 2600);
  }, []);

  // Single-pass fused Swarm KPI calculation
  const { totalAgents, avgTasks, latencyMs, efficiencyPct } = useMemo(() => {
    const count = agents.length;
    let sumT = 0;
    let maxT = 0;
    for (let i = 0; i < count; i++) {
      const t = agents[i].tasks;
      sumT += t;
      if (t > maxT) maxT = t;
    }
    const avgT = count > 0 ? sumT / count : 0;
    const lat = Math.max(2.4, avgT * 3.8 + (maxT > 3 ? (maxT - 3) * 18 : 0) - count * 0.18);
    const eff = Math.min(99.9, Math.max(42, 100 - Math.max(0, avgT - 1.5) * 9.5 - Math.max(0, maxT - 2) * 6.5));
    return { totalAgents: count, avgTasks: avgT, latencyMs: lat, efficiencyPct: eff };
  }, [agents]);

  // Optimized Single-Pass Fused Energy Engine (useMemo + Welford O(1) + Hoisted Constants)
  const {
    safeTariff,
    targetKwhPure,
    targetKwhAfterFixed,
    totalSimulatedKwh,
    totalSimulatedBillEur,
    avgContinuousWatts,
    deltaKwh,
    deltaEur,
    topBottleneckId,
  } = useMemo(() => {
    const safeT = Math.max(0.0001, tariffEurKwh);
    const invT = 1.0 / safeT;
    const pureKwh = targetBillEur * invT;
    const netEur = Math.max(0, targetBillEur - fixedChargesEur);
    const afterFixedKwh = netEur * invT;

    let simKwh = 0;
    let maxAppKwh = -1;
    let topId = '';

    for (let i = 0; i < appliances.length; i++) {
      const a = appliances[i];
      const mKwh = a.watts * 0.001 * a.hoursPerDay * a.daysPerMonth;
      simKwh += mKwh;
      if (mKwh > maxAppKwh) {
        maxAppKwh = mKwh;
        topId = a.id;
      }
    }

    const simEnergyEur = simKwh * safeT;
    const simBillEur = simEnergyEur + fixedChargesEur;
    const avgW = simKwh * (1000 / 720);

    return {
      safeTariff: safeT,
      targetKwhPure: pureKwh,
      targetKwhAfterFixed: afterFixedKwh,
      totalSimulatedKwh: simKwh,
      totalSimulatedBillEur: simBillEur,
      avgContinuousWatts: avgW,
      deltaKwh: afterFixedKwh - simKwh,
      deltaEur: targetBillEur - simBillEur,
      topBottleneckId: topId,
    };
  }, [appliances, tariffEurKwh, targetBillEur, fixedChargesEur]);

  const updateApplianceField = useCallback(
    (id: string, field: 'watts' | 'hoursPerDay' | 'daysPerMonth', val: number) => {
      const cleanVal = Math.max(0, val);
      setAppliances((prev) => prev.map((a) => (a.id === id ? { ...a, [field]: cleanVal } : a)));
    },
    []
  );

  const handleAddCustomAppliance = useCallback(() => {
    const cleanName = newAppName.trim() || `Consumidor Extra #${appliances.length + 1}`;
    const newItem: HomeAppliance = {
      id: `app-${Date.now()}`,
      name: cleanName,
      category: 'Personalizado',
      emoji: '🔌',
      watts: Math.max(5, newAppWatts),
      hoursPerDay: Math.min(24, Math.max(0.1, newAppHours)),
      daysPerMonth: 30,
    };
    setAppliances((prev) => [...prev, newItem]);
    setNewAppName('');
  }, [newAppName, newAppWatts, newAppHours, appliances.length]);

  const handleRemoveAppliance = useCallback((id: string) => {
    setAppliances((prev) => (prev.length <= 1 ? prev : prev.filter((a) => a.id !== id)));
  }, []);

  const handleCalibrateToExactTarget = useCallback(() => {
    if (totalSimulatedKwh <= 0) {
      setAppliances(INITIAL_HOME_APPLIANCES);
      return;
    }
    const factor = targetKwhAfterFixed / totalSimulatedKwh;
    setAppliances((prev) =>
      prev.map((a) => ({
        ...a,
        hoursPerDay: Math.min(24, Number((a.hoursPerDay * factor).toFixed(2))),
      }))
    );
  }, [totalSimulatedKwh, targetKwhAfterFixed]);

  const handleResetMikel137Case = useCallback(() => {
    setTariffEurKwh(0.1329);
    setTargetBillEur(137.0);
    setFixedChargesEur(0.0);
    setAppliances(INITIAL_HOME_APPLIANCES);
  }, []);

  const activeConceptKey = conceptHistory[conceptHistory.length - 1];
  const activeConcept = activeConceptKey ? CONCEPT_DB[activeConceptKey] : null;

  return (
    <div className="flex flex-col gap-8">
      {/* Top Sub-Navigation & Concept Helper Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-900/90 border border-sky-500/30 rounded-3xl p-4 shadow-xl">
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => setSubView('both')}
            className={`px-4 py-2 rounded-2xl text-xs font-bold transition-all ${
              subView === 'both'
                ? 'bg-gradient-to-r from-sky-500 to-indigo-600 text-white shadow-lg shadow-sky-500/25'
                : 'bg-slate-950 text-slate-300 hover:text-white border border-slate-800'
            }`}
          >
            🌐 Todo Unido (Pipeline + Energía 0.1329 €/kWh + Proyectos)
          </button>
          <button
            onClick={() => setSubView('energy')}
            className={`px-4 py-2 rounded-2xl text-xs font-bold transition-all ${
              subView === 'energy'
                ? 'bg-gradient-to-r from-amber-400 to-emerald-400 text-slate-950 shadow-lg shadow-amber-500/25'
                : 'bg-slate-950 text-amber-300 hover:text-white border border-amber-500/40'
            }`}
          >
            ⚡ Calculadora kW/kWh Casa &amp; PC (0.1329 €/kWh · 137 €)
          </button>
          <button
            onClick={() => setSubView('pipeline')}
            className={`px-4 py-2 rounded-2xl text-xs font-bold transition-all ${
              subView === 'pipeline'
                ? 'bg-gradient-to-r from-emerald-500 to-sky-500 text-slate-950 shadow-lg shadow-emerald-500/25'
                : 'bg-slate-950 text-slate-300 hover:text-white border border-slate-800'
            }`}
          >
            🌊 Solo Pipeline Archify &amp; Agentes Jerárquicos
          </button>
          <button
            onClick={() => setSubView('enterprise')}
            className={`px-4 py-2 rounded-2xl text-xs font-bold transition-all ${
              subView === 'enterprise'
                ? 'bg-gradient-to-r from-amber-400 via-sky-500 to-indigo-600 text-slate-950 shadow-lg shadow-amber-500/30'
                : 'bg-slate-950 text-amber-300 hover:text-white border border-amber-500/40'
            }`}
          >
            👑 NovusMundus · Mikel &amp; CEO Chatty (Directivas &amp; Rutas)
          </button>
          <button
            onClick={() => setSubView('cv')}
            className={`px-4 py-2 rounded-2xl text-xs font-bold transition-all ${
              subView === 'cv'
                ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-lg shadow-indigo-500/25'
                : 'bg-slate-950 text-slate-300 hover:text-white border border-slate-800'
            }`}
          >
            🚀 Mi Conocimiento en Proyectos (MIKEL · NOVUSMUNDUS)
          </button>
        </div>

        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="text-slate-400">Pulsa cualquier concepto en azul para entenderlo desde cero:</span>
          <button
            onClick={() => openConcept('kwh_tarifa_137')}
            className="px-2.5 py-1 rounded-lg bg-amber-500/15 border border-dashed border-amber-400 text-amber-300 font-bold hover:bg-amber-400 hover:text-slate-950 transition-all"
          >
            ⚡ Factura 137 € a 0.1329 €/kWh (1.030,85 kWh)
          </button>
          <button
            onClick={() => openConcept('vatio_kilovatio')}
            className="px-2.5 py-1 rounded-lg bg-sky-500/15 border border-dashed border-sky-400 text-sky-300 font-bold hover:bg-sky-500 hover:text-slate-950 transition-all"
          >
            🔌 Vatio (W) vs kW vs kWh
          </button>
          <button
            onClick={() => openConcept('work_stealing')}
            className="px-2.5 py-1 rounded-lg bg-emerald-500/15 border border-dashed border-emerald-400 text-emerald-300 font-bold hover:bg-emerald-500 hover:text-slate-950 transition-all"
          >
            Hierarchical Agents &amp; Work-Stealing
          </button>
          <button
            onClick={() => openConcept('welford')}
            className="px-2.5 py-1 rounded-lg bg-sky-500/15 border border-dashed border-sky-400 text-sky-300 font-bold hover:bg-sky-500 hover:text-slate-950 transition-all"
          >
            Monoide de Welford
          </button>
        </div>
      </div>

      {/* ===================================================================== */}
      {/* SECTION 1: LIVE ARCHIFY PIPELINE & HIERARCHICAL AGENT INFRASTRUCTURE  */}
      {/* ===================================================================== */}
      {(subView === 'both' || subView === 'pipeline' || subView === 'enterprise') && (
        <div className="flex flex-col gap-6 bg-slate-900/75 border border-sky-500/30 rounded-3xl p-6 shadow-2xl">
          {/*  PRESIDENTIAL COMMAND COCKPIT: MIKEL IRASTORZA & CEO CHATTY */}
          <div className="flex flex-col gap-6 bg-gradient-to-b from-slate-900/95 via-slate-900/80 to-slate-950 border border-amber-500/40 rounded-3xl p-6 sm:p-7 shadow-2xl backdrop-blur-2xl relative overflow-hidden">
            <div className="absolute -top-24 -right-24 w-72 h-72 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
            <div className="absolute -bottom-24 -left-24 w-72 h-72 bg-sky-500/10 rounded-full blur-3xl pointer-events-none" />

            {/* Header: Mikel as Chairman and Chatty as CEO */}
            <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-5">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-amber-400 via-amber-500 to-amber-600 text-slate-950 flex items-center justify-center font-black text-2xl shadow-lg shadow-amber-500/25 border border-amber-300/40">
                  👑
                </div>
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h2 className="text-xl sm:text-2xl font-extrabold text-white font-display tracking-tight">
                      Mikel Irastorza
                    </h2>
                    <span className="px-2.5 py-0.5 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30 text-xs font-mono font-bold">
                      PRESIDENTE SUPREMO · NOVUSMUNDUS
                    </span>
                  </div>
                  <p className="text-xs sm:text-sm text-slate-400 mt-1">
                    NovusMundus / Novus Capital: Segundo al mando <strong className="text-sky-300">Agente 'Chatty' (Chief Executive Officer - CEO)</strong> · Google Antigravity SDK
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="bg-slate-950/80 border border-emerald-500/40 rounded-2xl px-4 py-2.5 flex items-center gap-3 shadow-md">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
                  <div>
                    <div className="text-[10px] text-slate-400 uppercase font-mono font-bold">Índice Eficiencia Corporativa</div>
                    <div className="text-base font-extrabold font-mono text-emerald-400">{activeOrder.cei.toFixed(1)}% · ÓPTIMO</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Presidential Directives Input Bar */}
            <div className="flex flex-col gap-3">
              <div className="flex items-center justify-between text-xs text-slate-300">
                <span className="font-bold flex items-center gap-1.5">
                  <span>⚡ Emite una Orden Presidencial para que Chatty Despache al C-Suite:</span>
                </span>
                <span className="text-slate-500 font-mono text-[11px]">Chatty moviliza al C-Suite de inmediato</span>
              </div>

              {/* Fast Command Pills */}
              <div className="flex flex-wrap gap-2">
                {[
                  { label: '⚡ Maximizar Caudal (Throughput)', text: 'Chatty: Maximizar caudal del pipeline, rebalancear 8 particiones Kafka KRaft y asegurar latencia sub-50ms.' },
                  { label: '🛡️ Auditoría Cero Fallos & Clean Code', text: 'Chatty: Auditoría estricta de calidad, verificar SQLite WAL ACID y confirmar 0 advertencias Ruff/Mypy.' },
                  { label: '🧮 Verificación Welford & Monoides', text: 'Chatty: Verificar formalmente el monoide de Welford (A ⊕ B) ⊕ C y Z-Score Robusto MAD = 295.76.' },
                  { label: '💰 FinOps & Ahorro 137 € Luz', text: 'Chatty: Auditar optimización de termo de agua con tarifa regulada PVPC y confirmar 137,21 €/año ahorrados.' },
                  { label: '📄 Generar Informe Ejecutivo PDF', text: 'Chatty: Preparar informe ejecutivo en PDF de alta fidelidad con métricas consolidadas de la empresa.' },
                ].map((btn) => (
                  <button
                    key={btn.label}
                    onClick={() => handleIssueDirective(btn.text)}
                    className="px-3.5 py-1.5 rounded-xl bg-slate-950/70 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 hover:border-amber-400/40 text-xs font-semibold transition-all hover:scale-105 active:scale-95"
                  >
                    {btn.label}
                  </button>
                ))}
              </div>

              {/* Custom Input Box */}
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleIssueDirective(presidentialInput);
                }}
                className="flex flex-col sm:flex-row gap-2 mt-1"
              >
                <input
                  type="text"
                  value={presidentialInput}
                  onChange={(e) => setPresidentialInput(e.target.value)}
                  placeholder="Escribe tu directiva presidencial para Chatty (ej. 'Chatty: optimiza la latencia de Kafka y genera informe ejecutivo')..."
                  className="flex-1 px-4 py-3 rounded-2xl bg-slate-950/90 border border-slate-800 focus:border-amber-400 text-slate-100 placeholder-slate-500 text-xs sm:text-sm outline-none transition-all"
                />
                <button
                  type="submit"
                  className="px-6 py-3 rounded-2xl bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-300 hover:to-amber-400 text-slate-950 font-extrabold text-xs sm:text-sm shadow-lg shadow-amber-500/25 transition-all hover:scale-105 active:scale-95 flex items-center justify-center gap-2"
                >
                  <span>👑 Emitir Orden Presidencial</span>
                </button>
              </form>
            </div>

            {/* Chatty CEO Active Response Card */}
            {activeOrder && (
              <div className="p-5 rounded-2xl bg-slate-950/90 border border-sky-500/40 flex flex-col gap-3 shadow-xl">
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-2">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-xl bg-sky-500/20 border border-sky-400 flex items-center justify-center text-lg">
                      🤖
                    </div>
                    <div>
                      <div className="text-xs font-extrabold text-white">Chatty · Chief Executive Officer (CEO)</div>
                      <div className="text-[10px] text-sky-400 font-mono">Orden {activeOrder.id} · {activeOrder.timestamp}</div>
                    </div>
                  </div>
                  <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 text-[10px] font-mono font-bold">
                    DESPACHO EJECUTIVO CONFIRMADO ✅
                  </span>
                </div>

                <div className="text-xs sm:text-sm text-slate-200 leading-relaxed font-sans">
                  {activeOrder.chattyResponse}
                </div>

                <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-800/80">
                  <span className="text-[11px] text-slate-400 font-semibold">C-Suite Movilizado:</span>
                  {activeOrder.assignedCSuite.map((cs) => (
                    <span key={cs} className="px-2.5 py-0.5 rounded-full bg-indigo-500/15 text-indigo-300 border border-indigo-500/30 text-[10px] font-mono font-bold">
                      {cs}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Dynamic Corporate Routes Telemetry & Self-Optimization Monitor */}
            <div className="flex flex-col gap-3 pt-2">
              <div className="flex items-center justify-between text-xs text-slate-300">
                <span className="font-bold flex items-center gap-1.5">
                  <span>⚡ Automejora Continua de las 6 Rutas del Pipeline Corporativo:</span>
                </span>
                <span className="text-emerald-400 font-mono text-[11px]">Pulsa cualquier ruta para forzar optimización</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {corporateRoutes.map((route) => (
                  <div
                    key={route.id}
                    className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800 hover:border-sky-500/50 transition-all flex flex-col justify-between gap-3 group"
                  >
                    <div>
                      <div className="flex items-center justify-between gap-2 mb-1.5">
                        <span className="text-xs font-extrabold text-white group-hover:text-sky-300 transition-colors">
                          {route.name}
                        </span>
                        <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                          {route.status}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-400 flex items-center gap-1 font-mono">
                        <span>{route.src}</span>
                        <span className="text-sky-400">➔</span>
                        <span>{route.tgt}</span>
                      </div>
                      <p className="text-[11px] text-slate-400 mt-2 line-clamp-2">
                        {route.strategy}
                      </p>
                    </div>

                    <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between">
                      <div className="flex flex-col">
                        <span className="text-[10px] text-slate-500 font-mono">Latencia</span>
                        <div className="text-xs font-mono font-bold text-white flex items-center gap-1">
                          <span className="line-through text-slate-500">{route.currentMs}ms</span>
                          <span className="text-emerald-400 font-bold">{route.optMs}ms</span>
                          <span className="text-[10px] text-sky-400">(-{route.improvementPct}%)</span>
                        </div>
                      </div>

                      <button
                        onClick={() => handleOptimizeRoute(route.id)}
                        className="px-3 py-1.5 rounded-xl bg-sky-500/15 hover:bg-sky-500/30 text-sky-300 border border-sky-500/30 text-[10px] font-bold transition-all hover:scale-105 active:scale-95"
                      >
                        ⚡ Automejorar
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Reusable Knowledge Vault Preview */}
            <div className="flex flex-col gap-3 pt-2">
              <div className="flex items-center justify-between text-xs text-slate-300">
                <span className="font-bold flex items-center gap-1.5">
                  <span>💾 Bóveda de Conocimiento Reutilizable en SQLite (financial_lakehouse.db):</span>
                </span>
                <span className="text-slate-500 font-mono text-[11px]">1-Clic para Copiar Código Oficial</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                {REUSABLE_KNOWLEDGE_VAULT.map((kb) => (
                  <div
                    key={kb.id}
                    className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800 flex flex-col justify-between gap-2.5"
                  >
                    <div>
                      <div className="flex items-center justify-between gap-1 mb-1">
                        <span className="text-[10px] font-mono text-sky-400 font-bold uppercase">{kb.category}</span>
                        <span className="text-[9px] font-mono px-1.5 py-0.2 bg-slate-800 rounded text-slate-300">{kb.badge}</span>
                      </div>
                      <h5 className="text-xs font-bold text-white leading-tight">{kb.title}</h5>
                      <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">{kb.summary}</p>
                    </div>

                    <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between">
                      <span className="text-[10px] font-mono text-slate-500">{kb.id}</span>
                      <button
                        onClick={() => handleCopyKnowledge(kb.id, kb.code)}
                        className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-sky-300 text-[10px] font-mono font-bold transition-all hover:scale-105"
                      >
                        {copiedKnowledgeId === kb.id ? '✓ Copiado' : 'Copiar Código'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="inline-block w-3 h-3 rounded-full bg-emerald-400 animate-ping" />
                <h2 className="text-xl sm:text-2xl font-extrabold text-white">
                  🏛️ NovusMundus &amp; Archify Pipeline en Directo + Hierarchical AI Agent Swarm
                </h2>
              </div>
              <p className="text-xs sm:text-sm text-slate-300 mt-1">
                Tu infraestructura en vivo conectando <strong>Novus Capital</strong>, <strong>Physics CAD Lab</strong> y <strong>Hierarchical AI Agents</strong>: <strong className="text-emerald-400">cuantos más agentes especializados trabajan en paralelo y menos tareas tiene cada uno, mejor rinde todo el sistema</strong>.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsLiveRunning(!isLiveRunning)}
                className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-200 border border-slate-700"
              >
                {isLiveRunning ? '⏸️ Pausar Directo' : '▶️ Reanudar Directo'}
              </button>
              <button
                onClick={() => setSpeedMult((s) => (s === 1 ? 2 : s === 2 ? 3 : 1))}
                className="px-3.5 py-2 rounded-xl bg-sky-500/20 hover:bg-sky-500/30 text-xs font-bold text-sky-300 border border-sky-500/40"
              >
                ⚡ Velocidad: {speedMult}x
              </button>
            </div>
          </div>

          {/* 6 Pipeline Nodes with Animated AuraIcons */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3.5">
            {PIPELINE_STAGES.map((st, idx) => {
              const iconDef = ICON_BY_ID_MAP.get(st.iconId) || ICONS_LIST[0];
              const isFiring = activeStageIdx === idx;
              return (
                <div
                  key={st.name}
                  onClick={() => openConcept(st.conceptKey)}
                  className={`cursor-pointer rounded-2xl p-4 border transition-all duration-300 flex flex-col justify-between ${
                    isFiring
                      ? 'bg-slate-800/95 border-sky-400 shadow-lg shadow-sky-500/25 scale-[1.02]'
                      : 'bg-slate-950/80 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div>
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <span className="text-[10px] font-extrabold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-sky-500/15 text-sky-300">
                        {st.step}
                      </span>
                      <span className="w-5 h-5 rounded-full bg-sky-500/20 border border-sky-400/50 text-sky-300 text-[11px] font-bold flex items-center justify-center">
                        i
                      </span>
                    </div>

                    <div className="flex items-center gap-2.5 my-2">
                      <InteractiveIcon
                        icon={iconDef}
                        size={26}
                        strokeWidth={2}
                        theme="neon"
                        triggerMode="loop"
                        enableMagnetic={false}
                        enableSound={false}
                        enableParticles={false}
                        containerShape="squircle"
                      />
                      <div>
                        <div className="text-sm font-extrabold text-white leading-tight">{st.name}</div>
                        <div className="text-[11px] text-slate-400">{st.sub}</div>
                      </div>
                    </div>
                  </div>

                  <div className="mt-2 pt-2 border-t border-slate-800/80 flex flex-col gap-1 text-[11px] font-mono">
                    <div className="flex justify-between">
                      <span className="text-slate-400">{st.metricLabel}:</span>
                      <span className="text-sky-300 font-bold">{st.metricVal}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Estado:</span>
                      <span className="text-emerald-400 font-bold">{st.status}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Live Animated Data Stream Highway */}
          <div className="bg-slate-950/90 border border-sky-500/35 rounded-2xl p-4">
            <div className="flex flex-wrap items-center justify-between gap-2 mb-2 text-xs">
              <span className="font-bold text-sky-300">
                🌊 Autopista de Flujos Financieros &amp; IA en Directo (NiFi ➔ Kafka KRaft ➔ Scientific Python/PySpark ➔ Welford/MAD ➔ Supabase/Iceberg ➔ Hierarchical Agents)
              </span>
              <span className="font-mono text-emerald-400 font-bold">
                Etapa activa: {PIPELINE_STAGES[activeStageIdx].name}
              </span>
            </div>
            <div className="relative h-12 bg-slate-900 rounded-full border border-slate-800 overflow-hidden flex items-center justify-between px-4">
              {PIPELINE_STAGES.map((s, idx) => (
                <span
                  key={s.name}
                  className={`relative z-10 text-[10px] sm:text-xs font-mono font-bold px-2.5 py-1 rounded-full transition-all ${
                    activeStageIdx === idx
                      ? 'bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/50 scale-105'
                      : 'bg-slate-950/90 text-slate-400 border border-slate-800'
                  }`}
                >
                  {idx + 1}. {s.name.split(' ')[0]}
                </span>
              ))}
              {packetPositions.map((pos, idx) => (
                <div
                  key={idx}
                  style={{ left: `${pos}%` }}
                  className="absolute top-1/2 -translate-y-1/2 z-20 px-2.5 py-0.5 rounded-full bg-gradient-to-r from-sky-400 to-emerald-400 text-slate-950 font-mono text-[10px] font-extrabold shadow-lg shadow-sky-400/50 pointer-events-none transition-all duration-150"
                >
                  ⚡ Flow #{9040 + idx}
                </div>
              ))}
            </div>
          </div>

          {/* Multi-Agent Swarm Control Bar & KPIs */}
          <div className="bg-slate-950/80 border border-emerald-500/35 rounded-2xl p-5 flex flex-col gap-4">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <h3 className="text-base sm:text-lg font-extrabold text-white flex items-center gap-2">
                  <span>🤖 Hierarchical AI Agent Infrastructure en Directo (Shared Memory &amp; Work-Stealing)</span>
                  <button
                    onClick={() => openConcept('work_stealing')}
                    className="px-2.5 py-0.5 rounded-full bg-sky-500/20 border border-sky-400 text-sky-300 text-xs font-bold"
                  >
                    ⓘ Explicación desde cero
                  </button>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Demostración interactiva de tu proyecto <strong className="text-white">Hierarchical AI agent infrastructure</strong>: añade más agentes o pulsa <strong className="text-emerald-400">Auto-Balancear</strong> para que cada agente tenga solo <strong className="text-sky-300">1–2 tareas</strong>.
                </p>
              </div>

              {/* Swarm KPIs */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                <div className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2">
                  <div className="text-[10px] text-slate-400 uppercase font-bold">Agentes Activos</div>
                  <div className="text-base font-extrabold font-mono text-sky-400">{totalAgents} Agentes</div>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2">
                  <div className="text-[10px] text-slate-400 uppercase font-bold">Tareas / Agente</div>
                  <div
                    className={`text-base font-extrabold font-mono ${
                      avgTasks <= 2 ? 'text-emerald-400' : avgTasks <= 3.5 ? 'text-amber-400' : 'text-rose-400'
                    }`}
                  >
                    {avgTasks.toFixed(1)} tareas
                  </div>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2">
                  <div className="text-[10px] text-slate-400 uppercase font-bold">Latencia Media</div>
                  <div
                    className={`text-base font-extrabold font-mono ${
                      latencyMs <= 10 ? 'text-emerald-400' : latencyMs <= 30 ? 'text-amber-400' : 'text-rose-400'
                    }`}
                  >
                    {latencyMs.toFixed(1)} ms
                  </div>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2">
                  <div className="text-[10px] text-slate-400 uppercase font-bold">Eficiencia / Hechas</div>
                  <div className="text-base font-extrabold font-mono text-emerald-400">
                    {efficiencyPct.toFixed(1)}% ({totalCompleted})
                  </div>
                </div>
              </div>
            </div>

            {/* Interactive Swarm Buttons */}
            <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-800/80">
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={handleAddAgent}
                  className="px-3.5 py-2 rounded-xl bg-emerald-500/20 hover:bg-emerald-500 hover:text-slate-950 text-emerald-300 border border-emerald-500/50 text-xs font-extrabold transition-all"
                >
                  ➕ Añadir Agente Especializado (+1 Agente = Menos Tareas c/u)
                </button>
                <button
                  onClick={handleAutoBalance}
                  className="px-3.5 py-2 rounded-xl bg-sky-500/20 hover:bg-sky-400 hover:text-slate-950 text-sky-300 border border-sky-500/50 text-xs font-extrabold transition-all"
                >
                  ⚖️ Auto-Balancear Tareas (Work-Stealing)
                </button>
                <button
                  onClick={handleMicroTaskMode}
                  className="px-3.5 py-2 rounded-xl bg-indigo-500/20 hover:bg-indigo-500 hover:text-white text-indigo-300 border border-indigo-500/50 text-xs font-extrabold transition-all"
                >
                  ⚡ Modo Ultra-Rápido (1 sola Tarea / Agente)
                </button>
              </div>

              <div className="flex flex-wrap gap-2">
                <button
                  onClick={handleRemoveAgent}
                  className="px-3 py-2 rounded-xl bg-amber-500/15 hover:bg-amber-500 hover:text-slate-950 text-amber-300 border border-amber-500/40 text-xs font-bold transition-all"
                >
                  ➖ Quitar Agente (-1)
                </button>
                <button
                  onClick={handleSimulateBurst}
                  className="px-3 py-2 rounded-xl bg-rose-500/15 hover:bg-rose-500 hover:text-white text-rose-300 border border-rose-500/40 text-xs font-bold transition-all"
                >
                  🔥 Simular Pico (+12 Tareas Desbalanceadas)
                </button>
              </div>
            </div>

            {/* Grid of Individual Agents Working in Real Time */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5 mt-1">
              {agents.map((ag, idx) => {
                const isOptimal = ag.tasks <= 2;
                const isMedium = ag.tasks > 2 && ag.tasks <= 4;
                const borderCol = isOptimal
                  ? 'border-emerald-500/50 bg-slate-900/90'
                  : isMedium
                  ? 'border-amber-500/60 bg-slate-900/90'
                  : 'border-rose-500/80 bg-rose-950/20 animate-pulse';

                return (
                  <div
                    key={ag.id}
                    className={`rounded-2xl p-4 border ${borderCol} flex flex-col justify-between gap-2.5 transition-all`}
                  >
                    <div>
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className="text-lg">{ag.emoji}</span>
                          <span className="text-xs sm:text-sm font-extrabold text-white">{ag.name}</span>
                        </div>
                        <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-sky-500/15 text-sky-300">
                          {ag.stage}
                        </span>
                      </div>

                      <div className="flex items-center justify-between text-[11px] text-slate-300 mt-2">
                        <span>🔨 {ag.currentAction}</span>
                        <span className="font-mono font-bold text-sky-400">{Math.round(ag.progress)}%</span>
                      </div>

                      {/* Progress Bar */}
                      <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden mt-1.5 border border-slate-800">
                        <div
                          style={{ width: `${Math.min(100, ag.progress)}%` }}
                          className={`h-full rounded-full transition-all duration-150 ${
                            isOptimal
                              ? 'bg-gradient-to-r from-emerald-400 to-sky-400'
                              : isMedium
                              ? 'bg-gradient-to-r from-amber-400 to-orange-500'
                              : 'bg-gradient-to-r from-rose-500 to-red-600'
                          }`}
                        />
                      </div>

                      {/* Task Queue Pills */}
                      <div className="flex flex-wrap gap-1.5 mt-2.5 p-2 rounded-xl bg-slate-950/80 border border-slate-800/80 min-h-[32px] items-center">
                        {Array.from({ length: ag.tasks }).map((_, tIdx) => (
                          <span
                            key={tIdx}
                            className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-md ${
                              tIdx === 0
                                ? 'bg-emerald-500/25 border border-emerald-400 text-emerald-200'
                                : ag.tasks > 4
                                ? 'bg-rose-500/25 border border-rose-400 text-rose-200'
                                : 'bg-sky-500/20 border border-sky-400/50 text-sky-200'
                            }`}
                          >
                            {tIdx === 0 ? `⚡ Ejecutando` : `⏳ Cola #${tIdx}`}
                          </span>
                        ))}
                        {ag.tasks === 0 && (
                          <span className="text-[11px] text-emerald-400 font-bold">
                            ✓ Libre (0 tareas en cola)
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-2 border-t border-slate-800/80 text-[11px]">
                      <div>
                        <span
                          className={`font-extrabold ${
                            isOptimal ? 'text-emerald-400' : isMedium ? 'text-amber-400' : 'text-rose-400'
                          }`}
                        >
                          {isOptimal
                            ? '⚡ ÓPTIMO (Pocas tareas)'
                            : isMedium
                            ? '⏳ CARGA MEDIA'
                            : '🚨 SOBRECARGADO'}
                        </span>
                        <div className="text-slate-400 font-mono text-[10px]">
                          Completadas: <strong className="text-white">{ag.completed}</strong> · En cola:{' '}
                          <strong className="text-white">{ag.tasks}</strong>
                        </div>
                      </div>

                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => adjustSingleAgentTask(idx, -1)}
                          className="px-2 py-1 rounded-lg bg-slate-800 hover:bg-sky-500 hover:text-slate-950 text-slate-200 font-bold text-[10px] transition-colors"
                        >
                          -1 Tarea
                        </button>
                        <button
                          onClick={() => adjustSingleAgentTask(idx, 1)}
                          className="px-2 py-1 rounded-lg bg-slate-800 hover:bg-sky-500 hover:text-slate-950 text-slate-200 font-bold text-[10px] transition-colors"
                        >
                          +1 Tarea
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Live Agent Activity Terminal */}
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-3 font-mono text-[11px] text-slate-300 max-h-28 overflow-y-auto space-y-1">
              {logs.map((l, i) => (
                <div key={i}>{l}</div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ===================================================================== */}
      {/* SECTION 1B: PROYECTO EN VIVO · CALCULADORA VATIOS (W) / kW / kWh CASA */}
      {/* ===================================================================== */}
      {useMemo(
        () =>
          (subView === 'both' || subView === 'energy' || subView === 'cv') && (
            <div className="flex flex-col gap-6 bg-slate-900/90 border border-amber-500/45 rounded-3xl p-6 sm:p-8 shadow-2xl">
              {/* Header Banner */}
              <div className="flex flex-wrap items-start justify-between gap-4 border-b border-slate-800 pb-5">
            <div>
              <div className="flex flex-wrap items-center gap-2 mb-2">
                <span className="px-3 py-1 rounded-full bg-amber-500/15 border border-amber-400/50 text-amber-300 text-xs font-extrabold">
                  ⚡ PROYECTO EN VIVO · FÍSICA APLICADA, PYTHON &amp; HOGAR INTELIGENTE
                </span>
                <span className="px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/40 text-emerald-300 text-xs font-extrabold">
                  ● CASO REAL MIKEL: CONTRATO 0,1329 €/kWh ➔ FACTURA 137,00 € = 1.030,85 kWh
                </span>
                <span className="px-3 py-1 rounded-full bg-sky-500/15 border border-sky-400/50 text-sky-300 text-xs font-mono font-extrabold">
                  🚀 MOTOR OPTIMIZADO: +69.6% VELOCIDAD CPU (36.4 ms) · -80.4% RAM (NamedTuple + O(1))
                </span>
              </div>
              <h2 className="text-xl sm:text-2xl font-extrabold text-white">
                🔌 Calculadora Interactiva de Vatios (W), Kilovatios (kW) y Factura Eléctrica de Casa, PC &amp; Electrodomésticos
              </h2>
              <p className="text-xs sm:text-sm text-slate-300 mt-1">
                Calcula al instante cuánto consume cada electrodoméstico, tu <strong>PC Workstation</strong> y tu <strong>Servidor Multi-PC / NAS</strong> según tu contrato real (<strong className="text-amber-300">0,1329 €/kWh</strong>). Pulsa sobre{' '}
                <button
                  onClick={() => openConcept('kwh_tarifa_137')}
                  className="text-sky-400 underline decoration-dashed font-bold hover:text-white"
                >
                  Factura 137 € a 0.1329 €/kWh (1.030,85 kWh)
                </button>{' '}
                o{' '}
                <button
                  onClick={() => openConcept('vatio_kilovatio')}
                  className="text-sky-400 underline decoration-dashed font-bold hover:text-white"
                >
                  Vatio (W) vs Kilovatio (kW) vs kWh
                </button>{' '}
                en azul para ver la explicación física paso a paso.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <button
                onClick={handleCalibrateToExactTarget}
                className="px-3.5 py-2 rounded-xl bg-amber-400 hover:bg-amber-300 text-slate-950 font-extrabold text-xs shadow-lg shadow-amber-400/20 transition-all"
              >
                🎯 Clavar los {targetBillEur.toFixed(0)} € ({targetKwhAfterFixed.toFixed(1)} kWh)
              </button>
              <button
                onClick={handleResetMikel137Case}
                className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs border border-slate-700 transition-all"
              >
                🔄 Tu Caso Real (0.1329 €/kWh · 137 €)
              </button>
            </div>
          </div>

          {/* Contract & Bill Sliders + Top 4 Mathematical KPIs */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Contract Controls */}
            <div className="bg-slate-950/90 border border-slate-800 rounded-2xl p-4 space-y-3">
              <div className="text-xs font-extrabold uppercase text-amber-400">
                1️⃣ Datos de Tu Contrato Eléctrico y Factura
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-300 font-semibold">Precio Contrato (€/kWh):</span>
                  <span className="font-mono font-extrabold text-amber-300">{tariffEurKwh.toFixed(4)} €/kWh</span>
                </div>
                <input
                  type="range"
                  min={0.05}
                  max={0.35}
                  step={0.0001}
                  value={tariffEurKwh}
                  onChange={(e) => setTariffEurKwh(parseFloat(e.target.value))}
                  className="w-full accent-amber-400"
                />
                <div className="flex gap-1.5 mt-1">
                  <button
                    onClick={() => setTariffEurKwh(0.1329)}
                    className="px-2 py-0.5 rounded bg-amber-500/20 border border-amber-400/40 text-amber-300 text-[10px] font-bold"
                  >
                    Tu Tarifa: 0.1329 €/kWh
                  </button>
                  <button
                    onClick={() => setTariffEurKwh(0.185)}
                    className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px] font-bold"
                  >
                    Media España: 0.1850 €/kWh
                  </button>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-300 font-semibold">Factura que quieres analizar (€/mes):</span>
                  <span className="font-mono font-extrabold text-emerald-400">{targetBillEur.toFixed(2)} €</span>
                </div>
                <input
                  type="range"
                  min={30}
                  max={350}
                  step={1}
                  value={targetBillEur}
                  onChange={(e) => setTargetBillEur(parseFloat(e.target.value))}
                  className="w-full accent-emerald-400"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-300 font-semibold">Costes Fijos Potencia/Impuestos (Opcional €):</span>
                  <span className="font-mono font-extrabold text-sky-400">{fixedChargesEur.toFixed(2)} €</span>
                </div>
                <input
                  type="range"
                  min={0}
                  max={60}
                  step={1}
                  value={fixedChargesEur}
                  onChange={(e) => setFixedChargesEur(parseFloat(e.target.value))}
                  className="w-full accent-sky-400"
                />
                <div className="text-[10px] text-slate-400 mt-1">
                  En <strong>0 €</strong> ves el cálculo puro: <code>{targetBillEur.toFixed(0)} € ÷ {tariffEurKwh.toFixed(4)} = {targetKwhPure.toFixed(2)} kWh</code>.
                </div>
              </div>
            </div>

            {/* Exact Inverse Equation & Live KPIs */}
            <div className="lg:col-span-2 bg-slate-950/90 border border-sky-500/35 rounded-2xl p-4 flex flex-col justify-between gap-4">
              <div>
                <div className="text-xs font-extrabold uppercase text-sky-400 mb-2">
                  2️⃣ Despeje Matemático Exacto · ¿Cuánto tienes que consumir para gastar {targetBillEur.toFixed(2)} € a {tariffEurKwh.toFixed(4)} €/kWh?
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="bg-slate-900 border border-amber-500/40 rounded-xl p-3">
                    <div className="text-[10px] uppercase font-bold text-slate-400">Necesitas Consumir</div>
                    <div className="text-lg font-extrabold font-mono text-amber-300">
                      {targetKwhAfterFixed.toFixed(2)} kWh
                    </div>
                    <div className="text-[10px] text-slate-400">
                      {(targetKwhAfterFixed / 30).toFixed(2)} kWh cada día
                    </div>
                  </div>

                  <div className="bg-slate-900 border border-emerald-500/40 rounded-xl p-3">
                    <div className="text-[10px] uppercase font-bold text-slate-400">Tus Aparatos Suman</div>
                    <div className="text-lg font-extrabold font-mono text-emerald-400">
                      {totalSimulatedKwh.toFixed(2)} kWh
                    </div>
                    <div className="text-[10px] text-slate-400">
                      {(totalSimulatedKwh / 30).toFixed(2)} kWh/día simulados
                    </div>
                  </div>

                  <div className="bg-slate-900 border border-sky-500/40 rounded-xl p-3">
                    <div className="text-[10px] uppercase font-bold text-slate-400">Factura Simulada</div>
                    <div className="text-lg font-extrabold font-mono text-sky-300">
                      {totalSimulatedBillEur.toFixed(2)} €
                    </div>
                    <div className="text-[10px] text-slate-400">
                      Dif: {deltaEur >= 0 ? `Faltan ${deltaEur.toFixed(2)} €` : `Te pasas ${Math.abs(deltaEur).toFixed(2)} €`}
                    </div>
                  </div>

                  <div className="bg-slate-900 border border-purple-500/40 rounded-xl p-3">
                    <div className="text-[10px] uppercase font-bold text-slate-400">Potencia Continua 24h</div>
                    <div className="text-lg font-extrabold font-mono text-purple-300">
                      {avgContinuousWatts.toFixed(0)} W
                    </div>
                    <div className="text-[10px] text-slate-400">
                      {(avgContinuousWatts / 1000).toFixed(3)} kW de media las 24h
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3.5 text-xs text-slate-200 leading-relaxed">
                <strong className="text-amber-300">💡 Conclusión para tu casa:</strong> Con tu tarifa de{' '}
                <strong className="text-white">{tariffEurKwh.toFixed(4)} €/kWh</strong>, para llegar a una factura de{' '}
                <strong className="text-emerald-400">{targetBillEur.toFixed(2)} €</strong> tu contador tiene que registrar{' '}
                <strong className="text-sky-300">{targetKwhAfterFixed.toFixed(2)} kWh al mes</strong> ({(targetKwhAfterFixed * 1000).toLocaleString()} Vatios-hora).
                {Math.abs(deltaKwh) < 5 ? (
                  <span className="text-emerald-400 font-bold">
                    {' '}¡Tus consumidores de abajo están clavados exactamente en tu factura de {targetBillEur.toFixed(0)} €!
                  </span>
                ) : deltaKwh > 0 ? (
                  <span className="text-amber-300 font-bold">
                    {' '}Aún te faltan {deltaKwh.toFixed(1)} kWh ({deltaEur.toFixed(2)} €) por repartir entre calefacción, termo, cocina o PC.
                  </span>
                ) : (
                  <span className="text-rose-400 font-bold">
                    {' '}Tus aparatos actuales superan la factura objetivo en {Math.abs(deltaKwh).toFixed(1)} kWh (+{Math.abs(deltaEur).toFixed(2)} €).
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Interactive Appliance & PC Table / Cards */}
          <div>
            <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
              <h3 className="text-xs font-extrabold uppercase tracking-wider text-emerald-400">
                3️⃣ Desglose Interactivo por Consumidor (PC, NAS, Climatización y Electrodomésticos · Ajusta Vatios y Horas)
              </h3>
              <span className="text-[11px] text-slate-400 font-mono">
                Fórmula Fusionada O(1): <code>kWh/mes = W × 0.001 × Horas/día × Días</code> · <code>Coste = kWh × {tariffEurKwh.toFixed(4)} €</code>
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
              {appliances.map((app) => {
                const kw = app.watts * 0.001;
                const monthlyKwh = kw * app.hoursPerDay * app.daysPerMonth;
                const monthlyEur = monthlyKwh * safeTariff;
                const sharePct = totalSimulatedKwh > 0 ? (monthlyKwh / totalSimulatedKwh) * 100 : 0;
                const isTopBottleneck = app.id === topBottleneckId;

                return (
                  <div
                    key={app.id}
                    className={`bg-slate-950/90 border rounded-2xl p-4 flex flex-col justify-between gap-3 transition-all ${
                      isTopBottleneck
                        ? 'border-amber-400/75 shadow-lg shadow-amber-500/10'
                        : 'border-slate-800 hover:border-sky-500/50'
                    }`}
                  >
                    <div>
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className="text-xl">{app.emoji}</span>
                          <div>
                            <div className="text-xs font-extrabold text-white leading-snug">{app.name}</div>
                            <div className="flex items-center gap-1.5 mt-0.5">
                              <span className="text-[10px] text-sky-400 font-mono">{app.category}</span>
                              {isTopBottleneck && (
                                <span className="px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 text-[9px] font-mono font-extrabold">
                                  #1 MAYOR CONSUMO
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                        {appliances.length > 1 && (
                          <button
                            onClick={() => handleRemoveAppliance(app.id)}
                            className="text-slate-500 hover:text-rose-400 text-xs font-bold px-1.5"
                            title="Quitar consumidor"
                          >
                            ✕
                          </button>
                        )}
                      </div>

                      {/* Sliders for Watts and Hours/day */}
                      <div className="mt-3 space-y-2">
                        <div>
                          <div className="flex justify-between text-[11px]">
                            <span className="text-slate-400">Potencia:</span>
                            <span className="font-mono font-bold text-amber-300">
                              {app.watts} W <span className="text-slate-400">({kw.toFixed(3)} kW)</span>
                            </span>
                          </div>
                          <input
                            type="range"
                            min={10}
                            max={3500}
                            step={10}
                            value={app.watts}
                            onChange={(e) => updateApplianceField(app.id, 'watts', parseFloat(e.target.value))}
                            className="w-full accent-amber-400"
                          />
                        </div>

                        <div>
                          <div className="flex justify-between text-[11px]">
                            <span className="text-slate-400">Uso diario:</span>
                            <span className="font-mono font-bold text-sky-300">{app.hoursPerDay} h / día</span>
                          </div>
                          <input
                            type="range"
                            min={0.25}
                            max={24}
                            step={0.25}
                            value={app.hoursPerDay}
                            onChange={(e) => updateApplianceField(app.id, 'hoursPerDay', parseFloat(e.target.value))}
                            className="w-full accent-sky-400"
                          />
                        </div>
                      </div>
                    </div>

                    {/* Progress Share Bar & Cost Footer */}
                    <div className="pt-2 border-t border-slate-800/90 space-y-1.5">
                      <div className="w-full h-1.5 bg-slate-900 rounded-full overflow-hidden">
                        <div
                          style={{ width: `${Math.min(100, sharePct)}%` }}
                          className="h-full bg-gradient-to-r from-amber-400 to-emerald-400"
                        />
                      </div>
                      <div className="flex items-center justify-between text-[11px] font-mono">
                        <span className="text-slate-300">
                          <strong>{monthlyKwh.toFixed(1)} kWh</strong>/mes ({sharePct.toFixed(1)}%)
                        </span>
                        <span className="text-emerald-400 font-extrabold text-xs">
                          {monthlyEur.toFixed(2)} € / mes
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Add Custom Appliance Bar */}
          <div className="bg-slate-950/85 border border-slate-800 rounded-2xl p-4 flex flex-wrap items-end justify-between gap-3">
            <div className="flex-1 min-w-[180px]">
              <label className="block text-[10px] font-extrabold uppercase text-slate-400 mb-1">
                ➕ Añadir otro electrodoméstico, GPU o consola a tu casa
              </label>
              <input
                type="text"
                value={newAppName}
                onChange={(e) => setNewAppName(e.target.value)}
                placeholder="Ej. Segundo PC Gaming, Radiador, Deshumidificador..."
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white"
              />
            </div>
            <div className="w-28">
              <label className="block text-[10px] font-extrabold uppercase text-slate-400 mb-1">Vatios (W)</label>
              <input
                type="number"
                value={newAppWatts}
                onChange={(e) => setNewAppWatts(parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-amber-300 font-mono font-bold"
              />
            </div>
            <div className="w-28">
              <label className="block text-[10px] font-extrabold uppercase text-slate-400 mb-1">Horas / día</label>
              <input
                type="number"
                step="0.5"
                value={newAppHours}
                onChange={(e) => setNewAppHours(parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-sky-300 font-mono font-bold"
              />
            </div>
            <button
              onClick={handleAddCustomAppliance}
              className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-extrabold text-xs transition-all"
            >
              ➕ Añadir a la Casa
            </button>
          </div>
        </div>
          ),
        [
          subView,
          tariffEurKwh,
          targetBillEur,
          fixedChargesEur,
          targetKwhPure,
          targetKwhAfterFixed,
          totalSimulatedKwh,
          totalSimulatedBillEur,
          avgContinuousWatts,
          deltaKwh,
          deltaEur,
          appliances,
          safeTariff,
          topBottleneckId,
          newAppName,
          newAppWatts,
          newAppHours,
          handleCalibrateToExactTarget,
          handleResetMikel137Case,
          handleRemoveAppliance,
          updateApplianceField,
          handleAddCustomAppliance,
          openConcept,
        ]
      )}

      {/* ===================================================================== */}
      {/* SECTION 2: MIKEL · NOVUSMUNDUS — CONOCIMIENTO DEMOSTRADO EN PROYECTOS */}
      {/* ===================================================================== */}
      {useMemo(
        () =>
          (subView === 'both' || subView === 'cv') && (
            <div className="flex flex-col gap-6 bg-slate-900/90 border border-indigo-500/45 rounded-3xl p-6 sm:p-8 shadow-2xl">
              {/* Header Banner: Project-First Builder Identity */}
          <div className="flex flex-wrap items-start justify-between gap-4 border-b border-slate-800 pb-6">
            <div>
              <div className="flex flex-wrap items-center gap-2 mb-2">
                <span className="px-3 py-1 rounded-full bg-amber-500/15 border border-amber-400/50 text-amber-300 text-xs font-extrabold tracking-wider">
                  NOVUSMUNDUS · PROJECT-FIRST BUILDER
                </span>
                <span className="px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/40 text-emerald-300 text-xs font-extrabold">
                  ● 100% CONOCIMIENTO DEMOSTRADO CONSTRUYENDO PROYECTOS REALES
                </span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
                MIKEL <span className="text-sky-400 font-light">·</span>{' '}
                <span className="text-xl sm:text-2xl text-emerald-400 font-bold">
                  Software Engineer · Backend &amp; AI Systems · Product Builder
                </span>
              </h2>
              <div className="flex flex-wrap items-center gap-3 text-xs sm:text-sm text-slate-300 font-medium mt-2">
                <span>📍 Donostia / Gipuzkoa, Spain</span>
                <span>•</span>
                <a
                  href="https://github.com/novomundus2-cmyk"
                  target="_blank"
                  rel="noreferrer"
                  className="text-sky-400 hover:underline font-mono font-bold"
                >
                  GitHub: github.com/novomundus2-cmyk
                </a>
                <span>•</span>
                <span className="text-amber-300 font-bold">
                  🌍 Idiomas: Español (Nativo) · Français (Bayonne &amp; IRC) · English (Técnico)
                </span>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <div className="flex items-center bg-slate-950 p-1 rounded-xl border border-slate-800">
                <button
                  onClick={() => setCvLang('es')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                    cvLang === 'es' ? 'bg-sky-500 text-slate-950' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  🇪🇸 Español + Conceptos Azul
                </button>
                <button
                  onClick={() => setCvLang('en')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                    cvLang === 'en' ? 'bg-emerald-500 text-slate-950' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  🇬🇧 English (Project Knowledge)
                </button>
              </div>

              <button
                onClick={handleCopyCv}
                className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-extrabold text-xs transition-all shadow-lg shadow-emerald-500/20"
              >
                {copiedCv ? '✓ ¡Copiado!' : '📋 Copiar Portafolio Markdown'}
              </button>
              <button
                onClick={() => window.print()}
                className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs border border-slate-700 transition-all"
              >
                🖨️ PDF
              </button>
            </div>
          </div>

          {/* 1. PHILOSOPHY: KNOWLEDGE PROVEN THROUGH PROJECTS, LANGUAGES & PRACTICAL COURSES */}
          <div className="bg-slate-950/85 border-l-4 border-sky-400 rounded-2xl p-5">
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-sky-400 mb-2">
              {cvLang === 'en'
                ? '1. BUILDER PHILOSOPHY · KNOWLEDGE PROVEN IN REAL PROJECTS (CLICK ANY BLUE CONCEPT)'
                : '1. FILOSOFÍA DE CONSTRUCTOR · CONOCIMIENTO DEMOSTRADO EN PROYECTOS (Pulsa cualquier palabra en azul)'}
            </h3>
            {cvLang === 'en' ? (
              <p className="text-sm text-slate-200 leading-relaxed">
                Self-taught technical builder focused on backend engineering,{' '}
                <button onClick={() => openConcept('work_stealing')} className="text-sky-400 underline decoration-dashed font-bold">
                  hierarchical AI-agent systems (Work-Stealing)
                </button>
                , data streaming platforms, automation and product architecture. Every piece of knowledge I have is proven directly by building end-to-end systems that connect interfaces, APIs, databases,{' '}
                <button onClick={() => openConcept('supabase_rls')} className="text-sky-400 underline decoration-dashed font-bold">
                  permissions (Supabase RLS) &amp; mathematical validation gates
                </button>
                , local/cloud AI workflows and distributed infrastructure. I speak <strong>Spanish, French and English</strong>, combine practical technical courses (including the <strong>EIP/EFA financial path</strong>) with 2 years of software development in <strong>Bayonne (France)</strong>, international railway sales (<strong>Spain &amp; France</strong>), and commercial banking (<strong>BBVA</strong>).
              </p>
            ) : (
              <p className="text-sm text-slate-200 leading-relaxed">
                Constructor técnico autodidacta enfocado en ingeniería backend,{' '}
                <button onClick={() => openConcept('work_stealing')} className="text-sky-400 underline decoration-dashed font-bold hover:text-white">
                  sistemas jerárquicos de agentes IA (Work-Stealing)
                </button>
                , plataformas de datos en streaming, automatización y arquitectura de producto. <strong>Demuestro todo mi conocimiento directamente construyendo proyectos reales</strong> que conectan interfaces, APIs, bases de datos,{' '}
                <button onClick={() => openConcept('supabase_rls')} className="text-sky-400 underline decoration-dashed font-bold hover:text-white">
                  permisos (Supabase RLS) y puertas de validación matemática
                </button>
                , flujos de IA e infraestructura local/cloud. Domino <strong>Español, Francés e Inglés</strong>, me formo mediante <strong>cursos especializados prácticos (ingeniería, IA y senda financiera EIP/EFA)</strong> y cuento con experiencia real desarrollando software en <strong>Bayonne (Francia)</strong>, comercio internacional (<strong>España y Francia</strong>) y banca comercial (<strong>BBVA</strong>).
              </p>
            )}
          </div>

          {/* 2. EVERY SKILL FROM YOUR KNOWLEDGE BASE APPLIED INSIDE YOUR 4 CORE PROJECTS */}
          <div>
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-amber-400 mb-3">
              {cvLang === 'en'
                ? '2. MY TECHNICAL KNOWLEDGE APPLIED DIRECTLY INSIDE REAL-WORLD PROJECTS'
                : '2. TODO MI CONOCIMIENTO TÉCNICO APLICADO DENTRO DE MIS PROYECTOS REALES'}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Project 1: Novus Capital / NovusMundus */}
              <div className="bg-slate-950/90 border border-sky-500/40 rounded-2xl p-5 flex flex-col justify-between gap-3">
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <h4 className="text-sm sm:text-base font-extrabold text-white">
                      🏦 Proyecto 1 · Novus Capital / NovusMundus — AI &amp; Finance Platform
                    </h4>
                    <span className="text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full bg-sky-500/20 text-sky-300">
                      Backend · SQL · Finanzas · IA
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {cvLang === 'en'
                      ? 'Multi-platform product for financial research, company analysis, valuation, macroeconomics, portfolio workflows and automation. Built from scratch with product direction, system architecture, Supabase/PostgreSQL backend, authentication & RLS permissions, REST APIs, financial-data flows (25,000 transactions / €5.34M Lakehouse) and mathematical validation gates.'
                      : 'Producto multiplataforma para investigación financiera, análisis de compañías, valoración, macroeconomía, flujos de carteras y automatización. Construido de principio a fin con arquitectura de sistemas, backend en Supabase/PostgreSQL + SQLite Lakehouse (25.000 transacciones / 5,34 M€), autenticación y permisos RLS, APIs y puertas de validación antifraude.'}
                  </p>
                </div>
                <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3 text-[11px] text-slate-200 space-y-1">
                  <div className="font-extrabold text-sky-400 uppercase text-[10px]">
                    🧠 Conocimiento demostrado en este proyecto:
                  </div>
                  <div>
                    <strong>Backend &amp; Datos:</strong> PostgreSQL, Supabase, SQL, APIs, Auth,{' '}
                    <button onClick={() => openConcept('supabase_rls')} className="text-sky-400 underline decoration-dashed font-bold">
                      RLS (Row-Level Security)
                    </button>
                    , migraciones, índices, constraints, SQLite ACID.
                  </div>
                  <div>
                    <strong>Matemática &amp; Finanzas:</strong>{' '}
                    <button onClick={() => openConcept('welford')} className="text-sky-400 underline decoration-dashed font-bold">
                      Monoide Welford-Chan O(1)
                    </button>
                    ,{' '}
                    <button onClick={() => openConcept('enmascaramiento')} className="text-sky-400 underline decoration-dashed font-bold">
                      Z-Score Robusto MAD (295.76)
                    </button>
                    , valoración de empresas, mercados y cursos <strong>EIP/EFA</strong>.
                  </div>
                </div>
              </div>

              {/* Project 2: Hierarchical AI Agent Infrastructure */}
              <div className="bg-slate-950/90 border border-emerald-500/40 rounded-2xl p-5 flex flex-col justify-between gap-3">
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <h4 className="text-sm sm:text-base font-extrabold text-white">
                      🤖 Proyecto 2 · Hierarchical AI Agent Infrastructure
                    </h4>
                    <span className="text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300">
                      LLMs · Ollama · RAG · MCP
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {cvLang === 'en'
                      ? 'Hierarchical multi-agent architecture with shared, auditable memory (ai_insights_registry), specialized roles, Work-Stealing load balancing (keeping 1–2 tasks per agent for maximum throughput), MCP tool use, RAG/embeddings and local-model workflows with Ollama + cloud AI.'
                      : 'Arquitectura jerárquica de agentes IA con memoria compartida auditable (ai_insights_registry), roles especializados, balanceo Work-Stealing en vivo (manteniendo 1–2 tareas por agente para máxima velocidad), uso de herramientas MCP, RAG/embeddings y flujos con modelos locales (Ollama) y en la nube.'}
                  </p>
                </div>
                <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3 text-[11px] text-slate-200 space-y-1">
                  <div className="font-extrabold text-emerald-400 uppercase text-[10px]">
                    🧠 Conocimiento demostrado en este proyecto:
                  </div>
                  <div>
                    <strong>Sistemas de IA:</strong> LLMs, IA local (<strong>Ollama</strong>), <strong>RAG</strong>, <strong>embeddings</strong>, protocolo <strong>MCP</strong>, <strong>tool use</strong>,{' '}
                    <button onClick={() => openConcept('work_stealing')} className="text-sky-400 underline decoration-dashed font-bold">
                      agentes jerárquicos con Work-Stealing
                    </button>
                    .
                  </div>
                  <div>
                    <strong>Orquestación Híbrida:</strong> Gemini 2.5 Flash, TimesFM 2.0 (forecasting), Antigravity SDK y memoria auditable en SQL/JSON.
                  </div>
                </div>
              </div>

              {/* Project 3: Physics CAD Lab & Scientific Engine */}
              <div className="bg-slate-950/90 border border-purple-500/40 rounded-2xl p-5 flex flex-col justify-between gap-3">
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <h4 className="text-sm sm:text-base font-extrabold text-white">
                      🔬 Proyecto 3 · Physics CAD Lab &amp; Scientific Python / C++ Engine
                    </h4>
                    <span className="text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full bg-purple-500/20 text-purple-300">
                      C/C++ · Python Científico · CAD/CAE
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {cvLang === 'en'
                      ? 'Modular engineering and simulation laboratory connecting mathematics, physics, scientific Python, C/C++, CAD/CAE workflows, queueing simulation and sensor telemetry with auditable shared memory and automated pytest verification.'
                      : 'Laboratorio modular de ingeniería y simulación que conecta matemáticas, física, Python científico, C/C++, flujos de trabajo CAD/CAE, simulación de colas y telemetría de sensores con memoria compartida auditable y verificación automatizada.'}
                  </p>
                </div>
                <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3 text-[11px] text-slate-200 space-y-1">
                  <div className="font-extrabold text-purple-400 uppercase text-[10px]">
                    🧠 Conocimiento demostrado en este proyecto:
                  </div>
                  <div>
                    <strong>Lenguajes &amp; Ciencia:</strong> <strong>Python</strong>, <strong>C</strong>, <strong>C++</strong>, <strong>Haskell</strong>, <strong>NumPy</strong>, <strong>SciPy</strong>, <strong>SymPy</strong>, <strong>Polars</strong>, <strong>pandas</strong>, <strong>Matplotlib</strong>, flujos <strong>CAD/CAE</strong>.
                  </div>
                  <div>
                    <strong>Calidad &amp; Simulación:</strong> Testing automatizado con <strong>pytest</strong>,{' '}
                    <button onClick={() => openConcept('teoria_colas')} className="text-sky-400 underline decoration-dashed font-bold">
                      Teoría de Colas M/M/c
                    </button>
                    , Ley de Little y Entropía de Shannon.
                  </div>
                </div>
              </div>

              {/* Project 4: Archify Big Data Lakehouse, Multi-PC NAS & AuraIcons */}
              <div className="bg-slate-950/90 border border-amber-500/40 rounded-2xl p-5 flex flex-col justify-between gap-3">
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <h4 className="text-sm sm:text-base font-extrabold text-white">
                      ✨ Proyecto 4 · Archify Streaming, Servidor Multi-PC NAS &amp; AuraIcons Studio
                    </h4>
                    <span className="text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300">
                      Streaming · Linux/Docker · React UX
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {cvLang === 'en'
                      ? 'End-to-end streaming architecture and local multi-PC server (0.0.0.0:8765) with NAS RAID synchronization, paired with a 60 FPS interactive vector icon studio in React/JavaScript and Cognitive Fractionation UI so any client can understand complex engineering from scratch.'
                      : 'Arquitectura de streaming de extremo a extremo y servidor central Multi-PC en red local (0.0.0.0:8765) sincronizado con NAS RAID, unido a un estudio de iconos vectoriales a 60 FPS en React/JavaScript y una interfaz con Fraccionamiento Cognitivo pensada para el cliente.'}
                  </p>
                </div>
                <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3 text-[11px] text-slate-200 space-y-1">
                  <div className="font-extrabold text-amber-400 uppercase text-[10px]">
                    🧠 Conocimiento demostrado en este proyecto:
                  </div>
                  <div>
                    <strong>Ingeniería &amp; Streaming:</strong>{' '}
                    <button onClick={() => openConcept('backpressure')} className="text-sky-400 underline decoration-dashed font-bold">
                      Apache NiFi
                    </button>
                    , <strong>Kafka KRaft</strong>, <strong>PySpark</strong>, <strong>Apache Iceberg</strong>, <strong>BigQuery (DTS &amp; Graph)</strong>, <strong>Docker</strong>, <strong>Linux</strong>, <strong>Git/GitHub</strong>,{' '}
                    <button onClick={() => openConcept('nas_cluster')} className="text-sky-400 underline decoration-dashed font-bold">
                      Servidor LAN Multi-PC &amp; NAS
                    </button>
                    .
                  </div>
                  <div>
                    <strong>Producto &amp; Frontend:</strong> <strong>JavaScript / TypeScript</strong>, <strong>React</strong>, UX/UI redondeada responsive, documentación técnica y revisión de seguridad.
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* 3. COMPLETE KNOWLEDGE MATRIX (6 Categorías de Conocimiento Verificadas en Código) */}
          <div>
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-emerald-400 mb-3">
              3. MATRIZ COMPLETA DE CONOCIMIENTO TÉCNICO (100% DEMOSTRABLE EN REPOSITORIO)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="bg-slate-950/85 border border-slate-800 rounded-2xl p-4">
                <div className="text-xs font-extrabold uppercase text-sky-400 mb-1.5">💻 Core Languages &amp; UI</div>
                <p className="text-xs text-slate-200 leading-relaxed">
                  <strong>Python (3.14 Clean Code)</strong>, <strong>JavaScript / TypeScript</strong>, <strong>React</strong>, <strong>C</strong>, <strong>C++</strong>, <strong>Haskell</strong> (álgebra funcional de Monoides).
                </p>
              </div>

              <div className="bg-slate-950/85 border border-slate-800 rounded-2xl p-4">
                <div className="text-xs font-extrabold uppercase text-emerald-400 mb-1.5">🗄️ Backend, Data &amp; Lakehouse</div>
                <p className="text-xs text-slate-200 leading-relaxed">
                  <strong>PostgreSQL</strong>, <strong>Supabase</strong> (Auth,{' '}
                  <button onClick={() => openConcept('supabase_rls')} className="text-sky-400 underline decoration-dashed font-bold">
                    RLS
                  </button>
                  , migrations, indexes, constraints), SQLite ACID, REST APIs,{' '}
                  <button onClick={() => openConcept('backpressure')} className="text-sky-400 underline decoration-dashed font-bold">
                    Apache NiFi
                  </button>
                  , <strong>Kafka KRaft</strong>, <strong>PySpark</strong>, <strong>Apache Iceberg</strong>, <strong>BigQuery (DTS &amp; Property Graph)</strong>.
                </p>
              </div>

              <div className="bg-slate-950/85 border border-slate-800 rounded-2xl p-4">
                <div className="text-xs font-extrabold uppercase text-purple-400 mb-1.5">🤖 AI Systems &amp; Agents</div>
                <p className="text-xs text-slate-200 leading-relaxed">
                  <strong>LLMs</strong>, <strong>local AI (Ollama)</strong>, <strong>RAG</strong>, <strong>embeddings</strong>, <strong>MCP</strong>, tool use,{' '}
                  <button onClick={() => openConcept('work_stealing')} className="text-sky-400 underline decoration-dashed font-bold">
                    hierarchical agents (Work-Stealing &amp; auditable memory)
                  </button>
                  , <strong>Gemini 2.5 Flash</strong>, <strong>TimesFM 2.0</strong>, <strong>Antigravity SDK</strong>.
                </p>
              </div>

              <div className="bg-slate-950/85 border border-slate-800 rounded-2xl p-4">
                <div className="text-xs font-extrabold uppercase text-amber-400 mb-1.5">🛠️ Engineering &amp; Infra</div>
                <p className="text-xs text-slate-200 leading-relaxed">
                  <strong>Git/GitHub</strong>, <strong>Docker</strong>, <strong>Linux</strong>, VS Code/Cursor, <strong>pytest</strong>, security review, CI/CD,{' '}
                  <button onClick={() => openConcept('nas_cluster')} className="text-sky-400 underline decoration-dashed font-bold">
                    Multi-PC LAN Server (0.0.0.0:8765) &amp; NAS RAID
                  </button>
                  , Firebase CLI.
                </p>
              </div>

              <div className="bg-slate-950/85 border border-slate-800 rounded-2xl p-4">
                <div className="text-xs font-extrabold uppercase text-rose-400 mb-1.5">🔬 Scientific &amp; Mathematical</div>
                <p className="text-xs text-slate-200 leading-relaxed">
                  <strong>NumPy</strong>, <strong>SciPy</strong>, <strong>SymPy</strong>, <strong>Polars</strong>, <strong>pandas</strong>, Matplotlib, CAD/CAE workflows,{' '}
                  <button onClick={() => openConcept('welford')} className="text-sky-400 underline decoration-dashed font-bold">
                    Monoide Welford-Chan
                  </button>
                  ,{' '}
                  <button onClick={() => openConcept('enmascaramiento')} className="text-sky-400 underline decoration-dashed font-bold">
                    Z-Score Robusto MAD
                  </button>
                  ,{' '}
                  <button onClick={() => openConcept('teoria_colas')} className="text-sky-400 underline decoration-dashed font-bold">
                    Teoría de Colas M/M/c
                  </button>
                  .
                </p>
              </div>

              <div className="bg-slate-950/85 border border-slate-800 rounded-2xl p-4">
                <div className="text-xs font-extrabold uppercase text-indigo-400 mb-1.5">🎨 Product, Finanzas &amp; UX</div>
                <p className="text-xs text-slate-200 leading-relaxed">
                  System architecture, UX/UI (AuraIcons 60 FPS Studio), validation gates, análisis de compañías, mercados, valoración, macroeconomía (cursos <strong>EIP/EFA</strong>) &amp; <strong>Fraccionamiento Cognitivo</strong>.
                </p>
              </div>
            </div>
          </div>

          {/* 4. IDIOMAS, CURSOS PRÁCTICOS & EXPERIENCIA PROFESIONAL REAL (Sin titulitis académica) */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* REAL PROFESSIONAL EXPERIENCE */}
            <div className="bg-slate-950/85 border border-slate-800 rounded-2xl p-5 space-y-4">
              <h3 className="text-xs font-extrabold uppercase tracking-wider text-sky-400">
                4. TRAYECTORIA REAL EN SOFTWARE, INDUSTRIA FRANCO-ESPAÑOLA Y BANCA
              </h3>

              <div className="border-l-2 border-sky-500 pl-3.5">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs sm:text-sm font-extrabold text-white">
                    Software / Web Development — Empresa tecnológica en Bayonne, Francia
                  </span>
                  <span className="text-[11px] font-mono text-sky-400 shrink-0">~2 años</span>
                </div>
                <p className="text-xs text-slate-300 mt-1">
                  {cvLang === 'en'
                    ? 'Worked on websites and applications in Bayonne (France), developing hands-on experience across software delivery, interfaces and product implementation in a French working environment.'
                    : 'Desarrollo práctico de sitios web y aplicaciones en Bayonne (Francia), construyendo interfaces, entregando software real e implementando producto trabajando directamente en francés.'}
                </p>
              </div>

              <div className="border-l-2 border-emerald-500 pl-3.5">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs sm:text-sm font-extrabold text-white">
                    International Sales / PMR Mobility Equipment — IRC International Railway Consulting
                  </span>
                  <span className="text-[11px] font-mono text-emerald-400 shrink-0">España &amp; Francia · 2026</span>
                </div>
                <p className="text-xs text-slate-300 mt-1">
                  {cvLang === 'en'
                    ? 'Commercial development for Spain and France in technical railway mobility equipment (PMR) and components. Client analysis, account development, technical communication and coordination with industrial customers.'
                    : 'Desarrollo comercial entre España y Francia en equipamiento técnico de movilidad ferroviaria (PMR) y componentes. Análisis de clientes, comunicación técnica bilingüe y coordinación con industria.'}
                </p>
              </div>

              <div className="border-l-2 border-amber-500 pl-3.5">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs sm:text-sm font-extrabold text-white">
                    Commercial Banking — BBVA
                  </span>
                  <span className="text-[11px] font-mono text-amber-400 shrink-0">~1 año</span>
                </div>
                <p className="text-xs text-slate-300 mt-1">
                  {cvLang === 'en'
                    ? 'Client-facing commercial experience in banking, strengthening financial literacy, risk/needs analysis, communication and business discipline applied directly to Novus Capital.'
                    : 'Experiencia comercial directa con clientes en banca (BBVA), consolidando cultura financiera, análisis de necesidades y riesgos, comunicación con cliente y disciplina de negocio aplicada hoy en Novus Capital.'}
                </p>
              </div>
            </div>

            {/* LANGUAGES (ES/FR/EN), PRACTICAL COURSES & VALUE PROPOSITION */}
            <div className="bg-slate-950/85 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between gap-4">
              <div className="space-y-3">
                <h3 className="text-xs font-extrabold uppercase tracking-wider text-emerald-400">
                  5. IDIOMAS (ES / FR / EN) &amp; CURSOS ESPECIALIZADOS APLICADOS A PROYECTOS
                </h3>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div className="bg-slate-900/90 border border-sky-500/35 rounded-xl p-3.5">
                    <div className="text-xs font-extrabold text-sky-300 mb-1">🌍 3 Idiomas de Trabajo</div>
                    <p className="text-[11px] text-slate-200 leading-relaxed">
                      • <strong>Español:</strong> Nativo.<br />
                      • <strong>Français:</strong> Fluido profesional (2 años trabajando en Bayonne + industria Francia/España).<br />
                      • <strong>English:</strong> Fluido en ingeniería, documentación y aprendizaje técnico.
                    </p>
                  </div>

                  <div className="bg-slate-900/90 border border-amber-500/35 rounded-xl p-3.5">
                    <div className="text-xs font-extrabold text-amber-300 mb-1">📈 Cursos de Finanzas &amp; Mercados</div>
                    <p className="text-[11px] text-slate-200 leading-relaxed">
                      Formación especializada en la senda <strong>EIP / EFA</strong>, análisis fundamental de compañías, valoración de activos, mercados financieros y macroeconomía aplicada en <strong>Novus Capital</strong>.
                    </p>
                  </div>

                  <div className="bg-slate-900/90 border border-emerald-500/35 rounded-xl p-3.5">
                    <div className="text-xs font-extrabold text-emerald-300 mb-1">🛠️ Cursos Técnicos &amp; Autodidacta</div>
                    <p className="text-[11px] text-slate-200 leading-relaxed">
                      Aprendizaje práctico continuo mediante cursos de <strong>Python Científico, SQL/Supabase, Sistemas de Agentes IA (RAG/MCP/Ollama) y CAD/CAE</strong> volcados al 100% en código real.
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-r from-emerald-950/50 to-sky-950/50 border border-emerald-500/40 rounded-2xl p-4">
                <div className="text-xs font-extrabold uppercase text-emerald-300 mb-1">
                  💎 Lo que demuestro con hechos (Sin titulitis · 100% Ejecución en Proyectos)
                </div>
                <p className="text-xs sm:text-sm text-slate-100 font-medium leading-relaxed">
                  {cvLang === 'en'
                    ? 'I prove my engineering value through working systems: systems thinking, rapid autonomous learning, trilingual communication (ES/FR/EN), product ownership and the ability to connect backend engineering, mathematical validation and AI-agent swarms with real business needs.'
                    : 'Demuestro mi valía con sistemas funcionando: pensamiento sistémico, capacidad autodidacta ultrarrápida, comunicación trilingüe con cliente (Español, Francés e Inglés), visión de propietario de producto (Product Ownership) y unión real entre ingeniería de software, matemáticas y agentes de IA.'}
                </p>
              </div>
            </div>
          </div>

          {/* 6. Los 10 Proyectos Integrados donde se demuestra cada tecnología */}
          <div>
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-purple-400 mb-3">
              6. DESGLOSE DE LOS 10 PROYECTOS TÉCNICOS DONDE APLICO TODO MI CONOCIMIENTO (NOVUSMUNDUS + ARCHIFY)
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
              {TEN_PROJECTS.map((p) => (
                <div
                  key={p.num}
                  className="bg-slate-950/90 border border-emerald-500/35 rounded-2xl p-3.5 flex flex-col justify-between gap-2"
                >
                  <div>
                    <div className="flex items-center justify-between text-[10px] font-mono font-bold text-emerald-400 mb-1">
                      <span>PROYECTO {p.num}</span>
                      <span>{p.status}</span>
                    </div>
                    <div className="text-xs font-extrabold text-white leading-snug">{p.title}</div>
                  </div>
                  <div className="text-[10px] text-slate-400 border-t border-slate-800 pt-2">
                    <div><strong className="text-sky-300">Conocimiento:</strong> {p.stack}</div>
                    <div><strong className="text-purple-300">Base:</strong> {p.math}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
          ),
        [subView, cvLang, copiedCv, handleCopyCv, openConcept]
      )}

      {/* ===================================================================== */}
      {/* RECURSIVE BLUE CONCEPT MODAL (FRACCIONAMIENTO COGNITIVO DESDE CERO)   */}
      {/* ===================================================================== */}
      {activeConcept && (
        <div
          onClick={() => setConceptHistory([])}
          className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="bg-slate-900 border-2 border-sky-400 rounded-3xl max-w-2xl w-full p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto"
          >
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-extrabold text-white">{activeConcept.title}</h3>
              <button
                onClick={() => setConceptHistory([])}
                className="w-8 h-8 rounded-full bg-rose-500/20 border border-rose-500/50 text-rose-300 font-bold hover:bg-rose-500 hover:text-white"
              >
                ✕
              </button>
            </div>

            {/* Breadcrumbs */}
            <div className="flex flex-wrap items-center gap-2 bg-slate-950 px-3 py-2 rounded-xl border border-slate-800 text-xs">
              {conceptHistory.length > 1 && (
                <button
                  onClick={goBackConcept}
                  className="px-2.5 py-1 rounded-full bg-sky-500/20 text-sky-300 font-bold hover:bg-sky-500 hover:text-slate-950"
                >
                  ⬅️ Volver atrás
                </button>
              )}
              <span className="text-slate-400 font-semibold">Ruta:</span>
              {conceptHistory.map((k, idx) => (
                <span key={k} className="text-sky-300 font-bold">
                  {CONCEPT_DB[k]?.shortLabel || k}
                  {idx < conceptHistory.length - 1 ? ' › ' : ''}
                </span>
              ))}
            </div>

            <div className="bg-slate-950/80 border border-slate-800 rounded-2xl p-4 space-y-1">
              <div className="text-[11px] font-extrabold uppercase text-sky-400">
                🌱 1. Explicación desde cero (Sin tecnicismos)
              </div>
              <p className="text-sm text-slate-200 leading-relaxed">{activeConcept.what}</p>
            </div>

            <div className="bg-slate-950/80 border border-slate-800 rounded-2xl p-4 space-y-1">
              <div className="text-[11px] font-extrabold uppercase text-amber-400">
                ⚙️ 2. ¿Cómo funciona paso a paso en tu proyecto?
              </div>
              <p className="text-sm text-slate-200 leading-relaxed">{activeConcept.how}</p>
            </div>

            <div className="bg-slate-950/80 border border-purple-500/30 rounded-2xl p-4 space-y-1">
              <div className="text-[11px] font-extrabold uppercase text-purple-300">
                📐 3. Fórmula Matemática e Ingeniería
              </div>
              <p className="text-xs font-mono text-purple-200">{activeConcept.math}</p>
            </div>

            <div className="bg-emerald-950/30 border border-emerald-500/40 rounded-2xl p-4 space-y-1">
              <div className="text-[11px] font-extrabold uppercase text-emerald-400">
                🎤 4. Frase clave para el Cliente o Entrevista
              </div>
              <p className="text-sm italic text-emerald-100">{activeConcept.interview}</p>
            </div>

            {/* Sub-concepts to keep drilling down */}
            <div className="pt-2 border-t border-slate-800">
              <div className="text-xs font-extrabold text-sky-400 mb-2">
                🧩 5. Sigue desglosando en azul cualquier sub-concepto relacionado:
              </div>
              <div className="flex flex-wrap gap-2">
                {activeConcept.subconcepts.map((subKey) => {
                  const sub = CONCEPT_DB[subKey];
                  if (!sub) return null;
                  return (
                    <button
                      key={subKey}
                      onClick={() => openConcept(subKey)}
                      className="px-3 py-1.5 rounded-full bg-sky-500/15 border border-sky-400/50 text-sky-300 text-xs font-bold hover:bg-sky-400 hover:text-slate-950 transition-all"
                    >
                      🔹 {sub.shortLabel}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
