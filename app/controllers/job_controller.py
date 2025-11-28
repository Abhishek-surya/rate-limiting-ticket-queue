from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.job_model import Job
from app.schemas.job_schema import SubmitJobRequest, JobStatusResponse
from app.services.rate_limiter import check_rate_limit
from app.services.idempotency import check_idempotency
from app.services.job_service import create_new_job, get_job_by_id

router = APIRouter()

@router.post("/submit_job", response_model=JobStatusResponse)
def submit_job(request: SubmitJobRequest, db: Session = Depends(get_db)):

    check_rate_limit(request.user_id)

    existing_job = check_idempotency(db, request.user_id, request.idempotency_key)

    if existing_job:
        return JobStatusResponse(
            job_id=existing_job.id,
            state=existing_job.state,
            result=existing_job.result,
            error_message=existing_job.error_message
        )
    
    
    job = create_new_job(
        db=db,
        user_id=request.user_id,
        payload=request.payload,
        idempotency_key=request.idempotency_key
    )

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
