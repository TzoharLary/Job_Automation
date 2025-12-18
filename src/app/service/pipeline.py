import asyncio
from types import SimpleNamespace
import asyncio
import logging
from typing import Any

from src.scraping.runner import BrowserManager
from src.scraping.parser import JobParser


logger = logging.getLogger(__name__)


class Pipeline:
    def __init__(self, run_manager=None):
        self.run_manager = run_manager
        self.parser = JobParser()

    async def run(self, run_request, run_id) -> dict[str, Any]:
        urls = run_request.urls
        logger.info(f"🚀 PIPELINE STARTED: Processing {len(urls)} URLs")

        processed: list[Any] = []
        sources: list[Any] = []

        # 1. Pipeline Input: The Browser Context
        async with BrowserManager() as browser:
            for i, url in enumerate(urls):
                try:
                    # 2. Rate Limiting (Crucial for stability)
                    await asyncio.sleep(2.0)

                    # 3. Step: SCAN
                    logger.info(f"[SCAN] ({i+1}/{len(urls)}) Processing: {url}")
                    
                    # 4. Step: FETCH
                    html = await browser.fetch_html(url)
                    
                    if not html:
                        logger.warning(f"⚠️ Failed to fetch HTML for {url}")
                        continue

                    # 5. Step: PARSE
                    raw_jobs = self.parser.parse(html, url)
                    
                    if not raw_jobs:
                        logger.warning(f"⚠️ No jobs found via selectors on {url}")
                        continue
                    
                    logger.info(f"[EXTRACT] 📥 Found {len(raw_jobs)} raw jobs. Starting Filter...")

                    # 6. Step: FILTER & SAVE
                    for job in raw_jobs:
                        title = getattr(job, 'title', 'Unknown')
                        company = getattr(job, 'company', 'Unknown')
                        job_dict = {
                            "url": getattr(job, 'url', None) or getattr(job, 'link', None),
                            "title": title,
                            "company": company,
                            "location": getattr(job, 'location', None),
                            "summary": getattr(job, 'summary', None),
                            "region": getattr(job, 'region', None),
                            "filter": getattr(job, 'filter', {}),
                        }
                        logger.info(f"[MATCH] ✅ Candidate found: {title} at {company}")
                        # TODO: Add DB save logic here
                        processed.append(job_dict)

                    sources.append({"url": url, "passed": len(raw_jobs), "links": len(raw_jobs), "status": "active"})

                except Exception as e:
                    logger.error(f"❌ Error processing {url}: {e}")

        logger.info("🏁 PIPELINE FINISHED: All URLs processed.")
        return {"jobs": processed, "sources": sources}

        await self._publish(run_id, "completed", strings.pipeline_completed())
        return {"jobs": processed, "sources": sources}
