"""Role filtering heuristics for Development/R&D positions."""
from __future__ import annotations

from typing import Tuple

DEV_KEYWORDS = {
    "developer",
    "software engineer",
    "backend",
    "frontend",
    "full stack",
    "full-stack",
    "devops",
    "data engineer",
    "machine learning engineer",
    "ml engineer",
    "research engineer",
    "r&d",
    "rd engineer",
    "mobile developer",
    "android developer",
    "ios developer",
    "site reliability",
    "sre",
    "platform engineer",
    "cloud engineer",
}

NON_DEV_EXCLUDE = {
    "sales",
    "marketing",
    "hr",
    "recruiter",
    "finance",
    "accountant",
    "legal",
    "designer",
    "ux",
    "ui",
    "customer success",
    "support",
    "success manager",
}


def is_dev_role(title: str | None, description: str | None = None, summary: str | None = None) -> Tuple[bool, str]:
    """Return (is_dev, reason). Applies permissive include + strict exclude."""
    # Only check exclusions in the title to avoid rejecting "Dev working with Marketing"
    title_lower = (title or "").lower()
    
    for bad in NON_DEV_EXCLUDE:
        if bad in title_lower:
            return False, f"לא פיתוח ({bad})"

    # Check keywords in the full blob
    text_parts = [part.lower() for part in [title or "", summary or "", description or ""] if part]
    blob = "\n".join(text_parts)

    for good in DEV_KEYWORDS:
        if good in blob:
            return True, "תפקיד פיתוח"

    return False, "לא זוהה כתבפקיד פיתוח"
