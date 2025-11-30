from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
load_dotenv()

import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback to SQLite if DATABASE_URL not set
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./queue.db"
    print(f"[Database] Using fallback SQLite database: {DATABASE_URL}")
else:
    print(f"[Database] Using DATABASE_URL from environment")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
