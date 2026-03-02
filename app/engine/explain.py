from __future__ import annotations
from datetime import datetime
from app.engine.policy import PolicyDecision
from app.schemas.insight import InsightResponse
from app.schemas.state import StudentStateResponse, SubtopicState


def _find_priority_subtopic(
    state: StudentStateResponse,
    priority_subtopic_id: str | None,
) -> SubtopicState | None:
    if priority_subtopic_id is None:
        return None

    for subtopic in state.subtopics:
        if subtopic.subtopic_id == priority_subtopic_id:
            return subtopic
    return None


def build_explanation_facts(
    state: StudentStateResponse,
    decision: PolicyDecision,
) -> dict[str, str | float | int]:
    """Build structured evidence payload for explainable recommendations."""

    facts: dict[str, str | float | int] = {
        "xp_total": state.xp_total,
        "weak_subtopic_count": len(decision.weak_subtopics),
        "updated_at": state.updated_at.isoformat(),
    }

    priority = _find_priority_subtopic(state, decision.priority_subtopic_id)
    if priority is None:
        facts["top_reason"] = (
            decision.reason_codes[0] if decision.reason_codes else "NO_DATA"
        )
        return facts

    accuracy = (
        (priority.correct_attempts / priority.attempts)
        if priority.attempts > 0
        else 0.0
    )
    facts.update(
        {
            "priority_module_id": priority.module_id,
            "priority_topic_id": priority.topic_id,
            "priority_subtopic_id": priority.subtopic_id,
            "priority_mastery": round(priority.mastery, 4),
            "priority_confidence": round(priority.confidence, 4),
            "priority_decay_risk_score": round(priority.decay_risk_score, 4),
            "priority_attempts": priority.attempts,
            "priority_correct_attempts": priority.correct_attempts,
            "priority_accuracy": round(accuracy, 4),
            "top_reason": decision.reason_codes[0]
            if decision.reason_codes
            else "GENERAL_REINFORCEMENT",
        }
    )
    return facts


def build_insight_response(
    state: StudentStateResponse,
    decision: PolicyDecision,
    generated_at: datetime,
) -> InsightResponse:
    """Compose final insights payload from state + policy output."""

    return InsightResponse(
        learner_id=state.learner_id,
        generated_at=generated_at,
        weak_subtopics=decision.weak_subtopics,
        priority_subtopic_id=decision.priority_subtopic_id,
        recommended_action=decision.recommended_action,
        reason_codes=decision.reason_codes,
        explanation_facts=build_explanation_facts(state, decision),
    )
