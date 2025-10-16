# Coffee Tracker API — Copilot Instructions

This repository implements a FastAPI-based API for tracking caffeine intake and heart rate, with analytics and Prometheus metrics. The goal is to log, validate, and correlate coffee consumption and heart rate data, enforcing rigorous input standards and playful honesty.

## Project Purpose

- Log coffee consumption (validated mg, 0–1000)
- Track heart rate readings (validated BPM, 30–250)
- Analyze correlations between caffeine and heart rate
- Provide Prometheus-compatible metrics
- Secure, documented, and rate-limited endpoints (see details below)
- API is consumable via Apple Shortcuts (think: mobile automations)

## API Design & Endpoints

- Endpoints follow REST conventions, with `/coffee/` and `/heartrate/` resources.
- Return JSON with clear, descriptive fields (see below for examples).
- Provide `/stats`, `/today`, `/week`, and correlation endpoints for analytics.
- Expose `/docs` (Swagger UI), `/redoc`, and `/info` endpoints for documentation.
- All input endpoints require Bearer token authentication (API key from `.env`).
- Health endpoints are public.

## Input Validation

- **Caffeine**: Accept 0–1000mg (`caffeine_mg`). Over 1000mg is invalid.
- **Heart Rate**: Accept 30–250 BPM (`bpm`). Values outside range are rejected.
- **Text Fields**: Reasonable max lengths: `coffee_type` (100), `notes` (1000), `context` (50).
- **Timezone**: All timestamps are ISO8601 and timezone-aware.
- Invalid data is rejected with descriptive error messages.

## Rate Limiting
- General endpoints: 30 req/min
- Health: 60 req/min
- Data logging endpoints: higher limits (e.g., 100/hour for coffee)
- Persistent via Redis (containerized)

## Analytics & Correlation

- Compute mean/median/std for caffeine and heart rate.
- Analyze baseline heart rate before vs. after caffeine.
- Configurable time windows for correlation (e.g., `?hours_after=3`).
- Automated health assessments via API.

## Security

- **API Key** required for private endpoints (except `/`, `/health`)
- **CORS** origins controlled via ENV
- **Trusted Hosts**: ENV-controlled, blocks host header attacks
- **Request Logging**: Logs all usage and errors

## Database

- Main: PostgreSQL (Docker, persistent via `pg_data` Docker volume)
- Dev/Fallback: SQLite
- See models: `coffee_logs` and `heart_rate_logs` tables, with timestamps, validated fields, and suggested indexes.
- Backups: Use `pg_dump` or `make backup`

## Tech & Directory

- Python 3.11+, FastAPI, PostgreSQL, Docker Compose, Redis for rate limits, Prometheus for metrics
- Structure:
  - `/app`: FastAPI main code
  - `/tests`: Tests (unit/integration)
  - `/metrics`: Prometheus metrics
  - `/docker-compose.yml`, `.env.example` for config

## Coding Conventions

- Use type hints on all functions
- Snake_case for code and REST endpoints
- Write pytest unit tests for new features and endpoints
- Docstrings for models, routes, and utility functions

## Example Requests & Payloads

**Log Coffee:**

```bash
curl -H "Authorization: Bearer $API_KEY" -X POST https://coffee.danilocloud.me/api/v1/coffee/
-d '{"caffeine_mg": 120, "coffee_type": "americano", "notes": "late night hustle"}'
```

**Log Heart Rate:**

```bash
curl -H "Authorization: Bearer $API_KEY" -X POST https://coffee.danilocloud.me/api/v1/heartrate/
-d '{"bpm": 88, "context": "post-coffee", "notes": "wired"}'
```bash
curl -H "Authorization: Bearer $API_KEY" -X POST https://coffee.danilocloud.me/api/v1/heartrate/
-d '{"bpm": 88, "context": "post-coffee", "notes": "wired"}'
```


**Sample Response (Coffee Today):**
```json
{
"date": "2025-07-23",
"total_caffeine_mg": 285.0,
"addiction_level": "moderate addict",
"recommended_max": 400,
"over_limit": false
}

```


## Prometheus Metrics

- Expose relevant metrics at `/metrics`
- Example: `coffee_total_caffeine_mg`, `heartrate_latest_bpm`

## Dev & Deployment

- Use Docker Compose for all services
- Add and edit ENV in `.env`
- Use `make up`, `make down`, `make logs`, `make test`, `make backup` for standard tasks

## References

Swagger: `/api/v1/docs`  
ReDoc: `/api/v1/redoc`  
Telemetry: `/api/v1/metrics`  
Info: `/api/v1/info`

---

Keep these rules in sync with README and codebase as features evolve. All code suggestions should respect these requirements and focus on reliability, observability, and input validation for health data.
