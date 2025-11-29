from sqlalchemy.orm import Session
from sqlalchemy import func
from models.job_model import Job
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
    
    # Calculate average processing time for completed jobs
    avg_time = None
    completed_jobs = db.query(Job).filter(Job.state.in_(["done", "failed"])).all()
    if completed_jobs:
        total_time = 0
        count = 0
        for job in completed_jobs:
            if job.last_served and job.created_at:
                delta = (job.last_served - job.created_at).total_seconds()
                total_time += delta
                count += 1
        if count > 0:
            avg_time = total_time / count
    
    return {
        "total_jobs": total or 0,
        "queued_count": queued or 0,
        "running_count": running or 0,
        "done_count": done or 0,
        "failed_count": failed or 0,
        "avg_processing_time": avg_time
    }


def get_failed_jobs(db: Session, limit: int = 10):
    """Get recent failed jobs"""
    return db.query(Job).filter(Job.state == "failed").order_by(Job.updated_at.desc()).limit(limit).all()


def get_recent_jobs(db: Session, limit: int = 20):
    """Get recent jobs"""
    return db.query(Job).order_by(Job.created_at.desc()).limit(limit).all()
