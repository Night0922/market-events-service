from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.events import EventRepository
from app.services.cache import CacheService
from app.services.providers import ProviderService


class SyncService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = EventRepository(session)
        self.providers = ProviderService()
        self.cache = CacheService()

    async def sync(self, symbols: list[str], force: bool) -> dict:
        symbols = [s.upper() for s in symbols]
        symbols_synced: list[str] = []
        symbols_skipped: list[str] = []
        errors: list[str] = []
        events_created = 0
        events_updated = 0

        for symbol in symbols:
            if await self.repo.should_skip_symbol(symbol, force, settings.sync_ttl_seconds):
                symbols_skipped.append(symbol)
                continue

            normalized_events, provider_errors = await self.providers.fetch_all([symbol])
            created, updated = await self.repo.upsert_normalized_events(normalized_events)
            await self.repo.mark_symbol_synced(symbol)
            symbols_synced.append(symbol)
            events_created += created
            events_updated += updated
            errors.extend(provider_errors)

        await self.cache.invalidate_events_cache()
        return {
            "status": "completed",
            "symbols_synced": symbols_synced,
            "symbols_skipped": symbols_skipped,
            "events_created": events_created,
            "events_updated": events_updated,
            "errors": errors,
        }
