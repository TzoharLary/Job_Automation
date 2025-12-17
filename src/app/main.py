from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.app.routers import runs, jobs, events, sources
from src.app.config import get_settings
from src.db.session import init_db

settings = get_settings()

app = FastAPI(title="Job Automation MVP", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router)
app.include_router(runs.router)
app.include_router(jobs.router)
app.include_router(sources.router)

app.mount("/ui", StaticFiles(directory="src/ui", html=True), name="ui")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
