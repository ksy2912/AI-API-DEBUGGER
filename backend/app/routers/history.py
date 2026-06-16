from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.crud import debug as debug_crud
from app.crud import run as run_crud
from app.database import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.debug import DebugSessionResponse
from app.schemas.execute import RequestRunResponse
from app.schemas.monitor import MonitorResponse

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/runs", response_model=PaginatedResponse[RequestRunResponse])
def history_runs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    success: bool | None = None,
    api_request_id: UUID | None = None,
    monitor_id: UUID | None = None,
    db: Session = Depends(get_db),
):
    items = run_crud.list_runs(
        db, skip=skip, limit=limit, success=success,
        api_request_id=api_request_id, monitor_id=monitor_id,
    )
    total = run_crud.count_runs(
        db, success=success, api_request_id=api_request_id, monitor_id=monitor_id,
    )
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/debug-sessions", response_model=PaginatedResponse[DebugSessionResponse])
def history_debug_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    run_id: UUID | None = None,
    db: Session = Depends(get_db),
):
    items = debug_crud.list_sessions(db, skip=skip, limit=limit, run_id=run_id)
    total = debug_crud.count_sessions(db, run_id=run_id)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/monitors", response_model=PaginatedResponse[MonitorResponse])
def history_monitors(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    items = run_crud.list_monitors(db, skip=skip, limit=limit)
    total = run_crud.count_monitors(db)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)
