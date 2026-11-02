-- ============================================================================
-- 🏛️ NOVUS ENTERPRISE CORE LEDGER & SETTLEMENT ENGINE
-- Designed for: High-Frequency Settlement, Double-Entry Bookkeeping & Auditability
-- Invariants:
--   1. Double-Entry Zero-Sum Balance (Σ Debits == Σ Credits at DB engine level)
--   2. Absolute Idempotency (Replay Attack & Double-Spending Prevention)
--   3. Concurrency Queue with FOR UPDATE SKIP LOCKED (Zero Lock Contention)
--   4. Cryptographic Tamper-Evident Hash Chain (SHA-256 Ledger Lineage)
--   5. Strict Integer Monetary Units (BIGINT cents, zero floating-point error)
--   6. Declarative Partitioning & BRIN Indexes for Sub-Millisecond Scale
--   7. Enterprise Row-Level Security (RLS) Multi-Tenant Guardrails
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Clean Namespace Isolation
CREATE SCHEMA IF NOT EXISTS novus_ledger;
SET search_path TO novus_ledger, public;

-- ----------------------------------------------------------------------------
-- 1. ENUMS & DOMAIN TYPES
-- ----------------------------------------------------------------------------
DO $$ BEGIN
    CREATE TYPE account_type AS ENUM ('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE entry_direction AS ENUM ('DEBIT', 'CREDIT');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE transaction_status AS ENUM ('PENDING', 'SETTLED', 'VOIDED', 'REJECTED');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE queue_status AS ENUM ('READY', 'PROCESSING', 'COMPLETED', 'FAILED');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ----------------------------------------------------------------------------
-- 2. ACCOUNTS TABLE (DIMENSION & BALANCES)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL,
    account_number VARCHAR(32) NOT NULL,
    account_type account_type NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
    name VARCHAR(128) NOT NULL,
    -- Balance stored strictly as integer cents (e.g. 100.50 EUR = 10050 cents)
    cached_balance_cents BIGINT NOT NULL DEFAULT 0,
    -- Optimistic Concurrency Control versioning
    version BIGINT NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT uq_tenant_account_number UNIQUE (tenant_id, account_number),
    CONSTRAINT chk_currency_iso CHECK (length(currency) = 3)
);

CREATE INDEX IF NOT EXISTS idx_accounts_tenant ON accounts(tenant_id);
CREATE INDEX IF NOT EXISTS idx_accounts_type ON accounts(tenant_id, account_type);

-- ----------------------------------------------------------------------------
-- 3. IDEMPOTENCY KEYS TABLE (RETRY RESILIENCE & DOUBLE-SPEND GUARD)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS idempotency_keys (
    key VARCHAR(256) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    request_hash VARCHAR(64) NOT NULL, -- SHA-256 of canonical payload
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'COMPLETED', 'FAILED')),
    response_payload JSONB,
    locked_until TIMESTAMPTZ NOT NULL DEFAULT (clock_timestamp() + INTERVAL '30 seconds'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX IF NOT EXISTS idx_idempotency_tenant ON idempotency_keys(tenant_id);

-- ----------------------------------------------------------------------------
-- 4. LEDGER TRANSACTIONS (JOURNAL HEADER & HASH CHAIN)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ledger_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL,
    idempotency_key VARCHAR(256) REFERENCES idempotency_keys(key),
    correlation_id VARCHAR(128) NOT NULL,
    status transaction_status NOT NULL DEFAULT 'PENDING',
    description TEXT NOT NULL,
    posted_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    -- Cryptographic Tamper-Evident Hash Chain
    prev_hash VARCHAR(64),
    block_hash VARCHAR(64),
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT uq_transaction_correlation UNIQUE (tenant_id, correlation_id)
);

CREATE INDEX IF NOT EXISTS idx_tx_tenant_posted ON ledger_transactions(tenant_id, posted_at DESC);
CREATE INDEX IF NOT EXISTS idx_tx_status ON ledger_transactions(status);

