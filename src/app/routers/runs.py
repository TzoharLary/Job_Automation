import re
import uuid
import json
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, field_validator

from src.app.config import get_settings
from src.app.service.run_manager import RunManager
from src.db.models import Run
from src.db.repository import RunRepository
from src.db.session import session_scope
from .events import publisher

router = APIRouter(prefix="/runs", tags=["runs"])
settings = get_settings()
run_manager = RunManager(publisher)


class StartRunRequest(BaseModel):
    urls: Optional[List[str]] = None
    raw_urls: Optional[str] = None
    use_mock_outbound: Optional[bool] = True

    @field_validator("urls", mode="before")
    @classmethod
    def _coerce_urls(cls, v):
        # Accept either list or string, keep as-is for later parsing
        return v

    def extract_urls(self) -> List[str]:
        """Extract clean URLs from provided raw inputs using regex."""
        candidates: List[str] = []
        if self.urls:
            for item in self.urls:
                candidates.append(str(item))
        if self.raw_urls:
            candidates.append(self.raw_urls)

        text_blob = "\n".join(candidates)
        found = re.findall(r"https?://[^\s\]\)<>]+", text_blob)
        cleaned: List[str] = []
        for url in found:
            cleaned.append(url.strip('>),.;"\''))
        # de-duplicate while preserving order
        seen = set()
        deduped: List[str] = []
        for u in cleaned:
            if u not in seen:
                seen.add(u)
                deduped.append(u)
        return deduped


class StartRunResponse(BaseModel):
    run_id: str


@router.post("/start", response_model=StartRunResponse)
async def start_run(payload: StartRunRequest, background_tasks: BackgroundTasks):
    print(f"DEBUG: Received start_run request. Raw input length: {len(payload.raw_urls or '')}")
    run_id = str(uuid.uuid4())
    urls = payload.extract_urls()
    print(f"DEBUG: Found {len(urls)} valid URLs from input")
    if not urls:
        raise HTTPException(status_code=400, detail="no valid urls provided")
    with session_scope() as session:
        repo = RunRepository(session)
        config = payload.model_dump()
        config["urls"] = urls
        repo.create(Run(run_id=run_id, status="running", config_json=json.dumps(config)))

    background_tasks.add_task(run_manager.start_run, run_id, json.dumps({"urls": urls, "use_mock_outbound": payload.use_mock_outbound}))
    return StartRunResponse(run_id=run_id)


class StopRunRequest(BaseModel):
    run_id: str


@router.post("/stop")
async def stop_run(req: StopRunRequest):
    run_manager.request_stop(req.run_id)
    with session_scope() as session:
        repo = RunRepository(session)
        run = repo.get(req.run_id)
        if not run:
            raise HTTPException(status_code=404, detail="run not found")
        repo.update_status(req.run_id, "stopped")
    return {"status": "stopped", "run_id": req.run_id}


@router.get("/{run_id}")
async def get_run(run_id: str):
    with session_scope() as session:
        repo = RunRepository(session)
        run = repo.get(run_id)
        if not run:
            raise HTTPException(status_code=404, detail="run not found")
        return run
