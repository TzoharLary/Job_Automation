import asyncio
from typing import Any, Dict

import httpx

from src.app.config import get_settings
from src.outbound.base import Base44Client


class HttpBase44Client(Base44Client):
    def __init__(self):
        self.settings = get_settings()
        self.client = httpx.AsyncClient(timeout=self.settings.base44_timeout_seconds)

    async def send_job(self, payload: Dict[str, Any]) -> None:
        retries = self.settings.base44_retries
        for attempt in range(retries):
            try:
                resp = await self.client.post(str(self.settings.base44_endpoint), json=payload)
                resp.raise_for_status()
                return
            except Exception:
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
