import asyncio
import json
from typing import Any, Dict

from src.app.service.pipeline import Pipeline
from src.db.models import Job, OutboundAttempt, ProgressEvent, Run
from src.db.repository import JobRepository, OutboundRepository, ProgressRepository, RunRepository, SourceRepository
from src.db.session import session_scope
from src.events.publisher import EventPublisher
from src.events.schema import EventType, ProgressEventModel
from src.localization import strings


class RunManager:
    def __init__(self, publisher: EventPublisher):
        self.publisher = publisher
        self.stop_flags: dict[str, bool] = {}

    def should_stop(self, run_id: str) -> bool:
        return self.stop_flags.get(run_id, False)

    def request_stop(self, run_id: str) -> None:
        self.stop_flags[run_id] = True

    async def _save_event(self, run_id: str, event_type: EventType, message: str, payload: Dict[str, Any] | None = None):
        with session_scope() as session:
            progress_repo = ProgressRepository(session)
            progress_repo.add(
                ProgressEvent(
                    run_id=run_id,
                    event_type=event_type.value,
                    message=message,
                    data_json=json.dumps(payload) if payload else None,
                )
            )

        await self.publisher.publish(
            ProgressEventModel(run_id=run_id, event_type=event_type, message=message, data=payload)
        )

    async def start_run(self, run_id: str, config_json: str) -> None:
        self.stop_flags[run_id] = False
        pipeline = Pipeline(self.publisher)

        config = json.loads(config_json)

        await self._save_event(run_id, EventType.START, strings.pipeline_start_run_id(run_id))

        try:
            result = await pipeline.run(
                run_id=run_id,
                urls=config.get("urls", []),
                use_mock_outbound=config.get("use_mock_outbound", True),
                stop_callback=lambda: self.should_stop(run_id),
            )
            jobs_processed = result.get("jobs", [])
            sources_summary = result.get("sources", [])

            with session_scope() as session:
                job_repo = JobRepository(session)
                outbound_repo = OutboundRepository(session)
                run_repo = RunRepository(session)
                source_repo = SourceRepository(session)

                for record in jobs_processed:
                    job = Job(
                        run_id=run_id,
                        url=record.get("url"),
                        title=record.get("title"),
                        company=record.get("company"),
                        location=record.get("location"),
                        region=record.get("region"),
                        description=record.get("description"),
                        summary=record.get("summary"),
                        classification_label=record.get("classification", {}).get("label"),
                        classification_score=record.get("classification", {}).get("score"),
                        score=record.get("filter", {}).get("score"),
                        passed_filter=record.get("filter", {}).get("passed", False),
                    )
                    job_repo.upsert(job)

                    if record.get("filter", {}).get("passed"):
                        attempt = outbound_repo.add(
                            OutboundAttempt(
                                run_id=run_id,
                                job_url=record.get("url"),
                                status="sent",
                                response_body="mock" if config.get("use_mock_outbound", True) else "sent",
                            )
                        )
                        # publish outbound saved event so the UI can update outbound status
                        try:
                            await self._save_event(
                                run_id,
                                EventType.PROGRESS,
                                strings.outbound_saved(record.get("url", "")),
                                {"job_url": record.get("url"), "attempt_id": attempt.id, "event": "outbound_saved"},
                            )
                        except Exception:
                            # do not fail the whole run for event publish issues
                            pass

                for summary in sources_summary:
                    source_repo.record_result(
                        url=summary.get("url"),
                        jobs_found=summary.get("passed", 0),
                        status=summary.get("status", "active"),
                    )

                run_repo.update_status(run_id, "stopped" if self.should_stop(run_id) else "completed")

            if self.should_stop(run_id):
                await self._save_event(run_id, EventType.STOP, strings.pipeline_stopped())
            else:
                await self._save_event(run_id, EventType.DONE, strings.pipeline_completed())

        except asyncio.CancelledError:
            with session_scope() as session:
                run_repo = RunRepository(session)
                run_repo.update_status(run_id, "cancelled")
            await self._save_event(run_id, EventType.STOP, "run cancelled")
        except Exception as exc:  # noqa: BLE001
            with session_scope() as session:
                run_repo = RunRepository(session)
                run_repo.update_status(run_id, "failed")
            await self._save_event(run_id, EventType.ERROR, f"run failed: {exc}")
