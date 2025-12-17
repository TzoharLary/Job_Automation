from abc import ABC, abstractmethod
from typing import Any, Dict


class Base44Client(ABC):
    @abstractmethod
    async def send_job(self, payload: Dict[str, Any]) -> None:
        ...
