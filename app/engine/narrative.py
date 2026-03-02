from __future__ import annotations

import json
from datetime import datetime

from openai import OpenAI
from pydantic import BaseModel, Field

from app.core.config import AISettings, get_ai_settings
from app.schemas.insight import InsightResponse
from app.schemas.narrative import NarrativeInsightResponse, PracticeQuestion


class _LLMNarrativeDraft(BaseModel):
    recommended_action: str = Field(min_length=1)
    narrative_summary: str = Field(min_length=1)
    narrative_explanation: str = Field(min_length=1)
    practice_questions: list[PracticeQuestion] = Field(default_factory=list)


def _strip_code_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if len(lines) >= 3:
            cleaned = "\n".join(lines[1:-1]).strip()
    return cleaned


def _difficulty_from_facts(insight: InsightResponse) -> int:
    mastery = insight.explanation_facts.get("priority_mastery")
    if isinstance(mastery, (int, float)):
        if mastery < 0.40:
            return 2
        if mastery < 0.70:
            return 3
        return 4
    return 3


def _fallback_questions(insight: InsightResponse, question_count: int) -> list[PracticeQuestion]:
    subtopic = insight.priority_subtopic_id or "your current focus area"
    base_difficulty = _difficulty_from_facts(insight)

    templates = [
        (
            f"Solve one medium-step problem on {subtopic} and explain each step in one sentence.",
            "Checks conceptual understanding and reduces brittle memorization.",
        ),
        (
            f"Attempt a timed question on {subtopic} in under 90 seconds and note where you hesitated.",
            "Builds retrieval speed and highlights uncertainty points.",
        ),
        (
            f"Create one example and one non-example for {subtopic}, then justify the difference.",
            "Strengthens boundary understanding and error detection.",
        ),
        (
            f"Answer a mixed-difficulty item on {subtopic}, then rewrite the final answer more clearly.",
            "Improves transfer and clarity under test conditions.",
        ),
        (
            f"Teach {subtopic} back in three bullet points without notes.",
            "Tests retention and highlights confidence gaps.",
        ),
    ]

    questions: list[PracticeQuestion] = []
    for idx in range(question_count):
        prompt, intent = templates[idx % len(templates)]
        questions.append(
            PracticeQuestion(
                question=prompt,
                intent=intent,
                difficulty=max(1, min(5, base_difficulty + (idx % 2))),
            )
        )
    return questions


def _fallback_narrative(insight: InsightResponse) -> tuple[str, str, str]:
    priority = insight.priority_subtopic_id or "foundational practice"
    weak_count = len(insight.weak_subtopics)
    top_reason = insight.reason_codes[0] if insight.reason_codes else "GENERAL_REINFORCEMENT"

    summary = (
        f"Current priority is {priority}. "
        f"{weak_count} weak subtopic(s) were detected from the latest learner state."
    )

    explanation = (
        f"This recommendation is driven by reason code {top_reason}. "
        "The action is grounded in computed mastery, confidence, decay risk, and attempt evidence "
        "from the structured backend output."
    )

    recommended_action = insight.recommended_action
    return summary, explanation, recommended_action


def _build_prompt(insight: InsightResponse, question_count: int) -> str:
    payload = {
        "learner_id": insight.learner_id,
        "generated_at": insight.generated_at.isoformat(),
        "weak_subtopics": insight.weak_subtopics,
        "priority_subtopic_id": insight.priority_subtopic_id,
        "recommended_action": insight.recommended_action,
        "reason_codes": insight.reason_codes,
        "explanation_facts": insight.explanation_facts,
    }
    payload_json = json.dumps(payload, ensure_ascii=True)

    return (
        "You are the Role 3 AI Explainer for a learning analytics system.\n"
        "Use only the provided structured signals.\n"
        "Do not invent metrics, events, or learner history.\n"
        "Return strict JSON only, no markdown, with this exact shape:\n"
        "{\n"
        '  "recommended_action": string,\n'
        '  "narrative_summary": string,\n'
        '  "narrative_explanation": string,\n'
        '  "practice_questions": [\n'
        "    {\n"
        '      "question": string,\n'
        '      "intent": string,\n'
        '      "difficulty": integer from 1 to 5\n'
        "    }\n"
        "  ]\n"
        "}\n"
        f"Generate exactly {question_count} practice questions.\n"
        "Keep summary to max 2 sentences. Keep explanation to max 4 sentences.\n"
        "Input structured signals:\n"
        f"{payload_json}"
    )


def _complete_with_llm(insight: InsightResponse, settings: AISettings) -> _LLMNarrativeDraft:
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not configured")

    client = OpenAI(
        api_key=settings.openai_api_key,
        timeout=settings.request_timeout_seconds,
    )

    response = client.responses.create(
        model=settings.openai_model,
        temperature=settings.temperature,
        max_output_tokens=settings.max_output_tokens,
        input=[
            {"role": "system", "content": "You convert learner metrics into clear coaching text."},
            {
                "role": "user",
                "content": _build_prompt(insight, settings.practice_question_count),
            },
        ],
    )

    raw_text = getattr(response, "output_text", "") or ""
    cleaned = _strip_code_fences(raw_text)
    if not cleaned:
        raise ValueError("LLM response did not contain text output")

    parsed = json.loads(cleaned)
    draft = _LLMNarrativeDraft.model_validate(parsed)
    if len(draft.practice_questions) != settings.practice_question_count:
        raise ValueError("LLM returned unexpected number of practice questions")
    return draft


def generate_narrative_insight(
    insight: InsightResponse,
    settings: AISettings | None = None,
    generated_at: datetime | None = None,
) -> NarrativeInsightResponse:
    """
    Build Role 3 narrative output from deterministic insights.

    Uses LLM generation when configured; otherwise returns deterministic fallback text.
    """

    cfg = settings or get_ai_settings()
    now = generated_at or insight.generated_at

    if cfg.can_call_llm:
        try:
            draft = _complete_with_llm(insight, cfg)
            return NarrativeInsightResponse(
                learner_id=insight.learner_id,
                generated_at=now,
                generation_mode="llm",
                priority_subtopic_id=insight.priority_subtopic_id,
                weak_subtopics=insight.weak_subtopics,
                reason_codes=insight.reason_codes,
                recommended_action=draft.recommended_action,
                narrative_summary=draft.narrative_summary,
                narrative_explanation=draft.narrative_explanation,
                practice_questions=draft.practice_questions,
                source_explanation_facts=insight.explanation_facts,
            )
        except Exception:
            pass

    summary, explanation, recommended_action = _fallback_narrative(insight)
    return NarrativeInsightResponse(
        learner_id=insight.learner_id,
        generated_at=now,
        generation_mode="fallback",
        priority_subtopic_id=insight.priority_subtopic_id,
        weak_subtopics=insight.weak_subtopics,
        reason_codes=insight.reason_codes,
        recommended_action=recommended_action,
        narrative_summary=summary,
        narrative_explanation=explanation,
        practice_questions=_fallback_questions(insight, cfg.practice_question_count),
        source_explanation_facts=insight.explanation_facts,
    )
