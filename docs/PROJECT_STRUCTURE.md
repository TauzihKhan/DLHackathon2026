# Project Structure Guide

This document explains the agreed backend-first scaffold for the hackathon problem:
model a learner's changing state over time and generate clear, actionable guidance.

## Folder Tree

```text
.
├─ app/
│  ├─ __init__.py
│  ├─ main.py
│  ├─ core/
│  │  ├─ config.py
│  │  ├─ logging.py
│  │  └─ security.py
│  ├─ api/
│  │  ├─ __init__.py
│  │  ├─ deps.py
│  │  └─ routers/
│  │     ├─ health.py
│  │     ├─ ingest.py
│  │     ├─ learners.py
│  │     ├─ guidance.py
│  │     └─ admin.py
│  ├─ schemas/
│  │  ├─ event.py
│  │  ├─ state.py
│  │  ├─ guidance.py
│  │  └─ common.py
│  ├─ domain/
│  │  ├─ state_engine.py
│  │  ├─ decay.py
│  │  ├─ mastery.py
│  │  ├─ features.py
│  │  ├─ policy.py
│  │  └─ explain.py
│  ├─ services/
│  │  ├─ __init__.py
│  │  ├─ guidance_service.py
│  │  ├─ llm_service.py
│  │  └─ simulation_service.py
│  ├─ repositories/
│  │  ├─ __init__.py
│  │  ├─ events_repo.py
│  │  ├─ state_repo.py
│  │  └─ guidance_repo.py
│  ├─ db/
│  │  ├─ __init__.py
│  │  ├─ session.py
│  │  ├─ models.py
│  │  └─ migrations/
│  ├─ jobs/
│  │  ├─ decay_scheduler.py
│  │  └─ recompute_snapshots.py
│  ├─ eval/
│  │  ├─ __init__.py
│  │  ├─ offline_metrics.py
│  │  └─ scenarios.py
│  └─ tests/
│     ├─ test_state_engine.py
│     ├─ test_decay.py
│     ├─ test_policy.py
│     └─ test_guidance_api.py
├─ scripts/
│  ├─ seed_demo_data.py
│  ├─ replay_events.py
│  └─ run_dev.sh
├─ data/
│  ├─ sample_events.jsonl
│  └─ demo_learners.json
└─ docs/
   ├─ PROJECT_STRUCTURE.md
   ├─ demo_story.md
   └─ api_contract.md
```

## Why Each Part Exists

- `app/main.py`
  Single FastAPI entrypoint so everyone runs the app the same way.

- `app/core/`
  Shared runtime setup (settings, logging, security) to avoid config logic spreading across features.

- `app/api/`
  HTTP layer only. Keeps request/response handling separate from learning logic.

- `app/schemas/`
  Canonical payload contracts for events, learner state, and guidance outputs.

- `app/domain/`
  Core intelligence. This is where learner state is updated, decay is applied, and next actions are chosen.

- `app/services/`
  Orchestration layer that combines domain logic, repositories, and optional LLM explanation generation.

- `app/repositories/`
  Data access methods grouped by aggregate, so DB logic stays out of API and domain modules.

- `app/db/`
  Database connection/session + ORM models + migration folder.

- `app/jobs/`
  Background or scheduled processes, especially periodic decay/recompute flows.

- `app/eval/`
  Offline checks for recommendation quality and deterministic scenarios for demo confidence.

- `app/tests/`
  Focused tests for state updates, decay behavior, policy outputs, and API behavior.

- `scripts/`
  Developer and demo helpers (seed data, replay events, run app quickly).

- `data/`
  Stable demo fixtures so all teammates can reproduce the same outputs.

- `docs/`
  Shared product and technical references for judges/demo prep and team alignment.

## Practical Team Rule

When adding a new feature, place code by responsibility:
- HTTP concern -> `api/`
- Learning logic -> `domain/`
- Multi-step flow -> `services/`
- DB query/write -> `repositories/`
- Batch/scheduled task -> `jobs/`

This keeps ownership clear and avoids mixing concerns under deadline pressure.
