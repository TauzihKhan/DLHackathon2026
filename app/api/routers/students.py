from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.engine.spaced_repetition import build_spaced_repetition_plan
from app.engine.state_engine import apply_inactivity_decay
from app.schemas.event import LearningEvent
from app.schemas.insight import SpacedRepetitionPlan
from app.schemas.state import StudentStateResponse
from app.store.demo_seed import seed_demo_for_learner_id
from app.store.in_memory_store import store

router = APIRouter(tags=["students"])


def _now_like(reference: datetime) -> datetime:
    if reference.tzinfo is None:
        return datetime.utcnow()
    return datetime.now(reference.tzinfo)


def _get_state_or_404(learner_id: str) -> StudentStateResponse:
    state = store.get(learner_id)
    if state is None and seed_demo_for_learner_id(learner_id):
        state = store.get(learner_id)
    if state is None:
        raise HTTPException(status_code=404, detail="learner state not found")
    return state


def _topic_accuracy_from_state(state: StudentStateResponse) -> List[Dict[str, Any]]:
    topic_rollup: Dict[str, Dict[str, float]] = {}
    for subtopic in state.subtopics:
        bucket = topic_rollup.setdefault(
            subtopic.topic_id,
            {"attempts": 0.0, "correct_attempts": 0.0, "response_total": 0.0},
        )
        bucket["attempts"] += float(subtopic.attempts)
        bucket["correct_attempts"] += float(subtopic.correct_attempts)
        # We do not persist per-event time in state, so this is a simple estimate.
        bucket["response_total"] += float(subtopic.attempts) * 30.0

    topics: List[Dict[str, Any]] = []
    for topic_id, values in topic_rollup.items():
        attempts = int(values["attempts"])
        correct_attempts = int(values["correct_attempts"])
        accuracy = (correct_attempts / attempts) if attempts else 0.0
        avg_response = (values["response_total"] / attempts) if attempts else 0.0
        topics.append(
            {
                "topic_id": topic_id,
                "attempts": attempts,
                "correct_attempts": correct_attempts,
                "accuracy": round(accuracy, 4),
                "accuracy_percent": round(accuracy * 100.0, 1),
                "avg_response_time_sec": round(avg_response, 2),
            }
        )

    topics.sort(key=lambda item: (item["accuracy"], item["topic_id"]))
    return topics


def _build_assignments_from_state(state: StudentStateResponse) -> List[Dict[str, Any]]:
    now = _now_like(state.updated_at)
    ranked = sorted(
        state.subtopics,
        key=lambda subtopic: (subtopic.mastery, -subtopic.decay_risk_score),
    )

    items: List[Dict[str, Any]] = []
    for idx, subtopic in enumerate(ranked[:8]):
        attempts = int(subtopic.attempts)
        accuracy = (
            (subtopic.correct_attempts / subtopic.attempts) * 100.0
            if subtopic.attempts > 0
            else subtopic.mastery * 100.0
        )
        status_value = "done" if subtopic.mastery >= 0.7 else "pending"
        due_date = None
        if status_value == "pending":
            due_date = (now + timedelta(days=idx + 1)).date().isoformat()

        items.append(
            {
                "assignment_id": f"asg-{subtopic.topic_id.lower().replace(' ', '-')}-{subtopic.subtopic_id.lower().replace(' ', '-')}",
                "title": f"{subtopic.topic_id}: {subtopic.subtopic_id}",
                "topic_id": subtopic.topic_id,
                "subtopic_id": subtopic.subtopic_id,
                "status": status_value,
                "attempts": attempts,
                "accuracy_percent": round(accuracy, 1),
                "last_activity_at": subtopic.last_interaction_at.isoformat(),
                "due_date": due_date,
            }
        )

    return items


