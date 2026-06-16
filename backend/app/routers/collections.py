from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud import collection as collection_crud
from app.database import get_db
from app.schemas import (
    CollectionCreate,
    CollectionResponse,
    CollectionUpdate,
    CollectionWithRequests,
)

router = APIRouter(prefix="/collections", tags=["collections"])


@router.get("", response_model=list[CollectionResponse])
def list_collections(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return collection_crud.list_collections(db, skip=skip, limit=limit)


@router.post("", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
def create_collection(data: CollectionCreate, db: Session = Depends(get_db)):
    return collection_crud.create_collection(db, data)


@router.get("/{collection_id}", response_model=CollectionWithRequests)
def get_collection(collection_id: UUID, db: Session = Depends(get_db)):
    collection = collection_crud.get_collection(db, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection


@router.patch("/{collection_id}", response_model=CollectionResponse)
def update_collection(
    collection_id: UUID, data: CollectionUpdate, db: Session = Depends(get_db)
):
    collection = collection_crud.get_collection(db, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection_crud.update_collection(db, collection, data)


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection(collection_id: UUID, db: Session = Depends(get_db)):
    collection = collection_crud.get_collection(db, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    collection_crud.delete_collection(db, collection)
