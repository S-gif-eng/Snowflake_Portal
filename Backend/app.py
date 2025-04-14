import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from snowflake_routes import snowflake_bp
from flask_session import Session

app = Flask(__name__)

# Set secret key from environment variable
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")  # Set a fallback value

CORS(app)

app.config["SESSION_TYPE"] = "filesystem"  # Store sessions in the filesystem
app.config["SESSION_PERMANENT"] = False    # Optional: Non-permanent sessions
Session(app)

# Register Blueprint
app.register_blueprint(snowflake_bp, url_prefix="/api/snowflake")

if __name__ == "__main__":
    app.run(debug=True)