def _build_tests_from_state(state: StudentStateResponse) -> List[Dict[str, Any]]:
    if not state.subtopics:
        return []

    attempts = int(sum(subtopic.attempts for subtopic in state.subtopics))
    correct_attempts = int(sum(subtopic.correct_attempts for subtopic in state.subtopics))
    score = (correct_attempts / attempts) * 100.0 if attempts else 0.0
    topic_count = len({subtopic.topic_id for subtopic in state.subtopics})

    return [
        {
            "test_id": f"diagnostic-{state.updated_at.date().isoformat()}",
            "test_name": "Diagnostic Snapshot",
            "taken_on": state.updated_at.date().isoformat(),
            "score_percent": round(score, 1),
            "attempts": attempts,
            "correct_attempts": correct_attempts,
            "topic_count": topic_count,
        }
    ]


def _is_demo_learner(learner_id: str) -> bool:
    return (
        learner_id == "demo-learner"
        or learner_id == "student-001"
        or learner_id.startswith("new_student_")
    )


def _event_study_minutes(event: LearningEvent) -> float:
    # Demo-friendly estimate for real effort per interaction (not literal response seconds).
    base_by_event_type = {
        "quiz_attempt": 18.0,
        "assignment_attempt": 32.0,
        "flashcard_review": 14.0,
    }
    base = base_by_event_type.get(event.event_type, 16.0)
    difficulty_boost = max(0.0, float(event.difficulty) - 1.0) * 3.2
    response_adjustment = max(0.0, float(event.response_time_sec)) / 120.0
    return base + difficulty_boost + response_adjustment


def _styled_demo_test_score(
    learner_id: str,
    day_key: str,
    raw_score: float,
    day_index: int,
    total_days: int,
    previous_score: Optional[float],
) -> float:
    progress = day_index / max(1, total_days - 1)
    trend_target = 34.0 + (progress * 46.0)
    seed_value = sum(ord(ch) for ch in f"{learner_id}:{day_key}")
    noise = ((seed_value % 13) - 6) * 1.2
    outlier = 0.0
    if seed_value % 17 == 0:
        outlier -= 13.0
    elif seed_value % 19 == 0:
        outlier += 9.0

    score = (raw_score * 0.60) + (trend_target * 0.40) + noise + outlier
    if previous_score is not None:
        if score > previous_score + 9.0:
            score = previous_score + 9.0
        if score < previous_score - 11.0:
            score = previous_score - 11.0

    return round(max(8.0, min(97.5, score)), 1)


def _streak_metrics(events: List[LearningEvent]) -> Dict[str, Any]:
    activity_days = sorted({event.timestamp.date() for event in events})
    if not activity_days:
        return {
            "active_days": 0,
            "current_streak_days": 0,
            "longest_streak_days": 0,
            "last_active_date": None,
        }

    longest = 1
    run = 1
    for idx in range(1, len(activity_days)):
        if activity_days[idx] - activity_days[idx - 1] == timedelta(days=1):
            run += 1
        else:
            run = 1
        longest = max(longest, run)

    current = 1
    for idx in range(len(activity_days) - 1, 0, -1):
        if activity_days[idx] - activity_days[idx - 1] == timedelta(days=1):
            current += 1
        else:
            break

    return {
        "active_days": len(activity_days),
        "current_streak_days": current,
        "longest_streak_days": longest,
        "last_active_date": activity_days[-1].isoformat(),
    }


@router.get("/students/{learner_id}/state", response_model=StudentStateResponse)
def get_student_state(learner_id: str) -> StudentStateResponse:
    state = _get_state_or_404(learner_id)

    now = _now_like(state.updated_at)
    return apply_inactivity_decay(state, now)


@router.get(
    "/students/{learner_id}/spaced-repetition",
    response_model=SpacedRepetitionPlan,
)
def get_spaced_repetition_plan(learner_id: str) -> SpacedRepetitionPlan:
    state = _get_state_or_404(learner_id)

    now = _now_like(state.updated_at)
    decayed_state = apply_inactivity_decay(state, now)
    return build_spaced_repetition_plan(decayed_state, now)


