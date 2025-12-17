# Architecture

## Component Boundaries
- **FastAPI app (`src/app`)**: routers for runs, SSE events, health, UI assets. Delegates to services.
- **Orchestrator (`src/app/services/run_service.py`)**: coordinates run lifecycle, manages state, and dispatches progress events.
- **Scraping (`src/scraping`)**: Playwright async runner, site discovery, fetcher, and ATS adapters.
- **Extraction (`src/extraction`)**: HTML → clean text/sections, boilerplate removal.
- **NLP (`src/nlp`)**: model loader + classifier wrapper (Transformers pipeline, configurable model).
- **Filtering (`src/filtering`)**: rule engine applying include/exclude keywords, locations, seniority, score thresholds.
- **DB (`src/db`)**: SQLModel/SQLAlchemy models, repositories, migrations.
- **Events (`src/events`)**: event definitions and publisher for SSE (fan-out to subscribers).
- **Outbound (`src/outbound`)**: Base44 client interface + HTTP and mock implementations.
- **UI (`src/ui`)**: static HTML/JS consuming SSE and calling APIs.

## Run Lifecycle
1. **Start**: UI posts run request with URLs, filters, NLP model, Base44 config, concurrency/rate limits. Orchestrator creates run record and emits `run_started`.
2. **Progress**: pipeline stages per job: discovery → fetch → extract → classify → filter → store → send. Each stage emits progress events with counters and current URL.
3. **Stop/Cancel**: UI triggers cancel; orchestrator signals workers to stop after in-flight steps, emits `run_cancelled`.
4. **Resume**: rerun with same run_id reuses persisted state, skips already completed/sent jobs; idempotent outbound enforced by unique constraints on (run_id, job_url) and outbound attempts.
5. **Complete**: after queue drain, emits `run_completed` and final summary.

## Event Model (SSE)
- Event types: `run_started`, `discovery_progress`, `fetch_progress`, `classify_progress`, `filter_progress`, `store_progress`, `send_progress`, `heartbeat`, `run_cancelled`, `run_completed`, `error`.
- Payload fields: `run_id`, `phase`, `counts` (found/fetched/classified/filtered/stored/sent), `current_url`, `message`, `error` (type, detail), `timestamp`.
- Heartbeat: comment every 10–15s to keep connections alive.

## Scraper Strategy
- **Adapters** for common ATS (e.g., Greenhouse, Lever, Workday, Ashby) under `src/scraping/adapters/` with URL pattern detection and DOM selectors.
- **Generic fallback**: scan for job listing links (semantic anchors, schema.org JobPosting) and follow detail pages.
- **Discovery isolation**: per-domain rate limiting and retries; failure on one site does not halt others.
- **Fetch**: Playwright page navigation with retries/backoff, user-agent setting, cookie banner helper, response status capture, and HTML snapshot for diagnostics.

## Error and Retry Policy
- Classification: retry once on model load/inference errors, otherwise mark job failed.
- Network/selector errors: exponential backoff (e.g., 1s, 3s, 7s) with max attempts (3–5) per URL; mark skipped after limit.
- Per-site isolation: maintain separate queues so one site's failures do not block others.
- Log structured errors with `run_id`, `site`, `url`, `stage`, `error_type`.

## Rate Limiting and Concurrency
- Global worker pool size configurable; per-domain concurrency defaults to 1–2 to avoid blocking.
- Throttle delay between requests per domain (configurable); obey robots.txt if present.
- Backpressure: bounded queues; if full, pause new discovery until downstream clears.

## Interfaces
- **PlaywrightRunner**: start/stop browser context, fetch URL → HTML/metadata, return diagnostics.
- **Extractor**: HTML → cleaned text + sections.
- **Classifier**: text → label + score using configured model.
- **FilterEngine**: label/score + job metadata → pass/fail + reasons.
- **Base44Client**: send job payload; supports mock.
- **EventPublisher**: async publish(event) → SSE stream subscribers.

## Deployment/Runtime
- Local-only by default; single FastAPI process with async tasks.
- Config via environment variables and `.env` for defaults; no external services required beyond target sites.
