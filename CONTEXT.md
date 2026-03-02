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
  - `index.html`, `styles.css`, `app.js`
  - visualized mastery bars, weak topics list, and recommendation panel
  - API integration path to `GET /students/{id}/state` and `GET /students/{id}/insights`
  - deterministic mock fallback when backend endpoints are unavailable
- Backend feature files are still pending for:
  - `app/api/routers`, `app/core`, `app/schemas`, `app/engine`, `app/store`
- Existing package markers:
  - `app/__init__.py`
  - `app/api/__init__.py`
- Most backend feature files are intentionally not created yet; focus remains on first runnable vertical slice.

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
   - start with `app/store/memory.py`
5. Seed deterministic demo data + replay script:
   - `scripts/seed_demo_data.py`
   - optional `scripts/replay_events.py`

## Minimum Demo Contract (v0)
- `POST /events`: accept an interaction event and update state
- `GET /students/{id}/state`: return current learner state snapshot
- `GET /students/{id}/insights`: return top actionable recommendation + explanation
- `GET /health`: service health for demos/checks

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
