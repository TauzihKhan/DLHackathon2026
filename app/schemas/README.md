# app/schemas

Pydantic models for event, state, and insight payloads.

## Current Contract Files
- `event.py`
  - Request model for `POST /events`.
- `state.py`
  - Response model for `GET /students/{learner_id}/state`.
- `insight.py`
  - Deterministic response model for `GET /students/{learner_id}/insights`.
- `narrative.py`
  - Role 3 response model for `GET /students/{learner_id}/insights/narrative`.
