from flask import Blueprint
from handlers import ExecutionHandler

execution_bp = Blueprint('execution', __name__)
execution_handler = ExecutionHandler()

@execution_bp.post('/code/<problem_id>')
def execute_problem_code(problem_id):
    """Execute code against stored test cases for a problem."""
    return execution_handler.execute_problem_code(problem_id)

@execution_bp.post('/run')
def custom_code_executor():
    """Execute arbitrary code without test cases."""
    return execution_handler.custom_code_executor()
