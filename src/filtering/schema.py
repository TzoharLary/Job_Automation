from typing import List, Optional

from pydantic import BaseModel


class FilterConfig(BaseModel):
    include_keywords: List[str] = []
    exclude_keywords: List[str] = []
    locations: List[str] = []
    min_seniority: Optional[str] = None
    min_score: float = 0.5
    max_results: Optional[int] = None
