from flask import jsonify, request
from repositories.chunk_repository import ChunkRepository

class ChunkHandler:
    def __init__(self):
        self.repo = ChunkRepository()

    def get_all_chunks(self):
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=10, type=int)
        lang = request.args.get('lang')
        
        chunks = self.repo.find_all(page=page, limit=limit, lang=lang)
        return jsonify(status="success", data=chunks), 200

    def get_chunk(self, chunk_id):
        lang = request.args.get('lang')
        chunk = self.repo.get_details(chunk_id, lang=lang)
        if not chunk:
            return jsonify(status="error", message="Chunk not found"), 404
        return jsonify(status="success", data=chunk), 200

    def get_random_chunks(self):
        limit = request.args.get('limit', default=1, type=int)
        lang = request.args.get('lang')
        
        chunks = self.repo.find_random(limit=limit, lang=lang)
        return jsonify(status="success", data=chunks), 200
