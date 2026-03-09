# Market Events Service

## Overview

Market Events Service is a FastAPI-based backend service that aggregates and normalizes market events from multiple external providers. The service stores events in PostgreSQL and uses Redis for caching to improve performance.

The system provides REST APIs to:

* Synchronize events from providers
* Query events with filters
* Retrieve a specific event by ID
* Check service health

## Tech Stack

* **Python 3.11+**
* **FastAPI**
* **PostgreSQL**
* **Redis**
* **Docker / Docker Compose**
* **SQLAlchemy (async)**
* **Poetry**

---

# Project Structure

```
market-events-service
│
├── app
│   ├── api
│   │   └── routes.py
│   ├── db
│   │   └── init_db.py
│   ├── services
│   │   ├── providers.py
│   │   ├── normalizers.py
│   │   └── sync.py
│   └── main.py
│
├── providers
│   ├── provider_a.py
│   └── provider_b.py
│
├── tests
│   └── test_example.py
│
├── docker-compose.yml
├── pyproject.toml
├── README.md
└── .env.example
```

---

# Setup Instructions

## 1. Clone Repository

```bash
git clone https://github.com/<your-username>/market-events-service.git
cd market-events-service
```

## 2. Create Environment File

Create a `.env` file:

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/postgres
REDIS_URL=redis://localhost:6379/0

PROVIDER_A_API_KEY=test-key
PROVIDER_B_API_KEY=test-key

SYNC_TTL_SECONDS=3600
CACHE_TTL_SECONDS=120
PROVIDER_DAYS_AHEAD=30
```

---

## 3. Start Infrastructure

Start PostgreSQL and Redis:

```bash
docker compose up -d
```

Verify containers:

```bash
docker ps
```

---

## 4. Install Dependencies

Install using Poetry:

```bash
$env:Path += ";$env:APPDATA\Python\Scripts;$env:USERPROFILE\AppData\Roaming\Python\Scripts"
poetry install
```

---

## 5. Run the Application

```bash
poetry run uvicorn app.main:app --reload --port 8000
```

Server will start at:

```
http://127.0.0.1:8000
```

---

# API Documentation

Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

# API Endpoints

## Health Check

```
GET /api/v1/health
```

Response:

```json
{
  "status": "ok"
}
```

---

## Sync Events

Fetch events from external providers and store them in the database.

```
POST /api/v1/events/sync
```

Example response:

```json
{
  "status": "synced"
}
```

---

## List Events

Retrieve events with optional filters.

```
GET /api/v1/events
```

Query parameters:

| Parameter  | Description                        |
| ---------- | ---------------------------------- |
| symbols    | Filter by symbol (comma separated) |
| event_type | Filter by event type               |
| from_date  | Start date                         |
| to_date    | End date                           |
| limit      | Pagination limit                   |
| offset     | Pagination offset                  |

Example:

```
GET /api/v1/events?symbols=AAPL,MSFT&limit=50
```

---

## Get Event by ID

```
GET /api/v1/events/{event_id}
```

Example:

```
GET /api/v1/events/123
```

---

# Testing

Run tests:

```bash
pytest
```

---

# Database

PostgreSQL stores:

* events
* sync states

Check tables:

```bash
docker exec -it market-events-service-db-1 psql -U postgres -d postgres
```

Then run:

```sql
\dt
SELECT * FROM events;
```

---

# Caching

Redis is used to cache responses for the events list endpoint to reduce repeated database queries.

Cache header example:

```
X-Cache: HIT
X-Cache: MISS
```

---

# Development Notes

* Events from providers are normalized before storage.
* Duplicate events are removed during synchronization.
* Redis caching improves performance for repeated event queries.

---

# Author

Technical assessment implementation for Market Events Service.
