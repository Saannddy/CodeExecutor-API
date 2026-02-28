from flask import Blueprint
from handlers.chunk_handler import ChunkHandler

chunk_bp = Blueprint('chunk', __name__)
handler = ChunkHandler()

@chunk_bp.route('/', methods=['GET'])
def get_all_chunks():
    return handler.get_all_chunks()

@chunk_bp.route('/random', methods=['GET'])
def get_random_chunks():
    return handler.get_random_chunks()

@chunk_bp.route('/<uuid:chunk_id>', methods=['GET'])
def get_chunk(chunk_id):
    return handler.get_chunk(chunk_id)
