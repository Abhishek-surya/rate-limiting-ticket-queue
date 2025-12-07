from sqlalchemy.orm import Session
import hashlib
from app.models.job_model import Job


def check_idempotency(db: Session, payload: str):
    idem_key = hashlib.md5(payload.encode()).hexdigest() # encode string payload to bytes before hasing
    existing_job = db.query(Job).filter(Job.idempotency_key == idem_key).first()
    return existing_job, idem_key
