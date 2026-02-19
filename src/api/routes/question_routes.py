from flask import Blueprint
from handlers import QuestionHandler

question_bp = Blueprint('question', __name__)
question_handler = QuestionHandler()

@question_bp.get('/')
def get_questions():
    """List all questions (Base: /question/)"""
    return question_handler.get_questions()

@question_bp.get('/<question_id>')
def get_question(question_id):
    """Retrieve question details with choices (Base: /question/<id>)"""
    return question_handler.get_question(question_id)

@question_bp.post('/')
def add_question():
    """Create a new question (Base: /question/)"""
    return question_handler.add_question()

@question_bp.patch('/<question_id>')
def update_question(question_id):
    """Update an existing question (Base: /question/<id>)"""
    return question_handler.update_question(question_id)

@question_bp.post('/<question_id>/choice')
def add_choice(question_id):
    """Add a choice to a question (Base: /question/<id>/choice)"""
    return question_handler.add_choice(question_id)

@question_bp.patch('/choice/<choice_id>')
def update_choice(choice_id):
    """Update an existing choice (Base: /question/choice/<id>)"""
    return question_handler.update_choice(choice_id)

@question_bp.get('/random')
def get_random_questions():
    """Get random questions by tag (Base: /question/random)"""
    return question_handler.get_random_questions()
