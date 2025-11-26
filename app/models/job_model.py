from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), index=True)
    payload = Column(String(255))
    state = Column(String(20), default="queued")
