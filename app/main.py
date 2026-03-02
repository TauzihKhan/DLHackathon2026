from fastapi import FastAPI

from app.api.routers.events import router as events_router
from app.api.routers.health import router as health_router
from app.api.routers.insights import router as insights_router
from app.api.routers.students import router as students_router

app = FastAPI(title="DLHackathon2026 API")

app.include_router(events_router)
app.include_router(health_router)
app.include_router(insights_router)
app.include_router(students_router)
