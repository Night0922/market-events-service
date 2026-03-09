# Market Events Service

FastAPI service that aggregates market events from two external providers, normalizes them into a single schema, stores them in PostgreSQL with deduplication, caches list responses in Redis, and exposes a REST API.

## Architecture

- **FastAPI** for API endpoints.
- **SQLAlchemy async + PostgreSQL** for persistence.
- **Redis** for `GET /api/v1/events` caching.
- **Provider adapters** normalize both simulated providers into one internal shape.
- **Deduplication** uses a deterministic key: `symbol + event_type + event_date + normalized title`.
- **Sync throttling** uses `sync_states` and skips symbols synced in the last hour unless `force=true`.

## Assumptions

- Provider overlap is deduplicated by business key, not provider ID.
- When the same event appears from both providers, the record is updated and both provider references are retained.
- Provider B pagination can get stuck, so duplicate cursors are guarded against.
- Economic events are supported because Provider B returns them and the API spec includes them.

## Run

```bash
docker-compose up -d
cp .env.example .env
poetry install
poetry run uvicorn app.main:app --reload --port 8000
```

## API

### List events

```bash
curl "http://localhost:8000/api/v1/events?symbols=AAPL,MSFT&event_type=earnings&limit=20&offset=0"
```

### Sync events

```bash
curl -X POST "http://localhost:8000/api/v1/events/sync" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "MSFT"], "force": false}'
```

### Health

```bash
curl "http://localhost:8000/api/v1/health"
```

## Tests

```bash
poetry run pytest
```

## Project structure

```text
app/
  api/routes.py
  core/config.py
  db/
  models/
  repositories/
  schemas/
  services/
providers/
  provider_a.py
  provider_b.py
tests/
```
