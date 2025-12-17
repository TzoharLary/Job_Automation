from pathlib import Path
from typing import Iterator
from contextlib import contextmanager

from sqlmodel import Session, SQLModel, create_engine

from src.app.config import get_settings


def _engine_url(db_path: str) -> str:
    path = Path(db_path)
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{path}"


def get_engine():
    settings = get_settings()
    url = _engine_url(settings.db_path)
    return create_engine(url, echo=settings.db_echo, connect_args={"check_same_thread": False})


def init_db(engine=None) -> None:
    engine = engine or get_engine()
    SQLModel.metadata.create_all(engine)
    _run_light_migrations(engine)


def _column_exists(engine, table: str, column: str) -> bool:
    with engine.connect() as conn:
        res = conn.exec_driver_sql(f"PRAGMA table_info({table})").fetchall()
        return any(row[1] == column for row in res)


def _run_light_migrations(engine) -> None:
    """Minimal, additive migrations for SQLite (safe no-ops if already applied)."""
    with engine.connect() as conn:
        if not _column_exists(engine, "job", "region"):
            conn.exec_driver_sql("ALTER TABLE job ADD COLUMN region VARCHAR")


@contextmanager
def session_scope(engine=None) -> Iterator[Session]:
    engine = engine or get_engine()
    with Session(engine) as session:
        yield session
