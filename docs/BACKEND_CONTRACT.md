# Backend Contract (Role 1 + Role 3)

Purpose: keep backend implementation aligned across roles and prevent API-key/shape drift.

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

### `GET /students/{id}/insights/narrative`
- Purpose: Role 3 natural-language layer on top of deterministic insights.
- Response (shape-level lock):
  - `learner_id: str`
  - `generated_at: datetime`
  - `generation_mode: "llm" | "fallback"`
  - `priority_subtopic_id: str | null`
  - `weak_subtopics: list[str]`
  - `reason_codes: list[str]`
  - `recommended_action: str`
  - `narrative_summary: str`
  - `narrative_explanation: str`
  - `practice_questions: list[PracticeQuestion]`
  - `source_explanation_facts: dict[str, str | float | int]`

- `PracticeQuestion`:
  - `question: str`
  - `intent: str`
  - `difficulty: int` (1-5)

Role 3 reliability semantics:
- Endpoint must never hard-fail because of LLM unavailability.
- If LLM is disabled/misconfigured/fails, response must still return with `generation_mode="fallback"`.
- `source_explanation_facts` should be grounded in deterministic `/insights` evidence.

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
- `app/store/memory.py`
- `app/main.py` (router registration)
- `app/schemas/insight.py` (response assembly models)

### Role 3 primary files
- `app/core/config.py`
- `app/engine/narrative.py`
- `app/schemas/narrative.py`
- `app/api/routers/insights.py` (narrative endpoint wiring)

### Shared file rule
- `app/schemas/event.py` is shared; changes require sync in both branches.

## Current Build Status (As of 2026-03-02)

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
- `app/store/memory.py` using `StudentStateResponse` keyed by `learner_id`
- `app/api/routers/events.py` calling `update_state(...)`
- `app/api/routers/students.py` calling `apply_inactivity_decay(...)`
- `app/api/routers/insights.py` consuming `generate_policy(...)` + `build_insight_response(...)`
- `app/main.py` router registration

Important: Role 1.2 should not change learning formulas in `app/engine/*`; treat engine outputs as source of truth.

Completed for Role 3:
- `app/core/config.py`
- `app/schemas/narrative.py`
- `app/engine/narrative.py`
- `GET /students/{id}/insights/narrative` in `app/api/routers/insights.py`

Role 3 remaining:
- frontend consumption and presentation of narrative payload

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
  - `GET /students/{id}/insights/narrative` works

## Example Narrative Response (contract illustration)

```json
{
  "learner_id": "learner-123",
  "generated_at": "2026-03-02T10:00:00Z",
  "generation_mode": "fallback",
  "priority_subtopic_id": "fractions-basics",
  "weak_subtopics": ["fractions-basics"],
  "reason_codes": ["LOW_MASTERY", "LOW_CONFIDENCE"],
  "recommended_action": "Do 3 targeted medium-difficulty questions on fractions-basics.",
  "narrative_summary": "Current priority is fractions-basics. 1 weak subtopic(s) were detected from the latest learner state.",
  "narrative_explanation": "This recommendation is driven by reason code LOW_MASTERY. The action is grounded in computed mastery, confidence, decay risk, and attempt evidence from the structured backend output.",
  "practice_questions": [
    {
      "question": "Solve one medium-step problem on fractions-basics and explain each step in one sentence.",
      "intent": "Checks conceptual understanding and reduces brittle memorization.",
      "difficulty": 3
    }
  ],
  "source_explanation_facts": {
    "priority_mastery": 0.42,
    "priority_confidence": 0.28,
    "priority_decay_risk_score": 0.31
  }
}
```

## Codex Session Bootstrap Prompt (for both of you)
Use this at the top of each Codex session:

"Read `README.md`, `CONTEXT.md`, `docs/ROLES.md`, and `docs/BACKEND_CONTRACT.md`.
I am working on Role 1.x. Follow the locked contracts and do not rename API keys."

## Codex Session Bootstrap Prompt (Role 1.2 specific)
Use this for partner sessions:

"Read `README.md`, `CONTEXT.md`, `docs/ROLES.md`, and `docs/BACKEND_CONTRACT.md`.
Implement only Role 1.2 files (`api`, `store`, `main` wiring).
Do not modify formulas in `app/engine/*`. Use existing schemas and locked response keys."

## Codex Session Bootstrap Prompt (Role 3 specific)
Use this for AI narrative sessions:

"Read `README.md`, `CONTEXT.md`, `docs/ROLES.md`, and `docs/BACKEND_CONTRACT.md`.
Implement Role 3 narrative only from structured backend signals.
Do not consume raw event logs directly in narrative output.
Do not rename locked response keys for `/students/{id}/insights` or `/students/{id}/insights/narrative`."
