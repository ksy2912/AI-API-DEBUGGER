from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud import environment as environment_crud
from app.database import get_db
from app.schemas.environment import (
    EnvironmentCreate,
    EnvironmentPublic,
    EnvironmentUpdate,
)

router = APIRouter(prefix="/environments", tags=["environments"])


@router.get("", response_model=list[EnvironmentPublic])
def list_environments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return [
        EnvironmentPublic.from_model(env)
        for env in environment_crud.list_environments(db, skip=skip, limit=limit)
    ]


@router.post("", response_model=EnvironmentPublic, status_code=status.HTTP_201_CREATED)
def create_environment(data: EnvironmentCreate, db: Session = Depends(get_db)):
    env = environment_crud.create_environment(db, data)
    return EnvironmentPublic.from_model(env)


@router.get("/{environment_id}", response_model=EnvironmentPublic)
def get_environment(environment_id: UUID, db: Session = Depends(get_db)):
    env = environment_crud.get_environment(db, environment_id)
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")
    return EnvironmentPublic.from_model(env)


@router.patch("/{environment_id}", response_model=EnvironmentPublic)
def update_environment(
    environment_id: UUID, data: EnvironmentUpdate, db: Session = Depends(get_db)
):
    env = environment_crud.get_environment(db, environment_id)
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")
    env = environment_crud.update_environment(db, env, data)
    return EnvironmentPublic.from_model(env)


@router.delete("/{environment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_environment(environment_id: UUID, db: Session = Depends(get_db)):
    env = environment_crud.get_environment(db, environment_id)
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")
    environment_crud.delete_environment(db, env)
