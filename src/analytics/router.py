from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from .service import AnalyticsService, get_analytics_service
from .schema import FullAnalyticsReport
from src.database.models import User
from src.auth.dependencies import get_current_user, require_scope

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
    dependencies=[Depends(require_scope("analytics"))]
)

@router.get("/report", response_model=FullAnalyticsReport)
async def get_analytics_report(
    time_period_days: int = 7,
    user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Generates a comprehensive analytics report for the authenticated user.
    """
    if not user:
        # This should theoretically not be reached if require_scope is working
        raise HTTPException(status_code=401, detail="Authentication required.")

    report = await analytics_service.generate_report(user.id, time_period_days)
    return report
