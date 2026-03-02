from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.state import StudentStateResponse, SubtopicState


class AttemptEvent(BaseModel):
    topic: str
    subtopic: str
    correctness: bool
    difficulty: float = Field(ge=0.0, le=1.0)
    response_time: float = Field(gt=0.0)
    timestamp: datetime | None = None


TOPIC_TREE = {
    "Algebra": ["Linear Equations", "Quadratics", "Inequalities", "Functions"],
    "Calculus": [
        "Limits",
        "Differentiation",
        "Applications of Derivatives",
        "Integration",
    ],
    "Probability": [
        "Basic Probability",
        "Conditional Probability",
        "Bayes Theorem",
        "Random Variables",
    ],
    "Statistics": [
        "Mean and Variance",
        "Normal Distribution",
        "Hypothesis Testing",
        "Confidence Intervals",
    ],
    "Discrete Math": ["Logic", "Proof Techniques", "Combinatorics", "Graph Theory"],
}


class LearningEngine:
    """Single-learner computation engine (no persistence)."""

    def __init__(self, learner_id: str, alpha: float = 0.3, module_id: str = "core") -> None:
        self.learner_id = learner_id
        self.alpha = float(alpha)
        self.moule_id = module_id
        self.attempt_log: list[AttemptEvent] = []
        self.subtopic_state: dict[str, dict[str, Any]] = {}

    def process_attempt(self, event: AttemptEvent) -> StudentStateResponse:
        self._validate_topic_subtopic(event.topic, event.subtopic)
        logged_event = self._with_timestamp(event)

        state = self.subtopic_state.setdefault(
            logged_event.subtopic,
            {
                "topic": logged_event.topic,
                "mastery": 0.5,
                "attempts": 0,
                "correct_attempts": 0,
                "last_updated": logged_event.timestamp,
            },
        )

        old_mastery = float(state["mastery"])
        score = 1.0 if logged_event.correctness else 0.0
        new_mastery = self.alpha * score + (1.0 - self.alpha) * old_mastery

        state["mastery"] = self._clamp01(new_mastery)
        state["attempts"] = int(state["attempts"]) + 1
        if logged_event.correctness:
            state["correct_attempts"] = int(state["correct_attempts"]) + 1
        state["last_updated"] = logged_event.timestamp

        self.attempt_log.append(logged_event)
        return self.get_state()

    def get_state(self) -> StudentStateResponse:
        subtopics: list[SubtopicState] = []
        for subtopic, state in self.subtopic_state.items():
            subtopics.append(
                SubtopicState(
                    module_id=self.module_id,
                    topic_id=str(state["topic"]),
                    subtopic_id=subtopic,
                    mastery=float(state["mastery"]),
                    confidence=float(state["mastery"]),
                    xp=int(state["attempts"]),
                    decay_risk_score=0.0,
                    last_interaction_at=state["last_updated"],
                    attempts=int(state["attempts"]),
                    correct_attempts=int(state["correct_attempts"]),
                )
            )

        return StudentStateResponse(
            learner_id=self.learner_id,
            xp_total=sum(s.xp for s in subtopics),
            updated_at=datetime.now(timezone.utc),
            subtopics=subtopics,
        )

    def get_weak_topics(self, n: int = 3) -> list[tuple[str, float]]:
        ranked = sorted(
            self.subtopic_state.items(),
            key=lambda item: float(item[1]["mastery"]),
        )
        return [(subtopic, float(state["mastery"])) for subtopic, state in ranked[:n]]

    @staticmethod
    def _clamp01(value: float) -> float:
        return max(0.0, min(1.0, value))

    @staticmethod
    def _validate_topic_subtopic(topic: str, subtopic: str) -> None:
        if topic not in TOPIC_TREE:
            raise ValueError(f"Unknown topic: {topic}")
        if subtopic not in TOPIC_TREE[topic]:
            raise ValueError(
                f"Subtopic '{subtopic}' does not belong to topic '{topic}'"
            )

    @staticmethod
    def _with_timestamp(event: AttemptEvent) -> AttemptEvent:
        if event.timestamp is not None:
            return event
        return event.model_copy(update={"timestamp": datetime.now(timezone.utc)})
