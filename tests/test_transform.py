from datetime import date

from src.transform.cleaner import clean_record, clean_records


def test_clean_record_parses_valid_row():
    raw = {"date": "2026-01-02", "ron95": 2.05, "ron97": 3.10, "diesel": 2.15, "diesel_eastmsia": 2.15}
    result = clean_record(raw)
    assert result["price_date"] == date(2026, 1, 2)
    assert result["ron95"] == 2.05


def test_clean_record_handles_null_fields():
    raw = {"date": "2026-01-02", "ron95": None, "ron97": 3.10, "diesel": 2.15, "diesel_eastmsia": None}
    result = clean_record(raw)
    assert result["ron95"] is None
    assert result["diesel_eastmsia"] is None


def test_clean_record_raises_on_missing_date():
    try:
        clean_record({"ron95": 2.05})
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_clean_records_skips_bad_rows_without_failing_batch():
    raw_batch = [
        {"date": "2026-01-02", "ron95": 2.05},
        {"ron95": 2.10},  # missing date — should be skipped, not crash the batch
    ]
    result = clean_records(raw_batch)
    assert len(result) == 1


def test_clean_records_skips_null_date_without_failing_batch():
    result = clean_records([{"date": None}, {"date": "2026-01-02", "ron95": 2.05}])
    assert len(result) == 1
