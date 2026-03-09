from __future__ import annotations

import asyncio

from providers.provider_a import ProviderA, ProviderAError
from providers.provider_b import ProviderB, ProviderBError

from app.core.config import settings
from app.services.normalizers import normalize_provider_a, normalize_provider_b


class ProviderService:
    async def fetch_provider_a(self, symbols: list[str]) -> tuple[list[dict], list[str]]:
        try:
            async with ProviderA(api_key=settings.provider_a_api_key) as provider:
                result = await provider.fetch_events(symbols, days_ahead=settings.provider_days_ahead)
            return [normalize_provider_a(item) for item in result], []
        except ProviderAError as exc:
            return [], [f"provider_a: {exc}"]

    async def fetch_provider_b(self, symbols: list[str]) -> tuple[list[dict], list[str]]:
        events: list[dict] = []
        errors: list[str] = []
        try:
            async with ProviderB(api_key=settings.provider_b_api_key) as provider:
                cursor = None
                seen_cursors: set[str | None] = set()
                while True:
                    result = await provider.fetch_events(
                        symbols,
                        days_ahead=settings.provider_days_ahead,
                        cursor=cursor,
                    )
                    events.extend(normalize_provider_b(item) for item in result["events"])
                    pagination = result["pagination"]
                    next_cursor = pagination["next_cursor"]
                    if not pagination["has_next"] or next_cursor in seen_cursors:
                        break
                    seen_cursors.add(next_cursor)
                    cursor = next_cursor
        except ProviderBError as exc:
            errors.append(f"provider_b: {exc}")
        return events, errors

    async def fetch_all(self, symbols: list[str]) -> tuple[list[dict], list[str]]:
        results = await asyncio.gather(
            self.fetch_provider_a(symbols),
            self.fetch_provider_b(symbols),
        )
        combined: list[dict] = []
        errors: list[str] = []
        for events, errs in results:
            combined.extend(events)
            errors.extend(errs)
        return combined, errors
