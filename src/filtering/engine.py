"""Strict filtering ("Iron Dome") enforcing R&D in Israel only."""
from dataclasses import asdict, dataclass
from typing import Dict, Optional

from src.filtering.geo_il import resolve_region
from src.filtering.roles import is_dev_role


@dataclass
class FilterResult:
    passed: bool
    reason: str
    score: float
    region: Optional[str] = None
    city: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class FilterContext:
    """Context for filtering decisions."""

    min_score: float = 0.5


def evaluate(
    *,
    text: str,
    classification: dict,
    title: str | None,
    description: str | None,
    summary: str | None,
    location: str | None,
    context: FilterContext,
) -> FilterResult:
    score = float(classification.get("score", 0) or 0)

    if score < context.min_score:
        return FilterResult(False, f"ציון מודל נמוך ({score:.2f}<{context.min_score})", score)

    is_dev, reason = is_dev_role(title, description, summary)
    if not is_dev:
        return FilterResult(False, reason, score)

    is_israel, region, city = resolve_region(location)
    if not is_israel:
        return FilterResult(False, "משרה שאינה בישראל", score, region=region, city=city)

    return FilterResult(True, "עבר סינון", score, region=region, city=city)
