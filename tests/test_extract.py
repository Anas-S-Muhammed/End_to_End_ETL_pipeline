import pytest

from src.extract.api_client import build_request_url, fetch_fuel_prices


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload
        self.raise_called = False

    def raise_for_status(self):
        self.raise_called = True

    def json(self):
        return self.payload


def test_build_request_url_includes_dataset_and_limit():
    assert build_request_url(25).endswith("?id=fuelprice&limit=25")


def test_fetch_fuel_prices_returns_list_and_uses_timeout(monkeypatch):
    response = FakeResponse([{"date": "2026-01-02"}])
    observed = {}

    def fake_get(url, timeout):
        observed.update(url=url, timeout=timeout)
        return response

    monkeypatch.setattr("src.extract.api_client.requests.get", fake_get)

    assert fetch_fuel_prices(limit=25, timeout=9) == [{"date": "2026-01-02"}]
    assert observed["url"] == build_request_url(25)
    assert observed["timeout"] == 9
    assert response.raise_called


def test_fetch_fuel_prices_rejects_non_list_response(monkeypatch):
    monkeypatch.setattr("src.extract.api_client.requests.get", lambda *_args, **_kwargs: FakeResponse({}))

    with pytest.raises(ValueError, match="Unexpected response shape"):
        fetch_fuel_prices()
