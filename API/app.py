from flask import Flask, request, jsonify
from executor import execute_code

app = Flask(__name__, static_folder='html')

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
