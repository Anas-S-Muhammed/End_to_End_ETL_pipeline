# Fuel Price ETL Pipeline

A weekly ETL pipeline that pulls Malaysian fuel price data (RON95, RON97, diesel) from the Malaysian government's public Open API, validates and transforms it, and loads it into a Postgres warehouse. Orchestrated with Airflow, containerized with Docker.

## Why this exists

Most ETL tutorials use toy or US-centric data. This uses a real, publicly available government API with weekly cadence, actual missing-data quirks, and no authentication overhead — closer to what a junior data engineer actually encounters than a curated tutorial dataset.

## Architecture

```
data.gov.my API --> extract --> transform --> load --> Postgres (raw + analytics schemas)
                                     |
                              Airflow DAG (weekly schedule, retries, data quality gate)
```

- **raw.fuel_price_loads** — append-only archive of every API response, stored as JSONB. Kept for audit purposes; nothing downstream depends on it being clean.
- **analytics.fuel_prices** — cleaned, typed table. `price_date` is a unique key, so re-running the pipeline for a week already loaded updates the row instead of duplicating it.

## Stack

- Python 3.11
- Apache Airflow 2.9 (LocalExecutor)
- PostgreSQL 16
- Docker Compose

## Project layout

```
dags/etl_pipeline_dag.py   Orchestration only — no business logic
src/extract/                API client, no transform/load logic
src/transform/               Pure functions, no I/O, unit-testable in isolation
src/load/                    Owns all warehouse writes and upsert logic
sql/schema.sql                Warehouse schema, applied on first container start
tests/                        Unit tests for the transform layer
```

## Running it

1. Copy `.env.example` to `.env` and set values.
2. `docker compose up -d`
3. Airflow UI at `localhost:8080` (default login: admin/admin, set in docker-compose).
4. Enable the `fuel_price_etl` DAG and trigger a run, or wait for the Friday 06:00 schedule.
5. Connect to the warehouse directly on `localhost:5433` to inspect `analytics.fuel_prices`.

## Data quality

The DAG includes a gate task that fails the run if more than half the batch is missing `ron95` values, rather than silently loading a broken source response. Retries are set to 3 attempts with a 5-minute backoff for transient API failures.

## Data source

Malaysia's Open Data Portal — `api.data.gov.my`, dataset id `fuelprice`. No API key required.

## Possible extensions

- Add MET Malaysia weather data as a second source feeding the same warehouse
- Add a `dbt` layer on top of `analytics.fuel_prices` for derived metrics (week-over-week change, moving averages)
- Swap LocalExecutor for CeleryExecutor if adding more DAGs
