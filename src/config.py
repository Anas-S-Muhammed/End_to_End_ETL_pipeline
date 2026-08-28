import os

API_BASE_URL = "https://api.data.gov.my/data-catalogue"
FUEL_PRICE_DATASET_ID = "fuelprice"

WAREHOUSE_DB_HOST = os.environ.get("WAREHOUSE_DB_HOST", "localhost")
WAREHOUSE_DB_PORT = os.environ.get("WAREHOUSE_DB_PORT", "5433")
WAREHOUSE_DB_NAME = os.environ.get("WAREHOUSE_DB_NAME", "fuel_warehouse")
WAREHOUSE_DB_USER = os.environ.get("WAREHOUSE_DB_USER", "etl_user")
WAREHOUSE_DB_PASSWORD = os.environ.get("WAREHOUSE_DB_PASSWORD", "change_me")


def get_warehouse_dsn() -> str:
    return (
        f"host={WAREHOUSE_DB_HOST} port={WAREHOUSE_DB_PORT} "
        f"dbname={WAREHOUSE_DB_NAME} user={WAREHOUSE_DB_USER} "
        f"password={WAREHOUSE_DB_PASSWORD}"
    )
