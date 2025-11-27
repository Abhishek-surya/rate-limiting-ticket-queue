from fastapi import FastAPI
from app.core.database import Base, engine
from app.controllers.job_controller import router as job_router

app = FastAPI(title="Ticket Queue")

Base.metadata.create_all(bind=engine)

app.include_router(job_router) 

@app.get("/")
def home():
    return {"message": "Ticket Queue Server is running."}
