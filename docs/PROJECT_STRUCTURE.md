# Project Structure Guide

This document explains the lean, demo-first scaffold for the hackathon problem:
model a learner's changing state over time and generate clear, actionable guidance.

## Folder Tree

```text
.
├─ frontend/
│  ├─ index.html
│  ├─ styles.css
│  └─ app.js
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
│  │  ├─ config.py
│  │  └─ logging.py
│  ├─ schemas/
│  │  ├─ event.py
│  │  ├─ state.py
│  │  └─ insight.py
│  ├─ engine/
│  │  ├─ state_engine.py
│  │  ├─ explain.py
│  │  ├─ policy.py
│  │  └─ decay.py
│  └─ store/
│     └─ memory.py
├─ scripts/
│  ├─ seed_demo_data.py
│  └─ run_dev.sh
├─ tests/
│  ├─ test_state_engine.py
│  └─ test_insights.py
└─ docs/
   └─ PROJECT_STRUCTURE.md
```

## Why Each Part Exists

- `frontend/`
  Web UI application. Owns layout, interaction flows, and API consumption for the live demo.
  Current MVP is a static dashboard page with API fetch + mock fallback.

- `app/main.py`
  Single FastAPI entrypoint so everyone runs the app the same way.

- `app/api/`
  HTTP layer only. Contains endpoints for health, event ingest, state, and insights.

- `app/core/`
  Shared runtime setup (settings, logging) to avoid config logic spreading across features.

- `app/schemas/`
  Canonical payload contracts for events, learner state, and insight outputs.

- `app/engine/`
  Core intelligence. This is where learner state is updated, decay is applied, and next actions are chosen.

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
