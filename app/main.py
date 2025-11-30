from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine, SessionLocal
from sqlalchemy import inspect, text
from app.models.job_model import Job
from app.controllers.job_controller import router as job_router
import threading
from app.worker.worker import run_worker



app = FastAPI(title="Ticket Queue System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

def start_worker_thread():
    worker_thread = threading.Thread(
        target=run_worker,
        daemon=True    
    )
    worker_thread.start()
    print("Background worker thread started!")

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    print("[Startup] Database tables created/verified")
    
    start_worker_thread()

app.include_router(job_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        __name__ + ":app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
