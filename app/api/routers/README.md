# app/api/routers

API route handlers (`health`, `events`, `students`, `insights`).

## Endpoints
- `health.py`
  - `GET /health`
- `events.py`
  - `POST /events`
- `students.py`
  - `GET /students/{learner_id}/state`
- `insights.py`
  - `GET /students/{learner_id}/insights`
  - `GET /students/{learner_id}/insights/narrative`
