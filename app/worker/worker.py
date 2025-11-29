# app/worker/worker.py

import time
from sqlalchemy.orm import Session
from core.database import SessionLocal

from services.scheduler import pick_next_job
from services.job_service import (
    mark_job_running,
    mark_job_done,
    mark_job_failed
)


def run_worker():
    print("Worker started...")

    while True:
        db: Session = SessionLocal()

        try:
            job = pick_next_job(db)

            if job:
                print(f"[Worker] Picked Job ID: {job.id}")

                mark_job_running(db, job)
                print(f"[Worker] Job {job.id} is running...")

                time.sleep(2)

                mark_job_done(db, job, result="Job completed successfully")
                print(f"[Worker] Job {job.id} completed.")

            else:
                time.sleep(1)

        except Exception as e:
            print("[Worker Error]:", e)
            if job:
                mark_job_failed(db, job, str(e))

        finally:
            db.close()
