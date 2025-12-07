from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine, SessionLocal
from app.controllers.job_controller import router as job_router
from app.services.job_service import reset_running_jobs_on_restart
import threading
from app.worker.worker import run_worker


app = FastAPI(title="Ticket Queue System")

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], # allow all origins for CORS
    allow_credentials=True, # browsers allowed to send cookies along with requests
    allow_methods=["*"],  # browsers allowed to use any HTTP method (GET, POST, etc)
    allow_headers=["*"],  # browsers allowed to send any headers (Authorization, Content-Type, etc)
)

def start_worker_thread():
    worker_thread = threading.Thread(
        target=run_worker, # target function for the thread
        daemon=True    # daemon thread will exit when main program exits
    )
    worker_thread.start() 
    print("Background worker thread started!")

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine) 
    print("[Startup] Database tables created/verified")

    db = SessionLocal()
    try:
        reset_running_jobs_on_restart(db)
        print("[Startup] Reset any running jobs back to queued state")
    finally:
        db.close()

    start_worker_thread()

app.include_router(job_router) # include job-related endpoints in the main app

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        __name__ + ":app",
        host="0.0.0.0", # it will make backend accessible
        port=8000, 
        reload=True # auto-reload on code changes
    )
