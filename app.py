from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
import os
from fuzzywuzzy import process
from utils import sanitize_input, error_response

app = Flask(__name__)

# Allow frontend requests
CORS(app, resources={r"/search": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}})

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["5 per minute"]
)
limiter.init_app(app)

# Load data
DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), "data", "celebrity_companies.json")
try:
    with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
        CELEBRITY_DATA = json.load(f)
except FileNotFoundError:
    CELEBRITY_DATA = []

CELEBRITY_NAMES = [entry["name"] for entry in CELEBRITY_DATA]

@app.route("/")
def home():
    return "✅ Backend is running!"

@app.route("/search")
@limiter.limit("5/minute")
def search():
    query = request.args.get("q", "").strip()
    sanitized_query = sanitize_input(query)

    if not sanitized_query:
        return error_response("Query parameter 'q' is required and must be valid characters.", 400)

    matches = process.extractBests(sanitized_query, CELEBRITY_NAMES, score_cutoff=60, limit=5)

    if not matches:
        return jsonify({
            "results": [],
            "message": "No company data available yet for this celebrity."
        })

    results = []
    for name, score in matches:
        celeb = next((c for c in CELEBRITY_DATA if c["name"] == name), None)
        if celeb:
            results.append(celeb)

    return jsonify({ "results": results })

@app.errorhandler(429)
def ratelimit_handler(e):
    return error_response("Rate limit exceeded. Please wait before retrying.", 429)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)