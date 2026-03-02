from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.engine.repetition import build_due_reviews_response
from app.engine.state_engine import apply_inactivity_decay
from app.schemas.review import DueReviewsResponse
from app.schemas.state import StudentStateResponse
from app.store.memory import store

router = APIRouter(tags=["students"])


def _now_like(reference: datetime) -> datetime:
    if reference.tzinfo is None:
        return datetime.utcnow()
    return datetime.now(reference.tzinfo)


@router.get("/students/{learner_id}/state", response_model=StudentStateResponse)
def get_student_state(learner_id: str) -> StudentStateResponse:
    state = store.get(learner_id)
    if state is None:
        raise HTTPException(status_code=404, detail="learner state not found")

    now = _now_like(state.updated_at)
    return apply_inactivity_decay(state, now)


@router.get("/students/{learner_id}/reviews/due", response_model=DueReviewsResponse)
def get_due_reviews(learner_id: str) -> DueReviewsResponse:
    """Return frontend-ready queue of subtopics that are due for review."""

    state = store.get(learner_id)
    if state is None:
        raise HTTPException(status_code=404, detail="learner state not found")

    now = _now_like(state.updated_at)
    decayed_state = apply_inactivity_decay(state, now)
    return build_due_reviews_response(decayed_state, now)
