import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_session import Session
from snowflake_routes import snowflake_bp

app = Flask(__name__, static_folder="../frontend", static_url_path='')

# Secret key & session
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)

CORS(app)

# Blueprint for Snowflake-related routes
app.register_blueprint(snowflake_bp, url_prefix="/api/snowflake")

# Route to serve frontend
@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.errorhandler(404)
def not_found(e):
    return app.send_static_file('index.html')

if __name__ == "__main__":
    app.run(debug=True)
