from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuthProfile
from app.schemas.environment import AuthProfileCreate, AuthProfileUpdate


def get_auth_profile(db: Session, profile_id: UUID) -> AuthProfile | None:
    return db.get(AuthProfile, profile_id)


def list_auth_profiles(db: Session, skip: int = 0, limit: int = 100) -> list[AuthProfile]:
    stmt = (
        select(AuthProfile)
        .offset(skip)
        .limit(limit)
        .order_by(AuthProfile.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def create_auth_profile(db: Session, data: AuthProfileCreate) -> AuthProfile:
    profile = AuthProfile(**data.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_auth_profile(
    db: Session, profile: AuthProfile, data: AuthProfileUpdate
) -> AuthProfile:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


def delete_auth_profile(db: Session, profile: AuthProfile) -> None:
    db.delete(profile)
    db.commit()
