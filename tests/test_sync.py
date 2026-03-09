from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.services.sync import SyncService


@pytest.mark.asyncio
async def test_sync_skips_recent_symbol(monkeypatch):
    service = SyncService(SimpleNamespace())
    service.repo.should_skip_symbol = AsyncMock(return_value=True)
    service.cache.invalidate_events_cache = AsyncMock()

    result = await service.sync(["AAPL"], force=False)

    assert result["symbols_skipped"] == ["AAPL"]
    assert result["symbols_synced"] == []


@pytest.mark.asyncio
async def test_sync_creates_events(monkeypatch):
    service = SyncService(SimpleNamespace())
    service.repo.should_skip_symbol = AsyncMock(return_value=False)
    service.providers.fetch_all = AsyncMock(return_value=([
        {
            "symbol": "AAPL",
            "event_type": "earnings",
            "event_date": "2026-02-20",
            "title": "AAPL Earnings",
            "details": {},
            "provider_name": "provider_a",
            "provider_event_id": "1",
            "source_payload": {},
            "dedupe_key": "AAPL|earnings|2026-02-20|aapl earnings",
        }
    ], []))
    service.repo.upsert_normalized_events = AsyncMock(return_value=(1, 0))
    service.repo.mark_symbol_synced = AsyncMock()
    service.cache.invalidate_events_cache = AsyncMock()

    result = await service.sync(["AAPL"], force=True)

    assert result["events_created"] == 1
    assert result["events_updated"] == 0
    assert result["symbols_synced"] == ["AAPL"]
