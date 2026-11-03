-- ============================================================================
-- EKC (ElektriKubercisC) — BIGQUERY TROUBLESHOOTING & BOTTLENECK DIAGNOSTICS
-- Lead Systems Architect: Mikel Irastorza (Data & Deployment Engineer · EFA)
-- Assigned Agent: EKC - Josué (Cloud SQL, BigQuery & Databricks Lead)
-- Scope Framing:
--   Project: `mikel-cloud-data` (or target project)
--   Region: `europe-west2` (London) / Default Fallback: `region-us`
-- Objective: Root-cause analysis of slow jobs, slot contention, and disk spills.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. ROOT-CAUSE TRIAGE: IDENTIFY "BULLY QUERIES" (HIGH CONSUMPTION)
-- Isolates the top queries consuming the vast majority of slot-hours or
-- scanning unpartitioned bytes over the last 7 days.
-- ----------------------------------------------------------------------------
SELECT
  job_id,
  user_email,
  creation_time,
  -- Execution duration in seconds
  TIMESTAMP_DIFF(end_time, start_time, SECOND) AS duration_seconds,
  -- Physical consumption metrics
  ROUND(total_slot_ms / (1000 * 60 * 60), 2) AS slot_hours_consumed,
  ROUND(total_bytes_billed / POW(1024, 4), 2) AS tib_billed,
  ROUND(total_bytes_processed / POW(1024, 4), 2) AS tib_processed,
  -- Cache and error status
  cache_hit,
  error_result.reason AS error_reason,
  -- Normalized query text snippet
  SUBSTR(query, 1, 250) AS query_snippet
FROM
  `region-europe-west2`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE
  creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND job_type = 'QUERY'
  AND statement_type != 'SCRIPT'
ORDER BY
  total_slot_ms DESC
LIMIT 20;

-- ----------------------------------------------------------------------------
-- 2. STAGE BOTTLENECK ANALYSIS: MEMORY SPILL & SLOT CONTENTION
-- Pinpoints query execution stages that spilled to disk (indicating memory
-- pressure / unoptimized JOINs) or suffered from slot starvation.
-- ----------------------------------------------------------------------------
SELECT
  job_id,
  stage.id AS stage_id,
  stage.name AS stage_name,
  stage.status AS stage_status,
  -- Timing breakdown
  stage.slot_ms AS stage_slot_ms,
  -- Memory pressure: spilled bytes to persistent disk
  ROUND(stage.shuffle_output_bytes_spilled / POW(1024, 3), 3) AS shuffle_spill_gib,
  ROUND(stage.records_read, 0) AS records_read,
  ROUND(stage.records_written, 0) AS records_written,
  -- Input amplification ratio (records written / records read)
  ROUND(SAFE_DIVIDE(stage.records_written, stage.records_read), 2) AS amplification_factor
FROM
  `region-europe-west2`.INFORMATION_SCHEMA.JOBS_BY_PROJECT,
  UNNEST(job_stages) AS stage
WHERE
  creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
  AND stage.shuffle_output_bytes_spilled > 0
ORDER BY
  stage.shuffle_output_bytes_spilled DESC
LIMIT 25;

-- ----------------------------------------------------------------------------
-- 3. CAPACITY RESERVATION SATURATION & CONCURRENT SPIKES
-- Identifies 1-minute intervals where average slot utilization exceeded 95%,
-- causing queuing and latency degradation for concurrent queries.
-- ----------------------------------------------------------------------------
SELECT
  TIMESTAMP_TRUNC(creation_time, MINUTE) AS time_window,
  COUNT(DISTINCT job_id) AS active_concurrent_jobs,
  ROUND(SUM(total_slot_ms) / (60 * 1000), 1) AS avg_slots_utilized,
  -- Flag saturated windows (>95% of typical 100-slot reservation baseline)
  CASE
    WHEN (SUM(total_slot_ms) / (60 * 1000)) >= 95.0 THEN 'CRITICAL_SLOT_SATURATION'
    WHEN (SUM(total_slot_ms) / (60 * 1000)) >= 80.0 THEN 'HIGH_UTILIZATION_WARNING'
    ELSE 'HEALTHY'
  END AS capacity_status
FROM
  `region-europe-west2`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE
  creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
  AND job_type = 'QUERY'
GROUP BY
  time_window
HAVING
  avg_slots_utilized > 50
ORDER BY
  avg_slots_utilized DESC
LIMIT 50;
