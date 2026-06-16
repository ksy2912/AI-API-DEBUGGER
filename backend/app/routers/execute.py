from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud import request as request_crud
from app.crud import run as run_crud
from app.database import get_db
from app.schemas.execute import ExecuteRequest, ExecuteResponse, RequestRunResponse
from app.services.execution_service import (
    build_execute_request_from_saved,
    execute_and_persist,
)

router = APIRouter(tags=["execute"])


@router.post("/execute", response_model=ExecuteResponse)
async def execute_request(data: ExecuteRequest, db: Session = Depends(get_db)):
    try:
        return await execute_and_persist(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/requests/{request_id}/execute", response_model=ExecuteResponse)
async def execute_saved_request(
    request_id: UUID,
    environment_id: UUID | None = None,
    db: Session = Depends(get_db),
):
    saved = request_crud.get_request(db, request_id)
    if not saved:
        raise HTTPException(status_code=404, detail="Request not found")

    execute_data = build_execute_request_from_saved(saved, environment_id)
    try:
        return await execute_and_persist(
            db, execute_data, api_request_id=saved.id
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/requests/{request_id}/runs", response_model=list[RequestRunResponse])
def list_request_runs(
    request_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    if not request_crud.get_request(db, request_id):
        raise HTTPException(status_code=404, detail="Request not found")
    return run_crud.list_runs(db, skip=skip, limit=limit, api_request_id=request_id)
