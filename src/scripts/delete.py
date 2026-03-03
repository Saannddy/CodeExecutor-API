import logging
from sqlalchemy import text
from sqlmodel import Session
from infrastructure import engine

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def delete_all_data():
    if not engine:
        logging.error("No database engine found. Skipping deletion.")
        return

    with Session(engine) as session:
        logging.info("Deleting all data from database...")
        
        # Order matters due to foreign key constraints if not using CASCADE
        # However, TRUNCATE with CASCADE is the most thorough way
        tables = [
            "riddle_tags",
            "question_tags",
            "question_categories",
            "choices",
            "questions",
            "riddles",
            "problem_categories",
            "problem_tags",
            "test_cases",
            "chunks_categories",
            "chunks_tags",
            "snippets",
            "expectations",
            "chunk_templates",
            "chunks",
            "problems",
            "categories",
            "tags"
        ]
        
        try:
            for table in tables:
                logging.info(f"Deleting data from {table}...")
                session.exec(text(f"DELETE FROM {table}"))
            
            session.commit()
            logging.info("Successfully deleted all data from the database.")
        except Exception as e:
            session.rollback()
            logging.error(f"Error during deletion: {e}")

if __name__ == "__main__":
    delete_all_data()
