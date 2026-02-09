from sqlmodel import select, or_
from sqlalchemy.orm import selectinload, joinedload
from infrastructure.database import SessionLocal
from models import Problem, Category, Tag

class ProblemRepository:
    def __init__(self, session=None):
        self._session = session

    def _get_session(self):
        return self._session if self._session else SessionLocal()

    def find_all(self):
        """Retrieve all problems with basic info."""
        with self._get_session() as session:
            statement = select(Problem).order_by(Problem.id)
            return [p.model_dump(exclude={"config", "description"}) for p in session.exec(statement).all()]

    def find_by_id(self, problem_id):
        """Retrieve a single problem by UUID (Internal use)."""
        with self._get_session() as session:
            return session.get(Problem, problem_id)

    def find_details_by_id(self, problem_id):
        """Retrieve a single problem by UUID with categories and tags hydrated (Dict)."""
        with self._get_session() as session:
            statement = select(Problem).where(Problem.id == problem_id).options(
                joinedload(Problem.categories),
                joinedload(Problem.tags)
            )
            problem = session.exec(statement).first()
            if not problem:
                return None
            
            # Hydrate while session is active
            p_dict = problem.model_dump()
            p_dict['categories'] = [c.name for c in problem.categories]
            p_dict['tags'] = [t.name for t in problem.tags]
            return p_dict

    def find_by_category(self, category_name):
        """Retrieve problems filtered by category name (case-insensitive)."""
        with self._get_session() as session:
            statement = select(Problem).join(Problem.categories).where(Category.name.ilike(category_name))
            return [p.model_dump(exclude={"config", "description"}) for p in session.exec(statement).all()]

    def find_by_tag(self, tag_name):
        """Retrieve problems filtered by tag name (case-insensitive)."""
        with self._get_session() as session:
            statement = select(Problem).join(Problem.tags).where(Tag.name.ilike(tag_name))
            return [p.model_dump(exclude={"config", "description"}) for p in session.exec(statement).all()]
