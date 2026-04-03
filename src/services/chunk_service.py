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
                parts = re.split(r'(\{{3}\s*\w+\s*\}{3})', tc)
                processed_list = []
                current_buffer = ""

                for part in parts:
                    match = re.match(r'\{{3}\s*(\w+)\s*\}{3}', part)
                    if match:
                        key_name = match.group(1)
                        comment_str = f"\n{cmt_pat.format(key_name)}"
                        processed_list.append(current_buffer + comment_str)
                        current_buffer = ""
                    else:
                        current_buffer = part

                processed_list.append(current_buffer if current_buffer else "\n")
                t_dict["template_code"] = processed_list

                snippets_dict = t_dict.get("snippets", {})
                if isinstance(snippets_dict, dict):
                    sorted_keys = sorted(snippets_dict.keys())
                
                    t_dict["snippets"] = sorted_keys
                    t_dict["code_content"] = [snippets_dict[k] for k in sorted_keys]

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
