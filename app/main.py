from fastapi import FastAPI
from app.core.database import Base, engine
from app.models import job_model

app = FastAPI(title="Ticket Queue OJT - Day 1")

Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "Ticket Queue Server is running."}
