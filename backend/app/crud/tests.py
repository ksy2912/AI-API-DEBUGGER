from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import GeneratedTest


def save_tests(
    db: Session,
    *,
    api_request_id: UUID | None,
    tests: list,
) -> list[GeneratedTest]:
    records = []
    for test in tests:
        record = GeneratedTest(
            api_request_id=api_request_id,
            name=test.name,
            test_type=test.test_type,
            description=test.description,
            method=test.method,
            url=test.url,
            headers=test.headers,
            body=test.body,
            expected_status=test.expected_status,
        )
        db.add(record)
        records.append(record)
    db.commit()
    for record in records:
        db.refresh(record)
    return records


def list_tests(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    api_request_id: UUID | None = None,
) -> list[GeneratedTest]:
    stmt = select(GeneratedTest)
    if api_request_id:
        stmt = stmt.where(GeneratedTest.api_request_id == api_request_id)
    stmt = stmt.offset(skip).limit(limit).order_by(GeneratedTest.created_at.desc())
    return list(db.scalars(stmt).all())


def count_tests(db: Session, api_request_id: UUID | None = None) -> int:
    stmt = select(func.count()).select_from(GeneratedTest)
    if api_request_id:
        stmt = stmt.where(GeneratedTest.api_request_id == api_request_id)
    return db.scalar(stmt) or 0
