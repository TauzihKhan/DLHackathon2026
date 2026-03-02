from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.schemas.state import StudentStateResponse, SubtopicState

LOW_MASTERY_THRESHOLD = 0.60
HIGH_DECAY_RISK_THRESHOLD = 0.50
LOW_CONFIDENCE_THRESHOLD = 0.35


@dataclass(frozen=True)
class PolicyDecision:
    weak_subtopics: list[str]
    priority_subtopic_id: Optional[str]
    recommended_action: str
    reason_codes: list[str]


def _priority_score(subtopic: SubtopicState) -> float:
    # Higher score means higher intervention urgency.
    mastery_gap = 1.0 - subtopic.mastery
    confidence_gap = 1.0 - subtopic.confidence
    return (0.55 * mastery_gap) + (0.35 * subtopic.decay_risk_score) + (0.10 * confidence_gap)


def _is_weak_subtopic(subtopic: SubtopicState) -> bool:
    return (
        subtopic.mastery < LOW_MASTERY_THRESHOLD
        or subtopic.decay_risk_score > HIGH_DECAY_RISK_THRESHOLD
    )


def _reason_codes_for_subtopic(subtopic: SubtopicState) -> list[str]:
    codes: list[str] = []

    if subtopic.mastery < LOW_MASTERY_THRESHOLD:
        codes.append("LOW_MASTERY")
    if subtopic.decay_risk_score > HIGH_DECAY_RISK_THRESHOLD:
        codes.append("HIGH_DECAY_RISK")
    if subtopic.confidence < LOW_CONFIDENCE_THRESHOLD:
        codes.append("LOW_CONFIDENCE")
    if subtopic.attempts < 3:
        codes.append("LOW_EVIDENCE")

    if not codes:
        codes.append("GENERAL_REINFORCEMENT")

    return codes


def _recommended_action(subtopic: Optional[SubtopicState], reason_codes: list[str]) -> str:
    if subtopic is None:
        return "Continue regular practice to build baseline evidence across topics."

    if "HIGH_DECAY_RISK" in reason_codes:
        return f"Review {subtopic.subtopic_id} now with a 5-question quick recap."
    if "LOW_MASTERY" in reason_codes:
        return f"Do 3 targeted medium-difficulty questions on {subtopic.subtopic_id}."
    if "LOW_CONFIDENCE" in reason_codes:
        return f"Take a short mixed quiz on {subtopic.subtopic_id} to stabilize confidence."

    return f"Practice one focused set on {subtopic.subtopic_id} to reinforce retention."


def generate_policy(state: StudentStateResponse) -> PolicyDecision:
    """Choose weak areas and next best action from current learner state."""

    if not state.subtopics:
        return PolicyDecision(
            weak_subtopics=[],
            priority_subtopic_id=None,
            recommended_action="Complete your first practice set to initialize your learning state.",
            reason_codes=["NO_DATA"],
        )

    ranked = sorted(state.subtopics, key=_priority_score, reverse=True)
    weak_subtopics = [s.subtopic_id for s in ranked if _is_weak_subtopic(s)]

    if weak_subtopics:
        priority = next(s for s in ranked if s.subtopic_id == weak_subtopics[0])
    else:
        priority = ranked[0]

    reason_codes = _reason_codes_for_subtopic(priority)
    return PolicyDecision(
        weak_subtopics=weak_subtopics,
        priority_subtopic_id=priority.subtopic_id,
        recommended_action=_recommended_action(priority, reason_codes),
        reason_codes=reason_codes,
    )
