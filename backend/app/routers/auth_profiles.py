from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud import auth_profile as auth_profile_crud
from app.database import get_db
from app.schemas.environment import (
    AuthProfileCreate,
    AuthProfileResponse,
    AuthProfileUpdate,
)

router = APIRouter(prefix="/auth-profiles", tags=["auth-profiles"])


@router.get("", response_model=list[AuthProfileResponse])
def list_auth_profiles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return auth_profile_crud.list_auth_profiles(db, skip=skip, limit=limit)


@router.post("", response_model=AuthProfileResponse, status_code=status.HTTP_201_CREATED)
def create_auth_profile(data: AuthProfileCreate, db: Session = Depends(get_db)):
    return auth_profile_crud.create_auth_profile(db, data)


@router.get("/{profile_id}", response_model=AuthProfileResponse)
def get_auth_profile(profile_id: UUID, db: Session = Depends(get_db)):
    profile = auth_profile_crud.get_auth_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Auth profile not found")
    return profile


@router.patch("/{profile_id}", response_model=AuthProfileResponse)
def update_auth_profile(
    profile_id: UUID, data: AuthProfileUpdate, db: Session = Depends(get_db)
):
    profile = auth_profile_crud.get_auth_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Auth profile not found")
    return auth_profile_crud.update_auth_profile(db, profile, data)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_auth_profile(profile_id: UUID, db: Session = Depends(get_db)):
    profile = auth_profile_crud.get_auth_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Auth profile not found")
    auth_profile_crud.delete_auth_profile(db, profile)
