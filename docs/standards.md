# Engineering Standards and Patterns

This document captures concise patterns to guide the Job Automation MVP. Sources include Awesome Copilot guidance (Playwright Python, Quarkus SSE) plus industry-standard FastAPI/SQLite practices.

## FastAPI layout for long-running jobs
- Use an **application package** (`src/app`) with routers separated by concern: `runs`, `jobs`, `health`, `ui`.
- Keep **background orchestration** isolated in a service module (e.g., `src/app/services/run_service.py`) that coordinates scraping pipeline, not the routers.
- Provide an **async runner** entrypoint that accepts a Run config (URLs, filters, NLP model, Base44 mode) and streams events via an injected publisher.
- Model **dependency wiring** in a `container.py` or `dependencies.py` to construct repositories (DB), clients (Base44), and the Playwright runner.
- Expose **Server-Sent Events (SSE)** endpoints via lightweight routers that call the event publisher; avoid blocking calls in route handlers—hand off to the orchestrator and return immediately.
- Configuration: use `pydantic-settings` for env-backed configs (DB path, NLP model name, Base44 endpoint, mock flag, concurrency limits).

## Playwright scraping reliability (Python)
- Favor **role-based locators** (`get_by_role`, `get_by_label`, `get_by_text`) for resilience (from Playwright Python guidance).
- Rely on **web-first assertions** with auto-retry; avoid hard sleeps. Use `expect(page).to_have_url(...)` / `expect(locator).to_have_text(...)`.
- Centralize **timeouts and retries**: small default timeout (e.g., 15–30s) with per-action overrides for slow pages; wrap navigation with retry/backoff.
- Use an **async browser pool** to avoid re-creating contexts per URL; per-run context to share cookies but isolate per-site if blocking/rate-limited.
- Implement **rate limiting** and polite delays between requests per domain; serialize per-domain if CAPTCHAs or bot checks appear.
- On failures, **capture diagnostics** (status, URL, HTML snapshot truncated) for logging and later review; classify errors (network, selector, blocked) to decide retry/skip.
- Prefer **stealthy navigation**: set user agent, viewport, and minimal script execution; handle cookie banners via simple accept/dismiss helpers.

## SSE progress streaming patterns
- Keep SSE endpoint lightweight: **immediately return a stream** that subscribes to an event bus; do not perform long work in the request handler.
- Emit structured events (`event: progress`, `data: JSON`) with small payloads; include `run_id`, `phase`, `counts`, `current_url`, and `error` fields.
- Send **heartbeat/keep-alive** comments every 10–15s to prevent idle disconnects; close stream on run completion or cancellation.
- Use **backpressure-friendly** buffering (small queue with drop-old or block strategy) so slow clients don't exhaust memory.
- Encode events as **JSON lines**; clients should handle reconnection and `Last-Event-ID` if supported.

## SQLite schema and migration approach
- Use **SQLModel/SQLAlchemy** models under `src/db/models.py` with explicit indexes for URL uniqueness and run/job lookup.
- Maintain a **schema version** via Alembic or lightweight migration scripts; even for SQLite, track migrations in `migrations/` to avoid ad-hoc DDL.
- Keep **foreign keys** enabled (`PRAGMA foreign_keys=ON`) and use **cascades** for run → progress/job rows.
- For text-heavy fields (job descriptions), store as `TEXT`; avoid huge blobs. Add **created_at/updated_at** timestamps.
- Use **connection pooling settings** tuned for SQLite (check_same_thread=False for async contexts via aiosqlite/SQLAlchemy 2.0 async engine) and keep the DB file path configurable.

## General operational guardrails
- **Isolation per site**: retries and failure counts should not halt the entire run; skip after max attempts.
- **Configurable concurrency**: cap workers to protect target sites and the local machine; expose via config/UI.
- **Observability**: structured logs with run_id/job_id and phase; log outbound Base44 payloads in mock mode.
- **Testability**: inject Playwright runner, NLP classifier, and Base44 client behind interfaces to enable local mocks during tests.
