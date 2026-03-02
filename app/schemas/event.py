from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class LearningEvent(BaseModel):
    """Atomic interaction event used to update learner state."""

    learner_id: str = Field(min_length=1)
    module_id: str = Field(min_length=1)
    topic_id: str = Field(min_length=1)
    subtopic_id: str = Field(min_length=1)
    event_type: Literal[
        "quiz_attempt",
        "assignment_attempt",
        "flashcard_review",
    ]
    timestamp: datetime
    difficulty: int = Field(ge=1, le=5)
    correct: bool
    response_time_sec: float = Field(gt=0)
