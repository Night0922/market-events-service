import json
from typing import Any

import redis.asyncio as redis

from app.core.config import settings


class CacheService:
    def __init__(self) -> None:
        self.client = redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)

    async def get_json(self, key: str) -> Any | None:
        value = await self.client.get(key)
        return json.loads(value) if value else None

    async def set_json(self, key: str, value: Any, ttl: int | None = None) -> None:
        await self.client.set(key, json.dumps(value, default=str), ex=ttl or settings.cache_ttl_seconds)

    async def ping(self) -> bool:
        try:
            await self.client.ping()
            return True
        except Exception:
            return False

    async def invalidate_events_cache(self) -> None:
        cursor = 0
        while True:
            cursor, keys = await self.client.scan(cursor=cursor, match="events:*")
            if keys:
                await self.client.delete(*keys)
            if cursor == 0:
                break
