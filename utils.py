import re
from flask import request, jsonify

def sanitize_input(query: str) -> str:
    """
    Sanitize user input by allowing only alphanumeric characters, spaces, and basic punctuation.
    Return sanitized string or empty string if invalid.
    """
    if not query:
        return ""
    # Allow letters, numbers, spaces, dot, hyphen, apostrophe
    sanitized = re.sub(r"[^a-zA-Z0-9\s\.\-\']", "", query)
    return sanitized.strip()

def error_response(message: str, status_code: int = 400):
    """
    JSON error response helper
    """
    return jsonify({"error": message}), status_code
