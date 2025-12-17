from functools import lru_cache
from typing import Dict

from transformers import pipeline

from src.app.config import get_settings


class Classifier:
    def __init__(self):
        settings = get_settings()
        self.task = settings.nlp_task
        self.model = settings.nlp_model
        self.max_length = settings.nlp_max_length
        self.batch_size = settings.nlp_batch_size
        self.pipe = pipeline(
            task=self.task,
            model=self.model,
            device=settings.nlp_device,
            truncation=True,
            max_length=self.max_length,
        )

    def classify(self, text: str) -> Dict[str, float | str]:
        result = self.pipe(text, batch_size=self.batch_size, truncation=True, max_length=self.max_length)
        # pipeline can return list or dict
        if isinstance(result, list):
            result = result[0]
        label = result.get("label")
        score = float(result.get("score")) if result.get("score") is not None else 0.0
        return {"label": label, "score": score}


@lru_cache(maxsize=1)
def get_classifier() -> Classifier:
    return Classifier()
