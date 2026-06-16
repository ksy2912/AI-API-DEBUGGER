import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pgvector.sqlalchemy import Vector

from app.database import Base


class HttpMethod(str, enum.Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class AuthType(str, enum.Enum):
    NONE = "none"
    BEARER = "bearer"
    BASIC = "basic"
    API_KEY = "api_key"


class DebugMode(str, enum.Enum):
    SINGLE = "single"
    MULTI_AGENT = "multi_agent"


class Collection(Base):
    __tablename__ = "collections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    requests: Mapped[list["ApiRequest"]] = relationship(
        back_populates="collection", cascade="all, delete-orphan"
    )


class Environment(Base):
    __tablename__ = "environments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    variables: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    secret_keys: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class AuthProfile(Base):
    __tablename__ = "auth_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    auth_type: Mapped[AuthType] = mapped_column(
        Enum(AuthType, name="auth_type", values_callable=lambda e: [a.value for a in e]),
        nullable=False,
        default=AuthType.NONE,
    )
    auth_config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class ApiRequest(Base):
    __tablename__ = "api_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    collection_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("collections.id", ondelete="CASCADE"), nullable=True
    )
    environment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("environments.id", ondelete="SET NULL"), nullable=True
    )
    auth_profile_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("auth_profiles.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    method: Mapped[HttpMethod] = mapped_column(
        Enum(HttpMethod, name="http_method", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
        default=HttpMethod.GET,
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    headers: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    query_params: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    auth_type: Mapped[AuthType] = mapped_column(
        Enum(AuthType, name="auth_type", values_callable=lambda e: [a.value for a in e]),
        nullable=False,
        default=AuthType.NONE,
    )
    auth_config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    collection: Mapped[Collection | None] = relationship(back_populates="requests")
    environment: Mapped[Environment | None] = relationship()
    auth_profile: Mapped[AuthProfile | None] = relationship()
    runs: Mapped[list["RequestRun"]] = relationship(
        back_populates="api_request", cascade="all, delete-orphan"
    )
    monitors: Mapped[list["MonitorSchedule"]] = relationship(
        back_populates="api_request", cascade="all, delete-orphan"
    )


class RequestRun(Base):
    __tablename__ = "request_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    api_request_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("api_requests.id", ondelete="SET NULL"), nullable=True
    )
    monitor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("monitor_schedules.id", ondelete="SET NULL"), nullable=True
    )
    environment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("environments.id", ondelete="SET NULL"), nullable=True
    )
    method: Mapped[HttpMethod] = mapped_column(
        Enum(HttpMethod, name="http_method", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    request_headers: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    request_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_headers: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    response_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    api_request: Mapped[ApiRequest | None] = relationship(back_populates="runs")
    monitor: Mapped["MonitorSchedule | None"] = relationship(back_populates="runs")
    debug_sessions: Mapped[list["DebugSession"]] = relationship(back_populates="run")


class DebugSession(Base):
    __tablename__ = "debug_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("request_runs.id", ondelete="SET NULL"), nullable=True
    )
    mode: Mapped[DebugMode] = mapped_column(
        Enum(DebugMode, name="debug_mode", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    fix: Mapped[str | None] = mapped_column(Text, nullable=True)
    diagnosis: Mapped[str | None] = mapped_column(Text, nullable=True)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_fix: Mapped[str | None] = mapped_column(Text, nullable=True)
    validated_fix: Mapped[str | None] = mapped_column(Text, nullable=True)
    optimized_request: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    agent_trace: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    llm_used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    run: Mapped[RequestRun | None] = relationship(back_populates="debug_sessions")


class LogEmbedding(Base):
    __tablename__ = "log_embeddings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding = mapped_column(Vector(1536), nullable=False)
    meta: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class GeneratedTest(Base):
    __tablename__ = "generated_tests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    api_request_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("api_requests.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    test_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    method: Mapped[HttpMethod] = mapped_column(
        Enum(HttpMethod, name="http_method", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    headers: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class MonitorSchedule(Base):
    __tablename__ = "monitor_schedules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    api_request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("api_requests.id", ondelete="CASCADE"), nullable=False
    )
    environment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("environments.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    interval_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    api_request: Mapped[ApiRequest] = relationship(back_populates="monitors")
    environment: Mapped[Environment | None] = relationship()
    runs: Mapped[list[RequestRun]] = relationship(back_populates="monitor")
