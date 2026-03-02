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

## Local Run (Current)
1. Backend (when implemented):
   - `pip install -r requirements.txt`
   - `uvicorn app.main:app --reload`
2. Frontend:
   - `cd frontend`
   - `python3 -m http.server 5500`
   - Open `http://localhost:5500/login.html`

Demo data behavior:
- Backend auto-seeds demo learners on startup (including `new_student_001`, `student-001`, `demo-learner`) so dashboard tabs have presentable data immediately.
- If a `new_student_*` learner ID is requested and missing, backend seeds that learner on-demand for demo continuity.
- Streak values now come from backend study-time stats (`current_streak_days`, `longest_streak_days`), not frontend hardcoded values.

Frontend currently reads:
- `GET /students/{id}/state`
- `GET /students/{id}/insights`
- `GET /students/{id}/spaced-repetition` (optional dedicated endpoint)

If backend is unavailable, it falls back to deterministic mock data for demo continuity.

Frontend auth flow (demo mode):
- Users must login/register before accessing dashboard.
- Login and register are separate pages:
  - `http://localhost:5500/login.html`
  - `http://localhost:5500/register.html`
- Register captures name, email, DOB, password and auto-generates `new_student_*` ID.
- Email verification is handled on register flow only.
- Verification tries backend endpoint `POST /auth/send-verification`; if unavailable, it falls back to demo code in UI.
- User records are stored in browser local storage for demo only.

Frontend tabs (UI shell ready):
- Dashboard
- Statistics
- Assignments
- Tests & Scores
- Profile
- Statistics/Assignments/Tests tabs now call backend sync endpoints when available, with graceful fallback UI.
- Dashboard no longer exposes editable student ID; student context is taken from logged-in session/profile.

## Current API Contract
- `POST /events` accepts `LearningEvent`, updates learner state, and returns `{ "status": "ok" }`.
- `GET /students/{id}/state` returns decayed-on-read `StudentStateResponse`.
- `GET /students/{id}/insights` returns explainable guidance plus a frontend-ready `spaced_repetition` plan (due-now count, next-24h count, ordered review queue).
- `GET /students/{id}/spaced-repetition` returns only the spaced repetition plan for simpler frontend wiring.
- `GET /students/{id}/statistics/study-time` returns session count + total study minutes + recent daily distribution.
- `GET /students/{id}/statistics/topic-accuracy` returns topic-wise accuracy and attempts.
- `GET /students/{id}/assignments?status=all|pending|done` returns assignment list with status/accuracy.
- `GET /students/{id}/tests` returns test history snapshots.
- `GET /students/{id}/tests/summary` returns aggregate score metrics.

## Spaced Repetition Status
- Implemented with explicit scheduling on `GET /students/{id}/insights` via `spaced_repetition.review_queue`.
- Review interval adapts using mastery, confidence, and time since last interaction (through decay-risk-informed urgency).
- Frontend can consume this directly without extra endpoint stitching.
