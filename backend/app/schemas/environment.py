from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models import AuthType


class EnvironmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    variables: dict[str, str] = Field(default_factory=dict)
    secret_keys: list[str] = Field(default_factory=list)


class EnvironmentCreate(EnvironmentBase):
    pass


class EnvironmentUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    variables: dict[str, str] | None = None
    secret_keys: list[str] | None = None


class EnvironmentResponse(EnvironmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


def mask_secrets(env: EnvironmentBase, secret_keys: list[str]) -> dict[str, str]:
    masked = dict(env.variables)
    for key in secret_keys:
        if key in masked:
            masked[key] = "***"
    return masked


class EnvironmentPublic(EnvironmentResponse):
    @classmethod
    def from_model(cls, env) -> "EnvironmentPublic":
        data = EnvironmentResponse.model_validate(env).model_dump()
        data["variables"] = mask_secrets(env, env.secret_keys or [])
        return cls(**data)


class AuthProfileBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    auth_type: AuthType = AuthType.NONE
    auth_config: dict = Field(default_factory=dict)


class AuthProfileCreate(AuthProfileBase):
    pass


class AuthProfileUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    auth_type: AuthType | None = None
    auth_config: dict | None = None


class AuthProfileResponse(AuthProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
