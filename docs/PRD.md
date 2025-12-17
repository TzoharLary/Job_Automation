# Job Automation MVP — Product Requirements

## Goals
- Automate discovery, extraction, classification, and routing of jobs from multiple career sites into a consistent pipeline.
- Provide a minimal local UI to launch runs, monitor progress in real time (SSE), and view passed jobs.
- Support outbound delivery to Base44 via a configurable client with mock mode for local verification.

## Non-goals
- Training or fine-tuning NLP models (inference only).
- Handling authentication-required job boards in MVP (assume public listings).
- Complex scheduling; MVP is user-triggered runs only.
- Full ATS-specific deep integrations beyond discovery + fetch (no apply automation).

## MVP Scope
- Accept multiple career site URLs from UI.
- Discover job links, fetch full job pages (JS-rendered with Playwright), extract text, classify with a configurable Hugging Face model, filter by user criteria, persist passed jobs to SQLite, and send passed jobs via Base44 client in mock mode.
- Real-time progress via SSE: lifecycle events for start, discovery, fetch, classify, filter, store, send, error, complete, cancel.
- Local configuration for NLP model, Base44 endpoint/mock flag, DB path, timeouts, and per-site rate limits.

## Post-MVP Scope (not in MVP)
- Authenticated boards and captcha solving.
- Advanced scheduling, recurrence, and run history export.
- Multi-tenant separation and RBAC.
- Cloud deployment artifacts and autoscaling.
- Analytics dashboards and alerting.

## Functional Requirements
- Start a run with: list of site URLs, filter config (keywords include/exclude, locations, min seniority), NLP model name, Base44 endpoint + mock flag, rate limit/concurrency settings.
- Discover job detail URLs from provided sites using site adapters (common ATS patterns) with generic fallback.
- Fetch job pages with Playwright (JS-capable), handle redirects, and capture HTML/text.
- Extract and clean job text (remove nav/chrome, normalize whitespace, keep sections like responsibilities/requirements).
- Classify jobs using a Transformers pipeline (configurable model); store score + label.
- Apply filtering rules; only passed jobs persist to DB and outbound client.
- Persist runs, jobs, progress events, and outbound attempts in SQLite.
- Send passed jobs to Base44 via client interface; mock mode logs payloads instead of network calls.
- UI shows real-time progress (SSE) and the list of passed jobs; allow stop/cancel.

## Non-functional Requirements
- Python 3.11+, FastAPI backend, Playwright async, SQLite/SQLModel, SSE for realtime.
- Runs are **resume-safe**: a canceled run can restart and skip already-sent jobs for the same run id.
- Robustness: per-site isolation; retries with backoff for network/selector errors; failures do not abort the whole run unless fatal.
- Performance: default conservative concurrency (e.g., 2–4 workers) with per-site rate limiting; ability to adjust via config.
- Observability: structured logs with run_id/job_id; progress events every significant stage plus heartbeat.
- Operates fully offline except for job sites and optional Base44 endpoint.

## Acceptance Criteria (locally verifiable)
- User can input at least two site URLs, start a run, see live progress events over SSE, and stop the run.
- For at least one public site, system discovers job links, fetches pages, extracts text, classifies, filters, and stores passed jobs in SQLite.
- Passed jobs are delivered through Base44 client in mock mode with payloads logged; toggleable via config.
- Data persisted: runs, jobs, progress events, outbound attempts; uniqueness enforced per job URL per run.
- Runbook instructions allow setup and execution from a clean machine.

## MVP Milestone Definition
- All acceptance criteria satisfied using mock Base44 mode.
- UI supports start/stop, shows progress counters and passed jobs list.
- Core pipeline (discover → fetch → extract → classify → filter → store → send) operational with retries and rate limits.
- Tests cover parsing/extraction helpers, classifier wrapper, filter logic, Base44 mock client, and SSE event stream contract.
