from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

class UsageSummary(BaseModel):
    total_requests: int
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    total_cost: float

class PlatformUsage(BaseModel):
    platform: str
    request_count: int
    total_tokens: int
    total_cost: float

class CostOverTime(BaseModel):
    timestamp: datetime
    cost: float

class LatencyOverTime(BaseModel):
    timestamp: datetime
    avg_latency_ms: float

class ErrorRate(BaseModel):
    total_requests: int
    failed_requests: int
    error_rate: float # As a percentage

class FullAnalyticsReport(BaseModel):
    user_id: str
    time_period_days: int
    summary: UsageSummary
    platform_breakdown: List[PlatformUsage]
    cost_trend: List[CostOverTime]
    latency_trend: List[LatencyOverTime]
    error_rate: ErrorRate
