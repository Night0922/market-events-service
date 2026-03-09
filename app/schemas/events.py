from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EventOut(BaseModel):
    id: UUID
    symbol: str
    event_type: str
    event_date: date
    title: str
    details: dict
    created_at: datetime


class EventListResponse(BaseModel):
    data: list[EventOut]
    total: int
    limit: int
    offset: int
    has_more: bool


class SyncRequest(BaseModel):
    symbols: list[str] = Field(default_factory=list)
    force: bool = False


class SyncResponse(BaseModel):
    status: str
    symbols_synced: list[str]
    symbols_skipped: list[str]
    events_created: int
    events_updated: int
    errors: list[str]


class HealthResponse(BaseModel):
    status: str
    database: str
    redis: str
