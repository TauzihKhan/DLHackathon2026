from __future__ import annotations

from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, Field


class ReviewQueueItem(BaseModel):
    module_id: str = Field(min_length=1)
    topic_id: str = Field(min_length=1)
    subtopic_id: str = Field(min_length=1)
    interval_days: int = Field(ge=1)
    due_in_days: float
    due_now: bool
    next_review_at: datetime
    priority_score: float = Field(ge=0.0, le=1.0)


class SpacedRepetitionPlan(BaseModel):
    generated_at: datetime
    due_now_count: int = Field(ge=0)
    due_next_24h_count: int = Field(ge=0)
    review_queue: list[ReviewQueueItem] = Field(default_factory=list)


class InsightResponse(BaseModel):
    """Response schema for GET /students/{id}/insights."""

    learner_id: str = Field(min_length=1)
    generated_at: datetime
    weak_subtopics: list[str] = Field(default_factory=list)
    priority_subtopic_id: Optional[str] = None
    recommended_action: str = Field(min_length=1)
    reason_codes: list[str] = Field(default_factory=list)
    explanation_facts: dict[str, Union[str, float, int]] = Field(default_factory=dict)
    spaced_repetition: Optional[SpacedRepetitionPlan] = None
