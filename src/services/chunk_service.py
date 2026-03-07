import re
from repositories.chunk_repository import ChunkRepository

class ChunkService:
    def __init__(self):
        self.repo = ChunkRepository()

    def _process_chunk(self, chunk):

        if not chunk:
            return None

        templates = chunk.get("config", {}).get("templates", {})
        for lang, t_dict in templates.items():
            # Split template_code into parts by handlebar patterns
            # When split handlerbar should not appear in array anymore
            tc = t_dict.get("template_code")
            if tc:
                t_dict["template_code"] = re.split(r'\{\{\{?|}}}?|\n', tc)
                t_dict["template_code"] = [x for x in t_dict["template_code"] if x]

            # Transform snippets dict into parallel arrays
            snippets_dict = t_dict.get("snippets", {})
            if isinstance(snippets_dict, dict):
                keys = list(snippets_dict.keys())
                values = [snippets_dict[k] for k in keys]
                t_dict["snippets"] = keys
                t_dict["code_content"] = values

        return chunk

    def get_all_chunks(self, page=1, limit=10, lang=None):
        chunks = self.repo.find_all(page=page, limit=limit, lang=lang)
        return [self._process_chunk(c) for c in chunks]

    def get_chunk(self, chunk_id, lang=None):
        chunk = self.repo.get_details(chunk_id, lang=lang)
        if chunk:
            return self._process_chunk(chunk)
        return None

    def get_random_chunks(self, limit=1, lang=None):
        chunks = self.repo.find_random(limit=limit, lang=lang)
        return [self._process_chunk(c) for c in chunks]
