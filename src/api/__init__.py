from flask import Blueprint
from .routes.docs_routes import docs_bp
from .routes.problem_routes import problem_bp
from .routes.question_routes import question_bp
from .routes.riddle_routes import riddle_bp
from .routes.execution_routes import execution_bp

api_bp = Blueprint('api', __name__)

# Register sub-blueprints with their respective prefixes
api_bp.register_blueprint(docs_bp, url_prefix='/docs')
api_bp.register_blueprint(problem_bp, url_prefix='/problem')
api_bp.register_blueprint(question_bp, url_prefix='/question')
api_bp.register_blueprint(riddle_bp, url_prefix='/riddle')
api_bp.register_blueprint(execution_bp) # execution handles its own prefixes (/code, /run)
