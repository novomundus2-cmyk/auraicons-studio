-- =============================================================================
-- BIGQUERY PROPERTY GRAPH (GQL) FINANCIAL INVESTIGATION SUITE
-- Standards: BigQuery GoogleSQL GQL (Native Graph Queries)
-- Graph: `financial_lakehouse.financial_network_graph`
-- Invariant: Zero Cypher syntax. 100% compliant with BigQuery ISO GQL standards.
-- =============================================================================

-- =============================================================================
-- 1. DETECCIÓN DE ANOMALÍAS DE ALTO VALOR (ROBUST MAD Z-SCORE > 3.0)
-- Identifica pagos directos hacia comercios donde el importe se desvía drásticamente
-- de la mediana robusta (evitando el efecto de enmascaramiento clásico).
-- =============================================================================
GRAPH `financial_lakehouse.financial_network_graph`
MATCH (c:Customer)-[p:PaymentFlow]->(m:MerchantNode)
WHERE p.robust_mad_z_score > 3.0 AND p.amount_eur > 500.0
RETURN
  c.user_id,
  c.risk_tier,
  c.country AS user_country,
  m.merchant_name,
  m.category AS merchant_category,
  p.transaction_id,
  p.amount_eur,
  p.robust_mad_z_score,
  p.is_fraud_anomaly
ORDER BY p.robust_mad_z_score DESC
LIMIT 25;

-- =============================================================================
-- 2. DETECCIÓN DE REDES DE FRAUDE COLUSIVO (MULE ACCOUNT / RING DETECTION)
-- Busca patrones donde dos usuarios distintos transfieren sumas anómalas
-- al mismo comercio en ventanas cercanas (posible red de mulas o colusión).
-- =============================================================================
GRAPH `financial_lakehouse.financial_network_graph`
MATCH (c1:Customer)-[p1:PaymentFlow]->(m:MerchantNode)<-[p2:PaymentFlow]-(c2:Customer)
WHERE c1.user_id != c2.user_id
  AND p1.robust_mad_z_score > 2.5
  AND p2.robust_mad_z_score > 2.5
  AND p1.transaction_id != p2.transaction_id
RETURN
  c1.user_id AS primary_suspect_id,
  c1.risk_tier AS primary_risk_tier,
  c2.user_id AS affiliate_suspect_id,
  c2.risk_tier AS affiliate_risk_tier,
  m.merchant_id,
  m.merchant_name,
  m.category,
  p1.amount_eur AS tx1_amount,
  p2.amount_eur AS tx2_amount,
  (p1.amount_eur + p2.amount_eur) AS total_coordinated_volume
ORDER BY total_coordinated_volume DESC
LIMIT 20;

-- =============================================================================
-- 3. RASTREO MULTISALTO DE FONDOS CON CAMINO VARIABLE (VARIABLE-LENGTH TRAVERSAL)
-- Rastrea la dispersión de fondos desde clientes de ALTO RIESGO (HIGH)
-- a través de múltiples saltos en el grafo para detectar pitufeo (smurfing / structuring).
-- =============================================================================
GRAPH `financial_lakehouse.financial_network_graph`
MATCH (src:Customer)-[p:PaymentFlow]->{1, 3}(dest)
WHERE src.risk_tier = 'HIGH'
RETURN
  src.user_id AS origin_user,
  src.risk_tier AS origin_risk,
  LABELS(dest) AS destination_labels,
  COUNT(p) AS path_edges_count
GROUP BY src.user_id, src.risk_tier, destination_labels
ORDER BY path_edges_count DESC
LIMIT 15;

-- =============================================================================
-- 4. AGREGACIÓN RELACIONAL AVANZADA CON `GRAPH_TABLE`
-- Combina el motor de grafo nativo con SQL relacional estándar de BigQuery
-- para generar el resumen ejecutivo de riesgo por segmento y país.
-- =============================================================================
SELECT
  gt.user_country,
  gt.risk_tier,
  COUNT(DISTINCT gt.user_id) AS total_suspect_users,
  COUNT(gt.transaction_id) AS total_flagged_transactions,
  ROUND(SUM(gt.amount_eur), 2) AS total_flagged_volume_eur,
  ROUND(AVG(gt.robust_mad_z_score), 2) AS avg_robust_z
FROM GRAPH_TABLE(
  `financial_lakehouse.financial_network_graph`
  MATCH (c:Customer)-[p:PaymentFlow]->(m:MerchantNode)
  WHERE p.robust_mad_z_score > 2.0 OR p.is_fraud_anomaly = 1
  COLUMNS (
    c.user_id,
    c.country AS user_country,
    c.risk_tier,
    m.merchant_name,
    p.transaction_id,
    p.amount_eur,
    p.robust_mad_z_score,
    p.is_fraud_anomaly
  )
) AS gt
GROUP BY gt.user_country, gt.risk_tier
ORDER BY total_flagged_volume_eur DESC;
