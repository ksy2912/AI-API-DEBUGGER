from datetime import datetime, timedelta, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.analytics import (
    AnalyticsResponse,
    EndpointUsage,
    KpiMetrics,
    LatencyBucket,
    TimeBucket,
    TopFailingEndpoint,
    TrafficBucket,
)

KPI_QUERY = text("""
SELECT
    COUNT(*)::int AS total_runs,
    COUNT(*) FILTER (WHERE success)::int AS success_count,
    COUNT(*) FILTER (WHERE NOT success)::int AS failure_count,
    COALESCE(ROUND(100.0 * COUNT(*) FILTER (WHERE success) / NULLIF(COUNT(*), 0), 2), 0) AS success_rate,
    COALESCE(ROUND(100.0 * COUNT(*) FILTER (WHERE NOT success) / NULLIF(COUNT(*), 0), 2), 0) AS failure_rate,
    COALESCE(ROUND(AVG(latency_ms)::numeric, 2), 0) AS avg_latency_ms,
    COALESCE(ROUND((PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms))::numeric, 2), 0) AS p95_latency_ms
FROM request_runs
WHERE created_at >= :since
""")

TRAFFIC_QUERY = text("""
SELECT
    date_trunc(:bucket, created_at AT TIME ZONE 'UTC') AS bucket,
    COUNT(*)::int AS total,
    COUNT(*) FILTER (WHERE success)::int AS success_count,
    COUNT(*) FILTER (WHERE NOT success)::int AS failure_count
FROM request_runs
WHERE created_at >= :since
GROUP BY 1
ORDER BY 1
""")

LATENCY_QUERY = text("""
SELECT
    date_trunc(:bucket, created_at AT TIME ZONE 'UTC') AS bucket,
    COALESCE(ROUND(AVG(latency_ms)::numeric, 2), 0) AS avg_latency_ms,
    COALESCE(ROUND((PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms))::numeric, 2), 0) AS p95_latency_ms
FROM request_runs
WHERE created_at >= :since
GROUP BY 1
ORDER BY 1
""")

ENDPOINT_USAGE_QUERY = text("""
SELECT
    url,
    method::text AS method,
    COUNT(*)::int AS total,
    COALESCE(ROUND(100.0 * COUNT(*) FILTER (WHERE success) / NULLIF(COUNT(*), 0), 2), 0) AS success_rate
FROM request_runs
WHERE created_at >= :since
GROUP BY url, method
ORDER BY total DESC
LIMIT :limit
""")

TOP_FAILING_QUERY = text("""
SELECT
    url,
    method::text AS method,
    COUNT(*) FILTER (WHERE NOT success)::int AS failure_count,
    MAX(created_at) FILTER (WHERE NOT success) AS last_seen,
    (
        ARRAY_AGG(error ORDER BY created_at DESC)
        FILTER (WHERE NOT success AND error IS NOT NULL)
    )[1] AS last_error
FROM request_runs
WHERE created_at >= :since
GROUP BY url, method
HAVING COUNT(*) FILTER (WHERE NOT success) > 0
ORDER BY failure_count DESC, last_seen DESC
LIMIT :limit
""")


def _since(hours: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(hours=hours)


def get_analytics(
    db: Session,
    *,
    hours: int = 24,
    bucket: TimeBucket = TimeBucket.HOUR,
    top_limit: int = 10,
) -> AnalyticsResponse:
    since = _since(hours)
    params = {"since": since, "bucket": bucket.value, "limit": top_limit}

    kpi_row = db.execute(KPI_QUERY, {"since": since}).mappings().one()
    kpis = KpiMetrics(**kpi_row)

    traffic_rows = db.execute(TRAFFIC_QUERY, params).mappings().all()
    latency_rows = db.execute(LATENCY_QUERY, params).mappings().all()
    usage_rows = db.execute(ENDPOINT_USAGE_QUERY, params).mappings().all()
    failing_rows = db.execute(TOP_FAILING_QUERY, params).mappings().all()

    return AnalyticsResponse(
        period_hours=hours,
        bucket=bucket,
        kpis=kpis,
        traffic_trend=[TrafficBucket(**row) for row in traffic_rows],
        latency_trend=[LatencyBucket(**row) for row in latency_rows],
        endpoint_usage=[EndpointUsage(**row) for row in usage_rows],
        top_failing=[TopFailingEndpoint(**row) for row in failing_rows],
    )
