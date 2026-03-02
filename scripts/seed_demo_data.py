from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.engine.state_engine import update_state
from app.schemas.event import LearningEvent
from app.store.in_memory_store import InMemoryStudentStateStore


def main() -> None:
    learner_id = "demo-learner"
    module_id = "core"
    now = datetime.now(timezone.utc)

    store = InMemoryStudentStateStore()
    prev_state = None

    # Strong topic: mostly correct
    for i in range(10):
        event = LearningEvent(
            learner_id=learner_id,
            module_id=module_id,
            topic_id="Algebra",
            subtopic_id="Quadratics",
            event_type="quiz_attempt",
            timestamp=now + timedelta(minutes=i),
            difficulty=4,
            correct=True,
            response_time_sec=8.0,
        )
        prev_state = update_state(event, prev_state)

    # Weak topic: mostly incorrect
    for i in range(10):
        event = LearningEvent(
            learner_id=learner_id,
            module_id=module_id,
            topic_id="Calculus",
            subtopic_id="Integration",
            event_type="quiz_attempt",
            timestamp=now + timedelta(minutes=10 + i),
            difficulty=4,
            correct=False,
            response_time_sec=18.0,
        )
        prev_state = update_state(event, prev_state)

    # Improving topic: early misses, later hits
    for i in range(10):
        event = LearningEvent(
            learner_id=learner_id,
            module_id=module_id,
            topic_id="Probability",
            subtopic_id="Conditional Probability",
            event_type="quiz_attempt",
            timestamp=now + timedelta(minutes=20 + i),
            difficulty=3,
            correct=(i >= 5),
            response_time_sec=12.0,
        )
        prev_state = update_state(event, prev_state)

    if prev_state is None:
        return

    store.save(prev_state)

    print(f"Learner: {prev_state.learner_id}")
    print(f"XP total: {prev_state.xp_total}")
    print("Subtopic mastery:")
    for subtopic in sorted(prev_state.subtopics, key=lambda s: s.mastery):
        print(
            f"- {subtopic.topic_id} / {subtopic.subtopic_id}: "
            f"{subtopic.mastery:.3f} ({subtopic.correct_attempts}/{subtopic.attempts})"
        )


if __name__ == "__main__":
    main()
