from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

FactValue = str | float | int


class PracticeQuestion(BaseModel):
    """A targeted practice item generated from structured learner signals."""

    question: str = Field(min_length=5)
    intent: str = Field(min_length=3)
    difficulty: int = Field(ge=1, le=5)


class NarrativeInsightResponse(BaseModel):
    """Role 3 narrative layer built on top of deterministic insight output."""

    learner_id: str = Field(min_length=1)
    generated_at: datetime
    generation_mode: Literal["llm", "fallback"]
    priority_subtopic_id: str | None = None
    weak_subtopics: list[str] = Field(default_factory=list)
    reason_codes: list[str] = Field(default_factory=list)
    recommended_action: str = Field(min_length=1)
    narrative_summary: str = Field(min_length=1)
    narrative_explanation: str = Field(min_length=1)
    practice_questions: list[PracticeQuestion] = Field(default_factory=list)
    source_explanation_facts: dict[str, FactValue] = Field(default_factory=dict)

