# NOVA - Your AI Learning Hub

Youtube Link : https://youtu.be/ovzpD7yP2oc?feature=shared

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

## FAQ -> What is mastery?
In NOVA, **mastery** is your current confidence score for a topic, shown as a percentage (0-100%).
It is updated from your learning events (quiz/assignment/flashcard attempts), and it is not just a raw average.

What affects mastery:
- **Correct vs incorrect attempts**: getting answers right consistently pushes mastery up.
- **Recency of practice**: long inactivity applies decay, so mastery can drift down over time.
- **Topic-level aggregation**: the dashboard rolls up subtopic behavior into topic mastery.

How to read it in the UI:
- **Mastered**: `>= 70%`
- **Developing**: `50% - 69%`
- **At-risk**: `< 50%`

So if your score drops even without new mistakes, that usually means the system detected inactivity/retention risk and wants you to revisit that topic.

## Run Locally

### Quick Start (recommended)
```bash
make setup
```

Then run in separate terminals:
```bash
make run-backend
make run-frontend
```

Backend runs at `http://localhost:8000`.

If you want both together:
```bash
make dev
```
- Thats it!

### Manual method for the terminal
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
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
- `.venv/` stays local, so all dependencies installed are boxed within the app, and wont pollute your system.
