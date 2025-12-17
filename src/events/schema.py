from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel


class EventType(str, Enum):
    START = "start"
    PROGRESS = "progress"
    ERROR = "error"
    DONE = "done"
    HEARTBEAT = "heartbeat"
    STOP = "stop"


class ProgressEventModel(BaseModel):
    run_id: str
    event_type: EventType
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
