from datetime import datetime, timedelta
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from functools import lru_cache

from src.database.models import UsageLog, User
from .schema import (
    UsageSummary,
    PlatformUsage,
    CostOverTime,
    LatencyOverTime,
    ErrorRate,
    FullAnalyticsReport,
)

class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_report(self, user_id: str, time_period_days: int) -> FullAnalyticsReport:
        start_date = datetime.utcnow() - timedelta(days=time_period_days)

        # Base query for the given user and time period
        base_query = select(UsageLog).where(
            UsageLog.user_id == user_id,
            UsageLog.timestamp >= start_date
        )

        # 1. Usage Summary
        summary_query = select(
            func.count(UsageLog.id).label("total_requests"),
            func.sum(UsageLog.total_tokens).label("total_tokens"),
            func.sum(UsageLog.prompt_tokens).label("prompt_tokens"),
            func.sum(UsageLog.completion_tokens).label("completion_tokens"),
            func.sum(UsageLog.cost).label("total_cost")
        ).where(UsageLog.user_id == user_id, UsageLog.timestamp >= start_date)
        summary_res = (await self.db.execute(summary_query)).first()
        summary = UsageSummary(
            total_requests=summary_res.total_requests or 0,
            total_tokens=summary_res.total_tokens or 0,
            prompt_tokens=summary_res.prompt_tokens or 0,
            completion_tokens=summary_res.completion_tokens or 0,
            total_cost=summary_res.total_cost or 0.0
        )

        # 2. Platform Breakdown
        platform_query = select(
            UsageLog.platform,
            func.count(UsageLog.id).label("request_count"),
            func.sum(UsageLog.total_tokens).label("total_tokens"),
            func.sum(UsageLog.cost).label("total_cost")
        ).where(
            UsageLog.user_id == user_id,
            UsageLog.timestamp >= start_date
        ).group_by(UsageLog.platform)
        platform_res = (await self.db.execute(platform_query)).all()
        platform_breakdown = [PlatformUsage(**row._asdict()) for row in platform_res]

        # 3. Cost Over Time
        cost_trend_query = select(
            func.date_trunc('day', UsageLog.timestamp).label("timestamp"),
            func.sum(UsageLog.cost).label("cost")
        ).where(
            UsageLog.user_id == user_id,
            UsageLog.timestamp >= start_date
        ).group_by(func.date_trunc('day', UsageLog.timestamp)).order_by(func.date_trunc('day', UsageLog.timestamp))
        cost_trend_res = (await self.db.execute(cost_trend_query)).all()
        cost_trend = [CostOverTime(**row._asdict()) for row in cost_trend_res]

        # 4. Latency Over Time
        latency_trend_query = select(
            func.date_trunc('day', UsageLog.timestamp).label("timestamp"),
            func.avg(UsageLog.latency_ms).label("avg_latency_ms")
        ).where(
            UsageLog.user_id == user_id,
            UsageLog.timestamp >= start_date
        ).group_by(func.date_trunc('day', UsageLog.timestamp)).order_by(func.date_trunc('day', UsageLog.timestamp))
        latency_trend_res = (await self.db.execute(latency_trend_query)).all()
        latency_trend = [LatencyOverTime(**row._asdict()) for row in latency_trend_res]

        # 5. Error Rate (Placeholder - requires error logging)
        # For now, we'll return a zero error rate. This requires enhancing UsageLog or adding a new table.
        error_rate = ErrorRate(total_requests=summary.total_requests, failed_requests=0, error_rate=0.0)

        return FullAnalyticsReport(
            user_id=user_id,
            time_period_days=time_period_days,
            summary=summary,
            platform_breakdown=platform_breakdown,
            cost_trend=cost_trend,
            latency_trend=latency_trend,
            error_rate=error_rate
        )

from fastapi import Depends
from src.database.session import get_db

def get_analytics_service(db: AsyncSession = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)
