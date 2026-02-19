from flask import Blueprint
from handlers import DocsHandler

docs_bp = Blueprint('docs', __name__)
docs_handler = DocsHandler()

@docs_bp.route('/openapi.yaml')
def serve_openapi():
    """Serve the OpenAPI specification file."""
    return docs_handler.serve_openapi()

@docs_bp.route('/')
def scalar_docs():
    """Serve interactive API documentation via Scalar (Base: /docs/)"""
    return docs_handler.serve_docs()
