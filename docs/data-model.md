# Data Model

## Canonical Job Schema (SQLModel)
- `id` (UUID/ULID)
- `run_id` (FK → runs.id, cascade)
- `source_url` (TEXT, indexed, unique with run_id)
- `title` (TEXT)
- `company` (TEXT, nullable)
- `location` (TEXT, nullable)
- `department` (TEXT, nullable)
- `description` (TEXT)
- `sections` (JSON: responsibilities, requirements, benefits, etc.)
- `raw_html` (optional TEXT, truncated or hashed)
- `classification_label` (TEXT)
- `classification_score` (REAL)
- `filter_decision` (ENUM pass/fail)
- `filter_reasons` (JSON array)
- `sent_to_base44` (BOOL)
- `sent_at` (DATETIME, nullable)
- `created_at` / `updated_at` (DATETIME)

## Run Schema
- `id` (UUID/ULID)
- `started_at` / `completed_at` / `cancelled_at`
- `status` (enum: pending, running, cancelled, completed, failed)
- `input_urls` (JSON array)
- `filter_config` (JSON)
- `nlp_config` (JSON)
- `base44_config` (JSON: endpoint, api_key placeholder, mock flag)
- `rate_limit_config` (JSON)
- `stats` (JSON counters: discovered, fetched, classified, filtered, stored, sent, errors)

## Progress Event Schema
- `id` (UUID/ULID)
- `run_id` (FK)
- `event_type` (enum: run_started, discovery_progress, fetch_progress, classify_progress, filter_progress, store_progress, send_progress, heartbeat, run_cancelled, run_completed, error)
- `payload` (JSON: counts, current_url, message, error detail)
- `created_at` (DATETIME)

## Filtering Config Schema
- `include_keywords` (array[str])
- `exclude_keywords` (array[str])
- `locations` (array[str])
- `seniority_levels` (array[str])
- `min_score` (float)
- `max_results` (int, optional)

## NLP Config Schema
- `model_name` (string, default Hugging Face model id)
- `task` (string, e.g., text-classification)
- `device` (cpu default)
- `batch_size` (int, optional)
- `max_length` (int, optional truncation)
- `thresholds` (JSON: label → min score)

## Outbound Attempt Schema
- `id` (UUID/ULID)
- `run_id` (FK)
- `job_id` (FK)
- `status` (enum: pending, success, failed, skipped, mocked)
- `response_code` (int, nullable)
- `response_body` (TEXT, nullable/truncated)
- `attempted_at` (DATETIME)
- `error` (TEXT, nullable)

## Indexing and Constraints
- Unique `(run_id, source_url)` to enforce idempotency.
- Indexes on `run_id`, `sent_to_base44`, `classification_label`, `filter_decision` for queries.
- Foreign keys with cascade delete from runs to jobs and progress events.
