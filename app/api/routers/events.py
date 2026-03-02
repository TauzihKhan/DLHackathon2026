from fastapi import APIRouter

from app.engine.state_engine import update_state
from app.schemas.event import LearningEvent
from app.store.memory import store

router = APIRouter(tags=["events"])


@router.post("/events")
def post_event(event: LearningEvent) -> dict[str, str]:
    prev_state = store.get(event.learner_id)
    next_state = update_state(event, prev_state)
    store.save(next_state)
    return {"status": "ok"}