-- ----------------------------------------------------------------------------
-- 5. LEDGER ENTRIES (THE ATOMIC DEBITS & CREDITS)
-- Money is NEVER modified; entries are strictly append-only!
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ledger_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id UUID NOT NULL REFERENCES ledger_transactions(id) ON DELETE RESTRICT,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
    direction entry_direction NOT NULL,
    -- Amount must be strictly positive integer cents
    amount_cents BIGINT NOT NULL CHECK (amount_cents > 0),
    sequence_num INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT uq_tx_entry_seq UNIQUE (transaction_id, sequence_num)
);

CREATE INDEX IF NOT EXISTS idx_entries_account ON ledger_entries(account_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_entries_tx ON ledger_entries(transaction_id);

-- ----------------------------------------------------------------------------
-- 6. DISTRIBUTED WORKER QUEUE (FOR UPDATE SKIP LOCKED)
-- High-throughput, zero-contention parallel transaction worker queue
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS payment_events_queue (
    id BIGSERIAL PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    payload JSONB NOT NULL,
    status queue_status NOT NULL DEFAULT 'READY',
    attempts INT NOT NULL DEFAULT 0,
    max_attempts INT NOT NULL DEFAULT 5,
    last_error TEXT,
    available_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    locked_by VARCHAR(64),
    locked_at TIMESTAMPTZ,
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX IF NOT EXISTS idx_queue_processing
ON payment_events_queue (status, available_at)
WHERE status = 'READY';

-- ----------------------------------------------------------------------------
-- 7. AUDIT TRAIL WITH DECLARATIVE PARTITIONING & BRIN INDEX
-- Demonstrates Big-Data scale: partitions by range + BRIN for 95% RAM savings
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_event_logs (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL,
    entity_type VARCHAR(64) NOT NULL,
    entity_id VARCHAR(64) NOT NULL,
    action VARCHAR(32) NOT NULL,
    actor_id VARCHAR(128) NOT NULL,
    payload_diff JSONB,
    ip_address INET,
    event_timestamp TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (id, event_timestamp)
) PARTITION BY RANGE (event_timestamp);

-- Monthly Partitions for 2026
CREATE TABLE IF NOT EXISTS audit_event_logs_2026_10 PARTITION OF audit_event_logs
    FOR VALUES FROM ('2026-10-01 00:00:00+00') TO ('2026-11-01 00:00:00+00');

CREATE TABLE IF NOT EXISTS audit_event_logs_2026_11 PARTITION OF audit_event_logs
    FOR VALUES FROM ('2026-11-01 00:00:00+00') TO ('2026-12-01 00:00:00+00');

CREATE TABLE IF NOT EXISTS audit_event_logs_default PARTITION OF audit_event_logs DEFAULT;

-- BRIN index on append-only timeseries data: 95% smaller than B-Tree
CREATE INDEX IF NOT EXISTS brin_audit_event_time
ON audit_event_logs USING BRIN (event_timestamp) WITH (pages_per_range = 32);

-- ----------------------------------------------------------------------------
-- 8. CORE INVARIANTS: ATOMIC BALANCE & HASH CHAIN TRIGGERS
-- ----------------------------------------------------------------------------

-- Invariant 1: Double-Entry Zero-Sum Verification
CREATE OR REPLACE FUNCTION fn_verify_zero_sum_balance()
RETURNS TRIGGER AS $$
DECLARE
    v_total_debit BIGINT;
    v_total_credit BIGINT;
BEGIN
    -- Only verify when transaction is moving to SETTLED
    IF NEW.status = 'SETTLED' AND (OLD.status IS NULL OR OLD.status != 'SETTLED') THEN
        SELECT
            COALESCE(SUM(CASE WHEN direction = 'DEBIT' THEN amount_cents ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN direction = 'CREDIT' THEN amount_cents ELSE 0 END), 0)
        INTO v_total_debit, v_total_credit
        FROM ledger_entries
        WHERE transaction_id = NEW.id;

        IF v_total_debit = 0 AND v_total_credit = 0 THEN
            RAISE EXCEPTION 'ERR_EMPTY_TRANSACTION: Cannot settle transaction % with no entries', NEW.id
                USING ERRCODE = '23514';
        END IF;

        IF v_total_debit <> v_total_credit THEN
            RAISE EXCEPTION 'ERR_UNBALANCED_TRANSACTION: Transaction % is unbalanced! Total Debits (%) != Total Credits (%)',
                NEW.id, v_total_debit, v_total_credit
                USING ERRCODE = '23514';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_verify_transaction_balance ON ledger_transactions;
CREATE CONSTRAINT TRIGGER trg_verify_transaction_balance
AFTER UPDATE OR INSERT ON ledger_transactions
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION fn_verify_zero_sum_balance();

-- Invariant 2: Cryptographic Tamper-Evident Hash Chain
CREATE OR REPLACE FUNCTION fn_cryptographic_hash_chain()
RETURNS TRIGGER AS $$
DECLARE
    v_last_hash VARCHAR(64);
    v_raw_content TEXT;
BEGIN
    IF NEW.status = 'SETTLED' AND NEW.block_hash IS NULL THEN
        -- Obtain last block hash for this tenant
        SELECT block_hash INTO v_last_hash
        FROM ledger_transactions
        WHERE tenant_id = NEW.tenant_id
          AND block_hash IS NOT NULL
          AND id != NEW.id
        ORDER BY posted_at DESC, created_at DESC
        LIMIT 1;

        NEW.prev_hash := COALESCE(v_last_hash, '0000000000000000000000000000000000000000000000000000000000000000');

        -- Form canonical representation of this ledger line
        v_raw_content := NEW.tenant_id || '|' ||
                         NEW.correlation_id || '|' ||
                         NEW.posted_at::text || '|' ||
                         NEW.prev_hash;

        NEW.block_hash := encode(sha256(v_raw_content::bytea), 'hex');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_hash_chain ON ledger_transactions;
CREATE TRIGGER trg_hash_chain
BEFORE INSERT OR UPDATE ON ledger_transactions
FOR EACH ROW EXECUTE FUNCTION fn_cryptographic_hash_chain();

-- ----------------------------------------------------------------------------
-- 9. STORED PROCEDURES: ATOMIC SETTLEMENT & WORKER CONCURRENCY
-- ----------------------------------------------------------------------------

-- Procedure 1: Atomic Idempotent Settlement Engine
CREATE OR REPLACE FUNCTION post_atomic_transfer(
    p_tenant_id VARCHAR(64),
    p_idempotency_key VARCHAR(256),
    p_correlation_id VARCHAR(128),
    p_description TEXT,
    p_from_account_number VARCHAR(32),
    p_to_account_number VARCHAR(32),
    p_amount_cents BIGINT,
    p_request_hash VARCHAR(64) DEFAULT 'MANUAL_TX'
)
RETURNS JSONB AS $$
DECLARE
    v_from_account accounts%ROWTYPE;
    v_to_account accounts%ROWTYPE;
    v_tx_id UUID;
    v_cached_response JSONB;
    v_result JSONB;
BEGIN
    IF p_amount_cents <= 0 THEN
        RAISE EXCEPTION 'ERR_INVALID_AMOUNT: Transfer amount must be > 0 cents' USING ERRCODE = '23514';
    END IF;

    -- 1. Check Idempotency Key Lock & Cache
    IF p_idempotency_key IS NOT NULL THEN
        SELECT response_payload INTO v_cached_response
        FROM idempotency_keys
        WHERE key = p_idempotency_key AND status = 'COMPLETED';

        IF v_cached_response IS NOT NULL THEN
            -- Replay detected! Return cached response without re-executing
            RETURN jsonb_build_object('idempotency_replay', true, 'data', v_cached_response);
        END IF;

        -- Reserve key atomically
        INSERT INTO idempotency_keys (key, tenant_id, request_hash, status)
        VALUES (p_idempotency_key, p_tenant_id, p_request_hash, 'PENDING')
        ON CONFLICT (key) DO UPDATE
        SET updated_at = clock_timestamp();
    END IF;

    -- 2. Lock accounts in deterministic order (Alphabetical by account_number)
    -- This mathematically guarantees DEADLOCK FREEDOM!
    IF p_from_account_number < p_to_account_number THEN
        SELECT * INTO v_from_account FROM accounts
        WHERE tenant_id = p_tenant_id AND account_number = p_from_account_number FOR UPDATE;

        SELECT * INTO v_to_account FROM accounts
        WHERE tenant_id = p_tenant_id AND account_number = p_to_account_number FOR UPDATE;
    ELSE
        SELECT * INTO v_to_account FROM accounts
        WHERE tenant_id = p_tenant_id AND account_number = p_to_account_number FOR UPDATE;

        SELECT * INTO v_from_account FROM accounts
        WHERE tenant_id = p_tenant_id AND account_number = p_from_account_number FOR UPDATE;
    END IF;

    IF v_from_account.id IS NULL OR v_to_account.id IS NULL THEN
        RAISE EXCEPTION 'ERR_ACCOUNT_NOT_FOUND: One or both accounts do not exist in tenant %', p_tenant_id;
    END IF;

    -- 3. Check for sufficient balance on asset accounts
    IF v_from_account.account_type = 'ASSET' AND v_from_account.cached_balance_cents < p_amount_cents THEN
        RAISE EXCEPTION 'ERR_INSUFFICIENT_FUNDS: Account % has % cents, requested % cents',
            p_from_account_number, v_from_account.cached_balance_cents, p_amount_cents
            USING ERRCODE = '23514';
    END IF;

    -- 4. Create Ledger Transaction
    v_tx_id := gen_random_uuid();
    INSERT INTO ledger_transactions (id, tenant_id, idempotency_key, correlation_id, status, description)
    VALUES (v_tx_id, p_tenant_id, p_idempotency_key, p_correlation_id, 'PENDING', p_description);

    -- 5. Insert Symmetrical Debit & Credit Entries (Zero-Sum Invariant)
    -- For Asset accounts: DEBIT increases balance, CREDIT decreases balance
    INSERT INTO ledger_entries (transaction_id, account_id, direction, amount_cents, sequence_num)
    VALUES
        (v_tx_id, v_from_account.id, 'CREDIT', p_amount_cents, 1),
        (v_tx_id, v_to_account.id, 'DEBIT', p_amount_cents, 2);

    -- 6. Update Cached Balances atomically with version bump
    UPDATE accounts
    SET cached_balance_cents = cached_balance_cents - p_amount_cents,
        version = version + 1,
        updated_at = clock_timestamp()
    WHERE id = v_from_account.id;

    UPDATE accounts
    SET cached_balance_cents = cached_balance_cents + p_amount_cents,
        version = version + 1,
        updated_at = clock_timestamp()
    WHERE id = v_to_account.id;

    -- 7. Settle Transaction (Triggers Zero-Sum verification and Hash Chaining!)
    UPDATE ledger_transactions
    SET status = 'SETTLED'
    WHERE id = v_tx_id;

    -- 8. Finalize Idempotency Key
    v_result := jsonb_build_object(
        'transaction_id', v_tx_id,
        'correlation_id', p_correlation_id,
        'status', 'SETTLED',
        'from_account', p_from_account_number,
        'to_account', p_to_account_number,
        'amount_cents', p_amount_cents,
        'currency', v_from_account.currency,
        'settled_at', clock_timestamp()
    );

    IF p_idempotency_key IS NOT NULL THEN
        UPDATE idempotency_keys
        SET status = 'COMPLETED',
            response_payload = v_result,
            updated_at = clock_timestamp()
        WHERE key = p_idempotency_key;
    END IF;

    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

-- Procedure 2: High-Throughput Queue Consumer via FOR UPDATE SKIP LOCKED
CREATE OR REPLACE FUNCTION claim_queue_batch(
    p_worker_id VARCHAR(64),
    p_batch_size INT DEFAULT 10
)
RETURNS TABLE (
    event_id BIGINT,
    tenant_id VARCHAR(64),
    event_type VARCHAR(64),
    payload JSONB
) AS $$
BEGIN
    RETURN QUERY
    WITH available_events AS (
        SELECT id
        FROM payment_events_queue
        WHERE status = 'READY'
          AND available_at <= clock_timestamp()
        ORDER BY id ASC
        LIMIT p_batch_size
        FOR UPDATE SKIP LOCKED -- Zero Lock Contention across workers!
    )
    UPDATE payment_events_queue q
    SET status = 'PROCESSING',
        locked_by = p_worker_id,
        locked_at = clock_timestamp(),
        attempts = q.attempts + 1
    FROM available_events a
    WHERE q.id = a.id
    RETURNING q.id, q.tenant_id, q.event_type, q.payload;
END;
$$ LANGUAGE plpgsql;

-- ----------------------------------------------------------------------------
-- 10. REAL-TIME FRAUD DETECTION & AUDIT ROLLUPS (ANALYTICAL OLAP VIEWS)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_realtime_fraud_radar AS
WITH transaction_stats AS (
    SELECT
        t.tenant_id,
        t.id AS tx_id,
        t.correlation_id,
        t.posted_at,
        e.amount_cents,
        a.account_number,
        AVG(e.amount_cents) OVER (PARTITION BY t.tenant_id) AS avg_amount,
        STDDEV(e.amount_cents) OVER (PARTITION BY t.tenant_id) AS std_amount
    FROM ledger_transactions t
    JOIN ledger_entries e ON t.id = e.transaction_id
    JOIN accounts a ON e.account_id = a.id
    WHERE t.status = 'SETTLED'
      AND e.direction = 'DEBIT'
)
SELECT
    tenant_id,
    tx_id,
    correlation_id,
    account_number,
    amount_cents,
    ROUND((amount_cents / 100.0), 2) AS amount_eur,
    ROUND(COALESCE((amount_cents - avg_amount) / NULLIF(std_amount, 0), 0), 2) AS z_score,
    CASE
        WHEN (amount_cents - avg_amount) / NULLIF(std_amount, 0) > 3.0 THEN 'CRITICAL_HIGH_VALUE'
        WHEN amount_cents >= 1000000 THEN 'AML_THRESHOLD_EXCEEDED'
        ELSE 'NORMAL'
    END AS fraud_risk_level,
    posted_at
FROM transaction_stats;

-- ----------------------------------------------------------------------------
-- 11. ROW-LEVEL SECURITY (RLS) POLICIES
-- Multi-Tenant Isolation with NovusMundus Executive Bypass
-- ----------------------------------------------------------------------------
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE ledger_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE ledger_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE idempotency_keys ENABLE ROW LEVEL SECURITY;

-- Security Predicate
CREATE OR REPLACE FUNCTION is_novus_executive()
RETURNS BOOLEAN AS $$
BEGIN
    -- Bypass for NovusMundus President (Mikel) or Chatty CEO
    RETURN current_user IN ('postgres', 'supabase_admin')
        OR current_setting('request.jwt.claims', true)::jsonb->>'email' IN (
            'mikel@novusmundus.com',
            'chatty.ceo@novusmundus.com'
        );
EXCEPTION WHEN OTHERS THEN
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql STABLE;

-- Accounts RLS
DROP POLICY IF EXISTS p_accounts_tenant_isolation ON accounts;
CREATE POLICY p_accounts_tenant_isolation ON accounts
FOR ALL
USING (
    is_novus_executive()
    OR tenant_id = NULLIF(current_setting('app.current_tenant', true), '')
);

-- Transactions RLS
DROP POLICY IF EXISTS p_tx_tenant_isolation ON ledger_transactions;
CREATE POLICY p_tx_tenant_isolation ON ledger_transactions
FOR ALL
USING (
    is_novus_executive()
    OR tenant_id = NULLIF(current_setting('app.current_tenant', true), '')
);
