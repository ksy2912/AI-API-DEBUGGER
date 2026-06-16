from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud import request as request_crud
from app.crud import run as run_crud
from app.database import get_db
from app.schemas.execute import RequestRunResponse
from app.schemas.monitor import MonitorCreate, MonitorResponse, MonitorUpdate

router = APIRouter(prefix="/monitors", tags=["monitors"])


@router.get("", response_model=list[MonitorResponse])
def list_monitors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return run_crud.list_monitors(db, skip=skip, limit=limit)


@router.post("", response_model=MonitorResponse, status_code=status.HTTP_201_CREATED)
def create_monitor(data: MonitorCreate, db: Session = Depends(get_db)):
    if not request_crud.get_request(db, data.api_request_id):
        raise HTTPException(status_code=404, detail="API request not found")
    return run_crud.create_monitor(db, data)


@router.get("/{monitor_id}", response_model=MonitorResponse)
def get_monitor(monitor_id: UUID, db: Session = Depends(get_db)):
    monitor = run_crud.get_monitor(db, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return monitor


@router.patch("/{monitor_id}", response_model=MonitorResponse)
def update_monitor(
    monitor_id: UUID, data: MonitorUpdate, db: Session = Depends(get_db)
):
    monitor = run_crud.get_monitor(db, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return run_crud.update_monitor(db, monitor, data)


@router.delete("/{monitor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_monitor(monitor_id: UUID, db: Session = Depends(get_db)):
    monitor = run_crud.get_monitor(db, monitor_id)
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    run_crud.delete_monitor(db, monitor)


@router.get("/{monitor_id}/runs", response_model=list[RequestRunResponse])
def list_monitor_runs(
    monitor_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    if not run_crud.get_monitor(db, monitor_id):
        raise HTTPException(status_code=404, detail="Monitor not found")
    return run_crud.list_runs(db, skip=skip, limit=limit, monitor_id=monitor_id)
