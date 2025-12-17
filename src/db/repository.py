import datetime as dt
from typing import Iterable, Optional

from sqlmodel import Session, select

from src.db.models import Job, OutboundAttempt, ProgressEvent, Run, JobSource


class RunRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, run: Run) -> Run:
        self.session.add(run)
        self.session.commit()
        self.session.refresh(run)
        return run

    def update_status(self, run_id: str, status: str) -> None:
        run = self.session.exec(select(Run).where(Run.run_id == run_id)).first()
        if run:
            run.status = status
            self.session.add(run)
            self.session.commit()

    def get(self, run_id: str) -> Optional[Run]:
        return self.session.exec(select(Run).where(Run.run_id == run_id)).first()


class JobRepository:
    def __init__(self, session: Session):
        self.session = session

    def upsert(self, job: Job) -> Job:
        existing = self.session.exec(
            select(Job).where(Job.run_id == job.run_id, Job.url == job.url)
        ).first()
        if existing:
            for field, value in job.dict(exclude_unset=True).items():
                setattr(existing, field, value)
            self.session.add(existing)
            self.session.commit()
            self.session.refresh(existing)
            return existing
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        return job

    def list_passed(self, run_id: str) -> Iterable[Job]:
        return self.session.exec(select(Job).where(Job.run_id == run_id, Job.passed_filter == True))  # noqa: E712


class ProgressRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, event: ProgressEvent) -> ProgressEvent:
        self.session.add(event)
        self.session.commit()
        self.session.refresh(event)
        return event

    def list_for_run(self, run_id: str) -> Iterable[ProgressEvent]:
        return self.session.exec(select(ProgressEvent).where(ProgressEvent.run_id == run_id))


class OutboundRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, attempt: OutboundAttempt) -> OutboundAttempt:
        self.session.add(attempt)
        self.session.commit()
        self.session.refresh(attempt)
        return attempt

    def update_status(self, attempt_id: int, status: str, response_status: Optional[int] = None, response_body: Optional[str] = None) -> None:
        attempt = self.session.get(OutboundAttempt, attempt_id)
        if not attempt:
            return
        attempt.status = status
        attempt.response_status = response_status
        attempt.response_body = response_body
        self.session.add(attempt)
        self.session.commit()


class SourceRepository:
    """Persistence layer for JobSource records (career page memory)."""

    def __init__(self, session: Session):
        self.session = session

    def record_result(self, url: str, jobs_found: int, last_error: str | None = None, status: str | None = None) -> JobSource:
        source = self.session.exec(select(JobSource).where(JobSource.url == url)).first()
        if not source:
            source = JobSource(url=url)
        source.last_scraped_at = dt.datetime.utcnow()
        source.last_run_yield = jobs_found
        source.total_jobs_found = (source.total_jobs_found or 0) + max(jobs_found, 0)
        source.last_error = last_error
        if status:
            source.status = status
        else:
            source.status = "active" if jobs_found > 0 else (source.status or "empty")
        self.session.add(source)
        self.session.commit()
        self.session.refresh(source)
        return source

    def mark_failure(self, url: str, error: str) -> JobSource:
        source = self.session.exec(select(JobSource).where(JobSource.url == url)).first()
        if not source:
            source = JobSource(url=url)
        source.last_scraped_at = dt.datetime.utcnow()
        source.last_error = error
        source.status = "failed"
        self.session.add(source)
        self.session.commit()
        self.session.refresh(source)
        return source

    def list_successful(self, limit: int = 50) -> list[JobSource]:
        return list(
            self.session.exec(
                select(JobSource)
                .where(JobSource.status == "active", JobSource.last_run_yield > 0)
                .order_by(JobSource.last_scraped_at.desc())
                .limit(limit)
            )
        )
