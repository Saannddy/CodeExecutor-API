from sqlmodel import select
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from infrastructure import SessionLocal
from models import Problem, Category, Tag

class ProblemRepository:
    def __init__(self, session=None):
        self._session = session

    def _get_session(self):
        return self._session if self._session else SessionLocal()

    def find_all(self):
        """Retrieve all problems with basic information."""
        with self._get_session() as session:
            statement = select(Problem).order_by(Problem.id)
            return [p.model_dump(exclude={"config", "description"}) for p in session.exec(statement).all()]

    def find_by_id(self, problem_id):
        """Internal helper to fetch a Problem model by UUID."""
        with self._get_session() as session:
            return session.get(Problem, problem_id)

    def find_details_by_id(self, problem_id):
        """Fetch full problem details with hydrated relationships for API response."""
        with self._get_session() as session:
            statement = select(Problem).where(Problem.id == problem_id).options(
                joinedload(Problem.categories),
                joinedload(Problem.tags)
            )
            problem = session.exec(statement).first()
            if not problem:
                return None
            
            p_dict = problem.model_dump()
            p_dict['categories'] = [c.name for c in problem.categories]
            p_dict['tags'] = [t.name for t in problem.tags]
            return p_dict

    def find_by_category(self, category_name):
        """Filter problems by category name (case-insensitive)."""
        with self._get_session() as session:
            statement = select(Problem).join(Problem.categories).where(Category.name.ilike(category_name))
            return [p.model_dump(exclude={"config", "description"}) for p in session.exec(statement).all()]

    def find_by_tag(self, tag_name):
        """Filter problems by tag name (case-insensitive)."""
        with self._get_session() as session:
            statement = select(Problem).join(Problem.tags).where(Tag.name.ilike(tag_name))
            return [p.model_dump(exclude={"config", "description"}) for p in session.exec(statement).all()]
        
    def find_random(self, category_name=None, tag_name=None, limit=1):
        """Fetch random problems with their details.

        If `category_name` or `tag_name` is provided, restrict selection accordingly.
        Returns a list of problem dicts (empty list if none found).
        """
        with self._get_session() as session:
            statement = select(Problem)
            if category_name:
                statement = statement.join(Problem.categories).where(Category.name.ilike(category_name))
            elif tag_name:
                statement = statement.join(Problem.tags).where(Tag.name.ilike(tag_name))

            statement = statement.order_by(func.random()).limit(limit)
            results = session.exec(statement).all()
            if not results:
                return []

            problems = []
            for problem in results:
                p_dict = problem.model_dump()
                p_dict['categories'] = [c.name for c in problem.categories]
                p_dict['tags'] = [t.name for t in problem.tags]
                problems.append(p_dict)

            return problems
