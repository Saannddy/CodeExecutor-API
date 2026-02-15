from repositories import ProblemRepository, TestCaseRepository
from core import execute_code as core_execute

class ExecutionService:
    def __init__(self):
        self.test_case_repo = TestCaseRepository()
        self.problem_repo = ProblemRepository()

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
