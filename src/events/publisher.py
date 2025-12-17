import asyncio
import json
from typing import AsyncIterator, Callable, Set

from sse_starlette.sse import EventSourceResponse

from src.events.schema import EventType, ProgressEventModel


class EventPublisher:
    def __init__(self, heartbeat_seconds: int = 15):
        self.heartbeat_seconds = heartbeat_seconds
        # Maintain a set of active listener queues for broadcast
        self.listeners: Set[asyncio.Queue] = set()

    async def publish(self, event: ProgressEventModel) -> None:
        # Broadcast to all active listeners
        # Iterate over a copy to avoid issues if listeners are removed during iteration
        for queue in list(self.listeners):
            await queue.put(event)

    async def heartbeat_loop(self, run_id: str, stop_flag: Callable[[], bool]) -> None:
        while not stop_flag():
            await asyncio.sleep(self.heartbeat_seconds)
            await self.publish(ProgressEventModel(run_id=run_id, event_type=EventType.HEARTBEAT))

    async def stream(self) -> EventSourceResponse:
        queue = asyncio.Queue()
        self.listeners.add(queue)

        async def event_generator() -> AsyncIterator[dict]:
            try:
                while True:
                    event = await queue.get()
                    yield {
                        "event": event.event_type.value,
                        "data": json.dumps(event.model_dump()),
                    }
            except asyncio.CancelledError:
                # Client disconnected
                pass
            finally:
                self.listeners.discard(queue)

        return EventSourceResponse(event_generator())
