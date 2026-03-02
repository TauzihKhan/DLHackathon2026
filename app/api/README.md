# app/api

HTTP-layer modules and endpoint routing.

## Contract Surface
- `POST /events`
  - Ingest one `LearningEvent` and update learner state.
- `GET /students/{learner_id}/state`
  - Return current learner snapshot with inactivity decay applied at read-time.
- `GET /students/{learner_id}/reviews/due`
  - Return spaced-repetition due queue sorted for immediate frontend rendering.
- `GET /students/{learner_id}/insights`
  - Return deterministic recommendation (`reason_codes` + `explanation_facts`).
- `GET /students/{learner_id}/insights/narrative`
  - Return Role 3 natural-language explanation + targeted practice questions.
