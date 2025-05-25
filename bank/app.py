from collections import defaultdict
from typing import Dict, List

from flask import Flask, jsonify, request

from bank.models.bank_account import BankAccount
from bank.models.enums import AccountType, TransactionType
from bank.models.transaction import Transaction
from bank.models.user import ContactInfo, User
from bank.utils.utils import parse_boolean_query_param

app = Flask(__name__)

# Store Users: username -> User
USERS: Dict[str, User] = {}
# Store Users: account_name -> username
ACCOUNT_NAME_TO_USERNAME: Dict[str, str] = {}
# Store BankAccounts: username -> List[BankAccount]
ACCOUNTS: Dict[str, List[BankAccount]] = defaultdict(list)
# Store all Transactions, typically linked to accounts for history retrieval
TRANSACTIONS: List[Transaction] = []


@app.route("/", methods=["GET"])
def index() -> str:
    """Welcome message for the API.
    Returns:
        str: A welcome message.
    """
    return "Welcome to the Simple Bank API!"


@app.route("/api/v1/check_account_name_to_username_cache", methods=["GET"])
def check_account_name_to_username_cache() -> str:
    """Check the account name to username cache.
    Returns:
        str: A JSON response containing the account name to username mapping.
    """
    return jsonify(ACCOUNT_NAME_TO_USERNAME), 200


# --- User Management Endpoints ---
@app.route("/api/v1/users", methods=["GET"])
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


@app.route("/api/v1/users/<string:user_name>", methods=["GET"])
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


@app.route("/api/v1/users", methods=["POST"])
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


@app.route("/api/v1/users/<string:user_name>", methods=["PUT"])
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
        return (
            jsonify({"message": "User updated successfully.", "user": user.__dict__}),
            200,
        )
    except Exception as e:
        return jsonify({"error": f"Failed to update user: {str(e)}"}), 400


