import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse

from src.app.routers import runs, jobs, sources
from src.app.config import get_settings
from src.db.session import init_db
from src.app.logger_stream import log_queue, setup_global_logging

settings = get_settings()

app = FastAPI(title="Job Automation MVP", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(runs.router)
app.include_router(jobs.router)
app.include_router(sources.router)

app.mount("/ui", StaticFiles(directory="src/ui", html=True), name="ui")


@app.on_event("startup")
def on_startup() -> None:
    setup_global_logging()
    init_db()


@app.get("/events/stream")
async def run_events():
    """
    Streams all server logs to the UI in real-time.
    """

    async def event_generator():
        while True:
            # Wait for the next log message from the queue
            data = await log_queue.get()

            # Yield it as a specialized "log" event
            yield {
                "event": "log",
                "data": json.dumps(data)
            }

    return EventSourceResponse(event_generator())


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
