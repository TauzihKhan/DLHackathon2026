from fastapi import APIRouter

from app.engine.state_engine import update_state
from app.schemas.event import LearningEvent
from app.schemas.state import StudentStateResponse
from app.store.in_memory_store import store

router = APIRouter(tags=["events"])


@router.post("/events", response_model=StudentStateResponse)
def post_event(event: LearningEvent) -> StudentStateResponse:
    prev_state = store.get(event.learner_id)
    next_state = update_state(event, prev_state)
    store.save(next_state)
    return next_state
