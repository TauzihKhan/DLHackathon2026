from __future__ import annotations

from threading import Lock

from app.schemas.state import StudentStateResponse


class InMemoryStudentStateStore:
    """Demo in-memory learner state store keyed by learner_id."""

    def __init__(self) -> None:
        self._states: dict[str, StudentStateResponse] = {}
        self._lock = Lock()

    def get(self, learner_id: str) -> StudentStateResponse | None:
        with self._lock:
            state = self._states.get(learner_id)
            return state.model_copy(deep=True) if state is not None else None

    def save(self, state: StudentStateResponse) -> None:
        with self._lock:
            self._states[state.learner_id] = state.model_copy(deep=True)

    def clear(self) -> None:
        with self._lock:
            self._states.clear()


store = InMemoryStudentStateStore()
