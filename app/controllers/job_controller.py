from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import hashlib

from app.core.database import get_db
from app.schemas.job_schema import SubmitJobRequest, JobStatusResponse, DashboardResponse, DashboardStats, JobDetailResponse
from app.services.rate_limiter import check_rate_limit
from app.services.idempotency import check_idempotency
from app.services.job_service import create_new_job, get_job_by_id, mark_job_failed
from app.services.dashboard_service import get_running_jobs, get_dashboard_stats, get_recent_jobs, get_failed_jobs

router = APIRouter(prefix="/jobs", tags=["Jobs"]) # grouping endpoints in jobs section 

@router.post("/submit_job", response_model=JobStatusResponse) # response_model defines the expected response schema
def submit_job(request: SubmitJobRequest, db: Session = Depends(get_db)): # dependency injection for database session 

    existing_job, idem_key = check_idempotency(db, request.payload) 

    if existing_job:
        return JobStatusResponse(
            job_id=existing_job.id, # existing_job is instance of Job model 
            state=existing_job.state,
            result=existing_job.result,
            error_message=existing_job.error_message,
            idempotency_key=existing_job.idempotency_key,
            is_duplicate=True
        )
    
    rate_limit_error = None 
    try:
        check_rate_limit(request.user_id)
    except HTTPException as e:
        rate_limit_error = e.detail if isinstance(e.detail, str) else str(e.detail) # isinstance check to ensure detail is string

    job = create_new_job(
        db=db, 
        user_id=request.user_id,
        payload=request.payload,
        idempotency_key=idem_key
    )
    
    if rate_limit_error:
        mark_job_failed(db, job, rate_limit_error)
        
        return JobStatusResponse(
            job_id=job.id,
            state="failed",
            result=None,
            error_message=rate_limit_error,
            idempotency_key=idem_key,
            is_duplicate=False
        )
    
    return JobStatusResponse(
        job_id=job.id,
        state=job.state,
        result=job.result,
        error_message=job.error_message,
        idempotency_key=idem_key,
        is_duplicate=False
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
    running_jobs = get_running_jobs(db)
    failed_jobs = get_failed_jobs(db, limit=10)
    recent_jobs = get_recent_jobs(db, limit=20)
    
    return DashboardResponse(
        stats=DashboardStats(**stats), # unpacking stats dictionary into DashboardStats model 
        running_jobs=[JobDetailResponse.model_validate(job) for job in  running_jobs], # model_validate converts ORM objects to pydantic schema for json reponse and stores in list
        failed_jobs=[JobDetailResponse.model_validate(job) for job in failed_jobs], 
        recent_jobs=[JobDetailResponse.model_validate(job) for job in recent_jobs]
    )
