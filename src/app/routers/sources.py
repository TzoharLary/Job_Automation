from fastapi import APIRouter

from src.db.repository import SourceRepository
from src.db.session import session_scope

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("/suggest")
def suggest_sources(limit: int = 50) -> dict:
    """Return recently successful source URLs for auto-fill."""
    with session_scope() as session:
        repo = SourceRepository(session)
        records = repo.list_successful(limit=limit)
        return {"urls": [rec.url for rec in records]}
