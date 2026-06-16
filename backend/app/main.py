from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import (
    analytics,
    auth_profiles,
    collections,
    debug,
    environments,
    execute,
    generate_tests,
    history,
    monitors,
    requests,
    runs,
)

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(collections.router, prefix="/api")
app.include_router(requests.router, prefix="/api")
app.include_router(execute.router, prefix="/api")
app.include_router(runs.router, prefix="/api")
app.include_router(environments.router, prefix="/api")
app.include_router(auth_profiles.router, prefix="/api")
app.include_router(monitors.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(debug.router, prefix="/api")
app.include_router(generate_tests.router, prefix="/api")
app.include_router(history.router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name}
