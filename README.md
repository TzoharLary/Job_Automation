# Job Automation MVP

Local FastAPI-based pipeline to discover, fetch, extract, classify, filter, persist, and dispatch job postings. No Taskmaster/MCP dependency is used.

## Project Structure
See `docs/manual-task-plan.md` for the working task list.

```
src/
  app/            # FastAPI app, routers, services
  scraping/       # Playwright discovery/fetch
  extraction/     # HTML -> text/sections
  nlp/            # Transformers classifier wrapper
  filtering/      # Rules engine
  db/             # SQLModel models and session
  outbound/       # Base44 client (HTTP + mock)
  ui/             # Minimal static UI
  events/         # SSE schemas and publisher
scripts/
docs/
tests/
```

## Setup
1. Python 3.11+
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Playwright browsers:
   ```
   python -m playwright install chromium
   ```
4. Copy `.env.example` to `.env` and adjust as needed.

## Run
```
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```
UI served at `http://localhost:8000/ui`.

Quick commands (Makefile):
- `make run` – start API/UI
- `make dev` – start with autoreload
- `make playwright` – install Chromium runtime
- `make test` – run pytest

macOS double-click launcher:
- Run `RunJobAutomation.command` (already executable). It opens the UI and starts the server using the project venv if present.

### Kick off a run (examples)
- POST `/runs/start` with JSON body, e.g.
   ```json
   {
      "urls": ["https://example.com/jobs"],
      "include_keywords": ["python", "backend"],
      "exclude_keywords": ["senior"],
      "locations": ["remote"],
      "use_mock_outbound": true
   }
   ```
- Stop a run: `POST /runs/stop` with `{"run_id": "<id>"}`.
- Passed jobs: `GET /jobs/passed/{run_id}`.
- Progress SSE: `GET /events/stream` (UI subscribes automatically).

## Notes
- Taskmaster MCP was removed; workflow is fully manual.
- DB will be created at `DB_PATH` (default `./data/jobs.db`).
- SSE stream at `/events/stream`.
- Outbound defaults to mock; set `use_mock_outbound=false` when starting a run to hit the HTTP Base44 client (configure `BASE44_ENDPOINT` and `BASE44_API_KEY`).
