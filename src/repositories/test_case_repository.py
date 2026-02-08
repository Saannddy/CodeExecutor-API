from infrastructure.database import query_all

class TestCaseRepository:
    @staticmethod
    def find_all_by_problem(problem_id):
        """Fetch all test cases for a problem (internal/execution use)."""
        return query_all("""
            SELECT input, output as expected_output, sort_order as test_number 
            FROM test_cases 
            WHERE problem_id = %s 
            ORDER BY sort_order
        """, (problem_id,))

    @staticmethod
    def find_public_by_problem(problem_id):
        """Fetch only non-hidden test cases (public description use)."""
        return query_all("""
            SELECT input, output, sort_order 
            FROM test_cases 
            WHERE problem_id = %s AND is_hidden = FALSE 
            ORDER BY sort_order
        """, (problem_id,))
