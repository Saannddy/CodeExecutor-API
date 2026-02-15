from sqlmodel import select
from infrastructure import SessionLocal
from models import Choice
from uuid import UUID

class ChoiceRepository:
    def __init__(self, session=None):
        self._session = session

    def _get_session(self):
        return self._session if self._session else SessionLocal()

    def find_by_id(self, choice_id: UUID):
        """Fetch a choice by ID."""
        with self._get_session() as session:
            return session.get(Choice, choice_id)

    def create(self, choice: Choice):
        """Save a new choice."""
        with self._get_session() as session:
            session.add(choice)
            session.commit()
            session.refresh(choice)
            return choice

    def update(self, choice: Choice):
        """Update existing choice."""
        with self._get_session() as session:
            session.add(choice)
            session.commit()
            session.refresh(choice)
            return choice

    def count_by_question_id(self, question_id: UUID):
        """Count how many choices a question has."""
        with self._get_session() as session:
            statement = select(Choice).where(Choice.question_id == question_id)
            return len(session.exec(statement).all())
