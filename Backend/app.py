import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_session import Session
from snowflake_routes import snowflake_bp

# Point to the frontend directory correctly (use absolute path)
frontend_path = os.path.join(os.path.dirname(__file__), '../Frontend')

app = Flask(__name__, static_folder=frontend_path, static_url_path='')

# Flask session setup
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)

CORS(app)

# Register Snowflake Blueprint
app.register_blueprint(snowflake_bp, url_prefix="/api/snowflake")

# Serve index.html
@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

# Serve other frontend files (CSS/JS)
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# Handle 404s by returning index.html (for SPA)
@app.errorhandler(404)
def not_found(e):
    return app.send_static_file('index.html')

if __name__ == "__main__":
    app.run(debug=True)
