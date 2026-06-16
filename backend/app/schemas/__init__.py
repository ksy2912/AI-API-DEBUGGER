from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models import AuthType, HttpMethod


class CollectionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class CollectionCreate(CollectionBase):
    pass


class CollectionUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class CollectionResponse(CollectionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class CollectionWithRequests(CollectionResponse):
    requests: list["ApiRequestResponse"] = []


class ApiRequestBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    method: HttpMethod = HttpMethod.GET
    url: str = Field(..., min_length=1)
    headers: dict = Field(default_factory=dict)
    query_params: dict = Field(default_factory=dict)
    body: str | None = None
    auth_type: AuthType = AuthType.NONE
    auth_config: dict = Field(default_factory=dict)
    collection_id: UUID | None = None
    environment_id: UUID | None = None
    auth_profile_id: UUID | None = None


class ApiRequestCreate(ApiRequestBase):
    pass


class ApiRequestUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    method: HttpMethod | None = None
    url: str | None = Field(None, min_length=1)
    headers: dict | None = None
    query_params: dict | None = None
    body: str | None = None
    auth_type: AuthType | None = None
    auth_config: dict | None = None
    collection_id: UUID | None = None
    environment_id: UUID | None = None
    auth_profile_id: UUID | None = None


class ApiRequestResponse(ApiRequestBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


CollectionWithRequests.model_rebuild()
