import os
import logging
from sqlmodel import create_engine, Session
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get('DATABASE_URL')

engine = create_engine(DATABASE_URL, echo=False) if DATABASE_URL else None
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session) if engine else None

if engine:
    logging.info("SQLModel engine and sessionmaker initialized.")

def get_session():
    """Dependency for getting a database session."""
    if SessionLocal:
        with SessionLocal() as session:
            yield session
    else:
        yield None
