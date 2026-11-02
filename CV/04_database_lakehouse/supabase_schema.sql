-- =============================================================================
-- NOVUSMUNDUS / NOVUS CAPITAL · SUPABASE POSTGRESQL ENTERPRISE SCHEMA & RLS
-- Architect: Mikel Irastorza · Presidente Supremo (Nivel 0)
-- Orchestrator: Chatty · Chief Executive Officer (CEO Nivel 1)
-- Standards: PostgreSQL 15+, Row-Level Security (RLS), ACID, Index Optimization
-- =============================================================================

-- 1. EXTENSIONS
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. DIMENSION TABLES
CREATE TABLE IF NOT EXISTS public.dim_users (
    user_id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    country VARCHAR(3) NOT NULL DEFAULT 'ESP',
    email TEXT UNIQUE NOT NULL,
    account_type TEXT NOT NULL DEFAULT 'retail',
    balance_eur NUMERIC(14, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.dim_merchants (
    merchant_id TEXT PRIMARY KEY,
    merchant_name TEXT NOT NULL,
    category TEXT NOT NULL,
    country VARCHAR(3) NOT NULL DEFAULT 'ESP',
    risk_score NUMERIC(4, 3) NOT NULL DEFAULT 0.050,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. FACT TRANSACTIONS TABLE (Novus Capital 25k Stream)
CREATE TABLE IF NOT EXISTS public.fact_transactions (
    transaction_id TEXT PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    user_id TEXT NOT NULL REFERENCES public.dim_users(user_id) ON DELETE CASCADE,
    merchant_id TEXT NOT NULL REFERENCES public.dim_merchants(merchant_id) ON DELETE CASCADE,
    amount_eur NUMERIC(12, 2) NOT NULL,
    category TEXT NOT NULL,
    is_fraud_anomaly BOOLEAN NOT NULL DEFAULT FALSE,
    classic_z_score NUMERIC(8, 2) NOT NULL DEFAULT 0.00,
    robust_mad_z_score NUMERIC(8, 2) NOT NULL DEFAULT 0.00,
    kafka_partition INT NOT NULL DEFAULT 0,
    ingestion_latency_ms NUMERIC(6, 2) NOT NULL DEFAULT 15.00,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. GOLD ANALYTICS METRICS (Welford-Chan Associative Aggregations)
CREATE TABLE IF NOT EXISTS public.gold_category_metrics (
    category TEXT PRIMARY KEY,
    txn_count BIGINT NOT NULL DEFAULT 0,
    total_volume_eur NUMERIC(16, 2) NOT NULL DEFAULT 0.00,
    welford_mean_eur NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    welford_variance_eur2 NUMERIC(16, 2) NOT NULL DEFAULT 0.00,
    robust_median_eur NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    robust_mad_eur NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    shannon_entropy_bits NUMERIC(6, 3) NOT NULL DEFAULT 2.950,
    fraud_alerts_count INT NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 5. CORPORATE ENTERPRISE TABLES (NovusMundus Governance)
CREATE TABLE IF NOT EXISTS public.corporate_hierarchy (
    agent_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    title TEXT NOT NULL,
    tier INT NOT NULL, -- 0: Presidente, 1: CEO, 2: C-Suite, 3: Worker
    department TEXT NOT NULL,
    reports_to TEXT NOT NULL,
    model_engine TEXT NOT NULL,
    current_status TEXT NOT NULL,
    tasks_queued INT NOT NULL DEFAULT 0,
    tasks_completed INT NOT NULL DEFAULT 0,
    routing_efficiency_pct NUMERIC(5, 2) NOT NULL DEFAULT 100.00,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.corporate_routes (
    route_id TEXT PRIMARY KEY,
    route_name TEXT NOT NULL,
    source_node TEXT NOT NULL,
    target_node TEXT NOT NULL,
    sla_target_ms NUMERIC(6, 2) NOT NULL,
    current_latency_ms NUMERIC(6, 2) NOT NULL,
    optimized_latency_ms NUMERIC(6, 2) NOT NULL,
    throughput_msg_sec NUMERIC(10, 2) NOT NULL DEFAULT 35000.00,
    optimization_strategy TEXT NOT NULL,
    improvement_pct NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    status TEXT NOT NULL DEFAULT 'AUTOMEJORADA ⚡',
    last_optimized_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.corporate_executive_orders (
    order_id TEXT PRIMARY KEY,
    order_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    issuer TEXT NOT NULL DEFAULT 'Mikel Irastorza · Presidente',
    directive_text TEXT NOT NULL,
    assigned_c_suite TEXT NOT NULL,
    chatty_response TEXT NOT NULL,
    resulting_action TEXT NOT NULL,
    efficiency_impact_pct NUMERIC(5, 2) NOT NULL DEFAULT 100.00,
    status TEXT NOT NULL DEFAULT 'EJECUTADA EXITOSAMENTE ✅'
);

CREATE TABLE IF NOT EXISTS public.corporate_reusable_knowledge (
    knowledge_id TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    executable_code TEXT NOT NULL,
    reusable_prompt TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 6. INDEXES FOR ZERO-LATENCY QUERIES
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON public.fact_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON public.fact_transactions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON public.fact_transactions(category);
CREATE INDEX IF NOT EXISTS idx_transactions_fraud ON public.fact_transactions(is_fraud_anomaly) WHERE is_fraud_anomaly = TRUE;
CREATE INDEX IF NOT EXISTS idx_corporate_hierarchy_tier ON public.corporate_hierarchy(tier);
CREATE INDEX IF NOT EXISTS idx_corporate_routes_latency ON public.corporate_routes(optimized_latency_ms);

-- 7. SQL VIEW: FRAUD ALERTS DETECTED BY ROBUST MAD SHIELD
CREATE OR REPLACE VIEW public.vw_fraud_alerts AS
SELECT 
    t.transaction_id,
    t.timestamp,
    t.user_id,
    u.full_name AS user_name,
    u.country AS user_country,
    t.merchant_id,
    m.merchant_name,
    t.category,
    t.amount_eur,
    ROUND(t.classic_z_score, 2) AS classic_z,
    ROUND(t.robust_mad_z_score, 2) AS robust_mad_z,
    t.kafka_partition
FROM public.fact_transactions t
JOIN public.dim_users u ON t.user_id = u.user_id
JOIN public.dim_merchants m ON t.merchant_id = m.merchant_id
WHERE t.is_fraud_anomaly = TRUE
ORDER BY t.robust_mad_z_score DESC;

-- 8. ROW-LEVEL SECURITY (RLS) POLICIES
ALTER TABLE public.dim_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dim_merchants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fact_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.gold_category_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.corporate_hierarchy ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.corporate_routes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.corporate_executive_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.corporate_reusable_knowledge ENABLE ROW LEVEL SECURITY;

-- Helper Function: Check if caller has Executive Privileges (Mikel President or Chatty CEO)
CREATE OR REPLACE FUNCTION public.is_novus_executive()
RETURNS BOOLEAN
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
  SELECT COALESCE(
    (auth.jwt() ->> 'role') = 'service_role' OR
    (auth.jwt() ->> 'email') = 'mikel@novusmundus.com' OR
    (auth.jwt() -> 'app_metadata' ->> 'is_executive')::boolean = true,
    false
  );
$$;

-- RLS: Public Read for Reusable Knowledge & Corporate Routes
DROP POLICY IF EXISTS "Public can view reusable knowledge" ON public.corporate_reusable_knowledge;
CREATE POLICY "Public can view reusable knowledge"
ON public.corporate_reusable_knowledge FOR SELECT
USING (true);

DROP POLICY IF EXISTS "Public can view corporate routes" ON public.corporate_routes;
CREATE POLICY "Public can view corporate routes"
ON public.corporate_routes FOR SELECT
USING (true);

DROP POLICY IF EXISTS "Public can view corporate hierarchy" ON public.corporate_hierarchy;
CREATE POLICY "Public can view corporate hierarchy"
ON public.corporate_hierarchy FOR SELECT
USING (true);

DROP POLICY IF EXISTS "Public can view gold metrics" ON public.gold_category_metrics;
CREATE POLICY "Public can view gold metrics"
ON public.gold_category_metrics FOR SELECT
USING (true);

-- RLS: User Data Isolation (Retail Users can only see own transactions and profile)
DROP POLICY IF EXISTS "Users can view own profile" ON public.dim_users;
CREATE POLICY "Users can view own profile"
ON public.dim_users FOR SELECT
USING (auth.uid()::text = user_id OR public.is_novus_executive());

DROP POLICY IF EXISTS "Users can view own transactions" ON public.fact_transactions;
CREATE POLICY "Users can view own transactions"
ON public.fact_transactions FOR SELECT
USING (auth.uid()::text = user_id OR public.is_novus_executive());

-- RLS: Only Executives can insert/update executive orders and routes
DROP POLICY IF EXISTS "Executives can manage executive orders" ON public.corporate_executive_orders;
CREATE POLICY "Executives can manage executive orders"
ON public.corporate_executive_orders FOR ALL
USING (public.is_novus_executive())
WITH CHECK (public.is_novus_executive());

DROP POLICY IF EXISTS "Executives can update corporate routes" ON public.corporate_routes;
CREATE POLICY "Executives can update corporate routes"
ON public.corporate_routes FOR UPDATE
USING (public.is_novus_executive());
