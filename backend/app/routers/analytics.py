from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.analytics import AnalyticsResponse, TimeBucket
from app.services.analytics import get_analytics

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=AnalyticsResponse)
def analytics_dashboard(
    hours: int = Query(24, ge=1, le=720, description="Lookback period in hours"),
    bucket: TimeBucket = Query(TimeBucket.HOUR, description="Time bucket granularity"),
    top_limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return get_analytics(db, hours=hours, bucket=bucket, top_limit=top_limit)
