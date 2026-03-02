# NOVA - Your AI Learning Hub

NOVA is a learner-intelligence web app built for hackathon demos.
It helps a student see where they are doing well, where they are slipping, and what to do next.

The experience is simple:
- Login/Register flow
- Personalized dashboard
- Weak-topic insights + recommendations
- Statistics, Assignments, Tests & Scores, Calendar, and Profile tabs
- Smooth fallback to deterministic demo data when backend is unavailable

## What This Project Includes
- `frontend/`: static web UI (`index.html`, `styles.css`, `app.js`, auth pages)
- `app/`: FastAPI backend with learner-state and analytics endpoints
- `scripts/`: demo/seed helpers
- `tests/`: backend test scaffolding

## Key Features
- Topic mastery tracking and risk labels (`Mastered`, `Developing`, `At-risk`)
- Recommendation card with evidence and quick YouTube search
- Study streak + study-time metrics
- Statistics, assignments, and test history synced from backend when available
- Calendar planner with local event storage

## Run Locally

### 1) Backend
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Backend runs at `http://localhost:8000`.

### 2) Frontend
In another terminal:
```bash
cd frontend
python3 -m http.server 5500
```
Open:
- `http://localhost:5500/login.html`
- `http://localhost:5500/register.html`
- `http://localhost:5500/index.html`

## API Endpoints Used by Frontend
- `GET /students/{id}/state`
- `GET /students/{id}/insights`
- `GET /students/{id}/spaced-repetition`
- `GET /students/{id}/statistics/study-time`
- `GET /students/{id}/statistics/topic-accuracy`
- `GET /students/{id}/assignments`
- `GET /students/{id}/tests`
- `GET /students/{id}/tests/summary`

## Demo Behavior
- Backend seeds demo learners so the dashboard is presentation-ready.
- If backend calls fail, frontend automatically uses deterministic mock data.

## Notes
- This repo is optimized for speed-to-demo and clear visuals.
- Architecture is intentionally lightweight for hackathon iteration.
