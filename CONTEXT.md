# Project Context: DLHackathon2026

## Mission
Build and demo a working hackathon project by the deadline with clear ownership, fast iteration loops, and a stable demo path.

## Non-Goals
- Perfect architecture for long-term scale
- Premature optimization
- Building optional features before core demo flow works

## Deadline and Scope
- Event: Hackathon 2026
- Working model: prioritize a thin, end-to-end vertical slice first, then iterate.

## Team Working Model
- Keep PRs/slices small and merge often.
- Prefer "working and visible" over "theoretically ideal."
- Every significant change should update this file if assumptions change.

## Current Repo State
- Demo-first scaffold is set and documented in `docs/PROJECT_STRUCTURE.md`.
- Full-stack boundaries are intentionally lean to maximize speed-to-demo.
- Backend parallel-work contract is documented in `docs/BACKEND_CONTRACT.md` for Role 1.1 and Role 1.2 alignment.
- Frontend now has a working Role 2 dashboard slice in `frontend/`:
  - `index.html`, `login.html`, `register.html`, `auth.js`, `styles.css`, `app.js`
  - separate login and register pages before dashboard access
  - register flow includes email verification (backend hook + demo fallback); login is verification-free
  - registration auto-generates a `new_student_*` ID and stores it in session
  - dashboard now includes tabs: Dashboard, Statistics, Assignments, Tests & Scores, Profile
  - student ID is no longer editable in dashboard UI; it is bound to authenticated user profile/session
  - visualized mastery bars, weak topics list, recommendations, and calendar planner
  - API integration path to `GET /students/{id}/state`, `GET /students/{id}/insights`, and `GET /students/{id}/spaced-repetition` (optional fallback to `GET /students/{id}/plan?days=7`)
  - deterministic mock fallback when backend endpoints are unavailable
- Backend v0 implementation is now present for core demo flow:
  - `app/api/routers` (`health`, `events`, `students`, `insights`)
  - `app/schemas` (`event`, `state`, `insight`)
  - `app/engine` (`state_engine`, `decay`, `policy`, `explain`)
  - `app/store/in_memory_store.py` for thread-safe in-memory persistence keyed by learner.
- Existing package markers:
  - `app/__init__.py`
  - `app/api/__init__.py`

## Problem Statement Alignment
We are building an AI-powered learning-state engine that:
- ingests learner interaction events over time,
- updates an evolving learner/topic state,
- generates explainable, actionable next-step guidance,
- adapts recommendations for inactivity and accelerated progress.

## Locked Decisions (As of Now)
- Stack direction: web frontend + Python FastAPI backend.
- Architecture direction: `frontend` (UI) + minimal backend layering (`api` -> `engine` -> `store`) for rapid iteration.
- Delivery strategy: ship one thin end-to-end flow first, then add depth only if time permits.
- Documentation references:
  - structure and ownership: `docs/PROJECT_STRUCTURE.md`
  - backend parallel contract: `docs/BACKEND_CONTRACT.md`
  - project-level summary: `README.md`
  - decision log/current state: `CONTEXT.md`

## Immediate Next Coding Slice (Priority Order)
1. Boot runnable API service:
   - `app/main.py`
   - `app/api/routers/health.py`
   - `app/api/routers/events.py`
   - `app/api/routers/students.py`
   - `app/api/routers/insights.py`
2. Define minimal schemas:
   - event input, student state, insight output
3. Implement core domain loop:
   - `app/engine/state_engine.py` with `update_state(event, prev_state)`
   - simple inactivity decay
   - initial next-best-action policy and explanation
4. Add persistence path:
   - start with `app/store/in_memory_store.py`
5. Seed deterministic demo data + replay script:
   - `scripts/seed_demo_data.py`
   - optional `scripts/replay_events.py`

## Minimum Demo Contract (v0)
- `POST /events`: accept an interaction event and update state
- `GET /students/{id}/state`: return current learner state snapshot
- `GET /students/{id}/insights`: return top actionable recommendation + explanation
- `GET /students/{id}/spaced-repetition`: return dedicated review queue and due schedule for frontend
- `GET /health`: service health for demos/checks

