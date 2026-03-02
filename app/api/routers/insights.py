from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.engine.explain import build_insight_response
from app.engine.policy import generate_policy
from app.engine.state_engine import apply_inactivity_decay
from app.schemas.insight import InsightResponse
from app.store.memory import store

router = APIRouter(tags=["insights"])


def _now_like(reference: datetime) -> datetime:
    if reference.tzinfo is None:
        return datetime.utcnow()
    return datetime.now(reference.tzinfo)


@router.get("/students/{learner_id}/insights", response_model=InsightResponse)
def get_student_insights(learner_id: str) -> InsightResponse:
    state = store.get(learner_id)
    if state is None:
        raise HTTPException(status_code=404, detail="learner state not found")

    now = _now_like(state.updated_at)
    decayed_state = apply_inactivity_decay(state, now)
    decision = generate_policy(decayed_state)
    return build_insight_response(decayed_state, decision, generated_at=now)
