# API Contracts

## Base44Client Interface
- `send_job(job: CanonicalJob) -> SendResult`: sends a single job.
- `send_batch(jobs: List[CanonicalJob]) -> List[SendResult]` (optional, default single calls).
- `close()`: clean up resources.

### Config
- `endpoint` (URL, required for real mode)
- `api_key` (optional placeholder; not required in mock)
- `mock` (bool; when true, no network calls)
- `timeout_seconds` (default 15s)
- `retry` (max_attempts, backoff initial/limit)

### SendResult DTO
- `job_id`
- `status` (success | failed | mocked)
- `response_code` (int, nullable)
- `response_body` (string, truncated)
- `error` (string, nullable)
- `attempted_at` (timestamp)

### Mapping Canonical Job → Outbound Payload
- `id`: job.id
- `run_id`: run_id
- `title`, `company`, `location`, `department`
- `description`: cleaned text
- `sections`: structured sections if present
- `source_url`
- `classification`: { label, score }
- `filter_reasons`
- `sent_at` (if available)

### Retry and Error Handling
- Use exponential backoff (e.g., 1s, 3s, 7s) up to `max_attempts` (default 3).
- Retry on network timeouts/5xx; do not retry on 4xx except 429 (respect Retry-After if present).
- Log payload id, attempt number, and result. Persist attempt records.
- Mark as `failed` after max attempts; do not block rest of pipeline.

### Mock Mode
- When `mock=true`, skip HTTP; log payload to structured logger and persist attempt with status `mocked`.
- Toggle via config/env and via run request; default to mock in MVP.

## Backend → UI APIs (HTTP)
- `POST /runs`: start run with body `{ urls: [...], filter_config, nlp_config, base44_config, rate_limit_config }`; returns `{ run_id }`.
- `POST /runs/{run_id}/cancel`: request cancellation.
- `GET /runs/{run_id}/sse`: SSE stream of progress events.
- `GET /runs/{run_id}/jobs`: paginated list of stored jobs (query params for filters).
- `GET /health`: health check.

## Internal Service Contracts
- **RunService**: `start(run_request) -> run_id`, `cancel(run_id)`, `resume(run_id)`.
- **Scraper**: `discover(urls) -> AsyncIterator[DiscoveredJob]`, `fetch(detail_url) -> PageContent`.
- **Extractor**: `extract(html) -> CleanText`.
- **Classifier**: `classify(text, meta) -> LabelScore`.
- **FilterEngine**: `evaluate(job, classification) -> FilterDecision`.
- **Repository**: CRUD for runs, jobs, progress, outbound attempts.
- **EventPublisher**: `publish(event)` used by services; SSE subscribes.
