from sqlmodel import select, func
from sqlalchemy.orm import joinedload
from infrastructure import SessionLocal
from models import Riddle, Tag
from uuid import UUID
import random

class RiddleRepository:
    def __init__(self, session=None):
        self._session = session

    def _get_session(self):
        return self._session if self._session else SessionLocal()

    def find_by_id(self, riddle_id: UUID):
        """Fetch riddle by ID."""
        with self._get_session() as session:
            statement = select(Riddle).where(Riddle.id == riddle_id).options(
                joinedload(Riddle.tags)
            )
            return session.exec(statement).first()

    def create(self, riddle: Riddle):
        """Save a new riddle."""
        with self._get_session() as session:
            session.add(riddle)
            session.commit()
            session.refresh(riddle)
            return riddle

    def update(self, riddle: Riddle):
        """Update existing riddle."""
        with self._get_session() as session:
            session.add(riddle)
            session.commit()
            session.refresh(riddle)
            return riddle

    def find_all(self, offset: int = 0, limit: int = 10):
        """Retrieve riddles and total count using pagination."""
        with self._get_session() as session:
            count_stmt = select(func.count()).select_from(Riddle)
            total_count = session.exec(count_stmt).one()
            
            statement = select(Riddle).options(joinedload(Riddle.tags)).offset(offset).limit(limit)
            riddles = session.exec(statement).unique().all()
            
            return riddles, total_count

    def find_random_per_index(self, amount: int):
        """Pick one random riddle for each refer_index from 1 to amount."""
        riddles_group = []
        with self._get_session() as session:
            for i in range(1, amount + 1):
                statement = select(Riddle).where(Riddle.refer_index == i)
                results = session.exec(statement).all()
                if results:
                    riddles_group.append(random.choice(results))
                else:
                    # If we can't find a riddle for a specific index, we stop or skip?
                    # Usually we want a complete group, but let's just skip for now or add None
                    pass
        return riddles_group
