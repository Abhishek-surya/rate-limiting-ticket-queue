from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.job_model import Job
from datetime import datetime


def get_all_jobs(db: Session):
    """Get all jobs"""
    return db.query(Job).all()


def get_jobs_by_state(db: Session, state: str):
    """Get jobs by state"""
    return db.query(Job).filter(Job.state == state).all()


def get_running_jobs(db: Session):
    """Get all running jobs"""
    return db.query(Job).filter(Job.state == "running").all()


def get_dashboard_stats(db: Session):
    """Get dashboard statistics"""
    total = db.query(func.count(Job.id)).scalar()
    queued = db.query(func.count(Job.id)).filter(Job.state == "queued").scalar()
    running = db.query(func.count(Job.id)).filter(Job.state == "running").scalar()
    done = db.query(func.count(Job.id)).filter(Job.state == "done").scalar()
    failed = db.query(func.count(Job.id)).filter(Job.state == "failed").scalar()
    
    return {
        "total_jobs": total or 0,
        "queued_count": queued or 0,
        "running_count": running or 0,
        "done_count": done or 0,
        "failed_count": failed or 0,
    }


def get_failed_jobs(db: Session, limit: int = 10):
    """Get recent failed jobs"""
    return db.query(Job).filter(Job.state == "failed").order_by(Job.updated_at.desc()).limit(limit).all()


def get_recent_jobs(db: Session, limit: int = 20):
    """Get recent jobs"""
    return db.query(Job).order_by(Job.created_at.desc()).limit(limit).all()
