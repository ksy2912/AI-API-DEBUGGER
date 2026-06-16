from celery import Celery
from celery.schedules import schedule

from app.config import settings

celery_app = Celery(
    "apidebug",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.monitoring"],
)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "check-monitors": {
            "task": "app.tasks.monitoring.process_due_monitors",
            "schedule": schedule(run_every=settings.monitor_check_interval_seconds),
        },
    },
)

import app.tasks.monitoring  # noqa: E402, F401
