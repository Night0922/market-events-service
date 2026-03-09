from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event, SyncState


class EventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, event_id: str):
        return await self.session.get(Event, event_id)

    def _filters(
        self,
        stmt: Select,
        symbols: list[str] | None,
        event_type: str | None,
        from_date: date | None,
        to_date: date | None,
    ) -> Select:
        if symbols:
            stmt = stmt.where(Event.symbol.in_([s.upper() for s in symbols]))
        if event_type:
            stmt = stmt.where(Event.event_type == event_type)
        if from_date:
            stmt = stmt.where(Event.event_date >= from_date)
        if to_date:
            stmt = stmt.where(Event.event_date <= to_date)
        return stmt

    async def list_events(self, symbols, event_type, from_date, to_date, limit, offset):
        stmt = self._filters(select(Event), symbols, event_type, from_date, to_date)
        count_stmt = self._filters(select(func.count()).select_from(Event), symbols, event_type, from_date, to_date)

        stmt = stmt.order_by(Event.event_date.asc(), Event.symbol.asc()).offset(offset).limit(limit)
        total = await self.session.scalar(count_stmt)
        rows = (await self.session.scalars(stmt)).all()
        return rows, int(total or 0)

    async def upsert_normalized_events(self, normalized_events: list[dict]) -> tuple[int, int]:
        created = 0
        updated = 0

        for item in normalized_events:
            existing = await self.session.scalar(
                select(Event).where(Event.dedupe_key == item["dedupe_key"])
            )
            provider_entry = {
                "provider": item["provider_name"],
                "provider_event_id": item["provider_event_id"],
            }
            if existing:
                merged_sources = existing.provider_sources or []
                if provider_entry not in merged_sources:
                    merged_sources.append(provider_entry)
                existing.provider_sources = merged_sources
                existing.details = item["details"] or existing.details
                existing.source_payload = item["source_payload"]
                updated += 1
            else:
                self.session.add(
                    Event(
                        symbol=item["symbol"],
                        event_type=item["event_type"],
                        event_date=date.fromisoformat(item["event_date"]),
                        title=item["title"],
                        details=item["details"],
                        source_payload=item["source_payload"],
                        provider_sources=[provider_entry],
                        dedupe_key=item["dedupe_key"],
                    )
                )
                created += 1
        await self.session.commit()
        return created, updated

    async def should_skip_symbol(self, symbol: str, force: bool, ttl_seconds: int) -> bool:
        if force:
            return False
        state = await self.session.get(SyncState, symbol.upper())
        if not state:
            return False
        return state.last_synced_at >= datetime.now(timezone.utc) - timedelta(seconds=ttl_seconds)

    async def mark_symbol_synced(self, symbol: str) -> None:
        state = await self.session.get(SyncState, symbol.upper())
        now = datetime.now(timezone.utc)
        if state:
            state.last_synced_at = now
        else:
            self.session.add(SyncState(symbol=symbol.upper(), last_synced_at=now))
        await self.session.commit()
