from fastapi import APIRouter

from src.events.publisher import EventPublisher

router = APIRouter(prefix="/events", tags=["events"])

publisher = EventPublisher()


@router.get("/stream")
async def stream_events():
    return await publisher.stream()
