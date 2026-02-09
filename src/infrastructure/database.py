import os
import logging
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')

# SQLModel engine setup
engine = None
SessionLocal = None

if DATABASE_URL:
    engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)
    logging.info("SQLModel engine and sessionmaker initialized.")

def init_db():
    """Perform database initialization tasks like seeding."""
    try:
        pass # Seeding moved to entrypoint
    except Exception:
        logging.exception("Error during database initialization/seeding")

def get_session():
    """Dependency for getting a database session."""
    if SessionLocal:
        with SessionLocal() as session:
            yield session
    else:
        yield None

# Legacy helpers for raw SQL if absolutely needed during transition
def get_db_connection():
    # Deprecated: use SQLModel Session instead
    import psycopg2
    return psycopg2.connect(DATABASE_URL)
