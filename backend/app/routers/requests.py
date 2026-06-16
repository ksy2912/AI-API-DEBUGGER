from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud import request as request_crud
from app.database import get_db
from app.schemas import ApiRequestCreate, ApiRequestResponse, ApiRequestUpdate

router = APIRouter(prefix="/requests", tags=["requests"])


@router.get("", response_model=list[ApiRequestResponse])
def list_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    collection_id: UUID | None = None,
    db: Session = Depends(get_db),
):
    return request_crud.list_requests(
        db, skip=skip, limit=limit, collection_id=collection_id
    )


@router.post("", response_model=ApiRequestResponse, status_code=status.HTTP_201_CREATED)
def create_request(data: ApiRequestCreate, db: Session = Depends(get_db)):
    return request_crud.create_request(db, data)


@router.get("/{request_id}", response_model=ApiRequestResponse)
def get_request(request_id: UUID, db: Session = Depends(get_db)):
    request = request_crud.get_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request


@router.patch("/{request_id}", response_model=ApiRequestResponse)
def update_request(
    request_id: UUID, data: ApiRequestUpdate, db: Session = Depends(get_db)
):
    request = request_crud.get_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request_crud.update_request(db, request, data)


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(request_id: UUID, db: Session = Depends(get_db)):
    request = request_crud.get_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    request_crud.delete_request(db, request)
