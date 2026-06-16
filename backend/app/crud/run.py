from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import HttpMethod, MonitorSchedule, RequestRun


def create_run(
    db: Session,
    *,
    api_request_id: UUID | None,
    monitor_id: UUID | None,
    environment_id: UUID | None,
    method: HttpMethod,
    url: str,
    request_headers: dict,
    request_body: str | None,
    status_code: int | None,
    response_headers: dict,
    response_body: str | None,
    latency_ms: float,
    success: bool,
    error: str | None,
) -> RequestRun:
    run = RequestRun(
        api_request_id=api_request_id,
        monitor_id=monitor_id,
        environment_id=environment_id,
        method=method,
        url=url,
        request_headers=request_headers,
        request_body=request_body,
        status_code=status_code,
        response_headers=response_headers,
        response_body=response_body,
        latency_ms=latency_ms,
        success=success,
        error=error,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def get_run(db: Session, run_id: UUID) -> RequestRun | None:
    return db.get(RequestRun, run_id)


def list_runs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    api_request_id: UUID | None = None,
    monitor_id: UUID | None = None,
    success: bool | None = None,
) -> list[RequestRun]:
    stmt = select(RequestRun)
    if api_request_id is not None:
        stmt = stmt.where(RequestRun.api_request_id == api_request_id)
    if monitor_id is not None:
        stmt = stmt.where(RequestRun.monitor_id == monitor_id)
    if success is not None:
        stmt = stmt.where(RequestRun.success.is_(success))
    stmt = stmt.offset(skip).limit(limit).order_by(RequestRun.created_at.desc())
    return list(db.scalars(stmt).all())


def count_runs(
    db: Session,
    api_request_id: UUID | None = None,
    monitor_id: UUID | None = None,
    success: bool | None = None,
) -> int:
    stmt = select(func.count()).select_from(RequestRun)
    if api_request_id is not None:
        stmt = stmt.where(RequestRun.api_request_id == api_request_id)
    if monitor_id is not None:
        stmt = stmt.where(RequestRun.monitor_id == monitor_id)
    if success is not None:
        stmt = stmt.where(RequestRun.success.is_(success))
    return db.scalar(stmt) or 0


def get_monitor(db: Session, monitor_id: UUID) -> MonitorSchedule | None:
    return db.get(MonitorSchedule, monitor_id)


def list_monitors(db: Session, skip: int = 0, limit: int = 100) -> list[MonitorSchedule]:
    stmt = (
        select(MonitorSchedule)
        .offset(skip)
        .limit(limit)
        .order_by(MonitorSchedule.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def count_monitors(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(MonitorSchedule)) or 0


def create_monitor(db: Session, data) -> MonitorSchedule:
    monitor = MonitorSchedule(**data.model_dump())
    db.add(monitor)
    db.commit()
    db.refresh(monitor)
    return monitor


def update_monitor(db: Session, monitor: MonitorSchedule, data) -> MonitorSchedule:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(monitor, field, value)
    db.commit()
    db.refresh(monitor)
    return monitor


def delete_monitor(db: Session, monitor: MonitorSchedule) -> None:
    db.delete(monitor)
    db.commit()


def list_due_monitors(db: Session) -> list[MonitorSchedule]:
    now = datetime.now(timezone.utc)
    monitors = list(
        db.scalars(select(MonitorSchedule).where(MonitorSchedule.enabled.is_(True))).all()
    )
    due = []
    for monitor in monitors:
        if monitor.last_run_at is None:
            due.append(monitor)
            continue
        elapsed = (now - monitor.last_run_at).total_seconds()
        if elapsed >= monitor.interval_seconds:
            due.append(monitor)
    return due


def mark_monitor_run(db: Session, monitor: MonitorSchedule) -> None:
    monitor.last_run_at = datetime.now(timezone.utc)
    db.commit()
