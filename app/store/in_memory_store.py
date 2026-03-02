from __future__ import annotations

from threading import Lock
from typing import Optional

from app.schemas.event import LearningEvent
from app.schemas.state import StudentStateResponse


class InMemoryStudentStateStore:
    """Demo in-memory learner state store keyed by learner_id."""

    def __init__(self) -> None:
        self._states: dict[str, StudentStateResponse] = {}
        self._events: dict[str, list[LearningEvent]] = {}
        self._lock = Lock()

    def get(self, learner_id: str) -> Optional[StudentStateResponse]:
        with self._lock:
            state = self._states.get(learner_id)
            return state.model_copy(deep=True) if state is not None else None

    def save(self, state: StudentStateResponse) -> None:
        with self._lock:
            self._states[state.learner_id] = state.model_copy(deep=True)

    def append_event(self, event: LearningEvent) -> None:
        with self._lock:
            learner_events = self._events.setdefault(event.learner_id, [])
            learner_events.append(event.model_copy(deep=True))

    def get_events(self, learner_id: str) -> list[LearningEvent]:
        with self._lock:
            events = self._events.get(learner_id, [])
            return [event.model_copy(deep=True) for event in events]

    def clear(self) -> None:
        with self._lock:
            self._states.clear()
            self._events.clear()


store = InMemoryStudentStateStore()
