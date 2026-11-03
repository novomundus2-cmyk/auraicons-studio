-- ============================================================================
-- EKC (ElektriKubercisC) — BIGQUERY OPTIMIZATION & STORAGE ARCHITECTURE
-- Lead Systems Architect: Mikel Irastorza (Data & Deployment Engineer · EFA)
-- Assigned Agent: EKC - Josué (Cloud SQL, BigQuery & Databricks Lead)
-- Scope Framing:
--   Project: `mikel-cloud-data` (or target project)
--   Region: `europe-west2` (London) / Default Fallback: `region-us`
-- Objective: Improving cost-efficiency and optimizing slot performance.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. PHYSICAL VS. LOGICAL STORAGE BILLING EVALUATION
-- Evaluates compression ratio across tables. If ratio > 2:1, switching to
-- PHYSICAL storage billing improves cost-efficiency significantly.
-- ----------------------------------------------------------------------------
SELECT
  project_id,
  table_schema AS dataset_id,
  table_name,
  -- Storage sizes in GiB
  ROUND(total_logical_bytes / POW(1024, 3), 2) AS logical_gib,
  ROUND(total_physical_bytes / POW(1024, 3), 2) AS physical_gib,
  -- Effective compression ratio
  ROUND(SAFE_DIVIDE(total_logical_bytes, total_physical_bytes), 2) AS compression_ratio,
  -- Billing Model Recommendation (based on standard ~2:1 break-even threshold)
  CASE
    WHEN total_physical_bytes = 0 THEN 'INSUFFICIENT_DATA'
    WHEN SAFE_DIVIDE(total_logical_bytes, total_physical_bytes) >= 2.0 
      THEN 'RECOMMEND_PHYSICAL (High Compression Benefit)'
    ELSE 'RECOMMEND_LOGICAL (Maintain Current Model)'
  END AS billing_recommendation,
  -- Fail-Safe and Time Travel overhead
  ROUND(time_travel_physical_bytes / POW(1024, 3), 2) AS time_travel_gib,
  ROUND(failsafe_physical_bytes / POW(1024, 3), 2) AS failsafe_gib
FROM
  `region-europe-west2`.INFORMATION_SCHEMA.TABLE_STORAGE
WHERE
  total_logical_bytes > 0
ORDER BY
  logical_gib DESC
LIMIT 50;

-- ----------------------------------------------------------------------------
-- 2. PRODUCTION DDL: PARTITIONING & CLUSTERING STRATEGY
-- Enforces partition pruning (require_partition_filter = true) to eliminate
-- accidental table scans. Clustered by high-cardinality query keys.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `mikel-cloud-data.ekc_streaming.telemetry_events_partitioned`
(
  event_id STRING NOT NULL,
  agent_codename STRING NOT NULL,
  source_node STRING NOT NULL,
  metric_name STRING NOT NULL,
  metric_value FLOAT64,
  cad_delta_mm FLOAT64,
  pacioli_cents INT64,
  metadata_json JSON,
  ingestion_timestamp TIMESTAMP NOT NULL,
  event_date DATE NOT NULL
)
PARTITION BY event_date
CLUSTER BY agent_codename, metric_name, source_node
OPTIONS (
  description = "EKC high-speed telemetry table partitioned by day and clustered by agent codename.",
  require_partition_filter = true,
  partition_expiration_days = 90
);

-- ----------------------------------------------------------------------------
-- 3. ACCELERATION STRUCTURE: SEARCH INDEX ON JSON/STRING
-- Accelerates selective lookups and needle-in-a-haystack queries over JSON data.
-- ----------------------------------------------------------------------------
CREATE SEARCH INDEX IF NOT EXISTS ekc_telemetry_search_idx
ON `mikel-cloud-data.ekc_streaming.telemetry_events_partitioned`(metadata_json)
OPTIONS (
  analyzer = 'NO_OP'
);

-- ----------------------------------------------------------------------------
-- 4. ACCELERATION STRUCTURE: MATERIALIZED VIEW FOR STREAMING AGGREGATIONS
-- Provides pre-aggregated Welford statistics with smart tuning rewrite.
-- ----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS `mikel-cloud-data.ekc_streaming.mv_hourly_agent_metrics`
PARTITION BY event_date
CLUSTER BY agent_codename, metric_name
OPTIONS (
  enable_refresh = true,
  refresh_interval_minutes = 30
) AS
SELECT
  event_date,
  TIMESTAMP_TRUNC(ingestion_timestamp, HOUR) AS metric_hour,
  agent_codename,
  metric_name,
  COUNT(1) AS event_count,
  AVG(metric_value) AS mean_value,
  SUM(metric_value) AS sum_value,
  MIN(metric_value) AS min_value,
  MAX(metric_value) AS max_value,
  -- Variance M2 sum component
  VAR_SAMP(metric_value) AS sample_variance
FROM
  `mikel-cloud-data.ekc_streaming.telemetry_events_partitioned`
GROUP BY
  event_date,
  metric_hour,
  agent_codename,
  metric_name;
