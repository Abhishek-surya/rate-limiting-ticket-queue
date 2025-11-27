from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.job_model import Job
from app.schemas.job_schema import SubmitJobRequest, JobStatusResponse

router = APIRouter()

@router.post("/submit_job", response_model=JobStatusResponse)
def submit_job(request: SubmitJobRequest, db: Session = Depends(get_db)):
    

    job = Job(
        user_id=request.user_id,
        payload=request.payload,
        idempotency_key=request.idempotency_key,
        state="queued"
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return JobStatusResponse(
        job_id=job.id,
        state=job.state,
        result=job.result,
        error_message=job.error_message
    )


@router.get("/job_status/{job_id}", response_model=JobStatusResponse)
def job_status(job_id: int, db: Session = Depends(get_db)):

    job = db.query(Job).filter(Job.id == job_id).first()

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
