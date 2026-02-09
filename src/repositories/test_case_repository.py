from sqlmodel import select
from infrastructure.database import SessionLocal
from models import TestCase

class TestCaseRepository:
    def __init__(self, session=None):
        self._session = session

    def _get_session(self):
        return self._session if self._session else SessionLocal()

    def find_all_by_problem(self, problem_id):
        """Fetch all test cases for a problem (internal/execution use)."""
        with self._get_session() as session:
            statement = select(TestCase).where(TestCase.problem_id == problem_id).order_by(TestCase.sort_order)
            results = session.exec(statement).all()
            # Map to expected format for execution engine
            return [{"input": tc.input, "expected_output": tc.output, "test_number": tc.sort_order} for tc in results]

    def find_public_by_problem(self, problem_id):
        """Fetch only non-hidden test cases (public description use)."""
        with self._get_session() as session:
            statement = select(TestCase).where(
                TestCase.problem_id == problem_id, 
                TestCase.is_hidden == False
            ).order_by(TestCase.sort_order)
            return [tc.model_dump(exclude={"is_hidden"}) for tc in session.exec(statement).all()]
