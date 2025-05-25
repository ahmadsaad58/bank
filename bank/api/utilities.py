from flask import Blueprint, jsonify

from bank.api.data.data import ACCOUNT_NAME_TO_USERNAME

utilities_bp = Blueprint("utilities", __name__)


@utilities_bp.route("/api/v1/debug/check_cache", methods=["GET"])
def check_account_name_to_username_cache() -> str:
    """Check the account name to username cache. This endpoint is for debugging purposes.
    It returns the current state of the cache.
    ---
    tags:
      - Utilities
    responses:
        200:
            description: A JSON response containing the account name to username mapping.
    """
    return jsonify(ACCOUNT_NAME_TO_USERNAME), 200


@utilities_bp.route("/", methods=["GET"])
def index() -> str:
    """Welcome message for the API.
    ---
    tags:
      - Home
    responses:
        200:
            description: A welcome message for the API.
    """
    return "Welcome to the Simple Bank API!"

@utilities_bp.route("/health", methods=["GET"])
def health_check() -> str:
    """Health check endpoint to verify the API is running.
    ---
    tags:
      - Health Check
    responses:
        200:
            description: A message indicating the API is healthy.
        503:
            description: Service Unavailable if the API is not healthy.
    """
    return "API is healthy!", 200

@utilities_bp.route("/ping", methods=["GET"])
def ping() -> str:
    """Ping endpoint to check if the API is responsive.
    ---
    tags:
      - Ping
    responses:
        200:
            description: A message indicating the API is responsive.
    """
    return "Pong!", 200