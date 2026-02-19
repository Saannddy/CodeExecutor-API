from flask import send_from_directory, current_app

class DocsHandler:
    @staticmethod
    def serve_openapi():
        """Serve the OpenAPI specification file."""
        return send_from_directory(current_app.root_path, 'openapi.yaml')

    @staticmethod
    def serve_docs():
        """Serve interactive API documentation via Scalar."""
        return f"""
        <!doctype html>
        <html>
          <head>
            <title>CodeExecutor-API Documentation</title>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <style>body {{ margin: 0; }}</style>
          </head>
          <body>
            <script id="api-reference" data-url="/docs/openapi.yaml"></script>
            <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
          </body>
        </html>
        """, 200
