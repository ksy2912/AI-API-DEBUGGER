from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TimeBucket(str, Enum):
    HOUR = "hour"
    DAY = "day"


class KpiMetrics(BaseModel):
    total_runs: int = 0
    success_count: int = 0
    failure_count: int = 0
    success_rate: float = 0.0
    failure_rate: float = 0.0
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0


class TrafficBucket(BaseModel):
    bucket: datetime
    total: int
    success_count: int
    failure_count: int


class LatencyBucket(BaseModel):
    bucket: datetime
    avg_latency_ms: float
    p95_latency_ms: float


class EndpointUsage(BaseModel):
    url: str
    method: str
    total: int
    success_rate: float


class TopFailingEndpoint(BaseModel):
    url: str
    method: str
    failure_count: int
    last_seen: datetime | None
    last_error: str | None


class AnalyticsResponse(BaseModel):
    period_hours: int
    bucket: TimeBucket
    kpis: KpiMetrics
    traffic_trend: list[TrafficBucket] = Field(default_factory=list)
    latency_trend: list[LatencyBucket] = Field(default_factory=list)
    endpoint_usage: list[EndpointUsage] = Field(default_factory=list)
    top_failing: list[TopFailingEndpoint] = Field(default_factory=list)
