from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class SubtopicState(BaseModel):
    """Tracked learning state for one subtopic."""

    module_id: str = Field(min_length=1)
    topic_id: str = Field(min_length=1)
    subtopic_id: str = Field(min_length=1)
    mastery: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    xp: int = Field(ge=0)
    decay_risk_score: float = Field(ge=0.0, le=1.0)
    last_interaction_at: datetime
    attempts: int = Field(ge=0)
    correct_attempts: int = Field(ge=0)
    review_interval_days: float = Field(default=1.0, ge=0.0)
    next_review_at: datetime | None = None
    review_due: bool = False

    @model_validator(mode="after")
    def validate_attempt_counts(self) -> "SubtopicState":
        if self.correct_attempts > self.attempts:
            raise ValueError("correct_attempts cannot exceed attempts")
        if self.next_review_at is None and self.review_due:
            raise ValueError("review_due cannot be true when next_review_at is None")
        return self


class StudentStateResponse(BaseModel):
    """Response schema for GET /students/{id}/state."""

    learner_id: str = Field(min_length=1)
    xp_total: int = Field(ge=0)
    updated_at: datetime
    subtopics: list[SubtopicState] = Field(default_factory=list)
