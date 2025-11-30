from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.job_model import Job
from app.schemas.job_schema import SubmitJobRequest, JobStatusResponse, DashboardResponse, DashboardStats, JobDetailResponse
from app.services.rate_limiter import check_rate_limit
from app.services.idempotency import check_idempotency
from app.services.job_service import create_new_job, get_job_by_id, mark_job_failed
from app.services.dashboard_service import get_running_jobs, get_dashboard_stats, get_recent_jobs, get_failed_jobs

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/submit_job", response_model=JobStatusResponse)
def submit_job(request: SubmitJobRequest, db: Session = Depends(get_db)):

    # Idempotency check first (per user + idempotency key)
    existing_job = check_idempotency(db, request.user_id, request.idempotency_key)

    if existing_job:
        return JobStatusResponse(
            job_id=existing_job.id,
            state=existing_job.state,
            result=existing_job.result,
            error_message=existing_job.error_message
        )
    
    # Check rate limit BEFORE creating the job
    rate_limit_error = None
    try:
        check_rate_limit(request.user_id)
    except HTTPException as e:
        # Capture the error message (global or per-user limit)
        rate_limit_error = e.detail if isinstance(e.detail, str) else str(e.detail)
    
    # Create job based on request/payload type
    job = create_new_job(
        db=db,
        user_id=request.user_id,
        payload=request.payload,
        idempotency_key=request.idempotency_key
    )
    
    # If rate limit was exceeded, mark job as failed with specific error
    if rate_limit_error:
        mark_job_failed(db, job, rate_limit_error)
        
        return JobStatusResponse(
            job_id=job.id,
            state="failed",
            result=None,
            error_message=rate_limit_error
        )
    
    # Job created successfully and queued
    return JobStatusResponse(
        job_id=job.id,
        state=job.state,
        result=job.result,
        error_message=job.error_message
    )


@router.get("/job_status/{job_id}", response_model=JobStatusResponse)
def job_status(job_id: int, db: Session = Depends(get_db)):

    job = get_job_by_id(db, job_id)

    if not job:
        return JobStatusResponse(
            job_id=job_id,
            state="not_found",
            result=None,
            error_message="Job not found"
        )

    return JobStatusResponse(
        job_id=job.id,
        state=job.state,
        result=job.result,
        error_message=job.error_message
    )


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(db: Session = Depends(get_db)):
    """Get dashboard with job statistics and recent jobs"""
    
    stats = get_dashboard_stats(db)
    
    # Get running jobs
    running_jobs = get_running_jobs(db)
    
    # Get failed jobs
    failed_jobs = get_failed_jobs(db, limit=10)
    
    # Get recent jobs (last 20)
    recent_jobs = get_recent_jobs(db, limit=20)
    
    return DashboardResponse(
        stats=DashboardStats(**stats),
        running_jobs=[JobDetailResponse.from_orm(job) for job in running_jobs],
        failed_jobs=[JobDetailResponse.from_orm(job) for job in failed_jobs],
        recent_jobs=[JobDetailResponse.from_orm(job) for job in recent_jobs]
    )
