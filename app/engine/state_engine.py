from __future__ import annotations
import math
from datetime import datetime
from app.engine.decay import apply_decay_to_mastery, compute_decay_risk_score
from app.engine.repetition import (
    compute_next_review_at,
    compute_review_interval_days,
    is_review_due,
    schedule_for_subtopic,
)
from app.schemas.event import LearningEvent
from app.schemas.state import StudentStateResponse, SubtopicState


def _clamp_01(value: float) -> float:
    return max(
        0.0, min(1.0, value)
    )  # Must always clamp so mastery always between 0 and 1


def _subtopic_key(module_id: str, topic_id: str, subtopic_id: str) -> str:
    return f"{module_id}::{topic_id}::{subtopic_id}"


def empty_student_state(learner_id: str, now: datetime) -> StudentStateResponse:
    """Create an empty learner state snapshot."""

    return StudentStateResponse(
        learner_id=learner_id,
        xp_total=0,
        updated_at=now,
        subtopics=[],
    )


def _index_subtopics(subtopics: list[SubtopicState]) -> dict[str, SubtopicState]:
    return {_subtopic_key(s.module_id, s.topic_id, s.subtopic_id): s for s in subtopics}


def _starting_subtopic(event: LearningEvent) -> SubtopicState:
    initial_interval_days = 1.0
    initial_next_review_at = compute_next_review_at(event.timestamp, initial_interval_days)
    return SubtopicState(
        module_id=event.module_id,
        topic_id=event.topic_id,
        subtopic_id=event.subtopic_id,
        mastery=0.5,  # Defaults at 0.5
        confidence=0.1,
        xp=0,
        decay_risk_score=0.0,
        last_interaction_at=event.timestamp,
        attempts=0,
        correct_attempts=0,
        review_interval_days=initial_interval_days,
        next_review_at=initial_next_review_at,
        review_due=False,
    )


def _xp_delta(event: LearningEvent) -> int:
    base = 10 if event.correct else 2
    difficulty_bonus = max(0, event.difficulty - 1) * (2 if event.correct else 0)
    speed_bonus = 3 if event.correct and event.response_time_sec <= 20 else 0
    return base + difficulty_bonus + speed_bonus


def _updated_mastery(decayed_mastery: float, event: LearningEvent) -> float:
    # Change mastery after learnEvent
    target = 1.0 if event.correct else 0.0
    difficulty_weight = 1.0 + ((event.difficulty - 3) * 0.1)
    learning_rate = 0.15 * difficulty_weight
    return _clamp_01(decayed_mastery + (learning_rate * (target - decayed_mastery)))


def _updated_confidence(prev_confidence: float, attempts: int) -> float:
    evidence_term = 0.18 * math.log1p(attempts)
    return _clamp_01(max(prev_confidence, 0.1 + evidence_term))


def update_state(
    event: LearningEvent,
    prev_state: StudentStateResponse | None,
) -> StudentStateResponse:
    """Apply one event to learner state and return a new snapshot."""

    state = prev_state or empty_student_state(
        event.learner_id, event.timestamp
    )  # If first time updating state
    if state.learner_id != event.learner_id:
        raise ValueError("event learner_id does not match existing state learner_id")

    subtopics_by_key = _index_subtopics(state.subtopics)
    key = _subtopic_key(event.module_id, event.topic_id, event.subtopic_id)
    previous_subtopic = subtopics_by_key.get(key) or _starting_subtopic(event)

    decayed_mastery = apply_decay_to_mastery(
        mastery=previous_subtopic.mastery,
        last_interaction_at=previous_subtopic.last_interaction_at,
        now=event.timestamp,
    )

    attempts = previous_subtopic.attempts + 1
    correct_attempts = previous_subtopic.correct_attempts + (1 if event.correct else 0)
    mastery = _updated_mastery(decayed_mastery, event)
    confidence = _updated_confidence(previous_subtopic.confidence, attempts)
    xp_gain = _xp_delta(event)
    review_interval_days = compute_review_interval_days(
        mastery=mastery,
        confidence=confidence,
        attempts=attempts,
        correct_attempts=correct_attempts,
        decay_risk_score=0.0,
    )
    next_review_at = compute_next_review_at(event.timestamp, review_interval_days)

    updated_subtopic = SubtopicState(
        module_id=event.module_id,
        topic_id=event.topic_id,
        subtopic_id=event.subtopic_id,
        mastery=mastery,
        confidence=confidence,
        xp=previous_subtopic.xp + xp_gain,
        decay_risk_score=0.0,
        last_interaction_at=event.timestamp,
        attempts=attempts,
        correct_attempts=correct_attempts,
        review_interval_days=review_interval_days,
        next_review_at=next_review_at,
        review_due=False,
    )

    subtopics_by_key[key] = updated_subtopic
    subtopics = list(subtopics_by_key.values())
    xp_total = sum(subtopic.xp for subtopic in subtopics)

    return StudentStateResponse(
        learner_id=state.learner_id,
        xp_total=xp_total,
        updated_at=event.timestamp,
        subtopics=subtopics,
    )


def apply_inactivity_decay(
    state: StudentStateResponse,
    now: datetime,
) -> StudentStateResponse:
    """Recompute decay-driven fields for a fresh read-time snapshot."""

    decayed_subtopics: list[SubtopicState] = []
    for subtopic in state.subtopics:
        risk = compute_decay_risk_score(subtopic.last_interaction_at, now)
        interval_days, next_review_at = schedule_for_subtopic(subtopic)
        decayed_subtopics.append(
            SubtopicState(
                module_id=subtopic.module_id,
                topic_id=subtopic.topic_id,
                subtopic_id=subtopic.subtopic_id,
                mastery=apply_decay_to_mastery(
                    mastery=subtopic.mastery,
                    last_interaction_at=subtopic.last_interaction_at,
                    now=now,
                ),
                confidence=subtopic.confidence,
                xp=subtopic.xp,
                decay_risk_score=risk,
                last_interaction_at=subtopic.last_interaction_at,
                attempts=subtopic.attempts,
                correct_attempts=subtopic.correct_attempts,
                review_interval_days=interval_days,
                next_review_at=next_review_at,
                review_due=is_review_due(next_review_at, now),
            )
        )

    return StudentStateResponse(
        learner_id=state.learner_id,
        xp_total=state.xp_total,
        updated_at=now,
        subtopics=decayed_subtopics,
    )
