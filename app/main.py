from fastapi import FastAPI
from app.core.database import Base, engine
from app.controllers.job_controller import router as job_router

import threading
from app.worker.worker import run_worker
from app.services.job_service import reset_running_jobs_on_restart

app = FastAPI(title="Ticket Queue")

Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup_event():
    db = next(get_db())
    reset_running_jobs_on_restart(db)
    worker_thread = threading.Thread(target=run_worker, daemon=True)
    worker_thread.start()

app.include_router(job_router) 

@app.get("/")
def home():
    return {"message": "Ticket Queue Server is running."}
