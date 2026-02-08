import os
import psycopg2
import psycopg2.extras
from psycopg2 import pool
import logging

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')

# Connection pool setup
db_pool = None

def init_db():
    global db_pool
    try:
        if DATABASE_URL:
            db_pool = psycopg2.pool.SimpleConnectionPool(1, 10, dsn=DATABASE_URL)
            logging.info("Database connection pool initialized.")
        else:
            logging.warning("DATABASE_URL not set. Database integration disabled.")
    except Exception as e:
        logging.error(f"Error initializing database pool: {e}")

def get_db_connection():
    if db_pool:
        return db_pool.getconn()
    return None

def release_db_connection(conn):
    if db_pool and conn:
        db_pool.putconn(conn)

def query_db(query, args=(), one=False):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, args)
            rv = cur.fetchall()
            return (rv[0] if rv else None) if one else rv
    except Exception as e:
        logging.error(f"Database query error: {e}")
        return None
    finally:
        release_db_connection(conn)

def get_problem_details(problem_id):
    """Fetch problem metadata, categories, and tags."""
    problem = query_db("SELECT id, title, description, difficulty, config FROM problems WHERE id = %s", (problem_id,), one=True)
    if not problem:
        return None
    
    # Filter config to only include allowed keys
    allowed_keys = {'timeout', 'templates'}
    original_config = problem.get('config', {})
    problem['config'] = {k: v for k, v in original_config.items() if k in allowed_keys}
    
    problem['categories'] = [c['name'] for c in query_db("""
        SELECT c.name FROM categories c
        JOIN problem_categories pc ON c.id = pc.category_id
        WHERE pc.problem_id = %s
    """, (problem_id,))] or []
    
    problem['tags'] = [t['name'] for t in query_db("""
        SELECT t.name FROM tags t
        JOIN problem_tags pt ON t.id = pt.tag_id
        WHERE pt.problem_id = %s
    """, (problem_id,))] or []
    
    return problem

def get_problem_test_cases(problem_id):
    """Fetch all test cases for a problem (used for execution)."""
    return query_db("SELECT input, output as expected_output, sort_order as test_number FROM test_cases WHERE problem_id = %s ORDER BY sort_order", (problem_id,))

def get_public_test_cases(problem_id):
    """Fetch only non-hidden test cases (used for problem description)."""
    return query_db("SELECT input, output, sort_order FROM test_cases WHERE problem_id = %s AND is_hidden = FALSE ORDER BY sort_order", (problem_id,))

def list_problems():
    """List all problems with basic info."""
    return query_db("SELECT id, title, difficulty FROM problems ORDER BY created_at DESC")
