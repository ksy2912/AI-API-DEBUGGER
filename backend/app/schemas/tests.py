from uuid import UUID

from pydantic import BaseModel, Field

from app.models import HttpMethod


class GenerateTestsRequest(BaseModel):
    api_request_id: UUID | None = None
    spec: str | None = Field(None, description="API spec or description to generate tests from")
    method: HttpMethod | None = None
    url: str | None = None
    headers: dict = Field(default_factory=dict)
    body: str | None = None
    count: int = Field(5, ge=1, le=20)


class GeneratedTestCase(BaseModel):
    name: str
    test_type: str
    description: str
    method: HttpMethod
    url: str
    headers: dict = Field(default_factory=dict)
    body: str | None = None
    expected_status: int | None = None


class GeneratedTestResponse(BaseModel):
    id: UUID | None = None
    api_request_id: UUID | None
    llm_used: bool
    tests: list[GeneratedTestCase]
