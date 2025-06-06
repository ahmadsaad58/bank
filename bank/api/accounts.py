from flask import Blueprint, jsonify, request

from bank.api.data.data import (ACCOUNT_NAME_TO_USERNAME, ACCOUNTS, USERS,
                                save_data)
from bank.models.bank_account import BankAccount
from bank.models.enums import AccountType

accounts_bp = Blueprint("accounts", __name__)


@accounts_bp.route("/api/v1/accounts", methods=["GET"])
def get_all_accounts() -> str:
    """Retrieve all bank accounts in the system.
    ---
    tags:
      - Accounts
    responses:
        200:
            description: A JSON response containing a list of all bank accounts.
        404:
            description: No accounts found.
    """
    accounts_data = {
        user: [account.serialize_dict() for account in accounts]
        for user, accounts in ACCOUNTS.items()
    }
    return (
        jsonify(
            {
                "accounts": accounts_data,
                "users_with_accounts_count": len(accounts_data),
            }
        ),
        200,
    )


@accounts_bp.route("/api/v1/accounts/<string:user_name>", methods=["GET"])
def get_accounts(user_name: str) -> str:
    """Retrieve bank accounts by user name.
    ---
    tags:
      - Accounts
    parameters:
        - name: user_name
          in: path
          required: true
          description: The unique username of the user whose accounts to retrieve.
          schema:
            type: string
    responses:
        200:
            description: A JSON response containing the user's bank accounts.
        404:
            description: User not found.
    """
    accounts = ACCOUNTS.get(user_name, None)
    if not accounts:
        return jsonify({"error": "Account not found"}), 404
    return jsonify([account.serialize_dict() for account in accounts]), 200


@accounts_bp.route("/api/v1/accounts", methods=["POST"])
def create_account() -> str:
    """Creates a new bank account.
    ---
    tags:
      - Accounts
    parameters:
        - name: account
          in: body
          required: true
          description: The account object to create.
          schema:
            type: object
            properties:
                username:
                    type: string
                account_type:
                    type: string
                initial_deposit:
                    type: number
                currency:
                    type: string
    responses:
        201:
            description: A JSON response containing the created bank account's information.
        400:
            description: Bad request, missing required fields or invalid data.
    """
    data = request.get_json()
    required_fields = ["username", "account_type", "initial_deposit", "currency"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required account fields"}), 400

    # If the user does not exist, we cannot create an account
    if data["username"] not in USERS:
        return jsonify({"error": "Username does not exist"}), 400

    try:
        new_account = BankAccount(
            account_type=AccountType[data["account_type"].upper()],
            initial_deposit=float(data["initial_deposit"]),
            currency=data["currency"],
            account_owner=data["username"],
        )
        ACCOUNTS[data["username"]].append(new_account)
        ACCOUNT_NAME_TO_USERNAME[new_account.account_name] = data["username"]
        save_data()

        return (
            jsonify(
                {
                    "message": "Account created successfully.",
                    "account": new_account.serialize_dict(),
                }
            ),
            201,
        )
    except KeyError:
        return jsonify({"error": "Invalid account_type"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@accounts_bp.route(
    "/api/v1/accounts/<string:user_name>/<string:account_name>", methods=["PUT"]
)
def update_account(user_name: str, account_name: str) -> str:
    """Update a bank account.
    ---
    tags:
      - Accounts
    parameters:
        - name: user_name
          in: path
          required: true
          description: The unique username of the user whose account to update.
          schema:
            type: string
        - name: account_name
          in: path
          required: true
          description: The name of the account to update.
          schema:
            type: string
        - name: account
          in: body
          required: true
          description: The account object with updated information.
          schema:
            type: object
            properties:
              account_type:
                type: string
              currency:
                type: string
              balance:
                type: number
    responses:
        200:
            description: A JSON response containing the updated bank account's information.
        400:
            description: Bad request, missing required fields or invalid data.
        404:
            description: Account not found.
    """
    accounts = ACCOUNTS.get(user_name, None)
    if not accounts:
        return jsonify({"error": "Account not found"}), 404

    account_to_update = -1
    for idx, account in enumerate(accounts):
        if account.account_name == account_name:
            account_to_update = idx
            break
    if account_to_update == -1:
        return jsonify({"error": "Account not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided for update"}), 400

    try:
        if "account_type" in data:
            accounts[account_to_update].account_type = AccountType[
                data["account_type"].upper()
            ]
        if "currency" in data:
            accounts[account_to_update].currency = data["currency"]
        if "balance" in data:
            accounts[account_to_update].balance = float(data["balance"])
        save_data()
        return (
            jsonify(
                {
                    "message": "Account updated successfully.",
                    "accounts": accounts[account_to_update].serialize_dict(),
                }
            ),
            200,
        )
    except KeyError:
        return jsonify({"error": "Invalid account_type"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update account: {str(e)}"}), 500


@accounts_bp.route(
    "/api/v1/accounts/<string:user_name>/<string:account_name>", methods=["DELETE"]
)
def delete_account(user_name: str, account_name: str) -> str:
    """Delete a bank account.
    ---
    tags:
      - Accounts
    parameters:
        - name: user_name
          in: path
          required: true
          description: The unique username of the user whose account to delete.
          schema:
            type: string
        - name: account_name
          in: path
          required: true
          description: The name of the account to delete.
          schema:
            type: string
    responses:
        200:
            description: A JSON response confirming the deletion of the account.
        404:
            description: Account not found.
    """
    accounts = ACCOUNTS.get(user_name, None)
    if not accounts:
        return jsonify({"error": "Account not found"}), 404

    account_to_update = -1
    for idx, account in enumerate(accounts):
        if account.account_name == account_name:
            account_to_update = idx
            break
    if account_to_update == -1:
        return jsonify({"error": "Account not found"}), 404

    try:
        accounts.pop(account_to_update)
        ACCOUNT_NAME_TO_USERNAME.pop(account_name, None)
        save_data()
        return (
            jsonify({"message": "Account deleted successfully."}),
            200,
        )
    except KeyError:
        return jsonify({"error": "Invalid account_type"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update account: {str(e)}"}), 500
