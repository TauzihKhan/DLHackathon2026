from __future__ import annotations

from datetime import datetime, timedelta

from app.schemas.insight import ReviewQueueItem, SpacedRepetitionPlan
from app.schemas.state import StudentStateResponse, SubtopicState

MIN_INTERVAL_DAYS = 1
MAX_INTERVAL_DAYS = 14


def _base_interval_days(subtopic: SubtopicState) -> int:
    if subtopic.mastery < 0.35:
        interval = 1
    elif subtopic.mastery < 0.55:
        interval = 2
    elif subtopic.mastery < 0.75:
        interval = 4
    elif subtopic.mastery < 0.90:
        interval = 7
    else:
        interval = 10

    if subtopic.confidence < 0.35:
        interval -= 1
    elif subtopic.confidence > 0.75 and subtopic.attempts >= 5:
        interval += 2

    if subtopic.decay_risk_score > 0.60:
        interval -= 1

    return max(MIN_INTERVAL_DAYS, min(MAX_INTERVAL_DAYS, interval))


def _priority_score(subtopic: SubtopicState) -> float:
    score = (0.6 * (1.0 - subtopic.mastery)) + (0.3 * subtopic.decay_risk_score) + (0.1 * (1.0 - subtopic.confidence))
    return max(0.0, min(1.0, score))


def build_spaced_repetition_plan(
    state: StudentStateResponse,
    now: datetime,
) -> SpacedRepetitionPlan:
    queue: list[ReviewQueueItem] = []
    due_now_count = 0
    due_next_24h_count = 0

    for subtopic in state.subtopics:
        interval_days = _base_interval_days(subtopic)
        next_review_at = subtopic.last_interaction_at + timedelta(days=interval_days)
        due_in_days = (next_review_at - now).total_seconds() / 86400.0
        due_now = next_review_at <= now

        if due_now:
            due_now_count += 1
        if due_in_days <= 1.0:
            due_next_24h_count += 1

        queue.append(
            ReviewQueueItem(
                module_id=subtopic.module_id,
                topic_id=subtopic.topic_id,
                subtopic_id=subtopic.subtopic_id,
                interval_days=interval_days,
                due_in_days=round(due_in_days, 2),
                due_now=due_now,
                next_review_at=next_review_at,
                priority_score=round(_priority_score(subtopic), 4),
            )
        )

    queue.sort(key=lambda item: (not item.due_now, item.due_in_days, -item.priority_score))

    return SpacedRepetitionPlan(
        generated_at=now,
        due_now_count=due_now_count,
        due_next_24h_count=due_next_24h_count,
        review_queue=queue,
    )
