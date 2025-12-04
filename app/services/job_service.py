from sqlalchemy.orm import Session
from app.models.job_model import Job


def create_new_job(db: Session, user_id: str, payload: str, idempotency_key: str):
    new_job = Job(
        user_id=user_id,
        payload=payload,
        idempotency_key=idempotency_key,
        state="queued"
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job


def get_job_by_id(db: Session, job_id: int):
    return db.query(Job).filter(Job.id == job_id).first()


def mark_job_running(db: Session, job: Job):
    job.state = "running"
    db.commit()
    db.refresh(job)
    return job


def mark_job_done(db: Session, job: Job, result: str):
    from datetime import datetime
    job.state = "done"
    job.result = result
    job.last_served = datetime.utcnow()  
    db.commit()
    db.refresh(job)
    return job


def mark_job_failed(db: Session, job: Job, error_message: str):
    job.state = "failed"
    job.error_message = error_message
    db.commit()
    db.refresh(job)
    return job


def reset_running_jobs_on_restart(db: Session):
    jobs = db.query(Job).filter(Job.state == "running").all()
    for job in jobs:
        job.state = "queued"
    db.commit()
    return jobs
