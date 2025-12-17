"""Hebrew strings used across backend logs and SSE events."""
from __future__ import annotations


def start_pipeline(count: int) -> str:
    return f"מתחיל סריקה של {count} מקורות"


def fetch_listing(url: str) -> str:
    return f"טוען עמוד משרות: {url}"


def fetch_failed(url: str) -> str:
    return f"כשל בטעינת עמוד משרות: {url}"


def discovered_links(count: int) -> str:
    return f"נמצאו {count} קישורי משרות"


def fetch_job(url: str) -> str:
    return f"טוען משרה: {url}"


def job_passed(url: str, region: str | None = None) -> str:
    if region:
        return f"המשרה עברה (אזור {region}): {url}"
    return f"המשרה עברה סינון: {url}"


def job_skipped(url: str, reason: str) -> str:
    return f"המשרה נפסלה ({reason}): {url}"


def outbound_saved(url: str) -> str:
    return f"המידע נשמר למשרה: {url}"


def processing_error(url: str, err: str) -> str:
    return f"שגיאה בעיבוד {url}: {err}"


def pipeline_completed() -> str:
    return "הסריקה הושלמה"


def pipeline_stopped() -> str:
    return "הסריקה נעצרה לפי בקשה"


def pipeline_start_run_id(run_id: str) -> str:
    return f"התחלת ריצה {run_id}"
