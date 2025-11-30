from sqlalchemy.orm import Session
from app.models.job_model import Job
from sqlalchemy import asc

def pick_next_job(db: Session):
    return (
        db.query(Job)
        .filter(Job.state == "queued")
        .order_by(
            asc(Job.last_served),
            asc(Job.id)
        )
        .first()
    )
