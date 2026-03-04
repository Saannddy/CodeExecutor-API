from sqlmodel import select
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from infrastructure import SessionLocal
from models import Chunk, Snippet, ChunkTemplate

class ChunkRepository:
    def __init__(self, session=None):
        self._session = session

    def _get_session(self):
        return self._session if self._session else SessionLocal()

    def find_all(self, page=1, limit=10, lang=None):
        """Retrieve all chunks with their templates and nested snippets. Supports pagination and language filtering."""
        with self._get_session() as session:
            # Base query
            statement = select(Chunk).options(
                joinedload(Chunk.templates).joinedload(ChunkTemplate.snippets)
            )

            # If language is specified, filter chunks that HAVE at least one template in that language
            if lang:
                statement = statement.join(Chunk.templates).where(ChunkTemplate.language == lang)

            statement = statement.order_by(Chunk.id).offset((page - 1) * limit).limit(limit)
            
            # Use unique() for joinedload with collections
            results = session.exec(statement).unique().all()
            chunks = []
            for chunk in results:
                chunks.append(self._serialize_chunk(chunk, lang))
            return chunks

    def _serialize_chunk(self, chunk, lang=None):
        """Helper to serialize a chunk and optionally filter its templates by language."""
        c_dict = chunk.model_dump()
        
        # Move templates to config key in response
        c_dict["config"] = {"templates": {}}
        
        for t in chunk.templates:
            # Skip if language filter is active and doesn't match
            if lang and t.language != lang:
                continue
                
            t_dict = {
                "id": str(t.id),
                "name": t.name,
                "template_code": t.template_code,
                "description": t.description,
                "snippets": {s.placeholder_key: s.code_content for s in t.snippets}
            }
            c_dict["config"]["templates"][t.language] = t_dict
            
        # Add expectations to config for consistency
        if hasattr(chunk, "expectations") and chunk.expectations:
            c_dict["expectations"] = [
                {"input": e.input, "output": e.output} for e in chunk.expectations
            ]
            
        return c_dict

    def find_by_id(self, chunk_id):
        """Internal helper to fetch a Chunk model by UUID with its implementation details."""
        with self._get_session() as session:
            statement = select(Chunk).where(Chunk.id == chunk_id).options(
                joinedload(Chunk.templates).joinedload(ChunkTemplate.snippets),
                joinedload(Chunk.expectations)
            )
            return session.exec(statement).unique().first()

    def get_details(self, chunk_id, lang=None):
        """Fetch chunk details with templates and snippets, optionally filtered by language."""
        chunk = self.find_by_id(chunk_id)
        if not chunk:
            return None
            
        return self._serialize_chunk(chunk, lang)

    def find_random(self, limit=1, lang=None):
        """Fetch random N chunks with their implementation details. Filters by language if provided."""
        with self._get_session() as session:
            statement = select(Chunk).order_by(func.random())
            # For simplicity, if lang is provided, we fetch more and filter in Python
            # or just fetch all and filter.
            results = session.exec(statement).all()
            if not results:
                return []

            chunks = []
            for chunk in results:
                if lang and lang not in chunk.config.get("templates", {}):
                    continue
                chunks.append(self._serialize_chunk(chunk, lang))
                if len(chunks) >= limit:
                    break

            return chunks
