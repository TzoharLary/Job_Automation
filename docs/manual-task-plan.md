# Manual Task Plan (No Taskmaster)

## Scope
Plan derived from PRD for Job Automation MVP. Contains tasks, dependencies, DoD, files, and tests. Use as working checklist.

## Tasks

1. **Project Skeleton & Tooling**
   - **Depends on:** none
   - **DoD:** repo tree exists; Python env files; requirements/pyproject include FastAPI, Uvicorn, Playwright, SQLModel/SQLAlchemy, Transformers, BeautifulSoup/lxml, pytest; `.env.example` with DB path, Base44 URL/mock flag, NLP model name, rate limits; README bootstrap section.
   - **Files:** `requirements.txt` or `pyproject.toml`, `.env.example`, `README.md`, optional `scripts/` runner.
   - **Tests:** none (infra only).

2. **Configuration Module**
   - **Depends on:** 1
   - **DoD:** central config reading env with defaults; exposes DB path, Base44 endpoint + mock, NLP model name, concurrency/rate limits, timeouts; documented in README/runbook.
   - **Files:** `src/app/config.py`.
   - **Tests:** unit tests for env/defaults.

3. **Data Model & DB**
   - **Depends on:** 1,2
   - **DoD:** SQLModel/SQLAlchemy models for Run, Job, ProgressEvent, OutboundAttempt; engine init; uniqueness job URL per run; timestamps; run status; documented in `docs/data-model.md`.
   - **Files:** `src/db/models.py`, `src/db/session.py`, `src/db/repository.py`, `scripts/db_init.py`.
   - **Tests:** in-memory SQLite: creation, uniqueness, progress events persistence.

4. **Events & SSE Contract**
   - **Depends on:** 2,3
   - **DoD:** event schema (start/progress/error/done/heartbeat) + publisher; SSE endpoint in FastAPI; heartbeat; documented in `docs/api-contracts.md`.
   - **Files:** `src/events/schema.py`, `src/events/publisher.py`, `src/app/routers/events.py`.
   - **Tests:** unit for event shapes; integration SSE stream format.

5. **Scraping Runner (Playwright)**
   - **Depends on:** 2,3
   - **DoD:** async runner with retries/backoff/timeouts; discovery(site_url)->list[urls]; fetch(url)->html; per-site rate limit; adapters + generic fallback; config-driven.
   - **Files:** `src/scraping/runner.py`, `src/scraping/discovery.py`, `src/scraping/fetch.py`, `src/scraping/adapters/*.py`.
   - **Tests:** unit with mocks for Playwright; retry/timeout logic.

6. **Extraction & Cleaning**
   - **Depends on:** 5
   - **DoD:** extract(html)->{title,text,sections}; remove chrome/nav; normalize whitespace; keep key sections; documented in architecture.
   - **Files:** `src/extraction/extractor.py`.
   - **Tests:** unit on sample HTML fixtures.

7. **NLP Classification**
   - **Depends on:** 2,6
   - **DoD:** wrapper around Transformers pipeline; model name configurable; CPU friendly; returns label+score; handles load errors/timeouts.
   - **Files:** `src/nlp/classifier.py`.
   - **Tests:** unit with mocked pipeline; fallback when model missing.

8. **Filtering Engine**
   - **Depends on:** 2,6,7
   - **DoD:** rules for include/exclude keywords, locations, min seniority; returns pass/fail+reason; documented in data-model.
   - **Files:** `src/filtering/engine.py`, `src/filtering/schema.py`.
   - **Tests:** unit for each rule and combinations.

9. **Base44 Client (HTTP + Mock)**
   - **Depends on:** 2,3
   - **DoD:** interface + HTTP impl + mock; config for URL/timeout/headers; mock logs payload; retries/backoff; documented in api-contracts.
   - **Files:** `src/outbound/base.py`, `src/outbound/http_client.py`, `src/outbound/mock_client.py`.
   - **Tests:** unit with mocks for HTTP; retry/error paths; mock logging.

10. **Pipeline & Run Orchestration**
    - **Depends on:** 3,4,5,6,7,8,9
    - **DoD:** start_run/stop_run/status; emits events; persists run/job/progress/outbound; resume-safe (skip already-sent in same run); documented in architecture (run lifecycle).
    - **Files:** `src/app/service/run_manager.py`, `src/app/service/pipeline.py`.
    - **Tests:** integration with mocks (Playwright/NLP/Base44) for a tiny run; stop/resume behavior.

11. **FastAPI API Layer**
    - **Depends on:** 2,3,4,10
    - **DoD:** routes: start run (URLs, filters, model, rate limits, mock flag), stop run, status, SSE stream, passed jobs list; Pydantic schemas; validation; documented in api-contracts.
    - **Files:** `src/app/main.py`, `src/app/routers/runs.py`, `src/app/routers/jobs.py`.
    - **Tests:** integration via TestClient: start/stop/status, SSE handshake, validation errors.

12. **Minimal UI**
    - **Depends on:** 11
    - **DoD:** static HTML/JS/CSS served by FastAPI; form for URLs/filters/model/mock flag; start/stop buttons; SSE listener updating counters + passed jobs list.
    - **Files:** `src/ui/index.html`, `src/ui/app.js`, `src/ui/style.css` (served via StaticFiles).
    - **Tests:** smoke/integration manual; optional JS unit for SSE listener with mock source.

13. **Tests & Automation**
    - **Depends on:** 3–12
    - **DoD:** pytest configured; suites for db, scraping (mocked), extraction, nlp (mocked), filtering, outbound (mock/mock), service/pipeline, api; documented run commands in runbook.
    - **Files:** `tests/` subpackages; `pytest.ini` or `pyproject` config.
    - **Tests:** this is the suite itself.

## Repository Layout (target)
- src/
  - app/ (FastAPI entrypoints, routers)
  - scraping/ (playwright runner, adapters, discovery, fetch)
  - extraction/ (html to text, sectioning)
  - nlp/ (model loading, inference)
  - filtering/ (rules engine)
  - db/ (models, repository layer)
  - outbound/ (Base44 client, mock)
  - ui/ (static assets)
  - events/ (SSE definitions/publisher)
- tests/
- docs/
- tasks/
- scripts/
- .env.example
- README.md

## Acceptance Targets (from PRD)
- UI start/stop run, live SSE, list of passed jobs.
- For at least one public site: discover → fetch → extract → classify → filter → store to SQLite.
- Passed jobs delivered via Base44 mock; payload logged.
- Persist runs, jobs, progress events, outbound attempts; uniqueness per job URL per run.
- Runbook allows clean-machine setup and execution.
