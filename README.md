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

Frontend currently reads:
- `GET /students/{id}/state`
- `GET /students/{id}/insights`

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
- Statistics/Assignments/Tests tabs currently use placeholder cards and expected backend endpoint notes.
- Dashboard no longer exposes editable student ID; student context is taken from logged-in session/profile.
