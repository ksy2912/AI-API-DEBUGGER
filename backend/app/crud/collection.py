from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Collection
from app.schemas import CollectionCreate, CollectionUpdate


def get_collection(db: Session, collection_id: UUID) -> Collection | None:
    return db.get(Collection, collection_id)


def list_collections(db: Session, skip: int = 0, limit: int = 100) -> list[Collection]:
    stmt = select(Collection).offset(skip).limit(limit).order_by(Collection.created_at.desc())
    return list(db.scalars(stmt).all())


def create_collection(db: Session, data: CollectionCreate) -> Collection:
    collection = Collection(**data.model_dump())
    db.add(collection)
    db.commit()
    db.refresh(collection)
    return collection


def update_collection(
    db: Session, collection: Collection, data: CollectionUpdate
) -> Collection:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(collection, field, value)
    db.commit()
    db.refresh(collection)
    return collection


def delete_collection(db: Session, collection: Collection) -> None:
    db.delete(collection)
    db.commit()
