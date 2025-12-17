import logging
from typing import Any, Dict

from src.outbound.base import Base44Client

logger = logging.getLogger(__name__)


class MockBase44Client(Base44Client):
    async def send_job(self, payload: Dict[str, Any]) -> None:
        logger.info("Mock send to Base44: %s", payload)
