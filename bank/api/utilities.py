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