from sqlmodel import select
from infrastructure import SessionLocal
from models import TestCase

class TestCaseRepository:
    def __init__(self, session=None):
        self._session = session

    def _get_session(self):
        return self._session if self._session else SessionLocal()

    def find_all_by_problem(self, problem_id):
        """Fetch all test cases for execution, mapped to engine format."""
        with self._get_session() as session:
            statement = select(TestCase).where(TestCase.problem_id == problem_id).order_by(TestCase.sort_order)
            results = session.exec(statement).all()
            return [{"input": tc.input, "expected_output": tc.output, "test_number": tc.sort_order} for tc in results]

    def find_public_by_problem(self, problem_id, limit=None):
        """Fetch non-hidden test cases for public documentation.

        If `limit` is provided, return at most `limit` test cases.
        """
        with self._get_session() as session:
            statement = select(TestCase).where(
                TestCase.problem_id == problem_id,
                TestCase.is_hidden == False
            ).order_by(TestCase.sort_order)
            if limit:
                statement = statement.limit(limit)
            return [tc.model_dump(exclude={"is_hidden"}) for tc in session.exec(statement).all()]
