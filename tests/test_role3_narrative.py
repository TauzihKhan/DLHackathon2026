from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.config import get_ai_settings
from app.main import app
from app.store.memory import store

client = TestClient(app)


def _seed_event(learner_id: str) -> None:
    payload = {
        "learner_id": learner_id,
        "module_id": "mod-1",
        "topic_id": "topic-1",
        "subtopic_id": "fractions-basics",
        "event_type": "quiz_attempt",
        "timestamp": "2026-03-01T08:00:00Z",
        "difficulty": 3,
        "correct": False,
        "response_time_sec": 42.0,
    }
    response = client.post("/events", json=payload)
    assert response.status_code == 200


def setup_function() -> None:
    store.clear()
    get_ai_settings.cache_clear()


def teardown_function() -> None:
    store.clear()
    get_ai_settings.cache_clear()


def test_narrative_endpoint_fallback_when_disabled(monkeypatch) -> None:
    learner_id = "learner-fallback-disabled"
    _seed_event(learner_id)

    monkeypatch.setenv("ROLE3_AI_ENABLED", "false")
    get_ai_settings.cache_clear()

    response = client.get(f"/students/{learner_id}/insights/narrative")
    assert response.status_code == 200
    body = response.json()

    assert body["generation_mode"] == "fallback"
    assert body["learner_id"] == learner_id
    assert len(body["practice_questions"]) >= 1
    assert body["source_explanation_facts"]["priority_subtopic_id"] == "fractions-basics"


def test_narrative_endpoint_uses_llm_when_available(monkeypatch) -> None:
    learner_id = "learner-llm-success"
    _seed_event(learner_id)

    monkeypatch.setenv("ROLE3_AI_ENABLED", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    get_ai_settings.cache_clear()

    import app.engine.narrative as narrative_module

    def fake_complete_with_llm(insight, settings):
        return narrative_module._LLMNarrativeDraft(
            recommended_action="Attempt one short guided set on fractions-basics.",
            narrative_summary="Fractions basics is currently the top priority.",
            narrative_explanation=(
                "Mastery and confidence signals indicate this subtopic needs reinforcement."
            ),
            practice_questions=[
                {
                    "question": "Convert 3/4 into a decimal and explain the step.",
                    "intent": "Check concept translation.",
                    "difficulty": 3,
                }
            ]
            * settings.practice_question_count,
        )

    monkeypatch.setattr(narrative_module, "_complete_with_llm", fake_complete_with_llm)

    response = client.get(f"/students/{learner_id}/insights/narrative")
    assert response.status_code == 200
    body = response.json()

    assert body["generation_mode"] == "llm"
    assert body["recommended_action"] == "Attempt one short guided set on fractions-basics."
    assert len(body["practice_questions"]) == 3


def test_narrative_endpoint_falls_back_on_llm_error(monkeypatch) -> None:
    learner_id = "learner-llm-failure"
    _seed_event(learner_id)

    monkeypatch.setenv("ROLE3_AI_ENABLED", "true")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    get_ai_settings.cache_clear()

    import app.engine.narrative as narrative_module

    def fail_complete_with_llm(insight, settings):
        raise RuntimeError("simulated llm failure")

    monkeypatch.setattr(narrative_module, "_complete_with_llm", fail_complete_with_llm)

    response = client.get(f"/students/{learner_id}/insights/narrative")
    assert response.status_code == 200
    body = response.json()

    assert body["generation_mode"] == "fallback"
    assert len(body["practice_questions"]) == 3

