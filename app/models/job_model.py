from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.core.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), index=True)
    payload = Column(String(255))
    idempotency_key = Column(String(100), index=True)

    state = Column(String(20), default="queued")
    result = Column(String(255), nullable=True)
    error_message = Column(String(255), nullable=True)

    last_served = Column(DateTime, default=None, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
