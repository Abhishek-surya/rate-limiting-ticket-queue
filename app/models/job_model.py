from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
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
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc)) # lambda function called at insertion time to get current utc time
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)) # onupdate called at every update to set current utc time 
