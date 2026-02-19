from flask import Blueprint
from handlers import ProblemHandler

problem_bp = Blueprint('problem', __name__)
problem_handler = ProblemHandler()

@problem_bp.get('/')
def get_problems():
    """List problems (Base: /problems) - Note: Register with /problems if desired, or keep as /problem/"""
    return problem_handler.get_problems()

@problem_bp.get('/<problem_id>')
def get_problem(problem_id):
    """Get problem details (Base: /problem/<id>)"""
    return problem_handler.get_problem(problem_id)

@problem_bp.get('/random')
def get_random_problem():
    """Get random problem (Base: /problem/random)"""
    return problem_handler.get_random_problem()

@problem_bp.post('/<problem_id>/testcases')
def add_test_cases(problem_id):
    """Add test cases (Base: /problem/<id>/testcases)"""
    return problem_handler.add_test_cases(problem_id)
