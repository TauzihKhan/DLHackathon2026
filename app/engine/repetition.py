from __future__ import annotations

from datetime import datetime, timedelta

from app.schemas.review import DueReviewItem, DueReviewsResponse
from app.schemas.state import StudentStateResponse, SubtopicState

MIN_REVIEW_INTERVAL_DAYS = 0.25
MAX_REVIEW_INTERVAL_DAYS = 14.0


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def compute_review_interval_days(
    mastery: float,
    confidence: float,
    attempts: int,
    correct_attempts: int,
    decay_risk_score: float,
) -> float:
    """
    Compute next spaced-repetition interval.

    Lower mastery/confidence and higher decay risk produce shorter intervals.
    """

    if mastery < 0.40:
        base = 0.5
    elif mastery < 0.60:
        base = 1.0
    elif mastery < 0.80:
        base = 2.0
    elif mastery < 0.92:
        base = 4.0
    else:
        base = 7.0

    accuracy = (correct_attempts / attempts) if attempts > 0 else 0.0
    confidence_factor = 0.70 + (0.80 * _clamp(confidence, 0.0, 1.0))
    evidence_factor = 0.85 + (0.08 * min(attempts, 5))
    accuracy_factor = 0.80 + (0.40 * _clamp(accuracy, 0.0, 1.0))
    decay_factor = 1.0 - (0.50 * _clamp(decay_risk_score, 0.0, 1.0))

    interval = base * confidence_factor * evidence_factor * accuracy_factor * decay_factor
    return _clamp(interval, MIN_REVIEW_INTERVAL_DAYS, MAX_REVIEW_INTERVAL_DAYS)


def compute_next_review_at(last_interaction_at: datetime, interval_days: float) -> datetime:
    safe_interval = _clamp(interval_days, MIN_REVIEW_INTERVAL_DAYS, MAX_REVIEW_INTERVAL_DAYS)
    return last_interaction_at + timedelta(days=safe_interval)


def is_review_due(next_review_at: datetime, now: datetime) -> bool:
    return now >= next_review_at


def schedule_for_subtopic(subtopic: SubtopicState) -> tuple[float, datetime]:
    """
    Return stable schedule fields for a subtopic.

    If schedule already exists, keep it to avoid read-time drift.
    """

    if subtopic.next_review_at is not None:
        interval = _clamp(
            subtopic.review_interval_days,
            MIN_REVIEW_INTERVAL_DAYS,
            MAX_REVIEW_INTERVAL_DAYS,
        )
        return interval, subtopic.next_review_at

    interval = compute_review_interval_days(
        mastery=subtopic.mastery,
        confidence=subtopic.confidence,
        attempts=subtopic.attempts,
        correct_attempts=subtopic.correct_attempts,
        decay_risk_score=subtopic.decay_risk_score,
    )
    return interval, compute_next_review_at(subtopic.last_interaction_at, interval)


def review_priority_score(subtopic: SubtopicState) -> float:
    """Higher score means the review item should appear earlier in UI."""

    mastery_gap = 1.0 - _clamp(subtopic.mastery, 0.0, 1.0)
    confidence_gap = 1.0 - _clamp(subtopic.confidence, 0.0, 1.0)
    score = (
        (0.55 * mastery_gap)
        + (0.35 * _clamp(subtopic.decay_risk_score, 0.0, 1.0))
        + (0.10 * confidence_gap)
    )
    return _clamp(score, 0.0, 1.0)


def build_due_reviews_response(
    state: StudentStateResponse,
    now: datetime,
) -> DueReviewsResponse:
    """Create a frontend-friendly queue of currently due review items."""

    due_items: list[DueReviewItem] = []
    for subtopic in state.subtopics:
        interval_days, next_review_at = schedule_for_subtopic(subtopic)
        if not is_review_due(next_review_at, now):
            continue

        days_overdue = max(0.0, (now - next_review_at).total_seconds() / 86400.0)
        due_items.append(
            DueReviewItem(
                module_id=subtopic.module_id,
                topic_id=subtopic.topic_id,
                subtopic_id=subtopic.subtopic_id,
                mastery=subtopic.mastery,
                confidence=subtopic.confidence,
                decay_risk_score=subtopic.decay_risk_score,
                review_interval_days=round(interval_days, 4),
                next_review_at=next_review_at,
                days_overdue=round(days_overdue, 4),
                priority_score=round(review_priority_score(subtopic), 4),
            )
        )

    due_items.sort(
        key=lambda item: (item.priority_score, item.days_overdue),
        reverse=True,
    )
    return DueReviewsResponse(
        learner_id=state.learner_id,
        generated_at=now,
        due_count=len(due_items),
        items=due_items,
    )

