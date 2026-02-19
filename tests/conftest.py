"""
Shared pytest fixtures for the CodeExecutor-API test suite.

The production app runs inside Docker (Python 3.11 + pinned deps).
Locally, the pydantic / sqlmodel versions may differ and models won't
import cleanly.  We solve this by mocking the *infrastructure* and
*repository* layers before importing the app, so that:
  • No real DB session is created.
  • Models are never loaded by SQLAlchemy.
  • Handlers and routes import normally.

Strategy:
  Mock `infrastructure.SessionLocal` and every Repository class so that
  importing the service → repository → model chain is short-circuited.
"""

import sys
import os
from unittest.mock import MagicMock

import pytest


SRC_DIR = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, os.path.abspath(SRC_DIR))


infrastructure_mock = MagicMock()
sys.modules.setdefault('infrastructure', infrastructure_mock)
sys.modules.setdefault('infrastructure.database', infrastructure_mock)

# Mock models (SQLModel tables)
models_mock = MagicMock()
sys.modules.setdefault('models', models_mock)
sys.modules.setdefault('models.base', models_mock)

# Mock repositories
repos_mock = MagicMock()
sys.modules.setdefault('repositories', repos_mock)
sys.modules.setdefault('repositories.problem_repository', repos_mock)
sys.modules.setdefault('repositories.testcase_repository', repos_mock)
sys.modules.setdefault('repositories.question_repository', repos_mock)
sys.modules.setdefault('repositories.choice_repository', repos_mock)
sys.modules.setdefault('repositories.riddle_repository', repos_mock)

# Mock scripts (seed, etc.)
sys.modules.setdefault('scripts', MagicMock())
sys.modules.setdefault('scripts.seed', MagicMock())


@pytest.fixture
def app():
    """Create a Flask app configured for testing."""
    from app import create_app
    application = create_app()
    application.config.update({
        "TESTING": True,
    })
    yield application


@pytest.fixture
def client(app):
    """A Flask test client – use this to make HTTP requests in tests."""
    return app.test_client()
