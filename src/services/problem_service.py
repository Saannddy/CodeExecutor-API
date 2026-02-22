import io
import zipfile
from repositories import ProblemRepository, TestCaseRepository

class ProblemService:
    def __init__(self):
        self.problem_repo = ProblemRepository()
        self.test_case_repo = TestCaseRepository()

    def list_all_problems(self):
        """Retrieve a list of all problems with basic information."""
        return self.problem_repo.find_all()

    def get_problem_details(self, problem_id):
        """Fetch full problem details, including config and public test cases.

        Optional limits can be provided to restrict returned counts for
        `test_cases`, `tags`, and `categories`.
        """
        problem_dict = self.problem_repo.find_details_by_id(problem_id)
        if not problem_dict:
            return None

        # Filter configuration for API response
        allowed_keys = {'timeout', 'templates'}
        problem_dict['config'] = {k: v for k, v in problem_dict.get('config', {}).items() if k in allowed_keys}
        
        # Enrich with public test cases (apply optional limit)
        problem_dict['test_cases'] = self.test_case_repo.find_public_by_problem(problem_id)

        # Apply optional limits to tags and categories


        return problem_dict

    def list_problems_by_category(self, category_name):
        """Filter problems by category."""
        return self.problem_repo.find_by_category(category_name)

    def list_problems_by_tag(self, tag_name):
        """Filter problems by tag."""
        return self.problem_repo.find_by_tag(tag_name)
    
    def get_random_problem(self, category_name=None, tag_name=None, limit=1):   
        """Fetch `limit` random problems (optionally filtered) and include details.

        Returns a list of problem dicts (may be empty).
        """
        problems = self.problem_repo.find_random(category_name=category_name, tag_name=tag_name, limit=limit)
        if not problems:
            return []

        allowed_keys = {'timeout', 'templates'}
        enriched = []
        for problem_dict in problems:
            # Filter configuration for API response
            problem_dict['config'] = {k: v for k, v in problem_dict.get('config', {}).items() if k in allowed_keys}

            # Add public test cases (with optional limit)
            problem_id = problem_dict.get('id')
            problem_dict['test_cases'] = self.test_case_repo.find_public_by_problem(problem_id)

            # Apply optional limits to tags and categories

            enriched.append(problem_dict)

        return enriched
    

    
    def add_test_cases(self, problem_id, testcases):
        """ Add multiple test cases to problem """
        problem = self.problem_repo.find_by_id(problem_id)
        if not problem:
            return {'status': 'error', 'message': 'Problem not found'}
        
        created_testcases = []
        for test in testcases:
            if 'input' not in test or 'output' not in test:
                return {'status': 'error', 'message': 'Testcase must have input and output'}
            testcase_data = {
                'problem_id': problem_id,
                'input': test['input'],
                'output': test['output'],
                'is_hidden': test.get('isHidden', False)
            }

            created = self.test_case_repo.create_test_case(testcase_data)

            if created:
                created_testcases.append(created)
            
        return {'status': 'success', 'data': {
            'created_count': len(created_testcases),
            'testcases': created_testcases
        }}
    
    def import_test_cases(self, problem_id, zip_file):
        """ Import test cases from uploaded file """
        problem = self.problem_repo.find_by_id(problem_id)
        if not problem:
            return {'status': 'error', 'message': 'Problem not found'}
        
        created_testcases = []

        try:
            zip_data = zipfile.ZipFile(io.BytesIO(zip_file))

            if not any(name.startswith('in/') and name.endswith('.in') for name in zip_data.namelist()):
                return {'status': 'error', 'message': 'ZIP must contain input files in "in/" directory'}
            if not any(name.startswith('out/') and name.endswith('.out') for name in zip_data.namelist()):
                return {'status': 'error', 'message': 'ZIP must contain output files in "out/" directory'}
            
            is_shown = set()
            if "isShown.txt" in zip_data.namelist():
                content = zip_data.read("isShown.txt").decode('utf-8')
                is_shown = set(map(int, content.split(',')))

            testcases = []

            input_files = [name for name in zip_data.namelist()
                           if name.startswith('in/') and name.endswith('.in')]
            if not input_files:
                return {'status': 'error', 'message': 'No input files found in ZIP'}

            for input_file in input_files:
                test_number = int(input_file.split('/')[-1].replace('.in', ''))
                
                if f'out/{test_number}.out' not in zip_data.namelist():
                    return {'status': 'error', 'message': f'Missing output file for test case {test_number}'}

                input_data = zip_data.read(input_file).decode('utf-8')
                output_data = zip_data.read(f'out/{test_number}.out').decode('utf-8')

                testcases.append({
                    'input': input_data.strip(),
                    'output': output_data.strip(),
                    'is_hidden': test_number not in is_shown,
                    'sort_order': test_number
                })
            
            if not testcases:
                return {'status': 'error', 'message': 'No valid test cases found in ZIP'}
            
            for test in testcases:
                testcase_data = {
                    'problem_id': problem_id,
                    'input': test['input'],
                    'output': test['output'],
                    'is_hidden': test.get('is_hidden', False),
                    'sort_order': test.get('sort_order')
                }

                created = self.test_case_repo.create_test_case(testcase_data)

                if created:
                    created_testcases.append(created)

            return {'status': 'success', 'data': {
                'created_count': len(created_testcases),
                'testcases': created_testcases
            }}

        except Exception as e:
            return {'status': 'error', 'message': f'Invalid ZIP file: {str(e)}'}