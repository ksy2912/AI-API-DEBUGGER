from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Environment
from app.schemas.environment import EnvironmentCreate, EnvironmentUpdate


def get_environment(db: Session, environment_id: UUID) -> Environment | None:
    return db.get(Environment, environment_id)


def list_environments(db: Session, skip: int = 0, limit: int = 100) -> list[Environment]:
    stmt = (
        select(Environment)
        .offset(skip)
        .limit(limit)
        .order_by(Environment.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def create_environment(db: Session, data: EnvironmentCreate) -> Environment:
    environment = Environment(**data.model_dump())
    db.add(environment)
    db.commit()
    db.refresh(environment)
    return environment


def update_environment(
    db: Session, environment: Environment, data: EnvironmentUpdate
) -> Environment:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(environment, field, value)
    db.commit()
    db.refresh(environment)
    return environment


def delete_environment(db: Session, environment: Environment) -> None:
    db.delete(environment)
    db.commit()
