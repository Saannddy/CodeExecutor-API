import io
import zipfile
from flask import request, jsonify
from services import ProblemService

class ProblemHandler:
    def __init__(self):
        self.problem_service = ProblemService()

    def get_problems(self):
        """List problems with optional category/tag filtering."""
        category = request.args.get('category')
        tag = request.args.get('tag')

        if category:
            problems = self.problem_service.list_problems_by_category(category)
        elif tag:
            problems = self.problem_service.list_problems_by_tag(tag)
        else:
            problems = self.problem_service.list_all_problems()

        return jsonify(status="success", data=problems), 200

    def get_problem(self, problem_id):
        """Retrieve detailed information for a single problem."""
        problem = self.problem_service.get_problem_details(problem_id)
        if not problem:
            return jsonify(status="error", message="Problem not found"), 404
        return jsonify(status="success", data=problem), 200

    def get_random_problem(self):
        """Fetch a random problem, optionally filtered by category or tag."""
        category = request.args.get('category')
        tag = request.args.get('tag')
        limit = request.args.get('limit', 1, type=int)

        # Prefer category filter, then tag, otherwise random across all
        if category:
            problem = self.problem_service.get_random_problem(category_name=category, limit=limit)
        elif tag:
            problem = self.problem_service.get_random_problem(tag_name=tag, limit=limit)
        else:
            problem = self.problem_service.get_random_problem(category_name=None, limit=limit)

        if not problem:
            return jsonify(status="error", message="No problems found"), 404
        return jsonify(status="success", data=problem), 200

    def add_test_cases(self, problem_id):
        """ Add multiple test case  """
        if not request.is_json:
            return jsonify(status='error', message='Request must be JSON'), 400
        
        data = request.get_json()
        testcases = data.get('testcases')

        if not testcases or not isinstance(testcases, list):
            return jsonify(status='error', message='Testcases must be a list'), 400
        
        result = self.problem_service.add_test_cases(problem_id, testcases)

        if result['status'] == 'error':
            return jsonify(status='error', message=result.get('message')), 400
        return jsonify(status='success', data=result.get('data')), 201
    
    def import_test_cases(self, problem_id):
        """ Import test cases from a ZIP file """
        if not request.data:
            return jsonify(status='error', message='No file uploaded'), 400
        
        content_type = request.content_type or ''
        if 'application/zip' not in content_type and 'application/octet-stream' not in content_type:
            return jsonify(status='error', message='Content-Type must be application/zip'), 400

        try:
            zip_data = zipfile.ZipFile(io.BytesIO(request.data))

            if not any(name.startswith('in/') and name.endswith('.in') for name in zip_data.namelist()):
                return jsonify(status='error', message='ZIP must contain input files in "in/" directory'), 400
            if not any(name.startswith('out/') and name.endswith('.out') for name in zip_data.namelist()):
                return jsonify(status='error', message='ZIP must contain output files in "out/" directory'), 400

            is_shown = set()

            if "isShown.txt" in zip_data.namelist():
                content = zip_data.read("isShown.txt").decode('utf-8')
                is_shown = set(map(int, content.split(',')))

            testcases = []

            input_files = [name for name in zip_data.namelist() 
                           if name.startswith('in/') and name.endswith('.in')]
            if not input_files:
                return jsonify(status='error', message='No input files found in ZIP'), 400

            for input_file in input_files:
                try:
                    test_number = int(input_file.split('/')[-1].replace('.in', ''))
                except ValueError:
                    return jsonify(status='error', message=f'Invalid input file name: {input_file}'), 400

                if f'out/{test_number}.out' not in zip_data.namelist():
                    return jsonify(status='error', message=f'Missing output file for test case {test_number}'), 400

                input_data = zip_data.read(input_file).decode('utf-8')
                output_data = zip_data.read(f'out/{test_number}.out').decode('utf-8')

                testcases.append({
                    'input': input_data.strip(),
                    'output': output_data.strip(),
                    'is_hidden': test_number not in is_shown,
                    'sort_order': test_number
                })
            
            if not testcases:
                return jsonify(status='error', message='No valid test cases found in ZIP'), 400
                
            result = self.problem_service.add_test_cases(problem_id, testcases)

            if result.get('status') == 'error':
                return jsonify(status='error', message=result.get('message')), 400
            
            return jsonify(status='success', data=result.get('data')), 201
        except Exception as e:
            return jsonify(status='error', message=str(e)), 500