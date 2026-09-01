"""
Fuel Price ETL DAG.

This file ONLY orchestrates — it imports extract/transform/load functions
from src/ and wires them together with retries, scheduling, and basic data
quality checks. No business logic lives here; if you find yourself writing
an `if` statement that isn't about scheduling, it probably belongs in src/.
"""
from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.exceptions import AirflowFailException

from src.extract.api_client import fetch_fuel_prices, build_request_url
from src.transform.cleaner import clean_records
from src.load.loader import insert_raw_payload, upsert_fuel_prices, get_connection

default_args = {
    "owner": "anas",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    dag_id="fuel_price_etl",
    description="Extracts weekly fuel price data from data.gov.my and loads it into the warehouse",
    schedule="0 6 * * 5",  # every Friday at 06:00 — new prices usually post Thursday night
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["etl", "fuel-price", "portfolio"],
)
def fuel_price_etl():

    @task()
    def extract():
        records = fetch_fuel_prices(limit=100)
        if not records:
            raise AirflowFailException("API returned zero records — refusing to proceed")
        return records

    @task()
    def transform(raw_records: list[dict]):
        cleaned = clean_records(raw_records)
        if not cleaned:
            raise AirflowFailException("All records failed validation — check source schema")
        return cleaned

    @task()
    def load(raw_records: list[dict], cleaned_rows: list[dict]):
        conn = get_connection()
        try:
            load_id = insert_raw_payload(conn, build_request_url(), raw_records)
            row_count = upsert_fuel_prices(conn, cleaned_rows, load_id)
            print(f"[load] upserted {row_count} rows (load_id={load_id})")
        finally:
            conn.close()

    @task()
    def data_quality_check(cleaned_rows: list[dict]):
        """Basic sanity checks — fail loudly instead of loading garbage."""
        null_ron95 = sum(1 for r in cleaned_rows if r["ron95"] is None)
        if null_ron95 > len(cleaned_rows) * 0.5:
            raise AirflowFailException(
                f"{null_ron95}/{len(cleaned_rows)} rows missing ron95 — source data looks broken"
            )

    raw = extract()
    cleaned = transform(raw)
    dq_task = data_quality_check(cleaned)
    load_task = load(raw, cleaned)
    dq_task >> load_task


fuel_price_etl()
