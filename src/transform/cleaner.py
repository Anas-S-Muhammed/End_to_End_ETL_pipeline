"""
Transform stage: pure functions that turn raw API records into clean,
typed rows ready for loading. No network calls, no DB connections —
that separation is what lets you unit test this against a saved JSON
fixture instead of hitting the live API every time.
"""
from datetime import date, datetime


def _to_float(value) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def clean_record(record: dict) -> dict:
    """Validates and reshapes a single raw fuel price record."""
    if "date" not in record:
        raise ValueError(f"Record missing required 'date' field: {record}")

    return {
        "price_date": _to_date(record["date"]),
        "ron95": _to_float(record.get("ron95")),
        "ron97": _to_float(record.get("ron97")),
        "diesel": _to_float(record.get("diesel")),
        "diesel_eastmsia": _to_float(record.get("diesel_eastmsia")),
    }


def clean_records(records: list[dict]) -> list[dict]:
    """
    Cleans a batch of records, skipping (and logging) any row that fails
    validation instead of failing the whole batch — one bad row from the
    source shouldn't take down the pipeline.
    """
    cleaned = []
    for raw in records:
        try:
            cleaned.append(clean_record(raw))
        except ValueError as exc:
            print(f"[transform] skipping bad record: {exc}")
    return cleaned
