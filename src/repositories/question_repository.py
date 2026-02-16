from sqlmodel import select, func
from sqlalchemy.orm import joinedload
from infrastructure import SessionLocal
from models import Question, Tag, QuestionTagLink
from uuid import UUID
import random

class QuestionRepository:
    def __init__(self, session=None):
        self._session = session

    def _get_session(self):
        return self._session if self._session else SessionLocal()

    def find_by_id(self, question_id: UUID):
        """Fetch question with choices and tags."""
        with self._get_session() as session:
            statement = select(Question).where(Question.id == question_id).options(
                joinedload(Question.choices),
                joinedload(Question.tags),
                joinedload(Question.categories)
            )
            return session.exec(statement).first()

    def create(self, question: Question):
        """Save a new question."""
        with self._get_session() as session:
            session.add(question)
            session.commit()
            session.refresh(question)
            return question

    def update(self, question: Question):
        """Update existing question."""
        with self._get_session() as session:
            session.add(question)
            session.commit()
            session.refresh(question)
            return question

    def find_random_by_tag(self, tag_name: str, amount: int = 1):
        """Pick N random questions that have the specified tag."""
        with self._get_session() as session:
            # Join with tags to filter, and eagerly load them for the response
            statement = select(Question).join(Question.tags).where(Tag.name.ilike(tag_name)).options(
                joinedload(Question.tags)
            )
            questions = session.exec(statement).unique().all()
            
            if not questions:
                return []
            
            # Random selection from results
            return random.sample(questions, min(len(questions), amount))
    def find_all(self, offset: int = 0, limit: int = 10):
        """Retrieve questions and total count using pagination."""
        with self._get_session() as session:

            count_stmt = select(func.count()).select_from(Question)
            total_count = session.exec(count_stmt).one()

            statement = select(Question).options(joinedload(Question.choices)).offset(offset).limit(limit)
            questions = session.exec(statement).unique().all()
            
            return questions, total_count
