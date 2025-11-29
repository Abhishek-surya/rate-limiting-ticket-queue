from sqlalchemy.orm import Session
from models.job_model import Job


def check_idempotency(db: Session, user_id: str, idempotency_key: str):
    if not idempotency_key:
        return None

    existing_job = db.query(Job).filter(
        Job.user_id == user_id,
        Job.idempotency_key == idempotency_key
    ).first()

    return existing_job
