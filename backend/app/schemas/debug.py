from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models import AuthType, DebugMode, HttpMethod


class FailureContext(BaseModel):
    method: HttpMethod
    url: str
    request_headers: dict = Field(default_factory=dict)
    request_body: str | None = None
    status_code: int | None = None
    response_headers: dict = Field(default_factory=dict)
    response_body: str | None = None
    latency_ms: float | None = None
    success: bool = False
    error: str | None = None


class DebugAnalyzeRequest(BaseModel):
    run_id: UUID | None = None
    context: FailureContext | None = None
    force: bool = False


class AgentTraceStep(BaseModel):
    agent: str
    output: str


class SingleDebugResult(BaseModel):
    cause: str
    fix: str
    confidence: str = "medium"


class OptimizedRequest(BaseModel):
    method: HttpMethod
    url: str
    headers: dict = Field(default_factory=dict)
    query_params: dict = Field(default_factory=dict)
    body: str | None = None
    auth_type: AuthType = AuthType.NONE
    auth_config: dict = Field(default_factory=dict)
    notes: str | None = None


class MultiAgentDebugResult(BaseModel):
    diagnosis: str
    root_cause: str
    suggested_fix: str
    validated_fix: str
    validation_passed: bool
    optimized_request: OptimizedRequest
    agent_trace: list[AgentTraceStep]


class DebugSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    run_id: UUID | None
    mode: DebugMode
    cause: str | None
    fix: str | None
    diagnosis: str | None
    root_cause: str | None
    suggested_fix: str | None
    validated_fix: str | None
    optimized_request: dict
    agent_trace: list
    llm_used: bool
    created_at: datetime


class SingleDebugResponse(BaseModel):
    session_id: UUID
    llm_used: bool
    result: SingleDebugResult


class MultiAgentDebugResponse(BaseModel):
    session_id: UUID
    llm_used: bool
    result: MultiAgentDebugResult
