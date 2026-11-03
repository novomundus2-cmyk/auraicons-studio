# Núcleo de Ingeniería BigQuery & Data Autocleaning
### Mikel Irastorza · Lead Systems Architect & Big Data Engineer (EFA)
**Agente Especializado Asignado**: `EKC - Josué` (Cloud SQL, BigQuery & Databricks Lead)

Este módulo implementa las tres directivas oficiales de Google Cloud Data Agent Kit:
1. **/bigquery-optimization**: Optimización de facturación física/lógica, particionamiento diario con filtro obligatorio (`require_partition_filter`), clustering y vistas materializadas con Smart Tuning.
2. **/data-autocleaning**: Perfilado automatizado de datos (tasas de nulos, valores distintos, distribuciones), deduplicación idempotente por clave compuesta y acotamiento de tolerancias CAD $[-0.200, +0.200]\text{ mm}$.
3. **/bigquery-troubleshooting**: Diagnóstico de cuello de botella por etapas (stages), detección de consultas abusivas (*Bully Queries*), contención de slots y desbordamiento de memoria a disco (*Shuffle Spill*).

---

## Archivos del Módulo

| Archivo | Propósito Técnico | Directiva Google Cloud |
|---|---|---|
| [`bigquery_optimization.sql`](bigquery_optimization.sql) | DDL de particionamiento, clustering, Search Index en JSON y consultas `TABLE_STORAGE` para evaluar facturación física vs lógica (umbral > 2:1). | `/bigquery-optimization` |
| [`data_autocleaning_engine.py`](data_autocleaning_engine.py) | Motor Python Clean Code de perfilado estadístico, muestreo dinámico (>1M filas) y limpieza idempotente. | `/data-autocleaning` |
| [`bigquery_troubleshooting.sql`](bigquery_troubleshooting.sql) | Consultas forenses sobre `INFORMATION_SCHEMA.JOBS_BY_PROJECT` para aislar `slot_contention`, `shuffle_spill_gib` y picos de concurrencia (>95% saturación). | `/bigquery-troubleshooting` |

---

## Ejecución del Motor de Limpieza

```bash
python3 CV/08_bigquery_engineering_core/data_autocleaning_engine.py
```