@app.route("/api/v1/users/<string:user_name>", methods=["DELETE"])
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
    print(accounts_to_remove)
    if accounts_to_remove:
        for bank_account in accounts_to_remove:
            ACCOUNT_NAME_TO_USERNAME.pop(bank_account.account_name, None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": f"User {user_name} deleted"}), 200


# --- Bank Account Management Endpoints ---
@app.route("/api/v1/accounts", methods=["GET"])
def get_all_accounts() -> str:
    """Retrieve all bank accounts in the system.
    Returns:
        str: A JSON response containing a list of all bank accounts associated with the users.
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


@app.route("/api/v1/accounts/<string:user_name>", methods=["GET"])
def get_accounts(user_name: str) -> str:
    """Retrieve bank accounts by user name.
    Args:
        user_name (str): The unique username of the user whose accounts to retrieve.
    Returns:
        str: A JSON response containing the user's bank accounts.
    """
    accounts = ACCOUNTS.get(user_name, None)
    if not accounts:
        return jsonify({"error": "Account not found"}), 404
    return jsonify([account.serialize_dict() for account in accounts]), 200


@app.route("/api/v1/accounts", methods=["POST"])
def create_account() -> str:
    """Creates a new bank account.
    Returns:
        str: A JSON response containing the created bank account's information.
    """
    data = request.get_json()
    required_fields = ["username", "account_type", "initial_deposit", "currency"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required account fields"}), 400

    # If the user does not exist, we cannot create an account
    if data["username"] not in USERS:
        return jsonify({"error": "Username does not exist"}), 400

    print(data["account_type"].upper())

    try:
        new_account = BankAccount(
            account_type=AccountType[data["account_type"].upper()],
            initial_deposit=float(data["initial_deposit"]),
            currency=data["currency"],
            account_owner=data["username"],
        )
        ACCOUNTS[data["username"]].append(new_account)
        ACCOUNT_NAME_TO_USERNAME[new_account.account_name] = data["username"]

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


@app.route("/api/v1/accounts/<string:user_name>/<string:account_name>", methods=["PUT"])
def update_account(user_name: str, account_name: str) -> str:
    """Update a bank account.
    Args:
        user_name (str): The unique username of the user whose account to update.
        account_name (str): The name of the account to update.
    Returns:
        str: A JSON response containing the updated bank account's information.
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


@app.route(
    "/api/v1/accounts/<string:user_name>/<string:account_name>", methods=["DELETE"]
)
def delete_account(user_name: str, account_name: str) -> str:
    """Delete a bank account.
    Args:
        user_name (str): The unique username of the user whose account to update.
        account_name (str): The name of the account to update.
    Returns:
        str: A JSON response containing the updated bank account's information.
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


# --- Transaction Endpoints ---
@app.route(
    "/api/v1/accounts/deposit/<string:user_name>/<string:account_name>",
    methods=["POST"],
)
def deposit(user_name: str, account_name: str) -> str:
    """Deposit into a bank account.
    Args:
        user_name (str): The unique username of the user whose account to deposit into.
        account_name (str): The name of the account to deposit into.
    Returns:
        str: A JSON response containing the created transaction's information and the account modified.
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
    required_fields = ["amount", "currency", "description"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required transaction fields"}), 400

    try:
        new_transaction = Transaction(
            type=TransactionType.DEPOSIT,
            amount=float(data["amount"]),
            currency=data["currency"],
            source_account_name=accounts[account_to_update].account_name,
            description=data["description"],
        )
        TRANSACTIONS.append(new_transaction)
        accounts[account_to_update].process_transaction(new_transaction)

        return (
            jsonify(
                {
                    "message": "Transaction created successfully.",
                    "transaction": new_transaction.serialize_dict(),
                    "account": accounts[account_to_update].serialize_dict(),
                }
            ),
            201,
        )
    except KeyError:
        return jsonify({"error": "Invalid transaction_type"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route(
    "/api/v1/accounts/withdraw/<string:user_name>/<string:account_name>",
    methods=["POST"],
)
def withdraw(user_name: str, account_name: str) -> str:
    """Withdraw from a bank account.
    Args:
        user_name (str): The unique username of the user whose account to withdraw from.
        account_name (str): The name of the account to withdraw from.
    Returns:
        str: A JSON response containing the created transaction's information and the account modified.
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
    required_fields = ["amount", "currency", "description"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required transaction fields"}), 400

    try:
        new_transaction = Transaction(
            type=TransactionType.WITHDRAWAL,
            amount=float(data["amount"]),
            currency=data["currency"],
            source_account_name=accounts[account_to_update].account_name,
            description=data["description"],
        )
        TRANSACTIONS.append(new_transaction)
        accounts[account_to_update].process_transaction(new_transaction)

        return (
            jsonify(
                {
                    "message": "Transaction created successfully.",
                    "transaction": new_transaction.serialize_dict(),
                    "account": accounts[account_to_update].serialize_dict(),
                }
            ),
            201,
        )
    except KeyError:
        return jsonify({"error": "Invalid transaction_type"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route("/api/v1/accounts/transfer", methods=["POST"])
def transfer() -> str:
    """Transfer between accounts.
    Returns:
        str: A JSON response containing the created transaction's information and the accounts modified.
    """
    data = request.get_json()
    required_fields = [
        "amount",
        "currency",
        "source_account_name",
        "destination_account_name",
    ]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required transaction fields"}), 400

    # Find the source and destination accounts
    source_user_name = ACCOUNT_NAME_TO_USERNAME[data["source_account_name"]]
    destination_user_name = ACCOUNT_NAME_TO_USERNAME[data["destination_account_name"]]

    source_accounts = ACCOUNTS.get(source_user_name, None)
    if not source_accounts:
        return jsonify({"error": "Source account not found"}), 404
    destination_accounts = ACCOUNTS.get(destination_user_name, None)
    if not destination_accounts:
        return jsonify({"error": "Destination account not found"}), 404

    source_account_to_update = -1
    for idx, account in enumerate(source_accounts):
        if account.account_name == data["source_account_name"]:
            source_account_to_update = idx
            break
    if source_account_to_update == -1:
        return jsonify({"error": "Source account not found"}), 404

    destination_account_to_update = -1
    for idx, account in enumerate(destination_accounts):
        if account.account_name == data["destination_account_name"]:
            destination_account_to_update = idx
            break
    if destination_account_to_update == -1:
        return jsonify({"error": "Destination account not found"}), 404

    try:
        out_transaction = Transaction(
            type=TransactionType.TRANSFER_OUT,
            amount=float(data["amount"]),
            currency=data["currency"],
            source_account_name=data["source_account_name"],
            destination_account_name=data["destination_account_name"],
        )
        in_transaction = Transaction(
            type=TransactionType.TRANSFER_IN,
            amount=float(data["amount"]),
            currency=data["currency"],
            source_account_name=data["source_account_name"],
            destination_account_name=data["destination_account_name"],
        )

        TRANSACTIONS.extend([out_transaction, in_transaction])
        source_accounts[source_account_to_update].process_transaction(out_transaction)
        destination_accounts[destination_account_to_update].process_transaction(
            in_transaction
        )

        return (
            jsonify(
                {
                    "message": "Transfer Transactions created successfully.",
                    "transfer out transaction": out_transaction.serialize_dict(),
                    "transfer in transaction": in_transaction.serialize_dict(),
                    "source account": source_accounts[
                        source_account_to_update
                    ].serialize_dict(),
                    "destination account": destination_accounts[
                        destination_account_to_update
                    ].serialize_dict(),
                }
            ),
            201,
        )
    except KeyError:
        return jsonify({"error": "Invalid transaction_type"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route("/api/v1/accounts/<string:account_name>", methods=["GET"])
def get_balance_and_transaction_history(account_name: str) -> str:
    """Get the balance of a bank account.
    Args:
        account_name (str): The name of the account to retrieve the balance for.
    Returns:
        str: A JSON response containing the account's balance.
    """
    user_name = ACCOUNT_NAME_TO_USERNAME.get(account_name, None)
    if not user_name:
        return jsonify({"error": "Account not found"}), 404

    accounts = ACCOUNTS.get(user_name, None)
    if not accounts:
        return jsonify({"error": "Account not found"}), 404

    show_balance = parse_boolean_query_param(request.args.get("balance", "false"))
    show_transactions = parse_boolean_query_param(
        request.args.get("transactions", "false")
    )

    for account in accounts:
        if account.account_name == account_name:
            ret = {
                "account_name": account_name,
                "username": user_name,
            }
            if show_transactions:
                ret["transactions"] = [
                    transaction.serialize_dict() for transaction in account.transactions
                ]
            if show_balance:
                ret["balance"] = account.balance

            return (
                jsonify(ret),
                200,
            )

    return jsonify({"error": "Account not found"}), 404


# --- Run the application ---
if __name__ == "__main__":
    # When running in development, you can enable debug mode
    # app.run(debug=True) will automatically reload on code changes
    # and provide a debugger.
    app.run(debug=True, host="0.0.0.0", port=5001)
