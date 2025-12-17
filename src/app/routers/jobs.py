from fastapi import APIRouter, HTTPException

from src.db.repository import JobRepository
from src.db.session import session_scope

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/passed/{run_id}")
async def list_passed(run_id: str):
    with session_scope() as session:
        repo = JobRepository(session)
        jobs = list(repo.list_passed(run_id))
        if not jobs:
            # Return empty list, not 404, to simplify UI
            return []
        return jobs
