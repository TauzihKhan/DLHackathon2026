# DLHackathon2026

Hackathon project repository for building and demoing an end-to-end product quickly.

## Start Here
- Project context: `CONTEXT.md`
- Agent workflow rules: `AGENTS.md`
- Structure guide: `docs/PROJECT_STRUCTURE.md`

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
