from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class AttemptEvent(BaseModel):
    topic: str
    subtopic: str
    correctness: bool
    difficulty: float = Field(ge=0.0, le=1.0)
    response_time: float = Field(gt=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

TOPIC_TREE = {
    "Algebra": [
        "Linear Equations",
        "Quadratics",
        "Inequalities",
        "Functions"
    ],
    "Calculus": [
        "Limits",
        "Differentiation",
        "Applications of Derivatives",
        "Integration"
    ],
    "Probability": [
        "Basic Probability",
        "Conditional Probability",
        "Bayes Theorem",
        "Random Variables"
    ],
    "Statistics": [
        "Mean and Variance",
        "Normal Distribution",
        "Hypothesis Testing",
        "Confidence Intervals"
    ],
    "Discrete Math": [
        "Logic",
        "Proof Techniques",
        "Combinatorics",
        "Graph Theory"
    ]
}

from datetime import datetime, timezone
from typing import Any


class MemoryStore:
    def __init__(self, alpha: float = 0.3):
        self.alpha = float(alpha)
        self.attempt_log: list[AttemptEvent] = []
        self.subtopic_state: dict[str, dict[str, Any]] = {}

    def add_attempt(self, event: AttemptEvent) -> AttemptEvent:
        self._validate_topic_subtopic(event.topic, event.subtopic)

        if event.timestamp is None:
            event = event.model_copy(
                update={"timestamp": datetime.now(timezone.utc)}
            )

        state = self.subtopic_state.setdefault(
            event.subtopic,
            {
                "mastery": 0.5,
                "attempts": 0,
                "last_updated": event.timestamp,
            },
        )

        old_mastery = state["mastery"]
        score = 1.0 if event.correctness else 0.0
        new_mastery = self.alpha * score + (1 - self.alpha) * old_mastery

        state["mastery"] = self._clamp01(new_mastery)
        state["attempts"] += 1
        state["last_updated"] = event.timestamp

        self.attempt_log.append(event)
        return event

    def get_state(self) -> dict[str, dict[str, Any]]:
        return {
            subtopic: values.copy()
            for subtopic, values in self.subtopic_state.items()
        }

    def get_weak_topics(self, n: int = 3):
        ranked = sorted(
            self.subtopic_state.items(),
            key=lambda item: item[1]["mastery"],
        )
        return ranked[:n]

    @staticmethod
    def _clamp01(value: float) -> float:
        return max(0.0, min(1.0, value))

    @staticmethod
    def _validate_topic_subtopic(topic: str, subtopic: str):
        if topic not in TOPIC_TREE:
            raise ValueError(f"Unknown topic: {topic}")
        if subtopic not in TOPIC_TREE[topic]:
            raise ValueError(
                f"Subtopic '{subtopic}' does not belong to topic '{topic}'"
            )

if __name__ == "__main__":
    store = MemoryStore()

    event = AttemptEvent(
        topic="Algebra",
        subtopic="Quadratics",
        correctness=True,
        difficulty=0.7,
        response_time=4.2,
    )

    store.add_attempt(event)

    print(store.get_state())
    print(store.get_weak_topics())