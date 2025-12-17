from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

from src.app.config import get_settings
from src.events.publisher import EventPublisher
from src.extraction.extractor import extract_sections
from src.filtering.engine import FilterContext, FilterResult, evaluate
from src.localization import strings
from src.nlp.classifier import get_classifier
from src.outbound.base import Base44Client
from src.outbound.http_client import HttpBase44Client
from src.outbound.mock_client import MockBase44Client
from src.scraping.discovery import discover_job_links
from src.scraping.runner import fetch_html


def build_payload(job_data: Dict[str, Any]) -> Dict[str, Any]:
    settings = get_settings()
    return {
        "source": settings.project_name,
        "job": job_data,
    }


def select_outbound_client(mock: bool = False) -> Base44Client:
    if mock:
        return MockBase44Client()
    return HttpBase44Client()


class Pipeline:
    def __init__(self, publisher: Optional[EventPublisher] = None):
        self.publisher = publisher
        self.classifier = get_classifier()
        self.filter_context = FilterContext(min_score=get_settings().filter_min_score)

    async def _publish(self, run_id: str, type_: str, message: str, payload: Optional[Dict[str, Any]] = None):
        if not self.publisher:
            return
        from src.events.schema import EventType, ProgressEventModel  # local import to avoid cycles

        type_map = {
            "error": EventType.ERROR,
            "completed": EventType.DONE,
        }
        event_type = type_map.get(type_, EventType.PROGRESS)
        await self.publisher.publish(
            ProgressEventModel(run_id=run_id, event_type=event_type, message=message, data=payload)
        )

    async def _process_job(
        self,
        run_id: str,
        job_url: str,
        html: str,
        client: Base44Client,
    ) -> Tuple[Dict[str, Any], FilterResult]:
        extracted = extract_sections(html)
        text_blob = "\n".join(extracted.values())
        classification = self.classifier.classify(text_blob)
        filter_result = evaluate(
            text=text_blob,
            classification=classification,
            title=extracted.get("title"),
            description=extracted.get("description"),
            summary=extracted.get("summary"),
            location=extracted.get("location"),
            context=self.filter_context,
        )

        job_record: Dict[str, Any] = {
            "url": job_url,
            "title": extracted.get("title"),
            "company": extracted.get("company"),
            "location": extracted.get("location"),
            "region": filter_result.region,
            "description": extracted.get("description"),
            "summary": extracted.get("summary"),
            "classification": classification,
            "filter": filter_result.to_dict(),
        }

        if filter_result.passed:
            payload = build_payload(job_record)
            await client.send_job(payload)
            await self._publish(
                run_id,
                "job_passed",
                strings.job_passed(job_url, region=filter_result.region),
                {"job": job_record, "event": "job_passed"},
            )
        else:
            await self._publish(
                run_id,
                "job_skipped",
                strings.job_skipped(job_url, filter_result.reason),
                {"job": job_record, "event": "job_skipped"},
            )

        return job_record, filter_result

    async def run(
        self,
        run_id: str,
        urls: Iterable[str],
        use_mock_outbound: bool = True,
        stop_callback: Optional[Callable[[], bool]] = None,
    ) -> Dict[str, Any]:
        """Run the pipeline for the given URLs.

        Returns a dict with keys:
        - jobs: list of processed job records
        - sources: list of per-source summaries
        """
        urls_list = list(urls)
        client = select_outbound_client(mock=use_mock_outbound)

        await self._publish(run_id, "info", strings.start_pipeline(len(urls_list)))

        processed: list[Dict[str, Any]] = []
        sources: List[Dict[str, Any]] = []

        for site_url in urls_list:
            passed_count = 0
            if stop_callback and stop_callback():
                await self._publish(run_id, "completed", strings.pipeline_stopped())
                return {"jobs": processed, "sources": sources}
            await self._publish(run_id, "info", strings.fetch_listing(site_url))
            listing_html = await fetch_html(site_url)
            if not listing_html:
                await self._publish(run_id, "error", strings.fetch_failed(site_url))
                sources.append({"url": site_url, "passed": 0, "links": 0, "status": "failed"})
                continue

            job_links = discover_job_links(listing_html, base_url=site_url)
            await self._publish(run_id, "info", strings.discovered_links(len(job_links)))

            for job_url in job_links:
                if stop_callback and stop_callback():
                    await self._publish(run_id, "completed", strings.pipeline_stopped())
                    sources.append({"url": site_url, "passed": passed_count, "links": len(job_links)})
                    return {"jobs": processed, "sources": sources}
                job_html = await fetch_html(job_url)
                if not job_html:
                    await self._publish(run_id, "error", strings.processing_error(job_url, "טעינת עמוד נכשלה"))
                    continue
                try:
                    record, filter_result = await self._process_job(
                        run_id,
                        job_url,
                        job_html,
                        client,
                    )
                    processed.append(record)
                    if filter_result.passed:
                        passed_count += 1
                except Exception as exc:  # noqa: BLE001
                    await self._publish(run_id, "error", strings.processing_error(job_url, str(exc)))

            status = "active" if passed_count > 0 else "empty"
            sources.append({"url": site_url, "passed": passed_count, "links": len(job_links), "status": status})

        await self._publish(run_id, "completed", strings.pipeline_completed())
        return {"jobs": processed, "sources": sources}
