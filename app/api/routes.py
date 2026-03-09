from __future__ import annotations

import json
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.events import EventRepository
from app.schemas.events import EventListResponse, EventOut, HealthResponse, SyncRequest, SyncResponse
from app.services.cache import CacheService
from app.services.sync import SyncService

router = APIRouter(prefix="/api/v1")


@router.get("/events", response_model=EventListResponse)
async def list_events(
    response: Response,
    symbols: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    parsed_symbols = [s.strip().upper() for s in symbols.split(",")] if symbols else None
    cache = CacheService()
    cache_key = f"events:{json.dumps({'symbols': parsed_symbols, 'event_type': event_type, 'from_date': str(from_date), 'to_date': str(to_date), 'limit': limit, 'offset': offset}, sort_keys=True)}"
    cached = await cache.get_json(cache_key)
    if cached:
        response.headers["X-Cache"] = "HIT"
        return cached

    repo = EventRepository(db)
    rows, total = await repo.list_events(parsed_symbols, event_type, from_date, to_date, limit, offset)
    payload = EventListResponse(
        data=[EventOut.model_validate(row, from_attributes=True) for row in rows],
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit) < total,
    )
    await cache.set_json(cache_key, payload.model_dump(mode="json"))
    response.headers["X-Cache"] = "MISS"
    return payload


@router.get("/events/{event_id}", response_model=EventOut)
async def get_event(event_id: str, db: AsyncSession = Depends(get_db)):
    repo = EventRepository(db)
    event = await repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventOut.model_validate(event, from_attributes=True)


@router.post("/events/sync", response_model=SyncResponse)
async def sync_events(payload: SyncRequest, db: AsyncSession = Depends(get_db)):
    service = SyncService(db)
    result = await service.sync(payload.symbols, payload.force)
    return SyncResponse(**result)


@router.get("/health", response_model=HealthResponse)
async def health(db: AsyncSession = Depends(get_db)):
    db_status = "ok"
    redis_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    cache = CacheService()
    if not await cache.ping():
        redis_status = "error"

    status = "ok" if db_status == "ok" and redis_status == "ok" else "degraded"
    return HealthResponse(status=status, database=db_status, redis=redis_status)
