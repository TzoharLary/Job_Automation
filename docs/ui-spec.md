# UI Specification

## Screens
1. **Run Launcher** (landing): form to enter URLs and config, plus start/stop controls.
2. **Live Monitor** (same page, real-time): progress counters, current site/job, log of events, list of passed jobs.

## Inputs / Fields
- **Career site URLs**: textarea allowing multiple lines.
- **Filter config**: include keywords, exclude keywords, locations, seniority, min score.
- **NLP model name**: text input with default.
- **Base44**: endpoint URL, mock mode toggle (default on), timeout optional.
- **Concurrency/Rate limits**: global workers, per-site delay.

## Controls
- **Start run** button (disabled when empty URLs or run active).
- **Stop/Cancel** button (visible when running).
- Optional **Resume last run** if status is cancel/fail and data present.

## Real-time Widgets
- **Current site/URL**: shows domain + path.
- **Counters**: discovered, fetched, classified, filtered, stored, sent, errors.
- **Event log**: streaming list of SSE messages with timestamp and stage.
- **Passed jobs list**: table/cards showing title, company, location, score, link to source.
- **Errors panel**: recent errors with stage and retry info.
- **Status indicator**: running/cancelled/completed.

## Interaction Flow
1. User enters URLs + config, clicks Start.
2. UI POSTs `/runs` and begins listening to `/runs/{id}/sse`.
3. UI updates widgets on incoming events; handles `heartbeat` to keep connection alive.
4. Stop triggers cancel API; UI reflects `run_cancelled` when emitted.
5. Passed jobs list updates via SSE events or periodic refresh from `/runs/{id}/jobs`.

## UX Notes
- Keep static HTML+JS minimal; no build step.
- Handle SSE reconnect with exponential backoff; show a banner if disconnected.
- Preserve form inputs in localStorage for quick reruns.
