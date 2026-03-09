from app.services.normalizers import normalize_provider_a, normalize_provider_b


def test_normalize_provider_a():
    raw = {
        "event_id": "pa-AAPL-earnings-202602",
        "ticker": "aapl",
        "type": "earnings",
        "date": "2026-02-20",
        "title": "AAPL Earnings",
        "details": {"eps_estimate": 2.1},
        "metadata": {"source": "provider_a"},
    }
    out = normalize_provider_a(raw)
    assert out["symbol"] == "AAPL"
    assert out["event_type"] == "earnings"
    assert out["provider_name"] == "provider_a"


def test_normalize_provider_b():
    raw = {
        "id": "pb_AAPL_earnings_release_20260220_1111",
        "instrument": {"symbol": "AAPL", "exchange": "NASDAQ"},
        "event": {
            "category": "earnings_release",
            "scheduled_at": "2026-02-20T08:00:00Z",
            "title": "AAPL - Earnings Release",
            "earnings_data": {"eps_consensus": 1.5},
        },
    }
    out = normalize_provider_b(raw)
    assert out["event_type"] == "earnings"
    assert out["event_date"] == "2026-02-20"
    assert out["details"] == {"eps_consensus": 1.5}
