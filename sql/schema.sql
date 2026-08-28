-- Fuel Price ETL Pipeline schema
-- Two-layer design: raw (append-only, audit trail) + analytics (clean, upsertable)

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS analytics;

-- raw.fuel_price_loads: one row per pipeline run, stores the untouched API
-- payload as JSONB. Never overwritten — this is your audit trail if the
-- source data or your transform logic is ever in question.
CREATE TABLE IF NOT EXISTS raw.fuel_price_loads (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fetched_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    source_url      TEXT NOT NULL,
    payload         JSONB NOT NULL
);

-- analytics.fuel_prices: cleaned, typed, one row per week per price series.
-- date is the natural key from the source, so it's used as the upsert
-- conflict target — re-running the pipeline on the same week updates the
-- row instead of duplicating it.
CREATE TABLE IF NOT EXISTS analytics.fuel_prices (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    price_date          DATE NOT NULL UNIQUE,
    ron95               NUMERIC(5,2),
    ron97               NUMERIC(5,2),
    diesel              NUMERIC(5,2),
    diesel_eastmsia     NUMERIC(5,2),
    loaded_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    load_id             UUID REFERENCES raw.fuel_price_loads(id)
);

CREATE INDEX IF NOT EXISTS idx_fuel_prices_date ON analytics.fuel_prices (price_date);
