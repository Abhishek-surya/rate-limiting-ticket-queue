from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List

class SubmitJobRequest(BaseModel):
    user_id: str
    payload: str
    idempotency_key: str


class JobStatusResponse(BaseModel):
    job_id: int
    state: str
    result: str | None = None
    error_message: str | None = None

    model_config = ConfigDict(from_attributes=True)


class JobDetailResponse(BaseModel):
    id: int
    user_id: str
    payload: str
    idempotency_key: str
    state: str
    result: str | None = None
    error_message: str | None = None
    last_served: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DashboardStats(BaseModel):
    total_jobs: int
    queued_count: int
    running_count: int
    done_count: int
    failed_count: int
    avg_processing_time: float | None = None


class DashboardResponse(BaseModel):
    stats: DashboardStats
    running_jobs: List[JobDetailResponse]
    failed_jobs: List[JobDetailResponse]
    recent_jobs: List[JobDetailResponse]
