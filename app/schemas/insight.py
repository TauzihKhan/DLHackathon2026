from datetime import datetime

from pydantic import BaseModel, Field


class InsightResponse(BaseModel):
    """Response schema for GET /students/{id}/insights."""

    learner_id: str = Field(min_length=1)
    generated_at: datetime
    weak_subtopics: list[str] = Field(default_factory=list)
    priority_subtopic_id: str | None = None
    recommended_action: str = Field(min_length=1)
    reason_codes: list[str] = Field(default_factory=list)
    explanation_facts: dict[str, str | float | int] = Field(default_factory=dict)
