import logging

from app.celery_app import celery_app
from app.crud import run as run_crud
from app.database import SessionLocal
from app.services.execution_service import (
    build_execute_request_from_saved,
    execute_and_persist_sync,
)

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.monitoring.process_due_monitors")
def process_due_monitors() -> int:
    db = SessionLocal()
    processed = 0
    try:
        due = run_crud.list_due_monitors(db)
        for monitor in due:
            run_monitor.delay(str(monitor.id))
            processed += 1
    finally:
        db.close()
    return processed


@celery_app.task(name="app.tasks.monitoring.run_monitor")
def run_monitor(monitor_id: str) -> dict:
    db = SessionLocal()
    try:
        from uuid import UUID

        monitor = run_crud.get_monitor(db, UUID(monitor_id))
        if not monitor or not monitor.enabled:
            return {"status": "skipped"}

        saved = monitor.api_request
        if not saved:
            return {"status": "missing_request"}

        run_crud.mark_monitor_run(db, monitor)

        env_id = monitor.environment_id or saved.environment_id
        execute_data = build_execute_request_from_saved(saved, env_id)
        execute_data.environment_id = env_id

        result = execute_and_persist_sync(
            db,
            execute_data,
            api_request_id=saved.id,
            monitor_id=monitor.id,
        )
        return {
            "status": "ok",
            "run_id": str(result.run_id),
            "success": result.success,
            "latency_ms": result.latency_ms,
        }
    except Exception:
        logger.exception("Monitor run failed for %s", monitor_id)
        raise
    finally:
        db.close()
