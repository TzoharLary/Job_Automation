from functools import lru_cache
from typing import Optional

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = Field("local", alias="APP_ENV")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    project_name: str = Field("Job Automation", alias="PROJECT_NAME")

    # Database
    db_path: str = Field("./data/jobs.db", alias="DB_PATH")
    db_echo: bool = Field(False, alias="DB_ECHO")

    # NLP
    nlp_model: str = Field("distilbert-base-uncased-finetuned-sst-2-english", alias="NLP_MODEL")
    nlp_task: str = Field("text-classification", alias="NLP_TASK")
    nlp_device: str = Field("cpu", alias="NLP_DEVICE")
    nlp_max_length: int = Field(512, alias="NLP_MAX_LENGTH")
    nlp_batch_size: int = Field(4, alias="NLP_BATCH_SIZE")

    # Scraping
    playwright_browser: str = Field("chromium", alias="PLAYWRIGHT_BROWSER")
    playwright_nav_timeout_ms: int = Field(30_000, alias="PLAYWRIGHT_NAV_TIMEOUT_MS")
    playwright_max_retries: int = Field(3, alias="PLAYWRIGHT_MAX_RETRIES")
    playwright_rate_limit_per_domain: int = Field(1, alias="PLAYWRIGHT_RATE_LIMIT_PER_DOMAIN")
    playwright_delay_ms: int = Field(500, alias="PLAYWRIGHT_DELAY_MS")
    user_agent_override: str = Field("", alias="USER_AGENT_OVERRIDE")

    # Concurrency / SSE
    concurrency_global: int = Field(4, alias="CONCURRENCY_GLOBAL")
    concurrency_per_domain: int = Field(1, alias="CONCURRENCY_PER_DOMAIN")
    heartbeat_seconds: int = Field(15, alias="HEARTBEAT_SECONDS")

    # Filtering
    filter_min_score: float = Field(0.5, alias="FILTER_MIN_SCORE")
    filter_include_keywords: str = Field("", alias="FILTER_INCLUDE_KEYWORDS")
    filter_exclude_keywords: str = Field("", alias="FILTER_EXCLUDE_KEYWORDS")
    filter_locations: str = Field("", alias="FILTER_LOCATIONS")
    filter_seniority: str = Field("", alias="FILTER_SENIORITY")
    filter_max_results: Optional[int] = Field(None, alias="FILTER_MAX_RESULTS")

    # Base44 outbound
    base44_endpoint: Optional[AnyUrl] = Field(None, alias="BASE44_ENDPOINT")
    base44_timeout_seconds: int = Field(15, alias="BASE44_TIMEOUT_SECONDS")
    base44_retries: int = Field(3, alias="BASE44_RETRIES")
    base44_mock: bool = Field(True, alias="BASE44_MOCK")
    base44_api_key: str = Field("", alias="BASE44_API_KEY")

    # Server
    host: str = Field("0.0.0.0", alias="HOST")
    port: int = Field(8000, alias="PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[arg-type]
