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
    
    def create_test_case(self, testcase_data):
        """ Create new test case """
        with self._get_session() as session:
            statement = select(TestCase).where(
                TestCase.problem_id == testcase_data['problem_id']
            ).order_by(TestCase.sort_order.desc())

            last = session.exec(statement).first()
            next_sort_order = 1 if not last else last.sort_order + 1

            testcase = TestCase(
                problem_id = testcase_data['problem_id'],
                input = testcase_data['input'],
                output = testcase_data['output'],
                is_hidden = testcase_data.get('is_hidden', False),
                sort_order = next_sort_order
            )

            session.add(testcase)
            session.commit()
            session.refresh(testcase)
            return testcase.model_dump()