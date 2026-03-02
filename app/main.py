from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.events import router as events_router
from app.api.routers.health import router as health_router
from app.api.routers.insights import router as insights_router
from app.api.routers.students import router as students_router
from app.store.demo_seed import seed_demo_data_if_needed

app = FastAPI(title="DLHackathon2026 API")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events_router)
app.include_router(health_router)
app.include_router(insights_router)
app.include_router(students_router)


@app.on_event("startup")
def _seed_demo_data() -> None:
    seed_demo_data_if_needed()
