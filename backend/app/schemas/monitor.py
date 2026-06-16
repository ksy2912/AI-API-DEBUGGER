from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MonitorCreate(BaseModel):
    api_request_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    interval_seconds: int = Field(..., ge=30, le=86400)
    environment_id: UUID | None = None
    enabled: bool = True


class MonitorUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    interval_seconds: int | None = Field(None, ge=30, le=86400)
    environment_id: UUID | None = None
    enabled: bool | None = None


class MonitorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    api_request_id: UUID
    environment_id: UUID | None
    name: str
    interval_seconds: int
    enabled: bool
    last_run_at: datetime | None
    created_at: datetime
    updated_at: datetime
