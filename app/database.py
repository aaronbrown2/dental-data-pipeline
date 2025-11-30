from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# SQLite database file  
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dental_app.db")


# Use 'check_same_thread' only for SQLite
engine = create_engine(
    DATABASE_URL, 
    connect_args=
            {"check_same_thread": False} 
            if DATABASE_URL.startswith("sqlite") 
            else {}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()