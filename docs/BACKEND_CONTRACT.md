# Backend Contract (Role 1.1 + Role 1.2)

Purpose: keep both backend branches aligned while two people implement Role 1 in parallel.

## Owners
- Role 1.1 (you): learning-state engine + decay + core metrics.
- Role 1.2 (partner): API integration + storage wiring + response assembly.

## Branch Model
- Base integration branch: `backend`
- Your branch: `backend-1`
- Partner branch: `backend-2`
- Merge policy: both branches merge into `backend` in small PRs; rebase/merge from `backend` at least daily.

## Source of Truth Docs
- Problem/decisions: `CONTEXT.md`
- Team ownership: `docs/ROLES.md`
- Structure boundaries: `docs/PROJECT_STRUCTURE.md`
- This contract: `docs/BACKEND_CONTRACT.md`

## Locked API Contract (v0)

### `POST /events`
- Request body (`LearningEvent`):
  - `learner_id: str`
  - `module_id: str`
  - `topic_id: str`
  - `subtopic_id: str`
  - `event_type: "quiz_attempt" | "assignment_attempt" | "flashcard_review"`
  - `timestamp: datetime`
  - `difficulty: int` (1-5)
  - `correct: bool`
  - `response_time_sec: float` (>0)
- Response: `{ "status": "ok" }`

### `GET /students/{id}/state`
- Response (shape-level lock):
  - `learner_id: str`
  - `xp_total: int`
  - `updated_at: datetime`
  - `subtopics: list[SubtopicState]`

- `SubtopicState`:
  - `module_id: str`
  - `topic_id: str`
  - `subtopic_id: str`
  - `mastery: float` (0.0-1.0)
  - `confidence: float` (0.0-1.0)
  - `xp: int`
  - `decay_risk_score: float` (0.0-1.0)
  - `last_interaction_at: datetime`
  - `attempts: int`
  - `correct_attempts: int`

### `GET /students/{id}/insights`
- Response (shape-level lock):
  - `learner_id: str`
  - `generated_at: datetime`
  - `weak_subtopics: list[str]`
  - `priority_subtopic_id: str | null`
  - `recommended_action: str`
  - `reason_codes: list[str]`
  - `explanation_facts: dict[str, str | float | int]`
  - `spaced_repetition` (additive):
    - `generated_at: datetime`
    - `due_now_count: int`
    - `due_next_24h_count: int`
    - `review_queue: list[{ module_id, topic_id, subtopic_id, interval_days, due_in_days, due_now, next_review_at, priority_score }]`

### `GET /students/{id}/spaced-repetition`
- Response (shape-level lock):
  - `generated_at: datetime`
  - `due_now_count: int`
  - `due_next_24h_count: int`
  - `review_queue: list[{ module_id, topic_id, subtopic_id, interval_days, due_in_days, due_now, next_review_at, priority_score }]`

## Locked Metric Semantics (v0)
- `mastery`: estimated knowledge level per subtopic in `[0, 1]`.
- `confidence`: stability of estimate in `[0, 1]`; increases with evidence.
- `decay_risk_score`: forgetting risk in `[0, 1]`; increases with inactivity.
- `weak_subtopics`: subtopics selected by low mastery and/or high decay risk.

Exact formulas can evolve, but ranges and meaning above cannot change without agreement.

## File Ownership Split

### Role 1.1 primary files
- `app/engine/state_engine.py`
- `app/engine/decay.py`
- `app/engine/policy.py`
- `app/engine/explain.py`
- `app/schemas/state.py` (state fields, metric definitions)

### Role 1.2 primary files
- `app/api/routers/events.py`
- `app/api/routers/students.py`
- `app/api/routers/insights.py`
- `app/store/in_memory_store.py`
- `app/main.py` (router registration)
- `app/schemas/insight.py` (response assembly models)

### Shared file rule
- `app/schemas/event.py` is shared; changes require sync in both branches.

## Current Build Status (As of 2026-03-01)

Completed in `backend-1` (Role 1.1):
- `app/schemas/event.py`
- `app/schemas/state.py`
- `app/schemas/insight.py`
- `app/engine/decay.py`
- `app/engine/state_engine.py`
- `app/engine/policy.py`
- `app/engine/explain.py`

Role 1.1 remaining:
- none for core v0 contracts

Role 1.2 start point (safe to begin now):
- `app/store/in_memory_store.py` using `StudentStateResponse` keyed by `learner_id`
- `app/api/routers/events.py` calling `update_state(...)`
- `app/api/routers/students.py` calling `apply_inactivity_decay(...)`
- `app/api/routers/insights.py` consuming `generate_policy(...)` + `build_insight_response(...)`
- `app/main.py` router registration

Important: Role 1.2 should not change learning formulas in `app/engine/*`; treat engine outputs as source of truth.

## Non-Breaking Change Rules
- Do not rename existing JSON keys once used by frontend.
- Additive changes are allowed (new optional fields).
- If a required field must change, update:
  - `docs/BACKEND_CONTRACT.md`
  - affected schema files
  - both branches in the same day.

## Integration Handshake (Before Merge to `backend`)
- Confirm endpoints still return locked keys.
- Confirm `mastery/confidence/decay_risk_score` stay in `[0,1]`.
- Confirm `event_type` literals unchanged.
- Confirm both branches pass local smoke check:
  - app starts
  - `POST /events` works
  - `GET /students/{id}/state` works
  - `GET /students/{id}/insights` works
  - `GET /students/{id}/spaced-repetition` works

## Codex Session Bootstrap Prompt (for both of you)
Use this at the top of each Codex session:

"Read `README.md`, `CONTEXT.md`, `docs/ROLES.md`, and `docs/BACKEND_CONTRACT.md`.
I am working on Role 1.x. Follow the locked contracts and do not rename API keys."

## Codex Session Bootstrap Prompt (Role 1.2 specific)
Use this for partner sessions:

"Read `README.md`, `CONTEXT.md`, `docs/ROLES.md`, and `docs/BACKEND_CONTRACT.md`.
Implement only Role 1.2 files (`api`, `store`, `main` wiring).
Do not modify formulas in `app/engine/*`. Use existing schemas and locked response keys."

## Spaced Repetition Note
Current backend includes explicit spaced-repetition scheduling in insights output (`spaced_repetition.review_queue`).
Review urgency still uses inactivity decay and decay-risk prioritization, now with computed next-review timing.
