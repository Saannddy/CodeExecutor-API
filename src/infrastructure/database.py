import os
import psycopg2
import psycopg2.extras
from psycopg2 import pool
import logging

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')

# Connection pool setup
db_pool = None

from yoyo import read_migrations, get_backend

def init_db():
    global db_pool
    try:
        if DATABASE_URL:
            db_pool = psycopg2.pool.SimpleConnectionPool(1, 10, dsn=DATABASE_URL)
            logging.info("Database connection pool initialized.")
            
            # Run migrations
            backend = get_backend(DATABASE_URL)
            migrations = read_migrations('./migrations')
            with backend.lock():
                backend.apply_migrations(backend.to_apply(migrations))
            logging.info("Database migrations applied successfully.")
        else:
            logging.warning("DATABASE_URL not set. Database integration disabled.")
    except Exception as e:
        logging.error(f"Error initializing database pool or running migrations: {e}")

def get_db_connection():
    if db_pool:
        return db_pool.getconn()
    return None

def release_db_connection(conn):
    if db_pool and conn:
        db_pool.putconn(conn)

def query_one(query, args=()):
    """Execute query and return one result."""
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, args)
            return cur.fetchone()
    except Exception as e:
        logging.error(f"Database query error: {e}")
        return None
    finally:
        release_db_connection(conn)

def query_all(query, args=()):
    """Execute query and return all results."""
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, args)
            return cur.fetchall()
    except Exception as e:
        logging.error(f"Database query error: {e}")
        return []
    finally:
        release_db_connection(conn)
