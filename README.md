# DLHackathon2026

Hackathon project repository for building and demoing an end-to-end product quickly.

## Start Here
- Project context: `CONTEXT.md`
- Agent workflow rules: `AGENTS.md`
- Structure guide: `docs/PROJECT_STRUCTURE.md`
- Backend collaboration contract: `docs/BACKEND_CONTRACT.md`

## Team Goal
Ship a reliable demo before the deadline with clear scope and fast iteration.

## Current Status
Lean full-stack MVP scaffold is in place: web UI in `frontend/` and learner-state APIs in `app/`.
Role 3 narrative endpoint is now available on top of deterministic insights.

## Demo-First Structure
- `frontend/`
  - Web client app (pages, components, API calls, UI styling).
- `app/main.py`
  - FastAPI app entrypoint and router registration.
- `app/api/routers/`
  - HTTP endpoints (`/health`, event ingest, state fetch, guidance fetch).
- `app/schemas/`
  - Request/response models for events, state, and guidance payloads.
- `app/engine/`
  - Core learning logic: state updates, policy rules, explainable guidance text.
- `app/store/`
  - Demo persistence layer (start with in-memory; swap later if needed).
- `app/core/`
  - App settings and logging setup.
- `tests/`
  - Critical path tests for state engine and guidance behavior.
- `scripts/`
  - Demo helpers like seed/replay/run scripts.

See `docs/PROJECT_STRUCTURE.md` for the full folder tree and ownership rules.

## Next Steps
- Implement first end-to-end slice: `POST /events` -> state update -> `GET /students/{id}/insights`
- Add run/build/test commands

## Role 3 Narrative Layer (AI Explainer)
- New endpoint: `GET /students/{id}/insights/narrative`
- Input source: existing deterministic insight payload (`policy` + `explanation_facts`)
- Output: natural-language summary/explanation + targeted practice questions
- Reliability rule: if LLM is disabled or fails, endpoint returns deterministic fallback narrative

## Spaced Repetition (Backend v1)
- New endpoint: `GET /students/{id}/reviews/due`
- Purpose: return a frontend-ready queue of subtopics that are currently due for review
- Ranking fields in each item: `priority_score`, `days_overdue`, and schedule fields
- State integration: each subtopic now tracks `review_interval_days`, `next_review_at`, and `review_due`

Backend contract reference:
- Full request/response lock: `docs/BACKEND_CONTRACT.md`
- Folder responsibilities: `docs/PROJECT_STRUCTURE.md`

Environment variables:
- `ROLE3_AI_ENABLED` (default: `true`)
- `OPENAI_API_KEY` (required for live LLM generation)
- `OPENAI_MODEL` (default: `gpt-4.1-mini`)
- `OPENAI_TIMEOUT_SECONDS` (default: `12`)
- `ROLE3_AI_TEMPERATURE` (default: `0.2`)
- `ROLE3_MAX_OUTPUT_TOKENS` (default: `600`)
- `ROLE3_PRACTICE_QUESTION_COUNT` (default: `3`)
