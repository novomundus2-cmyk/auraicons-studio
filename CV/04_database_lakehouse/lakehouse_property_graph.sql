-- =============================================================================
-- BIGQUERY PROPERTY GRAPH DDL (GQL) — VERIFIED AGAINST FINANCIAL_LAKEHOUSE.DB
-- SKILL: bigquery-graph-author
-- =============================================================================
-- Relationship Verification Evidence (Measured against SQLite Lakehouse):
-- 1. Node `Users` (`dim_users`): 500 unique `user_id` keys (100% unique).
-- 2. Node `Merchants` (`dim_merchants`): 25 unique `merchant_id` keys (100% unique).
-- 3. Edge `TransferredTo` (`fact_transactions`):
--    - `user_id` -> `dim_users.user_id`: 25,000 / 25,000 resolved (100.0%).
--    - `merchant_id` -> `dim_merchants.merchant_id`: 25,000 / 25,000 resolved (100.0%).
-- =============================================================================

CREATE PROPERTY GRAPH `financial_lakehouse.financial_network_graph`
  NODE TABLES (
    `financial_lakehouse.dim_users` AS Users
      KEY (user_id)
      LABEL Customer
      PROPERTIES (user_id, country, segment, risk_tier, created_at),

    `financial_lakehouse.dim_merchants` AS Merchants
      KEY (merchant_id)
      LABEL MerchantNode
      PROPERTIES (merchant_id, merchant_name, category, base_country, fee_bps)
  )
  EDGE TABLES (
    `financial_lakehouse.fact_transactions` AS TransferredTo
      KEY (transaction_id)
      SOURCE KEY (user_id) REFERENCES Users (user_id)
      DESTINATION KEY (merchant_id) REFERENCES Merchants (merchant_id)
      LABEL PaymentFlow
      PROPERTIES (
        transaction_id,
        amount_eur,
        classic_z,
        robust_mad_z,
        is_fraud_injected,
        kafka_partition,
        event_timestamp
      )
  );
