from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models import AuthType, HttpMethod


class ExecuteRequest(BaseModel):
    method: HttpMethod = HttpMethod.GET
    url: str = Field(..., min_length=1)
    headers: dict[str, str] = Field(default_factory=dict)
    query_params: dict[str, str] = Field(default_factory=dict)
    body: str | None = None
    auth_type: AuthType = AuthType.NONE
    auth_config: dict = Field(default_factory=dict)
    timeout_seconds: float = Field(30.0, gt=0, le=120)
    environment_id: UUID | None = None
    api_request_id: UUID | None = None


class ExecuteResponse(BaseModel):
    run_id: UUID | None = None
    status_code: int | None = None
    headers: dict[str, str] = Field(default_factory=dict)
    body: str | None = None
    latency_ms: float
    success: bool
    error: str | None = None


class RequestRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    api_request_id: UUID | None
    monitor_id: UUID | None
    environment_id: UUID | None
    method: HttpMethod
    url: str
    request_headers: dict
    request_body: str | None
    status_code: int | None
    response_headers: dict
    response_body: str | None
    latency_ms: float
    success: bool
    error: str | None
    created_at: datetime
