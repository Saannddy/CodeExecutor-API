from flask import Blueprint
from handlers import RiddleHandler

riddle_bp = Blueprint('riddle', __name__)
riddle_handler = RiddleHandler()

@riddle_bp.get('/')
def get_riddles():
    """List all riddles (Base: /riddle/)"""
    return riddle_handler.get_riddles()

@riddle_bp.get('/group')
def get_riddles_group():
    """Get a random group of riddles (Base: /riddle/group)"""
    return riddle_handler.get_riddles_group()

@riddle_bp.get('/<riddle_id>')
def get_riddle(riddle_id):
    """Retrieve single riddle details (Base: /riddle/<id>)"""
    return riddle_handler.get_riddle(riddle_id)

@riddle_bp.post('/')
def create_riddle():
    """Add a new riddle (Base: /riddle/)"""
    return riddle_handler.create_riddle()

@riddle_bp.patch('/<riddle_id>')
def update_riddle(riddle_id):
    """Update an existing riddle (Base: /riddle/<id>)"""
    return riddle_handler.update_riddle(riddle_id)
