"""
Extract stage: fetches fuel price data from data.gov.my's Open API.
No transformation or DB logic here — this module's only job is to
return raw JSON (or raise on failure). Keeping it this "dumb" is what
makes it testable without a network connection or a database.
"""
import requests

from src.config import API_BASE_URL, FUEL_PRICE_DATASET_ID


def build_request_url(limit: int = 100) -> str:
    return f"{API_BASE_URL}?id={FUEL_PRICE_DATASET_ID}&limit={limit}"


def fetch_fuel_prices(limit: int = 100, timeout: int = 15) -> list[dict]:
    """
   
   
   
   
   
   
   
   
   

   
   

   
