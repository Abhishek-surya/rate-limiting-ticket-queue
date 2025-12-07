from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
load_dotenv()

import os

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set!")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in str(DATABASE_URL) else {}
)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, # bind the engine to the sessionmaker
)

Base = declarative_base() # base class for all ORM models 

def get_db(): # Dependency to get DB session
    db = SessionLocal() 
    try:
        yield db 
    finally:
        db.close()
