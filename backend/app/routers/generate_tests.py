from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud import request as request_crud
from app.crud import tests as tests_crud
from app.database import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.tests import GenerateTestsRequest, GeneratedTestCase, GeneratedTestResponse
from app.services.test_generator import generate_tests

router = APIRouter(prefix="/generate-tests", tags=["tests"])


@router.post("", response_model=GeneratedTestResponse)
async def create_tests(data: GenerateTestsRequest, db: Session = Depends(get_db)):
    if data.api_request_id:
        saved = request_crud.get_request(db, data.api_request_id)
        if not saved:
            raise HTTPException(status_code=404, detail="Request not found")
        data.method = data.method or saved.method
        data.url = data.url or saved.url
        data.headers = data.headers or dict(saved.headers)
        data.body = data.body if data.body is not None else saved.body
        if not data.spec:
            data.spec = f"{saved.method.value} {saved.url} — {saved.name}"

    if not data.url and not data.spec:
        raise HTTPException(status_code=400, detail="Provide api_request_id, url, or spec")

    test_cases, llm_used = await generate_tests(data)
    tests_crud.save_tests(db, api_request_id=data.api_request_id, tests=test_cases)
    return GeneratedTestResponse(
        api_request_id=data.api_request_id,
        llm_used=llm_used,
        tests=test_cases,
    )


@router.get("", response_model=PaginatedResponse[GeneratedTestCase])
def list_generated_tests(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    api_request_id: UUID | None = None,
    db: Session = Depends(get_db),
):
    records = tests_crud.list_tests(db, skip=skip, limit=limit, api_request_id=api_request_id)
    total = tests_crud.count_tests(db, api_request_id=api_request_id)
    items = [
        GeneratedTestCase(
            name=r.name,
            test_type=r.test_type,
            description=r.description,
            method=r.method,
            url=r.url,
            headers=r.headers,
            body=r.body,
            expected_status=r.expected_status,
        )
        for r in records
    ]
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)
