# Project Structure Guide

This document explains the lean, demo-first scaffold for the hackathon problem:
model a learner's changing state over time and generate clear, actionable guidance.

## Folder Tree

```text
.
├─ frontend/
│  ├─ public/
│  └─ src/
│     ├─ pages/
│     ├─ components/
│     ├─ services/
│     ├─ lib/
│     └─ styles/
├─ app/
│  ├─ __init__.py
│  ├─ main.py
│  ├─ api/
│  │  ├─ __init__.py
│  │  └─ routers/
│  │     ├─ health.py
│  │     ├─ events.py
│  │     ├─ students.py
│  │     └─ insights.py
│  ├─ core/
│  │  └─ config.py
│  ├─ schemas/
│  │  ├─ event.py
│  │  ├─ state.py
│  │  ├─ insight.py
│  │  ├─ narrative.py
│  │  └─ review.py
│  ├─ engine/
│  │  ├─ state_engine.py
│  │  ├─ explain.py
│  │  ├─ policy.py
│  │  ├─ decay.py
│  │  ├─ narrative.py
│  │  └─ repetition.py
│  └─ store/
│     └─ memory.py
├─ scripts/
│  ├─ seed_demo_data.py
│  └─ run_dev.sh
├─ tests/
│  └─ test_role3_narrative.py
└─ docs/
   └─ PROJECT_STRUCTURE.md
```

## Why Each Part Exists

- `frontend/`
  Web UI application. Owns layout, interaction flows, and API consumption for the live demo.

- `app/main.py`
  Single FastAPI entrypoint so everyone runs the app the same way.

- `app/api/`
  HTTP layer only. Contains endpoints for health, event ingest, state, due reviews, deterministic insights, and Role 3 narrative insights.

- `app/core/`
  Shared runtime setup (settings, logging) to avoid config logic spreading across features.

- `app/schemas/`
  Canonical payload contracts for events, learner state, due reviews, deterministic insights, and narrative outputs.

- `app/engine/`
  Core intelligence. This is where learner state is updated, decay is applied, spaced-repetition schedules are computed, next actions are chosen, and Role 3 narrative text/questions are generated.

- `app/store/`
  Lightweight persistence abstraction. Start with in-memory storage for predictable demo speed.

- `scripts/`
  Developer and demo helpers (seed data and quick local run scripts).

- `tests/`
  Critical checks for core state updates and insight behavior.

- `docs/`
  Shared structure and ownership reference for team alignment.

## Practical Team Rule

When adding a new feature, place code by responsibility:
- UI, pages, component behavior -> `frontend/`
- HTTP concern -> `api/`
- Learning logic -> `engine/`
- Short-term persistence -> `store/`
- Shared app settings/logging -> `core/`

This keeps ownership clear and avoids mixing concerns under deadline pressure.
