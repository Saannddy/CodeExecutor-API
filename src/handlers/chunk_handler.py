from flask import jsonify, request
from services.chunk_service import ChunkService

class ChunkHandler:
    def __init__(self):
        self.service = ChunkService()

    def get_all_chunks(self):
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=10, type=int)
        lang = request.args.get('lang')
        
        chunks = self.service.get_all_chunks(page=page, limit=limit, lang=lang)
        return jsonify(status="success", data=chunks), 200

    def get_chunk(self, chunk_id):
        lang = request.args.get('lang')
        chunk = self.service.get_chunk(chunk_id, lang=lang)
        if not chunk:
            return jsonify(status="error", message="Chunk not found"), 404
        return jsonify(status="success", data=chunk), 200

    def get_random_chunks(self):
        limit = request.args.get('limit', default=1, type=int)
        lang = request.args.get('lang')
        tags = request.args.get('tags')
        if tags:
            tags = [tag.strip() for tag in tags.split(',')]
        
        chunks = self.service.get_random_chunks(limit=limit, lang=lang, tags=tags)
        return jsonify(status="success", data=chunks), 200
