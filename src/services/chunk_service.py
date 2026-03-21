import re
from repositories.chunk_repository import ChunkRepository

class ChunkService:
    def __init__(self):
        self.repo = ChunkRepository()

    def _process_chunk(self, chunk):

        if not chunk:
            return None

        cmt_map = {
            "python": "# TODO: {} here",
            "c": "// TODO: {} here",
            "cpp": "// TODO: {} here",
            "java": "// TODO: {} here",
            "default": "// TODO: {} here"
        }

        templates = chunk.get("config", {}).get("templates", {})
        for lang, t_dict in templates.items():
            cmt_pat = cmt_map.get(lang.lower(), cmt_map["default"])
            tc = t_dict.get("template_code")
            if tc:
                processed = re.sub(
                    r'\{{3}\s*(\w+)\s*\}{3}', 
                    lambda m: f"\n{cmt_pat.format(m.group(1))}\n", 
                    tc
                )
                t_dict["template_code"] = [line for line in processed.split('\n') if line]

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

    def get_random_chunks(self, limit=1, lang=None, tags=None):
        chunks = self.repo.find_random(limit=limit, lang=lang, tags=tags)
        return [self._process_chunk(c) for c in chunks]
