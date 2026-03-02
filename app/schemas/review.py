from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class DueReviewItem(BaseModel):
    """One subtopic currently due for spaced-repetition review."""

    module_id: str = Field(min_length=1)
    topic_id: str = Field(min_length=1)
    subtopic_id: str = Field(min_length=1)
    mastery: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    decay_risk_score: float = Field(ge=0.0, le=1.0)
    review_interval_days: float = Field(ge=0.0)
    next_review_at: datetime
    days_overdue: float = Field(ge=0.0)
    priority_score: float = Field(ge=0.0, le=1.0)


class DueReviewsResponse(BaseModel):
    """Response schema for GET /students/{id}/reviews/due."""

    learner_id: str = Field(min_length=1)
    generated_at: datetime
    due_count: int = Field(ge=0)
    items: list[DueReviewItem] = Field(default_factory=list)

