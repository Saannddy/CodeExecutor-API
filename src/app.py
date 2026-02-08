from flask import Flask
from infrastructure import init_db
from api import api_bp

def create_app():
    app = Flask(__name__, static_folder='html')
    
    # Initialize infrastructure
    init_db()
    
    # Register routes
    app.register_blueprint(api_bp)
    
    @app.route('/')
    def home():
        return app.send_static_file('index.html')

    @app.errorhandler(404)
    def page_not_found(e):
        return app.send_static_file('404.html'), 404
        
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