@router.get("/students/{learner_id}/statistics/study-time")
def get_study_time_statistics(learner_id: str) -> Dict[str, Any]:
    state = _get_state_or_404(learner_id)
    events = store.get_events(learner_id)

    by_day_minutes: Dict[str, float] = {}
    by_event_type_minutes: Dict[str, float] = {}
    total_minutes = 0.0

    for event in events:
        minutes = _event_study_minutes(event)
        day_key = event.timestamp.date().isoformat()
        by_day_minutes[day_key] = by_day_minutes.get(day_key, 0.0) + minutes
        by_event_type_minutes[event.event_type] = (
            by_event_type_minutes.get(event.event_type, 0.0) + minutes
        )
        total_minutes += minutes

    last_7_days = [
        {"date": day, "minutes": round(minutes, 2)}
        for day, minutes in sorted(by_day_minutes.items())[-7:]
    ]
    by_event_type = [
        {"event_type": event_type, "minutes": round(minutes, 2)}
        for event_type, minutes in sorted(by_event_type_minutes.items())
    ]
    streak = _streak_metrics(events)

    return {
        "learner_id": learner_id,
        "updated_at": _now_like(state.updated_at).isoformat(),
        "total_minutes": round(total_minutes, 2),
        "total_hours": round(total_minutes / 60.0, 2),
        "session_count": len(events),
        "last_7_days": last_7_days,
        "by_event_type": by_event_type,
        "active_days": streak["active_days"],
        "current_streak_days": streak["current_streak_days"],
        "longest_streak_days": streak["longest_streak_days"],
        "last_active_date": streak["last_active_date"],
    }


@router.get("/students/{learner_id}/statistics/topic-accuracy")
def get_topic_accuracy_statistics(learner_id: str) -> Dict[str, Any]:
    state = _get_state_or_404(learner_id)
    topics = _topic_accuracy_from_state(state)
    return {
        "learner_id": learner_id,
        "updated_at": _now_like(state.updated_at).isoformat(),
        "topics": topics,
    }


@router.get("/students/{learner_id}/assignments")
def get_assignments(
    learner_id: str,
    status: str = Query(default="all", pattern="^(all|pending|done)$"),
) -> Dict[str, Any]:
    state = _get_state_or_404(learner_id)
    events = store.get_events(learner_id)
    assignment_events = [
        event for event in events if event.event_type == "assignment_attempt"
    ]

    if assignment_events:
        grouped: Dict[str, Dict[str, Any]] = {}
        for event in assignment_events:
            key = f"{event.topic_id}::{event.subtopic_id}"
            bucket = grouped.setdefault(
                key,
                {
                    "topic_id": event.topic_id,
                    "subtopic_id": event.subtopic_id,
                    "attempts": 0,
                    "correct_attempts": 0,
                    "last_activity_at": event.timestamp,
                },
            )
            bucket["attempts"] += 1
            bucket["correct_attempts"] += 1 if event.correct else 0
            if event.timestamp > bucket["last_activity_at"]:
                bucket["last_activity_at"] = event.timestamp

        items: List[Dict[str, Any]] = []
        for key, row in grouped.items():
            attempts = int(row["attempts"])
            correct_attempts = int(row["correct_attempts"])
            accuracy = (correct_attempts / attempts) if attempts else 0.0
            status_value = "done" if accuracy >= 0.7 else "pending"
            due_date = None
            if status_value == "pending":
                due_date = (row["last_activity_at"] + timedelta(days=2)).date().isoformat()

            items.append(
                {
                    "assignment_id": f"asg-{key.replace('::', '-').lower().replace(' ', '-')}",
                    "title": f"{row['topic_id']}: {row['subtopic_id']}",
                    "topic_id": row["topic_id"],
                    "subtopic_id": row["subtopic_id"],
                    "status": status_value,
                    "attempts": attempts,
                    "accuracy_percent": round(accuracy * 100.0, 1),
                    "last_activity_at": row["last_activity_at"].isoformat(),
                    "due_date": due_date,
                }
            )

        source = "events"
    else:
        items = _build_assignments_from_state(state)
        source = "state_derived"

    if status != "all":
        items = [item for item in items if item["status"] == status]

    items.sort(key=lambda item: (item["status"], item["due_date"] or "9999-12-31"))
    return {
        "learner_id": learner_id,
        "status_filter": status,
        "source": source,
        "count": len(items),
        "items": items,
    }