## Frontend-Driven Backend Hooks (Role 2 Request)
- `POST /auth/send-verification`: send email verification code for register flow.
- `GET /students/{id}/statistics/study-time`: tab data for statistics.
- `GET /students/{id}/statistics/topic-accuracy`: topic trend data for statistics.
- `GET /students/{id}/assignments?status=pending|done`: assignment tabs.
- `GET /students/{id}/tests`: recent test list.
- `GET /students/{id}/tests/summary`: aggregate score breakdown.

Status update:
- Implemented: statistics (`study-time`, `topic-accuracy`), assignments, tests, and tests summary endpoints in `app/api/routers/students.py`.
- Frontend now syncs Statistics, Assignments, and Tests tabs against these endpoints, with deterministic fallback when unavailable.
- Backend now auto-seeds demo learner records on startup (plus on-demand for `new_student_*` IDs) for presentation readiness, and frontend streak widgets consume backend streak metrics instead of hardcoded local values.

## Proposed Baseline Architecture
- `frontend/`: web UI (screens, components, API clients)
- `app/`: API routes, schemas, core engine, and lightweight store
- `tests/`: critical-flow tests only
- `scripts/`: seed/replay/dev helpers
- `docs/`: product and technical references

Reference structure and ownership rules:
- `docs/PROJECT_STRUCTURE.md`

## Environment Setup (To Update As You Decide Stack)
- Backend:
  - `pip install -r requirements.txt`
  - `uvicorn app.main:app --reload`
- Frontend:
  - `cd frontend`
  - `python3 -m http.server 5500`
  - open `http://localhost:5500`
- Tests/lint:
  - pending, to be added with first backend implementation slice

## Coding Conventions
- Keep functions/modules small and testable.
- Use clear names over clever abstractions.
- Add comments only where intent is non-obvious.
- Avoid broad refactors during hackathon unless blocking progress.

## Definition of Done (Hackathon)
- Feature is demoable end-to-end.
- Basic error handling exists for key paths.
- Minimal documentation updated (`README.md` + this file).
- Another teammate can run it locally.

## API and Data Contracts
Document API endpoints and payload shapes here once defined.

Template:
- Endpoint:
- Method:
- Request:
- Response:
- Error cases:

## Open Questions
- What is the exact demo narrative?
- What are must-have vs nice-to-have features?
- What should be mocked vs fully implemented?
- Do we include optional LLM phrasing in v1, or stay purely deterministic?
- Do we keep in-memory store only for demo, or add SQLite if time allows?

## Assumptions
- Speed-to-demo is prioritized over full production-hardening.
- Deterministic behavior is preferred for judging/demo reliability.
- We can start with rule-based guidance and add LLM polish as an optional layer.
- Frontend authentication is local/browser-stored for demo; backend auth/email verification can replace it incrementally.

## Known Risks
- Scope creep under time pressure
- Late integration surprises
- Environment drift across teammates
- Over-investing in architecture before first runnable vertical slice
- Non-deterministic outputs hurting live demo consistency

## Daily Operating Checklist
- Confirm top 1-2 priorities for next session.
- Ensure main/demo branch is runnable.
- Capture new decisions in this file.

## Implementation Snapshot (2026-03-02)
- Backend v0 flow is implemented and runnable by contract:
  - `POST /events`: `store.get -> update_state -> store.save -> {"status":"ok"}`
  - `GET /students/{id}/state`: fetch stored state, apply inactivity decay on read
  - `GET /students/{id}/insights`: generate policy + explainable insight from decayed state
  - `GET /students/{id}/spaced-repetition`: return frontend-ready review plan (`due_now_count`, `due_next_24h_count`, `review_queue`)
- Persistence is in-memory via `app/store/in_memory_store.py` keyed by `learner_id`.
- Learning computation is centralized in `app/engine/state_engine.py` (single source of mastery updates).
- Spaced-repetition behavior now includes explicit review scheduling in insights output (`spaced_repetition.review_queue`) with adaptive intervals based on mastery, confidence, and inactivity.
