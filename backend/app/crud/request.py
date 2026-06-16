from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ApiRequest
from app.schemas import ApiRequestCreate, ApiRequestUpdate


def get_request(db: Session, request_id: UUID) -> ApiRequest | None:
    return db.get(ApiRequest, request_id)


def list_requests(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    collection_id: UUID | None = None,
) -> list[ApiRequest]:
    stmt = select(ApiRequest)
    if collection_id is not None:
        stmt = stmt.where(ApiRequest.collection_id == collection_id)
    stmt = stmt.offset(skip).limit(limit).order_by(ApiRequest.created_at.desc())
    return list(db.scalars(stmt).all())


def create_request(db: Session, data: ApiRequestCreate) -> ApiRequest:
    request = ApiRequest(**data.model_dump())
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def update_request(db: Session, request: ApiRequest, data: ApiRequestUpdate) -> ApiRequest:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(request, field, value)
    db.commit()
    db.refresh(request)
    return request


def delete_request(db: Session, request: ApiRequest) -> None:
    db.delete(request)
    db.commit()