def _build_tests_payload(learner_id: str, state: StudentStateResponse) -> Dict[str, Any]:
    events = store.get_events(learner_id)
    quiz_events = [event for event in events if event.event_type == "quiz_attempt"]

    if quiz_events:
        grouped: Dict[str, Dict[str, Any]] = {}
        for event in quiz_events:
            day_key = event.timestamp.date().isoformat()
            bucket = grouped.setdefault(
                day_key,
                {
                    "attempts": 0,
                    "correct_attempts": 0,
                    "topic_ids": set(),
                },
            )
            bucket["attempts"] += 1
            bucket["correct_attempts"] += 1 if event.correct else 0
            bucket["topic_ids"].add(event.topic_id)

        items: List[Dict[str, Any]] = []
        daily_rows = sorted(grouped.items(), key=lambda pair: pair[0])
        previous_score: Optional[float] = None
        for day_index, (day_key, row) in enumerate(daily_rows):
            attempts = int(row["attempts"])
            correct_attempts = int(row["correct_attempts"])
            raw_score = (correct_attempts / attempts) * 100.0 if attempts else 0.0
            if _is_demo_learner(learner_id):
                score = _styled_demo_test_score(
                    learner_id=learner_id,
                    day_key=day_key,
                    raw_score=raw_score,
                    day_index=day_index,
                    total_days=len(daily_rows),
                    previous_score=previous_score,
                )
                previous_score = score
            else:
                score = round(raw_score, 1)
            items.append(
                {
                    "test_id": f"test-{day_key}",
                    "test_name": "Daily Quiz",
                    "taken_on": day_key,
                    "score_percent": round(score, 1),
                    "attempts": attempts,
                    "correct_attempts": correct_attempts,
                    "topic_count": len(row["topic_ids"]),
                }
            )

        items.sort(key=lambda item: item["taken_on"], reverse=True)
        source = "events"
    else:
        items = _build_tests_from_state(state)
        source = "state_derived"

    return {
        "learner_id": learner_id,
        "source": source,
        "count": len(items),
        "items": items,
    }


@router.get("/students/{learner_id}/tests")
def get_tests(learner_id: str) -> Dict[str, Any]:
    state = _get_state_or_404(learner_id)
    return _build_tests_payload(learner_id, state)


@router.get("/students/{learner_id}/tests/summary")
def get_tests_summary(learner_id: str) -> Dict[str, Any]:
    state = _get_state_or_404(learner_id)
    tests_payload = _build_tests_payload(learner_id, state)
    items = tests_payload["items"]

    if not items:
        weakest_topic = None
        if state.subtopics:
            weakest_topic = min(state.subtopics, key=lambda subtopic: subtopic.mastery).topic_id
        return {
            "learner_id": learner_id,
            "total_tests": 0,
            "average_score": 0.0,
            "best_score": 0.0,
            "latest_score": 0.0,
            "weakest_topic": weakest_topic,
            "source": tests_payload["source"],
        }

    scores = [float(item["score_percent"]) for item in items]
    weakest_topic: Optional[str] = None
    if state.subtopics:
        weakest_topic = min(state.subtopics, key=lambda subtopic: subtopic.mastery).topic_id

    return {
        "learner_id": learner_id,
        "total_tests": len(items),
        "average_score": round(sum(scores) / len(scores), 1),
        "best_score": round(max(scores), 1),
        "latest_score": round(scores[0], 1),
        "weakest_topic": weakest_topic,
        "source": tests_payload["source"],
    }
