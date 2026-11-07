<div align="center">

# API Monitor

### REST API for monitoring external HTTP services

Monitor endpoints, measure response times, and retain availability history.

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-pytest-0A9EDC?logo=pytest&logoColor=white)

</div>

## About

API Monitor is a backend portfolio project that provides a REST interface for registering external HTTP endpoints and manually checking their availability. Each check stores the HTTP status code (when a response exists), response time, availability result, error information, and timestamp.

## Features

- Monitor CRUD operations.
- Manual HTTP checks with configurable timeout.
- Distinguishes HTTP error responses (such as 404 and 500) from connection failures.
- Check history and latest status.
- Dashboard summary.
- PostgreSQL persistence with SQLAlchemy 2.0 and Alembic.
- Docker Compose environment.
- pytest suite and GitHub Actions CI.

## Technology

| Area | Tools |
|---|---|
| API | Python, FastAPI, Pydantic |
| HTTP client | HTTPX |
| Database | PostgreSQL, SQLAlchemy 2.0 |
| Migrations | Alembic |
| Tests | pytest, FastAPI TestClient |
| Delivery | Docker, Docker Compose, GitHub Actions |

## Getting started

### With Docker

1. Copy the environment template:

   ```bash
   cp .env.example .env
   ```

2. Start the application and database:

   ```bash
   docker compose up --build
   ```

3. Open the interactive API documentation at http://localhost:8000/docs.

The API container runs `alembic upgrade head` before starting Uvicorn.

### Local development

Create and activate a virtual environment, install dependencies, and configure `DATABASE_URL` in `.env` to point to a PostgreSQL database.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Run migrations and start the API:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

For local PostgreSQL, replace the Docker hostname `db` in `DATABASE_URL` with `localhost`.

## API endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/monitors` | Create a monitor |
| GET | `/monitors` | List monitors |
| GET | `/monitors/{id}` | Retrieve a monitor |
| PATCH | `/monitors/{id}` | Update a monitor |
| DELETE | `/monitors/{id}` | Delete a monitor |
| POST | `/monitors/{id}/check` | Run a manual check |
| GET | `/monitors/{id}/checks` | Retrieve check history |
| GET | `/monitors/{id}/status` | Retrieve latest status |
| GET | `/dashboard/summary` | Dashboard counters |
| GET | `/health` | API and database health |

## Example request

```bash
curl -X POST http://localhost:8000/monitors \
  -H "Content-Type: application/json" \
  -d '{"name":"Example","url":"https://example.com","check_interval":300}'
```

## Project structure

```text
app/
  api/routes/       # HTTP endpoints
  core/             # Application settings
  db/models/        # SQLAlchemy models
  repositories/     # Database access
  schemas/          # Pydantic request/response schemas
  services/         # Business logic and HTTP checks
migrations/         # Alembic migrations
tests/              # Automated tests
.github/workflows/  # CI pipeline
```

## Testing

```bash
pytest -q
```

Tests use an isolated in-memory SQLite database and mock external HTTP behavior; they do not require real external services.

## Security notes and limitations

- URL checks reject localhost and non-public IP destinations after DNS resolution. This is a baseline SSRF defense, not a complete production-grade egress security boundary: DNS rebinding and redirect policies require additional hardening.
- Redirects are disabled for checks to avoid following a target to an unvalidated destination.
- Response reading is bounded to reduce unnecessary body transfer.
- Automatic scheduling is not enabled in this initial release; `check_interval` is stored for a future scheduler implementation.
- The included dashboard summary is intentionally basic.

## Future improvements

- Add a hardened outbound request layer with DNS pinning / egress restrictions.
- Add background scheduling and bounded worker execution.
- Add rolling uptime and latency statistics.
- Add authentication, authorization, rate limiting, and operational metrics.
- Add integration tests against PostgreSQL.

## License

No license has been specified for this project.

<div align="center">

Built as a Backend Python portfolio project.

</div>
# api-monitor
