from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud import run as run_crud
from app.database import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.execute import RequestRunResponse

router = APIRouter(prefix="/runs", tags=["runs"])


@router.get("", response_model=PaginatedResponse[RequestRunResponse])
def list_runs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    api_request_id: UUID | None = None,
    monitor_id: UUID | None = None,
    success: bool | None = None,
    db: Session = Depends(get_db),
):
    items = run_crud.list_runs(
        db,
        skip=skip,
        limit=limit,
        api_request_id=api_request_id,
        monitor_id=monitor_id,
        success=success,
    )
    total = run_crud.count_runs(
        db,
        api_request_id=api_request_id,
        monitor_id=monitor_id,
        success=success,
    )
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/{run_id}", response_model=RequestRunResponse)
def get_run(run_id: UUID, db: Session = Depends(get_db)):
    run = run_crud.get_run(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
