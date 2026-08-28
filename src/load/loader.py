"""
Load stage: owns all writes to the warehouse. Two responsibilities:
  1. Archive the untouched API payload into raw.fuel_price_loads (audit trail)
  2. Upsert cleaned rows into analytics.fuel_prices (idempotent — safe to
     re-run the same DAG run without creating duplicates)
"""
import json

import psycopg2
import psycopg2.extras

from src.config import get_warehouse_dsn


def insert_raw_payload(conn, source_url: str, payload: list[dict]) -> str:
    """Stores the raw API response verbatim, returns the load_id (UUID)."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO raw.fuel_price_loads (source_url, payload)
            VALUES (%s, %s)
            RETURNING id;
            """,
            (source_url, json.dumps(payload)),
        )
        load_id = cur.fetchone()[0]
    conn.commit()
    return load_id


def upsert_fuel_prices(conn, cleaned_rows: list[dict], load_id: str) -> int:
    """
    Upserts cleaned rows keyed on price_date. ON CONFLICT means re-running
    this for a week you've already loaded updates the existing row instead
    of erroring or duplicating — this is what makes the pipeline safe to
    retry.
    """
    if not cleaned_rows:
        return 0

    query = """
        INSERT INTO analytics.fuel_prices
            (price_date, ron95, ron97, diesel, diesel_eastmsia, load_id)
        VALUES (%(price_date)s, %(ron95)s, %(ron97)s, %(diesel)s,
                %(diesel_eastmsia)s, %(load_id)s)
        ON CONFLICT (price_date) DO UPDATE SET
            ron95 = EXCLUDED.ron95,
            ron97 = EXCLUDED.ron97,
            diesel = EXCLUDED.diesel,
            diesel_eastmsia = EXCLUDED.diesel_eastmsia,
            loaded_at = now(),
            load_id = EXCLUDED.load_id;
    """
    rows = [{**row, "load_id": load_id} for row in cleaned_rows]

    with conn.cursor() as cur:
        psycopg2.extras.execute_batch(cur, query, rows)
    conn.commit()
    return len(rows)


def get_connection():
    return psycopg2.connect(get_warehouse_dsn())
