from __future__ import annotations

from datetime import datetime, timedelta, timezone
from random import Random
from typing import Dict, List

from app.engine.state_engine import update_state
from app.schemas.event import LearningEvent
from app.store.in_memory_store import store

TOPIC_PROFILES: List[Dict[str, object]] = [
    {
        "topic_id": "Algebra",
        "subtopics": ["Linear equations", "Quadratics", "Polynomials"],
        "correct_prob": 0.78,
    },
    {
        "topic_id": "Geometry",
        "subtopics": ["Triangles", "Circles", "Coordinate geometry"],
        "correct_prob": 0.66,
    },
    {
        "topic_id": "Trigonometry identities",
        "subtopics": ["Basic identities", "Transformations", "Applications"],
        "correct_prob": 0.48,
    },
    {
        "topic_id": "Calculus limits",
        "subtopics": ["Limit laws", "Continuity", "L'Hospital rule"],
        "correct_prob": 0.43,
    },
]

DEMO_LEARNER_IDS = ["student-001", "demo-learner"] + [
    f"new_student_{idx:03d}" for idx in range(1, 21)
]


def _build_demo_events(learner_id: str, seed: int) -> List[LearningEvent]:
    rng = Random(seed)
    now = datetime.now(timezone.utc).replace(hour=18, minute=0, second=0, microsecond=0)
    events: List[LearningEvent] = []

    for day_offset in range(13, -1, -1):
        day_start = (now - timedelta(days=day_offset)).replace(
            hour=9, minute=0, second=0, microsecond=0
        )
        timeline_index = 13 - day_offset
        progress = timeline_index / 13.0 if 13 else 0.0

        # Progressive improvement with daily jitter and occasional outliers.
        day_accuracy = 0.32 + (progress * 0.42)
        day_accuracy += ((seed + day_offset * 7) % 11 - 5) * 0.012
        if (seed + day_offset) % 9 == 0:
            day_accuracy -= 0.18  # dip outlier
        if (seed + day_offset) % 13 == 0:
            day_accuracy += 0.12  # spike outlier
        day_accuracy = max(0.18, min(0.90, day_accuracy))

        # Richer daily quiz volume gives more natural non-binary scores.
        quiz_attempts = rng.randint(4, 7)
        for slot in range(quiz_attempts):
            topic_profile = TOPIC_PROFILES[rng.randrange(len(TOPIC_PROFILES))]
            topic_id = str(topic_profile["topic_id"])
            subtopics = topic_profile["subtopics"]
            subtopic_id = str(subtopics[rng.randrange(len(subtopics))])
            topic_bias = (float(topic_profile["correct_prob"]) - 0.60) * 0.35
            attempt_accuracy = max(
                0.10, min(0.95, day_accuracy + topic_bias + rng.uniform(-0.05, 0.05))
            )
            correct = rng.random() < attempt_accuracy
            difficulty = rng.randint(2, 5)
            response_base = 20.0 if correct else 38.0
            response_time_sec = round(
                max(7.0, response_base + rng.uniform(-4.0, 12.0) + difficulty * 0.8), 2
            )
            timestamp = day_start + timedelta(minutes=slot * 32 + rng.randint(0, 14))

            events.append(
                LearningEvent(
                    learner_id=learner_id,
                    module_id="math",
                    topic_id=topic_id,
                    subtopic_id=subtopic_id,
                    event_type="quiz_attempt",
                    timestamp=timestamp,
                    difficulty=difficulty,
                    correct=correct,
                    response_time_sec=response_time_sec,
                )
            )

        # Add assignment/flashcard activity for richer tab data.
        extra_events = []
        if rng.random() < 0.70:
            extra_events.append("assignment_attempt")
        if rng.random() < 0.55:
            extra_events.append("flashcard_review")

        for slot, event_type in enumerate(extra_events):
            topic_profile = TOPIC_PROFILES[rng.randrange(len(TOPIC_PROFILES))]
            topic_id = str(topic_profile["topic_id"])
            subtopics = topic_profile["subtopics"]
            subtopic_id = str(subtopics[rng.randrange(len(subtopics))])
            extra_accuracy = max(
                0.12, min(0.92, day_accuracy - 0.06 + rng.uniform(-0.08, 0.08))
            )
            correct = rng.random() < extra_accuracy
            difficulty = rng.randint(2, 5)
            response_base = 22.0 if correct else 40.0
            response_time_sec = round(
                max(8.0, response_base + rng.uniform(-5.0, 11.0) + difficulty * 0.9), 2
            )
            timestamp = day_start + timedelta(
                hours=5 + slot, minutes=rng.randint(0, 45)
            )

            events.append(
                LearningEvent(
                    learner_id=learner_id,
                    module_id="math",
                    topic_id=topic_id,
                    subtopic_id=subtopic_id,
                    event_type=event_type,
                    timestamp=timestamp,
                    difficulty=difficulty,
                    correct=correct,
                    response_time_sec=response_time_sec,
                )
            )

    events.sort(key=lambda event: event.timestamp)
    return events


def seed_learner_if_missing(learner_id: str, seed: int) -> bool:
    if store.get(learner_id) is not None:
        return False

    events = _build_demo_events(learner_id, seed)
    next_state = None
    for event in events:
        next_state = update_state(event, next_state)
        store.append_event(event)

    if next_state is not None:
        store.save(next_state)
        return True
    return False


def seed_demo_data_if_needed() -> int:
    seeded_count = 0
    for idx, learner_id in enumerate(DEMO_LEARNER_IDS):
        if seed_learner_if_missing(learner_id, seed=20260303 + idx):
            seeded_count += 1
    return seeded_count


def seed_demo_for_learner_id(learner_id: str) -> bool:
    if not learner_id:
        return False

    allowed = (
        learner_id == "demo-learner"
        or learner_id.startswith("new_student_")
        or learner_id.startswith("student-")
    )
    if not allowed:
        return False

    derived_seed = 20260303 + sum(ord(char) for char in learner_id)
    return seed_learner_if_missing(learner_id, seed=derived_seed)
