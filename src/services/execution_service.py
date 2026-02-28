import logging
from repositories import ProblemRepository, TestCaseRepository, ChunkRepository
from core import execute_code as core_execute
from pybars import Compiler

class ExecutionService:
    def __init__(self):
        self.test_case_repo = TestCaseRepository()
        self.problem_repo = ProblemRepository()
        self.chunk_repo = ChunkRepository()
        self.compiler = Compiler()

    def run_problem_code(self, problem_id, code, lang):
        """Execute provided code against all test cases for a specific problem."""
        problem = self.problem_repo.find_by_id(problem_id)
        if not problem:
            return {"status": "error", "message": "Problem not found"}
            
        test_cases = self.test_case_repo.find_all_by_problem(problem_id)
        cfg = problem.config if hasattr(problem, 'config') else {}
        
        return core_execute(
            code=code, 
            lang=lang, 
            tests=test_cases, 
            timeout=cfg.get("timeout", 5),
            templates=cfg.get("templates", {}),
            rules=cfg.get("rules", {})
        )

    def run_chunk_code(self, chunk_id, snippets_payload, lang):
        """Execute chunk by combining template code with provided snippets against chunk's expectations."""
        chunk = self.chunk_repo.find_by_id(chunk_id)
        if not chunk:
            return {"status": "error", "message": "Chunk not found"}
        
        # Find implementation for the requested language
        template = next((t for t in chunk.templates if t.language == lang), None)
        if not template:
            return {"status": "error", "message": f"Implementation for language '{lang}' not found for this chunk"}
        
        # Build map of default snippets from the template
        snippet_map = {s.placeholder_key: s.code_content for s in template.snippets}
        
        # Update with provided snippets. Payload can be a dict key->content or list of dicts.
        if isinstance(snippets_payload, list):
            for s in snippets_payload:
                if 'placeholder_key' in s and 'code_content' in s:
                    snippet_map[s['placeholder_key']] = s['code_content']
        elif isinstance(snippets_payload, dict):
            snippet_map.update(snippets_payload)

        # Build final code from template using Handlebars (pybars)
        def indent_helper(this, text, spaces=4):
            if not text:
                return ""
            import re
            ind = " " * int(spaces)
            # Use regex to replace start of each line with the indentation
            return re.sub(r'^', ind, str(text), flags=re.MULTILINE)

        compiled = self.compiler.compile(template.template_code)
        final_code = compiled(snippet_map, helpers={'indent': indent_helper})

        test_cases = [{"input": tc.input, "expected_output": tc.output, "test_number": i} for i, tc in enumerate(chunk.expectations, 1)]

        # chunks don't have config right now, using default timeout 5
        return core_execute(
            code=final_code,
            lang=lang,
            tests=test_cases,
            timeout=5,
            templates={},
            rules={}
        )
