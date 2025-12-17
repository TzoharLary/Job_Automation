import datetime as dt
from typing import Optional

from sqlmodel import Field, SQLModel


class Run(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: str = Field(index=True, unique=True)
    status: str = Field(default="pending", index=True)
    started_at: dt.datetime = Field(default_factory=lambda: dt.datetime.utcnow())
    finished_at: Optional[dt.datetime] = None
    config_json: Optional[str] = None


class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: str = Field(index=True)
    url: str = Field(index=True)
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    region: Optional[str] = Field(default=None, index=True)
    description: Optional[str] = None
    summary: Optional[str] = None
    classification_label: Optional[str] = None
    classification_score: Optional[float] = None
    score: Optional[float] = None
    passed_filter: bool = Field(default=False, index=True)
    created_at: dt.datetime = Field(default_factory=lambda: dt.datetime.utcnow())


class ProgressEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: str = Field(index=True)
    event_type: str = Field(index=True)
    message: Optional[str] = None
    data_json: Optional[str] = None
    created_at: dt.datetime = Field(default_factory=lambda: dt.datetime.utcnow())


class OutboundAttempt(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: str = Field(index=True)
    job_url: str = Field(index=True)
    status: str = Field(default="pending", index=True)
    response_status: Optional[int] = None
    response_body: Optional[str] = None
    created_at: dt.datetime = Field(default_factory=lambda: dt.datetime.utcnow())


class JobSource(SQLModel, table=True):
    """Represents a career site source and its historical performance."""

    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(index=True, unique=True)
    status: str = Field(default="active", index=True)  # active|failed|empty
    last_scraped_at: Optional[dt.datetime] = Field(default=None, index=True)
    total_jobs_found: int = Field(default=0)
    last_run_yield: int = Field(default=0)
    last_error: Optional[str] = None
    created_at: dt.datetime = Field(default_factory=lambda: dt.datetime.utcnow())
