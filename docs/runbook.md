# Runbook

## Local Setup
1. Ensure Python 3.11+.
2. Install system deps for Playwright (Node not required for Python binding but browsers must be installed via Playwright script later).
3. Clone repo and create virtualenv.
4. Install Python deps once added (will include FastAPI, SQLModel, Playwright, transformers, httpx, uvicorn).
5. Install Playwright browsers: `python -m playwright install chromium` (documented command will be provided when deps are added).
6. Copy `.env.example` to `.env` and adjust settings (DB path, Base44 endpoint, mock flag, NLP model name, concurrency limits).

## Running Backend and UI
- Start FastAPI app (uvicorn) once implemented. UI is served as static assets under `/ui` and consumes the same backend.
- Access UI at `http://localhost:8000/` (expected default once implemented).

## Running Tests
- Use `pytest` after dependencies are in place. Include unit tests for extractor, classifier wrapper, filter logic, Base44 mock client, and SSE stream contract.

## Configuration Reference
- **URLs**: Provided via UI form (sent to `/runs`).
- **Filtering**: include/exclude keywords, locations, seniority, min score provided in run request; defaults may live in env.
- **NLP model**: set default model name via env (e.g., `HF_MODEL=textattack/distilbert-base-uncased-roberta` placeholder).
- **DB**: SQLite path via env; enable foreign keys. Migrations via Alembic in `migrations/`.
- **Base44 client**: endpoint + mock flag in env; mock flag should default true for local.
- **Rate limits**: env for global workers and per-site delay/backoff.

## Troubleshooting
- **Playwright timeouts**: lower concurrency, increase navigation timeout, capture HTML snapshot for debugging.
- **SSE disconnects**: check server logs for heartbeat and client reconnect backoff; ensure keep-alives not blocked by proxy.
- **DB locking**: ensure single writer; adjust `check_same_thread=False` for async SQLite; reduce concurrency if locks appear.
- **NLP model load slow**: warm up on startup; pin to a small CPU-friendly model.
- **Outbound failures**: in mock mode, payloads should log; if real mode, inspect response codes and backoff settings.
