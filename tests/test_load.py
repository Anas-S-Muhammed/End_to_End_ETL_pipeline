import json

from src.load import loader


class FakeCursor:
    def __init__(self, load_id="load-1"):
        self.load_id = load_id
        self.executed = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, query, params):
        self.executed.append((query, params))

    def fetchone(self):
        return (self.load_id,)


class FakeConnection:
    def __init__(self):
        self.cursor_instance = FakeCursor()
        self.commits = 0

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.commits += 1


def test_insert_raw_payload_archives_json_and_returns_load_id():
    conn = FakeConnection()
    payload = [{"date": "2026-01-02", "ron95": 2.05}]

    assert loader.insert_raw_payload(conn, "https://example.test", payload) == "load-1"
    _, params = conn.cursor_instance.executed[0]
    assert params[0] == "https://example.test"
    assert json.loads(params[1]) == payload
    assert conn.commits == 1


def test_upsert_fuel_prices_adds_load_id_and_commits(monkeypatch):
    conn = FakeConnection()
    calls = []
    rows = [{"price_date": "2026-01-02", "ron95": 2.05, "ron97": None, "diesel": None, "diesel_eastmsia": None}]

    monkeypatch.setattr(loader.psycopg2.extras, "execute_batch", lambda cur, query, values: calls.append((cur, query, values)))

    assert loader.upsert_fuel_prices(conn, rows, "load-1") == 1
    assert calls[0][2][0]["load_id"] == "load-1"
    assert "ON CONFLICT (price_date)" in calls[0][1]
    assert conn.commits == 1


def test_upsert_fuel_prices_does_not_commit_an_empty_batch():
    conn = FakeConnection()
    assert loader.upsert_fuel_prices(conn, [], "load-1") == 0
    assert conn.commits == 0
