from flask import Flask
from flask_cors import CORS
from routes.auth import auth_bp
from routes.qa import qa_bp
from routes.ingest import ingest_bp

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(qa_bp, url_prefix="/api/qa")
app.register_blueprint(ingest_bp, url_prefix="/api/ingest")


@app.route("/")
def home():
    return "Backend is running!"


if __name__ == "__main__":
    app.run(debug=True)