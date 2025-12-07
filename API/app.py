from flask import Flask, request, jsonify
from executor import execute_code, execute_custom_code

app = Flask(__name__, static_folder='html')

@app.post('/run')
def custom_code_executor():
    lang = request.args.get('lang')
    if not lang:
        return jsonify(status="error", message="Missing 'lang' query parameter"), 400

    if not request.is_json:
        return jsonify(status="error", message="Request must be JSON"), 400

    data = request.get_json()
    code = data.get('code')
    if not code:
        return jsonify(status="error", message="Missing 'code' in request body"), 400

    res = execute_custom_code(code, lang)
    return jsonify(res), (500 if res.get("status") == "error" else 200)

@app.post('/code/<question_id>')
def code_executor(question_id):
    """Endpoint to execute code for a given question ID."""
    if not request.is_json:
        return jsonify(status="error", message="Request must be JSON"), 400

    data = request.get_json()
    code, lang = data.get('code'), data.get('language')
    if not code or not lang:
        return jsonify(status="error", message="Missing 'code' or 'language'"), 400

    res = execute_code(code, lang, question_id)
    return jsonify(res), (500 if res.get("status") == "error" else 200)

@app.route('/')
def home():
    """Serve the main HTML page."""
    return app.send_static_file('index.html')

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors by serving a custom page."""
    return app.send_static_file('404.html'), 404
