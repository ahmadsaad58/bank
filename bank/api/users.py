from flask import Blueprint, jsonify, request

from bank.api.data.data import ACCOUNT_NAME_TO_USERNAME, ACCOUNTS, USERS, save_data
from bank.models.user import ContactInfo, User

users_bp = Blueprint("users", __name__)


@users_bp.route("/api/v1/users", methods=["GET"])
def get_all_users() -> str:
    """Retrieve all users in the system.
    Returns:
        str: A JSON response containing a list of all users.
    """
    users_data = [user.__dict__ for user in USERS.values()]
    return (
        jsonify(
            {
                "users": users_data,
                "count": len(users_data),
            }
        ),
        200,
    )


@users_bp.route("/api/v1/users/<string:user_name>", methods=["GET"])
def get_user(user_name: str) -> str:
    """Retrieve a user by their unique user_id.
    Args:
        user_name (str): The unique username of the user to retrieve.
    Returns:
        str: A JSON response containing the user's information.
    """
    user = USERS.get(user_name, None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.__dict__), 200


@users_bp.route("/api/v1/users", methods=["POST"])
def create_user() -> str:
    """Creates a new user account.
    Returns:
        str: A JSON response containing the created user's information.
    """
    data = request.get_json()
    # Validate the input data
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    required_fields = ["username", "first_name", "last_name", "contact_info"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required user fields"}), 400
    if not all(field in data.get("contact_info", {}) for field in ["email"]):
        return jsonify({"error": "Missing required contact_info fields"}), 400

    # Cannot create a user with an exisiting username
    if data["username"] in USERS:
        return jsonify({"error": "Username already exists"}), 400

    try:
        # Create a new user instance
        new_user = User(
            username=data["username"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            contact_info=ContactInfo(**data["contact_info"]),
        )
        USERS[new_user.username] = new_user
        save_data()
        return (
            jsonify(
                {
                    "message": f"User {new_user.first_name} {new_user.last_name} created",
                    "user": new_user.__dict__,
                }
            ),
            201,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@users_bp.route("/api/v1/users/<string:user_name>", methods=["PUT"])
def update_user(user_name: str) -> str:
    """Update a user's information.
    Args:
        user_name (str): The unique username of the user to update.
    Returns:
        str: A JSON response containing the updated user's information.
    """
    user = USERS.get(user_name, None)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided for update"}), 400

    try:
        if "first_name" in data:
            user.first_name = data["first_name"]
        if "last_name" in data:
            user.last_name = data["last_name"]
        if "contact_info" in data:
            for key, value in data["contact_info"].items():
                setattr(user.contact_info, key, value)
        save_data()
        return (
            jsonify({"message": "User updated successfully.", "user": user.__dict__}),
            200,
        )
    except Exception as e:
        return jsonify({"error": f"Failed to update user: {str(e)}"}), 400


@users_bp.route("/api/v1/users/<string:user_name>", methods=["DELETE"])
def delete_user(user_name: str) -> str:
    """Delete a user by their unique user_id.
    Args:
        user_name (str): The unique username of the user to delete.
    Returns:
        str: A JSON response confirming the deletion of the user.
    """
    user = USERS.get(user_name, None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    USERS.pop(user_name, None)
    accounts_to_remove = ACCOUNTS.pop(user_name, None)
    if accounts_to_remove:
        for bank_account in accounts_to_remove:
            ACCOUNT_NAME_TO_USERNAME.pop(bank_account.account_name, None)
    save_data()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": f"User {user_name} deleted"}), 200
