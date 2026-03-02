from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.store.memory import store

client = TestClient(app)


def setup_function() -> None:
    store.clear()


def teardown_function() -> None:
    store.clear()


def test_state_includes_spaced_repetition_fields() -> None:
    learner_id = "sr-state-fields"
    payload = {
        "learner_id": learner_id,
        "module_id": "mod-1",
        "topic_id": "topic-1",
        "subtopic_id": "fractions-basics",
        "event_type": "quiz_attempt",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "difficulty": 3,
        "correct": True,
        "response_time_sec": 15.0,
    }

    post = client.post("/events", json=payload)
    assert post.status_code == 200

    state = client.get(f"/students/{learner_id}/state")
    assert state.status_code == 200
    body = state.json()

    assert len(body["subtopics"]) == 1
    subtopic = body["subtopics"][0]
    assert "review_interval_days" in subtopic
    assert "next_review_at" in subtopic
    assert "review_due" in subtopic
    assert subtopic["review_due"] is False


def test_due_reviews_endpoint_returns_due_items() -> None:
    learner_id = "sr-due-list"
    payload = {
        "learner_id": learner_id,
        "module_id": "mod-1",
        "topic_id": "topic-1",
        "subtopic_id": "algebra-foundations",
        "event_type": "quiz_attempt",
        "timestamp": "2025-01-01T00:00:00Z",
        "difficulty": 3,
        "correct": False,
        "response_time_sec": 40.0,
    }

    post = client.post("/events", json=payload)
    assert post.status_code == 200

    due = client.get(f"/students/{learner_id}/reviews/due")
    assert due.status_code == 200
    body = due.json()

    assert body["learner_id"] == learner_id
    assert body["due_count"] >= 1
    assert len(body["items"]) >= 1
    first = body["items"][0]
    assert first["subtopic_id"] == "algebra-foundations"
    assert first["days_overdue"] >= 0
    assert 0 <= first["priority_score"] <= 1

